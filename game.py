
from copy import deepcopy
from piles import Stock,DiscardPile,FinalPile
from files import Grid,Game_queue



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

    def draw_from_stock(self):
        """Draw up to three cards from the stock to the discard pile."""
        drawn_cards = self.stock.draw()
        if drawn_cards:
            for card in drawn_cards:
                self.discard_pile.push(card)
            self.turns += 1
            self.save.save_state()
        else:
            print("Stock is empty.")

    def move_from_discard(self, destination):
        """Move top card from discard pile to destination."""
        card_to_move = self.discard_pile.pop()
        if card_to_move:
            if isinstance(destination, FinalPile):
                if destination.can_stack(card_to_move):
                    destination.push(card_to_move)
                    self.turns += 1
                    self.save.save_state()
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
                    return True
                else:
                    self.discard_pile.push(card_to_move)
                    print("Invalid move from discard pile.")
                    return False
        return False

    def move_card(self, source, destination, num_cards=1):
        """Move card(s) from source to destination if the move is valid."""
        if isinstance(source, Game_queue) and isinstance(destination, Game_queue):
            if source.move(num_cards, destination):
                self.turns += 1
                self.save.save_state()
                return True
            else:
                print("Invalid move between tableau piles.")
                return False

        elif isinstance(source, Game_queue) and isinstance(destination, FinalPile):
            card_to_move = source.dequeue()
            if card_to_move and destination.can_stack(card_to_move):
                destination.push(card_to_move)
                self.turns += 1
                self.save.save_state()
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