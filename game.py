from copy import deepcopy
from piles import Stock, DiscardPile, FinalPile
from files import Grid, Game_queue


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
        else:
            print("No more undos available.")


class GameController(Game):
    """Manages game state, player actions, and saving/loading."""

    def __init__(self):
        super().__init__()
        self.save = Save(self)
        self.turns = 0

    def recycle_discard_to_stock(self):
        """Remet toutes les cartes de la défausse dans le stock."""
        while not self.discard_pile.is_empty():
            card = self.discard_pile.pop()
            if card:
                self.stock.push(card)

    def draw_from_stock(self):
        """Draw up to three cards from the stock to the discard pile."""
        # Si le stock est vide, recycler la défausse
        if self.stock.is_empty():
            if not self.discard_pile.is_empty():
                self.recycle_discard_to_stock()
                self.turns += 1
                self.save.save_state()
                self._normalize_grid()
                return
            else:
                print("Stock and discard pile are both empty.")
                return
        
        # Tirer normalement 3 cartes
        drawn_cards = self.stock.draw()
        if drawn_cards:
            for card in drawn_cards:
                self.discard_pile.push(card)
            self.turns += 1
            self.save.save_state()
            self._normalize_grid()

    def _normalize_grid(self):
        """Normalise la grille si la méthode existe."""
        try:
            if hasattr(self.grid, 'normalize'):
                self.grid.normalize()
        except Exception as e:
            print(f"Warning: normalize failed - {e}")

    def move_from_discard(self, destination):
        """Move top card from discard pile to destination."""
        card_to_move = self.discard_pile.pop()
        dest_pile_index = None
        
        # Identifier l'index si la destination est dans le tableau
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
                    self.save.save_state()
                    self._normalize_grid()
                    # Vérifier si on peut auto-compléter
                    self.check_and_auto_complete()
                    return True
                else:
                    self.discard_pile.push(card_to_move)
                    print("Invalid move from discard pile.")
                    return False
            elif isinstance(destination, Game_queue):
                if destination.can_stack(card_to_move):
                    destination.enqueue(card_to_move)
                    self.turns += 1
                    self.save.save_state()
                    self._normalize_grid()
                    return True
                else:
                    self.discard_pile.push(card_to_move)
                    print("Invalid move from discard pile.")
                    return False
        return False

    def _reveal_top_card(self, pile_index):
        """Révèle la carte du dessus d'une pile du tableau après un déplacement."""
        try:
            elem = self.grid.game[pile_index]
            queue = elem[0]  # Cartes visibles
            stack = elem[1]  # Cartes cachées
            
            # Si la queue est vide et le stack a des cartes
            if queue.is_empty() and not stack.is_empty():
                # Prendre la carte du dessus du stack
                card = stack.pop()
                if card:
                    # La retourner face visible
                    card.face = True
                    # La mettre dans la queue
                    queue.enqueue(card)
                    print(f"Carte révélée sur la pile {pile_index}: {card.value} de {card.family}")
                    # Vérifier si on peut auto-compléter après révélation
                    self.check_and_auto_complete()
        except Exception as e:
            print(f"Erreur lors de la révélation de carte: {e}")

    def move_card(self, source, destination, num_cards=1):
        """Move card(s) from source to destination if the move is valid."""
        source_pile_index = None
        
        # Identifier l'index de la pile source dans le tableau
        for i, elem in enumerate(self.grid.game):
            if elem[0] == source:  # elem[0] est la queue
                source_pile_index = i
                break
        
        if isinstance(source, Game_queue) and isinstance(destination, Game_queue):
            if source.move(num_cards, destination):
                self.turns += 1
                # Révéler la carte derrière si nécessaire
                if source_pile_index is not None:
                    self._reveal_top_card(source_pile_index)
                self.save.save_state()
                self._normalize_grid()
                return True
            else:
                print("Invalid move between tableau piles.")
                return False

        elif isinstance(source, Game_queue) and isinstance(destination, FinalPile):
            card_to_move = source.dequeue()
            if card_to_move and destination.can_stack(card_to_move):
                destination.push(card_to_move)
                self.turns += 1
                # Révéler la carte derrière si nécessaire
                if source_pile_index is not None:
                    self._reveal_top_card(source_pile_index)
                self.save.save_state()
                self._normalize_grid()
                # Vérifier si on peut auto-compléter
                self.check_and_auto_complete()
                return True
            else:
                if card_to_move:
                    source.enqueue(card_to_move)
                print("Invalid move from tableau to foundation.")
                return False

        elif isinstance(source, FinalPile) and isinstance(destination, Game_queue):
            card_to_move = source.pop()
            if card_to_move and destination.can_stack(card_to_move):
                destination.enqueue(card_to_move)
                self.turns += 1
                self.save.save_state()
                self._normalize_grid()
                return True
            else:
                if card_to_move:
                    source.push(card_to_move)
                print("Invalid move from foundation to tableau.")
                return False

        return False

    def undo_move(self):
        """Undo the last move."""
        self.save.undo()
        self.turns += 1
        self._normalize_grid()

    def all_tableau_cards_revealed(self):
        """Vérifie si toutes les cartes du tableau sont retournées (face visible)."""
        try:
            for elem in self.grid.game:
                stack = elem[1]  # Cartes cachées
                # Si le stack a encore des cartes, toutes ne sont pas révélées
                try:
                    if not stack.is_empty():
                        return False
                except:
                    if len(list(stack.items)) > 0:
                        return False
            return True
        except Exception as e:
            print(f"Erreur lors de la vérification: {e}")
            return False

    def can_move_to_foundation(self, card):
        """Vérifie si une carte peut être placée sur une fondation."""
        for foundation in self.final_piles:
            if foundation.can_stack(card):
                return foundation
        return None

    def auto_complete(self):
        """Termine automatiquement le jeu en plaçant toutes les cartes sur les fondations."""
        print("🎉 Auto-complétion activée !")
        moves_made = True
        
        # Callback pour l'animation (sera défini par l'interface)
        redraw_callback = getattr(self, '_redraw_callback', None)
        
        while moves_made:
            moves_made = False
            
            # Essayer de déplacer depuis la défausse
            if not self.discard_pile.is_empty():
                top_card = self.discard_pile.peek()
                foundation = self.can_move_to_foundation(top_card)
                if foundation:
                    card = self.discard_pile.pop()
                    foundation.push(card)
                    self.turns += 1
                    moves_made = True
                    # Redessiner pour voir l'animation
                    if redraw_callback:
                        redraw_callback()
                        import time
                        time.sleep(0.15)  # Pause de 150ms entre chaque carte
                    continue
            
            # Essayer de déplacer depuis chaque pile du tableau
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
                            # Révéler la carte suivante si nécessaire
                            stack = elem[1]
                            if queue.is_empty() and not stack.is_empty():
                                hidden_card = stack.pop()
                                hidden_card.face = True
                                queue.enqueue(hidden_card)
                            moves_made = True
                            # Redessiner pour voir l'animation
                            if redraw_callback:
                                redraw_callback()
                                import time
                                time.sleep(0.15)  # Pause de 150ms entre chaque carte
                            break
                except Exception as e:
                    print(f"Erreur: {e}")
                    pass
        
        print("✅ Auto-complétion terminée !")
        return True

    def check_and_auto_complete(self):
        """Vérifie si toutes les cartes sont révélées et lance l'auto-complétion."""
        if self.all_tableau_cards_revealed():
            print("🎯 Toutes les cartes sont révélées ! Lancement de l'auto-complétion...")
            return self.auto_complete()
        return False
