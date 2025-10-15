from collections import deque
from cartes import Card 
import random

# cards defini
family = ("pique", "trefle", "carreau", "coeur")
height = ("as", "2", "3", "4", "5", "6", "7", "8", "9", "10", "valet", "dame", "roi")


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
        if self.is_empty:
            return None
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
