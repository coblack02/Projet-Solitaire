from tkinter import Tk, Label
from PIL import Image, ImageTk
import random
from collections import deque

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
    def __init__(self, c, h):
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
        self.deck = Stack()  # the deck is an array of 52 cards (4x13)
        for c in range(4):
            for h in range(13):
                new_card = Card(family[c], height[h])  # height starts at 1
                self.deck.push(new_card)

    def shuffle(self):
        """Shuffle the deck of cards."""
        t = self.deck.size()
        for _ in range(t):
            h1, h2 = random.randint(t), random.randint(t)
            self.deck[h1], self.deck[h2] = self.deck[h2], self.deck[h1]

    def draw(self):  # depile
        t = self.deck.size()
        res = []
        if t >= 3:
            carte1, carte2, carte3 = self.deck.pop(), self.deck.pop(), self.deck.pop()
            return [carte1, carte2, carte3]
        elif t > 0:
            for _ in range(t):
                carte = self.deck.pop()
                res.append(carte)
            return res
        else:
            return None


class DiscardPile(Stack):
    """Represents the discard pile in Solitaire."""

    def draw(self):
        """Remove and return the top card of the discard pile."""
        t = self.deck.size()
        if t > 0:
            card = self.deck.pop()
            return card
        else:
            return None

    def top(self):
        """Returns the top card of the discard pile without removing it."""
        return self.deck.peek()

    def visible(self):
        """Returns up to three cards from the top of the discard pile without removing them."""
        t = self.deck.size()
        res = []
        if t >= 3:
            e1, e2, e3 = self.deck.draw(), self.deck.draw(), self.deck.draw()
            self.deck.stack(e3)
            self.deck.stack(e2)
            self.deck.stack(e1)
            return [e1, e2, e3]
        elif t > 0:
            for _ in range(t):
                elem = self.deck.draw()
                self.deck.stack(elem)
                res.append(elem)
            return res
        else:
            return None


class FinalPile(Stock):
    """Represents one of the four foundation piles in Solitaire."""

    def __init__(self):
        super().__init__()
        self.deck = []  # start with an empty deck

    def can_stack(self, elem: Card):
        if len(self.deck) == 0:
            return elem.value == "as"
        else:
            top_card = self.deck[-1]
            if top_card.family == elem.family:
                top_index = height.index(top_card.value)
                elem_index = height.index(elem.value)
                return elem_index == top_index + 1
            else:
                return False

    def stack(self, elem: Card):
        if self.can_stack(elem):
            self.deck.stack(elem)
            return True
        else:
            return False


class Game_queue(Queue):
    """Represents one of the seven tableau piles in Solitaire."""

    def __init__(self, length):
        for _ in range(length):
            self.deck.enqueue(Stock().draw())

    def can_stack(self, elem: Card):
        if self.deck.size() == 0:
            return elem.value == "roi"
        else:
            top_card = self.deck.peek()
            match top_card.family:
                case "pique" | "trefle":
                    return (
                        elem.family in ("coeur", "carreau")
                        and height.index(elem.value) == height.index(top_card.value) - 1
                    )
                case "coeur" | "carreau":
                    return (
                        elem.family in ("pique", "trefle")
                        and height.index(elem.value) == height.index(top_card.value) - 1
                    )
                case _:
                    return False

    def move(self, i: int, queue: Queue):
        """Move the bottom i cards from this queue to a new pile and return them as a Queue."""
        temp = Stack()
        moved = Queue()
        t = self.deck.size()
        for _ in range(i):
            temp.push(self.deck.dequeue())
        if queue.can_stack(self.deck.peek()):
            for _ in range(t - i):
                moved.enqueue(self.deck.dequeue())
            for _ in range(temp.size()):
                self.deck.enqueue(temp.pop())
            for elem in moved.items:
                queue.enqueue(elem)
        else:
            for elem in queue.items:
                self.deck.enqueue(elem)
        

class Grid(Game_queue):
    def __init__(self):
        self.piles = [Game_queue(i) for i in range(1, 8)]

class Game:
    def __init__(self):
        self.stock = Stock()
        self.stock.shuffle()
        self.discard_pile = DiscardPile()
        self.final_piles = [FinalPile() for _ in range(4)]
        self.grid = Grid()

class Save:
    def __init__(self, game: Game):
        self.game_state = [game.stock, game.discard_pile, game.final_piles, game.grid]
        self.history = []
    
    def save_state(self):
        self.history.append(self.game_state)
    
    def undo(self):
        if self.history:
            self.game_state = self.history.pop()
        else:
            print("No more undos available.")
    