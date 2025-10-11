from tkinter import Tk, Label
from PIL import Image, ImageTk
import random
from collections import deque
from copy import deepcopy

# cards defini
family = ("pique", "trefle", "carreau", "coeur")
height = ("as", "2", "3", "4", "5", "6", "7", "8", "9", "10", "valet", "dame", "roi")
root = Tk()


class Stack:
    def __init__(self):
        self.items = deque()

    def is_empty(self):
        return len(self.items) == 0

    def push(self, item):
        self.items.append(item)

    def pop(self):
        if not self.is_empty():
            return self.items.pop()
        else:
            return None

    def peek(self):
        if not self.is_empty():
            return self.items[-1]
        else:
            return None

    def size(self):
        return len(self.items)


class Queue:
    def __init__(self):
        self.items = deque()

    def is_empty(self):
        return len(self.items) == 0

    def enqueue(self, item):
        self.items.appendleft(item)

    def dequeue(self):
        if not self.is_empty():
            return self.items.pop()
        else:
            return None

    def peek(self):
        if not self.is_empty():
            return self.items[-1]
        else:
            return None

    def size(self):
        return len(self.items)


class Card:
    def __init__(self, c: str, h: str):
        self.family = c
        self.value = h
        self.face = False

    def print_card(self):
        """Print the card's value and family."""
        randcard = Image.open("cartes/" + self.value + "_" + self.family + ".gif")
        photo = ImageTk.PhotoImage(randcard)
        label = Label(root, image=photo)
        label.pack()


class Stock(Stack):
    def __init__(self):
        super().__init__()
        # Create deck of 52 cards
        for c in range(4):
            for h in range(13):
                new_card = Card(family[c], height[h])
                self.push(new_card)

    def shuffle(self):
        """Shuffle the deck of cards."""
        temp_list = list(self.items)
        random.shuffle(temp_list)
        self.items = deque(temp_list)

    def draw(self):
        """Draw up to three cards from the stock."""
        t = self.size()
        res = []
        if t >= 3:
            carte1, carte2, carte3 = self.pop(), self.pop(), self.pop()
            return [carte1, carte2, carte3]
        elif t > 0:
            for _ in range(t):
                carte = self.pop()
                res.append(carte)
            return res
        else:
            return None


class DiscardPile(Stack):
    """Represents the discard pile in Solitaire."""

    def __init__(self):
        super().__init__()

    def draw(self):
        """Remove and return the top card of the discard pile."""
        return self.pop()

    def top(self):
        """Returns the top card of the discard pile without removing it."""
        return self.peek()

    def visible(self):
        """Returns up to three cards from the top of the discard pile without removing them."""
        t = self.size()
        res = []
        if t >= 3:
            # Get the last 3 items without removing them
            res = [self.items[-3], self.items[-2], self.items[-1]]
            return res
        elif t > 0:
            res = list(self.items)
            return res
        else:
            return None


class FinalPile(Stack):
    """Represents one of the four foundation piles in Solitaire."""

    def __init__(self):
        super().__init__()

    def can_stack(self, elem: Card):
        """Check if a card can be placed on this final pile."""
        if self.is_empty():
            return elem.value == "as"
        else:
            top_card = self.peek()
            if top_card.family == elem.family:
                top_index = height.index(top_card.value)
                elem_index = height.index(elem.value)
                return elem_index == top_index + 1
            else:
                return False

    def stack(self, elem: Card):
        """Place a card on this final pile if the move is valid."""
        if self.can_stack(elem):
            self.push(elem)
            return True
        else:
            return False


class Game_queue(Queue):
    """Represents one of the seven tableau piles in Solitaire."""

    def __init__(self, stock, length):
        super().__init__()
        # Draw cards from the shared stock
        for _ in range(length):
            card = stock.pop()
            if card:
                self.enqueue(card)

    def can_stack(self, elem: Card):
        """Check if a card can be placed on this tableau pile."""
        if self.is_empty():
            return elem.value == "roi"
        else:
            top_card = self.peek()
            if top_card.family in ("pique", "trefle"):
                return (
                    elem.family in ("coeur", "carreau")
                    and height.index(elem.value) == height.index(top_card.value) - 1
                )
            elif top_card.family in ("coeur", "carreau"):
                return (
                    elem.family in ("pique", "trefle")
                    and height.index(elem.value) == height.index(top_card.value) - 1
                )
            else:
                return False

    def move(self, num_cards: int, destination_queue):
        """Move the bottom num_cards cards from this queue to destination."""
        if num_cards > self.size():
            return False

        temp = Stack()

        # Remove num_cards from bottom
        for _ in range(num_cards):
            card = self.dequeue()
            if card:
                temp.push(card)

        # Check if top card of temp can be placed on destination
        top_card = temp.peek()
        if top_card and destination_queue.can_stack(top_card):
            # Place cards on destination
            while not temp.is_empty():
                destination_queue.enqueue(temp.pop())
            return True
        else:
            # Put cards back
            while not temp.is_empty():
                self.enqueue(temp.pop())
            return False


class Grid:
    """Represents the seven tableau piles in Solitaire."""

    def __init__(self, stock):
        self.piles = [Game_queue(stock, i) for i in range(1, 8)]


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
