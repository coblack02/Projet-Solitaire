from copy import deepcopy
from piles import Stock, DiscardPile, FinalPile
from files import Grid, Game_queue
from typing import Union
import tkinter as tk
from cartes import Card


class Game:
    """Represents the overall game state."""

    def __init__(self) -> None:
        self.stock = Stock()
        self.stock.shuffle()
        self.discard_pile = DiscardPile()
        self.final_piles = [FinalPile() for _ in range(4)]
        self.grid = Grid(self.stock)


class Save:
    """Handles saving and undoing game states."""

    def __init__(self, game: Game) -> None:
        self.game = game
        self.history = []

    def save_state(self) -> None:
        """Save current game state."""
        state = {
            "stock": deepcopy(self.game.stock),
            "discard_pile": deepcopy(self.game.discard_pile),
            "final_piles": deepcopy(self.game.final_piles),
            "grid": deepcopy(self.game.grid),
        }
        self.history.append(state)

    def undo(self) -> None:
        """Restore previous game state."""
        if self.history:
            state = self.history.pop()
            self.game.stock = state["stock"]
            self.game.discard_pile = state["discard_pile"]
            self.game.final_piles = state["final_piles"]
            self.game.grid = state["grid"]


class GameController(Game):
    """Manages game state, player actions, and saving/loading."""

    def __init__(self) -> None:
        super().__init__()
        self.save = Save(self)
        self.turns = 0
        # Optional callback that will be called when the game is completed
        self.on_victory = None

    def recycle_discard_to_stock(self) -> None:
        """Recycle all cards from the discard pile back to the stock."""
        while not self.discard_pile.is_empty():
            card = self.discard_pile.pop()
            if card:
                self.stock.push(card)

    def draw_from_stock(self) -> None:
        """Draw up to three cards from the stock to the discard pile."""
        self.save.save_state()

        if self.stock.is_empty():
            if not self.discard_pile.is_empty():
                self.recycle_discard_to_stock()
                self.turns += 1
                self._normalize_grid()
                return
            else:
                return

        drawn_cards = self.stock.draw()
        if drawn_cards:
            for card in drawn_cards:
                self.discard_pile.push(card)
            self.turns += 1
            self._normalize_grid()

    def _normalize_grid(self) -> None:
        """Normalize the grid if the method exists."""
        try:
            if hasattr(self.grid, "normalize"):
                self.grid.normalize()
        except Exception as e:
            pass

    def move_from_discard(self, destination: Union[FinalPile, Game_queue]) -> bool:
        """Move top card from discard pile to destination."""
        self.save.save_state()

        card_to_move = self.discard_pile.pop()
        dest_pile_index = None

        if isinstance(destination, Game_queue):
            for i, elem in enumerate(self.grid.game):
                if elem[0] == destination:
                    dest_pile_index = i
                    break

        if card_to_move:
            if isinstance(destination, FinalPile):
                if destination.can_stack(card_to_move):
                    destination.push(card_to_move)
                    self.turns += 1
                    self._normalize_grid()
                    self.check_and_auto_complete()
                    return True
                else:
                    self.discard_pile.push(card_to_move)
                    self.save.history.pop()
                    return False
            elif isinstance(destination, Game_queue):
                if destination.can_stack(card_to_move):
                    destination.enqueue(card_to_move)
                    self.turns += 1
                    self._normalize_grid()
                    return True
                else:
                    self.discard_pile.push(card_to_move)
                    self.save.history.pop()
                    return False
        return False

    def _reveal_top_card(self, pile_index: int) -> None:
        """reveal the top hidden card of the specified tableau pile if needed."""
        try:
            elem = self.grid.game[pile_index]
            queue = elem[0]
            stack = elem[1]

            if queue.is_empty() and not stack.is_empty():
                card = stack.pop()
                if card:
                    card.face = True
                    queue.enqueue(card)
                    self.check_and_auto_complete()
        except Exception as e:
            pass

    def move_card(
        self,
        source: Union[Game_queue, FinalPile],
        destination: Union[Game_queue, FinalPile],
        num_cards: int = 1,
    ) -> bool:
        """Move card from source to destination if the move is valid."""
        self.save.save_state()

        source_pile_index = None

        for i, elem in enumerate(self.grid.game):
            if elem[0] == source:
                source_pile_index = i
                break

        if isinstance(source, Game_queue) and isinstance(destination, Game_queue):
            if source.move(num_cards, destination):
                self.turns += 1
                if source_pile_index is not None:
                    self._reveal_top_card(source_pile_index)
                self._normalize_grid()
                return True
            else:
                self.save.history.pop()
                return False

        elif isinstance(source, Game_queue) and isinstance(destination, FinalPile):
            card_to_move = source.dequeue()
            if card_to_move and destination.can_stack(card_to_move):
                destination.push(card_to_move)
                self.turns += 1
                if source_pile_index is not None:
                    self._reveal_top_card(source_pile_index)
                self._normalize_grid()
                self.check_and_auto_complete()
                return True
            else:
                if card_to_move:
                    source.enqueue(card_to_move)
                self.save.history.pop()
                return False

        elif isinstance(source, FinalPile) and isinstance(destination, Game_queue):
            card_to_move = source.pop()
            if card_to_move and destination.can_stack(card_to_move):
                destination.enqueue(card_to_move)
                self.turns += 1
                self._normalize_grid()
                return True
            else:
                if card_to_move:
                    source.push(card_to_move)
                self.save.history.pop()
                return False

        return False

    def undo_move(self) -> None:
        """Undo the last move."""
        if self.save.history:
            self.save.undo()
            self.turns += 1
            self._normalize_grid()

    def all_tableau_cards_revealed(self) -> bool:
        """check if all tableau cards are revealed."""
        try:
            for elem in self.grid.game:
                stack = elem[1]
                try:
                    if not stack.is_empty():
                        return False
                except:
                    if len(list(stack.items)) > 0:
                        return False
            return True
        except Exception as e:
            return False

    def can_move_to_foundation(self, card: Card) -> Union[FinalPile, None]:
        """Check if a card can be moved to any foundation pile."""
        for foundation in self.final_piles:
            if foundation.can_stack(card):
                return foundation
        return None

    def auto_complete(self) -> None:
        """Automatically complete the game by placing all cards on the foundations."""
        moves_made = True
        redraw_callback = getattr(self, "_redraw_callback", None)

        while moves_made:
            moves_made = False

            if not self.discard_pile.is_empty():
                top_card = self.discard_pile.peek()
                foundation = self.can_move_to_foundation(top_card)
                if foundation:
                    card = self.discard_pile.pop()
                    foundation.push(card)
                    self.turns += 1
                    moves_made = True
                    if redraw_callback:
                        redraw_callback()
                        import time

                        time.sleep(0.15)
                    continue

            for i, elem in enumerate(self.grid.game):
                queue = elem[0]
                try:
                    if not queue.is_empty():
                        top_card = queue.peek()
                        foundation = self.can_move_to_foundation(top_card)
                        if foundation:
                            card = queue.dequeue()
                            foundation.push(card)
                            self.turns += 1
                            stack = elem[1]
                            if queue.is_empty() and not stack.is_empty():
                                hidden_card = stack.pop()
                                hidden_card.face = True
                                queue.enqueue(hidden_card)
                            moves_made = True
                            if redraw_callback:
                                redraw_callback()
                                import time

                                time.sleep(0.15)
                            break
                except Exception as e:
                    pass

        # After auto-complete finishes, if all foundations are full show a victory overlay
        try:
            complete = all([p.size() == 13 for p in self.final_piles])
            if complete:
                # Try to get the UI app instance from the redraw callback
                redraw_callback = getattr(self, '_redraw_callback', None)
                app_instance = None
                try:
                    if callable(redraw_callback) and hasattr(redraw_callback, '__self__'):
                        app_instance = redraw_callback.__self__
                except Exception:
                    app_instance = None

                if app_instance is not None:
                    ui_root = getattr(app_instance, 'root', None)
                    menu_root = getattr(app_instance, '_menu_root', None)
                    if ui_root is not None:
                        # Create overlay on UI root
                        overlay = tk.Toplevel(ui_root)
                        overlay.attributes("-fullscreen", True)
                        overlay.config(bg="black")
                        try:
                            overlay.attributes("-alpha", 0.85)
                        except Exception:
                            pass

                        frame = tk.Frame(overlay, bg="black")
                        frame.place(relx=0.5, rely=0.5, anchor="center")
                        label = tk.Label(frame, text="Victoire!", font=("Arial", 64, "bold"), fg="white", bg="black")
                        label.pack(padx=20, pady=20)

                        def finish():
                            try:
                                overlay.destroy()
                            except Exception:
                                pass
                            try:
                                ui_root.destroy()
                            except Exception:
                                pass
                            try:
                                if menu_root:
                                    menu_root.deiconify()
                            except Exception:
                                pass

                        overlay.after(4000, finish)
                else:
                    # No UI instance available; nothing to display here
                    pass
        except Exception:
            pass

        return True

    def check_and_auto_complete(self) -> bool:
        """Check if all tableau cards are revealed and start auto-completion."""
        if self.all_tableau_cards_revealed():
            return self.auto_complete()
        return False

    def find_best_hint(self) -> Union[dict, None]:
        """Find the best move hint for the player."""
        hints = []

        # Priority 1: Move to foundation (highest priority)
        # Check discard pile
        if not self.discard_pile.is_empty():
            top_card = self.discard_pile.peek()
            foundation = self.can_move_to_foundation(top_card)
            if foundation:
                foundation_index = self.final_piles.index(foundation)
                hints.append(
                    {
                        "priority": 1,
                        "type": "discard_to_foundation",
                        "card": top_card,
                        "foundation_index": foundation_index,
                        "message": f"Placer {top_card.value} de {top_card.family} de la défausse vers la fondation {foundation_index + 1}",
                    }
                )

        # Check tableau piles for moves to foundation
        for i, elem in enumerate(self.grid.game):
            queue = elem[0]
            try:
                if not queue.is_empty():
                    top_card = queue.peek()
                    foundation = self.can_move_to_foundation(top_card)
                    if foundation:
                        foundation_index = self.final_piles.index(foundation)
                        hints.append(
                            {
                                "priority": 1,
                                "type": "tableau_to_foundation",
                                "card": top_card,
                                "source_pile": i,
                                "foundation_index": foundation_index,
                                "message": f"Placer {top_card.value} de {top_card.family} de la colonne {i + 1} vers la fondation {foundation_index + 1}",
                            }
                        )
            except:
                pass

        # Priority 2: Reveal hidden cards
        for i, elem in enumerate(self.grid.game):
            queue = elem[0]
            stack = elem[1]
            try:
                if not queue.is_empty():
                    # Check if moving this pile would reveal a hidden card
                    try:
                        if queue.size() > 0 and not stack.is_empty():
                            top_card = queue.peek()
                            # Try to find a destination for this card
                            for j, dest_elem in enumerate(self.grid.game):
                                if i != j:
                                    dest_queue = dest_elem[0]
                                    if dest_queue.can_stack(top_card):
                                        hints.append(
                                            {
                                                "priority": 2,
                                                "type": "tableau_to_tableau_reveal",
                                                "card": top_card,
                                                "source_pile": i,
                                                "dest_pile": j,
                                                "message": f"Déplacer {top_card.value} de {top_card.family} de la colonne {i + 1} vers la colonne {j + 1} pour révéler une carte",
                                            }
                                        )
                    except:
                        pass
            except:
                pass

        # Priority 3: Move from discard to tableau
        if not self.discard_pile.is_empty():
            top_card = self.discard_pile.peek()
            for i, elem in enumerate(self.grid.game):
                queue = elem[0]
                if queue.can_stack(top_card):
                    hints.append(
                        {
                            "priority": 3,
                            "type": "discard_to_tableau",
                            "card": top_card,
                            "dest_pile": i,
                            "message": f"Placer {top_card.value} de {top_card.family} de la défausse vers la colonne {i + 1}",
                        }
                    )

        # Priority 4: General tableau moves
        for i, elem in enumerate(self.grid.game):
            queue = elem[0]
            try:
                if not queue.is_empty():
                    # Try moving multiple cards
                    cards_list = list(queue.items)
                    for card_idx, card in enumerate(cards_list):
                        for j, dest_elem in enumerate(self.grid.game):
                            if i != j:
                                dest_queue = dest_elem[0]
                                if dest_queue.can_stack(card):
                                    num_cards = len(cards_list) - card_idx
                                    hints.append(
                                        {
                                            "priority": 4,
                                            "type": "tableau_to_tableau",
                                            "card": card,
                                            "source_pile": i,
                                            "dest_pile": j,
                                            "num_cards": num_cards,
                                            "message": f"Déplacer {num_cards} carte(s) de la colonne {i + 1} vers la colonne {j + 1}",
                                        }
                                    )
            except:
                pass

        # Priority 5: Draw from stock
        if not self.stock.is_empty():
            hints.append(
                {
                    "priority": 5,
                    "type": "draw_stock",
                    "message": "Piocher 3 cartes du stock",
                }
            )
        elif not self.discard_pile.is_empty():
            hints.append(
                {
                    "priority": 5,
                    "type": "recycle_stock",
                    "message": "Recycler la défausse vers le stock",
                }
            )

        # Sort by priority and return the best hint
        if hints:
            hints.sort(key=lambda h: h["priority"])
            return hints[0]

        return None

    def get_hint_message(self):
        """Get a hint message for the player."""
        hint = self.find_best_hint()
        if hint:
            return hint
        else:
            return {
                "message": "Aucun coup évident disponible. Essayez de piocher ou de réorganiser les colonnes."
            }
