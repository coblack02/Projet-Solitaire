from copy import deepcopy
from piles import Stock, DiscardPile, FinalPile
from files import Grid, Game_queue
from typing import Union
from cartes import Card


class Game:
    """Represents the overall game state."""

    def __init__(self):
        self.stock = Stock()
        self.stock.shuffle()
        self.discard_pile = DiscardPile()
        self.final_piles = [FinalPile() for _ in range(4)]
        self.grid = Grid(self.stock)


class Save:
    """Handles saving and undoing game states."""

    def __init__(self, game: Game):
        self.game = game
        self.history = []

    def save_state(self):
        """Save current game state."""
        state = {
            "stock": deepcopy(self.game.stock),
            "discard_pile": deepcopy(self.game.discard_pile),
            "final_piles": deepcopy(self.game.final_piles),
            "grid": deepcopy(self.game.grid),
        }
        self.history.append(state)

    def undo(self):
        """Restore previous game state."""
        if self.history:
            state = self.history.pop()
            self.game.stock = state["stock"]
            self.game.discard_pile = state["discard_pile"]
            self.game.final_piles = state["final_piles"]
            self.game.grid = state["grid"]


class GameController(Game):
    """Manages game state, player actions, and saving/loading."""

    def __init__(self):
        super().__init__()
        self.save = Save(self)
        self.turns = 0

    def recycle_discard_to_stock(self):
        """Recycle all cards from the discard pile back to the stock."""
        while not self.discard_pile.is_empty():
            card = self.discard_pile.pop()
            if card:
                self.stock.push(card)

    def draw_from_stock(self):
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

    def _normalize_grid(self):
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

    def _reveal_top_card(self, pile_index: int):
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
    ):
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

    def undo_move(self):
        """Undo the last move."""
        if self.save.history:
            self.save.undo()
            self.turns += 1
            self._normalize_grid()

    def all_tableau_cards_revealed(self):
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

    def can_move_to_foundation(self, card: Card):
        """Check if a card can be moved to any foundation pile."""
        for foundation in self.final_piles:
            if foundation.can_stack(card):
                return foundation
        return None

    def auto_complete(self):
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

        return True

    def check_and_auto_complete(self):
        """Check if all tableau cards are revealed and start auto-completion."""
        if self.all_tableau_cards_revealed():
            return self.auto_complete()
        return False