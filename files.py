from collections import deque
from cartes import Card
from piles import Stock, Stack, height


class Queue:
    def __init__(self) -> None:
        self.items = deque()

    def is_empty(self) -> bool:
        return len(self.items) == 0

    def enqueue(self, item) -> None:
        # Append to the right so the newest card becomes the top (peek() uses [-1])
        self.items.append(item)

    def dequeue(self) -> Card | None:
        if not self.is_empty():
            return self.items.pop()
        else:
            return None

    def peek(self) -> Card | None:
        if not self.is_empty():
            return self.items[-1]
        else:
            return None

    def size(self) -> int:
        return len(self.items)


class Game_queue(Queue):
    """Represents one of the seven tableau piles in Solitaire."""

    def __init__(self, stock: Stock, length: int) -> None:
        super().__init__()
        # Draw cards from the shared stock
        for _ in range(length):
            card = stock.pop()
            if card:
                self.enqueue(card)

    def can_stack(self, elem: Card) -> bool:
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

    def move(self, num_cards: int, destination_queue: "Game_queue") -> bool:
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



class GameStack(Stack):
    def __init__(self, stock: Stock, length: int) -> None:
        super().__init__()
        for _ in range(length):
            card = stock.pop()
            if card:
                self.push(card)

    def flip_into_queue(self, queue: Game_queue) -> bool:
        """Pop the top card from this hidden stack and enqueue it into the provided queue.
        Returns True if a card was flipped, False otherwise."""
        try:
            card = self.pop()
        except Exception:
            # fallback to list manipulation
            items = list(getattr(self, "items", []))
            card = items.pop() if items else None
            from collections import deque

            self.items = deque(items)

        if card:
            card.face = True
            try:
                queue.enqueue(card)
            except Exception:
                # fallback for older queue implementations
                try:
                    queue.items.append(card)
                except Exception:
                    pass
            return True
        return False


class Grid:
    """Represents the seven tableau piles in Solitaire."""

    def __init__(self, stock: Stock) -> None:
        # Initialize each column with exactly one visible card in the queue
        # and hidden stack with increasing size (0..6). The queue card is marked face=True.
        # queue: one visible card per column
        self.queue = [Game_queue(stock, 1) for _ in range(7)]
        # stack: hidden cards increasing from 0 to 6 (left to right)
        self.stack = [GameStack(stock, i) for i in range(0, 7)]

        # mark queued cards as visible
        for q in self.queue:
            try:
                card = q.peek()
                if card:
                    card.face = True
            except Exception:
                # fallback if peek not available
                try:
                    items = list(getattr(q, "items", []))
                    if items:
                        items[-1].face = True
                except Exception:
                    pass

        self.game = [[self.queue[i], self.stack[i]] for i in range(7)]

    def normalize(self) -> None:
        """For each column: if the queue is empty and the stack has cards,
        move the top card from the stack into the queue and mark it face-down.
        This keeps the internal game state consistent when cards are moved.
        """
        # Normalization is disabled: GameStack cards are intentionally static
        # and must remain in GameStack. The UI and controller must not move
        # hidden stack cards directly.
        return
