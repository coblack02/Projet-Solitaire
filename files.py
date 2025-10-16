from collections import deque
from cartes import Card
from piles import Stock,Stack,height

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
        
    def __repr__(self):
        return f"GameQueue({list(self.items)})"


class GameStack(Stack):
    def __init__(self, stock,lenght):
        super().__init__()
        for _ in range(lenght):
            card=stock.pop()
            if card:
                self.push(card)

    def __repr__(self):
        return f"GameStack({self.items})"

        

class Grid:
    """Represents the seven tableau piles in Solitaire."""
    
    def __init__(self, stock):
        self.queue=[Game_queue(stock, i) for i in range(0, 7)]
        self.stack =[GameStack(stock,1) for _ in range(7)]
        self.game=[[self.queue[i],self.stack[i]] for i in range (7)]
    def __str__(self) -> str:
        return f"GameStack({self.game})"
