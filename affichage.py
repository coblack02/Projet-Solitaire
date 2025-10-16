import tkinter as tk
from PIL import Image, ImageTk
from game import GameController


class SolitaireApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Solitaire")
        self.root.geometry("1200x800")
        self.root.configure(bg="darkgreen")

        # Game initialization
        self.game = GameController()

        # Main canvas
        self.canvas = tk.Canvas(
            root, width=1200, height=800, bg="darkgreen", highlightthickness=0
        )
        self.canvas.pack()

        # Base positions
        self.stock_position = (100, 100)
        self.discard_position = (250, 100)
        self.foundation_start_x = 600
        self.foundation_spacing = 150
        self.tableau_start_y = 300
        self.column_spacing = 150

        # List to keep image references
        self.image_refs = []

        # Selection system
        self.selected_card = None  # (pile_index, card_index, pile_type)
        self.selected_cards_count = 0  # Number of selected cards

        # Dictionary to store clickable zones for each card
        self.card_zones = {}

        # Bind mouse events
        self.canvas.bind("<Button-1>", self.on_mouse_click)

        # First display
        self.draw_game()

    def load_card_image(self, card):
        """Load a card image (or back if face down)."""
        if not card.face:
            img = Image.open("cartes/dos_de_carte.webp")
        else:
            img = Image.open(f"cartes/{card.value}_{card.family}.gif")

        img = img.resize((100, 150))
        photo = ImageTk.PhotoImage(img)
        self.image_refs.append(photo)
        return photo

    def draw_game(self):
        """Update the entire graphical display of the game."""
        self.canvas.delete("all")
        self.image_refs.clear()
        self.card_zones.clear()  # Reset clickable zones

        # Stock (draw pile)
        if not self.game.stock.is_empty():
            stock_img = Image.open("cartes/dos_de_carte.webp").resize((100, 150))
            stock_photo = ImageTk.PhotoImage(stock_img)
            self.image_refs.append(stock_photo)
            self.canvas.create_image(
                self.stock_position[0],
                self.stock_position[1],
                image=stock_photo,
                anchor="nw",
                tags="stock",
            )
            # Clickable zone for stock
            self.card_zones["stock"] = {
                "x1": self.stock_position[0],
                "y1": self.stock_position[1],
                "x2": self.stock_position[0] + 100,
                "y2": self.stock_position[1] + 150,
                "type": "stock",
            }
        else:
            # Empty stock
            self.canvas.create_rectangle(
                self.stock_position[0],
                self.stock_position[1],
                self.stock_position[0] + 100,
                self.stock_position[1] + 150,
                fill="darkgreen",
                outline="white",
                width=2,
                dash=(5, 5),
                tags="stock",
            )
            self.canvas.create_text(
                self.stock_position[0] + 50,
                self.stock_position[1] + 75,
                text="Empty",
                fill="white",
                font=("Arial", 12),
            )
            # Clickable zone for empty stock (to recycle discard pile)
            self.card_zones["stock"] = {
                "x1": self.stock_position[0],
                "y1": self.stock_position[1],
                "x2": self.stock_position[0] + 100,
                "y2": self.stock_position[1] + 150,
                "type": "stock",
            }

        # Discard pile - Display the last 3 cards
        if not self.game.discard_pile.is_empty():
            visible_cards = self.game.discard_pile.visible()
            if visible_cards:
                card_offset = 30
                for i, card in enumerate(visible_cards):
                    card.face = True
                    img = self.load_card_image(card)
                    if img:
                        x_pos = self.discard_position[0] + (i * card_offset)
                        self.canvas.create_image(
                            x_pos,
                            self.discard_position[1],
                            image=img,
                            anchor="nw",
                            tags=f"discard_{i}",
                        )

                        # Last card = full zone, others = partial zone
                        is_last = i == len(visible_cards) - 1
                        self.card_zones[f"discard_{i}"] = {
                            "x1": x_pos,
                            "y1": self.discard_position[1],
                            "x2": x_pos + 100,
                            "y2": self.discard_position[1]
                            + (150 if is_last else card_offset),
                            "type": "discard",
                            "index": i,
                            "is_last": is_last,
                        }
        else:
            self.canvas.create_rectangle(
                self.discard_position[0],
                self.discard_position[1],
                self.discard_position[0] + 100,
                self.discard_position[1] + 150,
                outline="white",
                width=2,
            )

        # Foundation piles
        for i, pile in enumerate(self.game.final_piles):
            x = self.foundation_start_x + i * self.foundation_spacing

            if not pile.is_empty():
                top_card = pile.peek()
                top_card.face = True
                img = self.load_card_image(top_card)

                if img:
                    self.canvas.create_image(
                        x, 100, image=img, anchor="nw", tags=f"final_{i}"
                    )
                    # Clickable zone for foundation piles
                    self.card_zones[f"final_{i}"] = {
                        "x1": x,
                        "y1": 100,
                        "x2": x + 100,
                        "y2": 250,
                        "type": "final",
                        "index": i,
                    }
            else:
                self.canvas.create_rectangle(
                    x, 100, x + 100, 250, outline="white", width=2
                )

        # Tableau piles (7 columns)
        for elem in self.game.grid.game:
            elem_file=elem[0]
            elem_pile=elem[1]

            x = 100 + i * self.column_spacing
            y = self.tableau_start_y
            offset = 30

            if elem_file.size == 0 and elem_pile.size == 0 :
                # Empty pile - clickable zone to place a King
                self.canvas.create_rectangle(
                    x, y, x + 100, y + 150, outline="white", width=2, dash=(5, 5)
                )
                self.card_zones[f"tableau_{i}_empty"] = {
                    "x1": x,
                    "y1": y,
                    "x2": x + 100,
                    "y2": y + 150,
                    "type": "tableau",
                    "pile_index": i,
                    "card_index": None,
                    "is_empty": True,
                }

            else:
                for j, card in enumerate(elem_pile.items):
                    # Only the last card is visible
                    card.face = False
                    is_last = j==elem_file.size
                    img = self.load_card_image(card)

                    if img:
                        card_y = y + j * offset
                        self.canvas.create_image(
                            x, card_y, image=img, anchor="nw", tags=f"tableau_{i}_{j}"
                        )

                        # Middle card: only visible part (offset)
                        clickable_height = offset

                        self.card_zones[f"tableau_{i}_{j}"] = {
                            "x1": x,
                            "y1": card_y,
                            "x2": x + 100,
                            "y2": card_y + clickable_height,
                            "type": "tableau",
                            "pile_index": i,
                            "card_index": j,
                            "is_last": is_last,
                        }

                for j, card in enumerate(elem_file.items):
                    # Only the last card is visible
                    card.face = True
                    is_last = j==elem_file.size
                    img = self.load_card_image(card)

                    if img:
                        card_y = y + j * offset
                        self.canvas.create_image(
                            x, card_y, image=img, anchor="nw", tags=f"tableau_{i}_{j}"
                        )

                        # Determine clickable zone
                        if is_last:
                            # Last card: full zone (100x150)
                            clickable_height = 150
                        else:
                            # Middle card: only visible part (offset)
                            clickable_height = offset

                        self.card_zones[f"tableau_{i}_{j}"] = {
                            "x1": x,
                            "y1": card_y,
                            "x2": x + 100,
                            "y2": card_y + clickable_height,
                            "type": "tableau",
                            "pile_index": i,
                            "card_index": j,
                            "is_last": is_last,
                        }


        # Display number of moves
        self.canvas.create_text(
            600,
            50,
            text=f"Moves: {self.game.turns}",
            fill="white",
            font=("Arial", 16, "bold"),
        )

    def get_clicked_card(self, x, y):
        """Determine which card was clicked based on coordinates."""
        # Go through card zones in reverse order to handle overlaps
        # (cards drawn last are on top)

        clicked_zones = []

        for zone_id, zone in self.card_zones.items():
            if zone["x1"] <= x <= zone["x2"] and zone["y1"] <= y <= zone["y2"]:
                clicked_zones.append((zone_id, zone))

        # If multiple zones match, take the one with highest y
        # (lowest card = drawn last)
        if clicked_zones:
            clicked_zones.sort(key=lambda z: z[1]["y1"], reverse=True)
            return clicked_zones[0]

        return None, None

    def on_mouse_click(self, event):
        """Handle mouse clicks."""
        x, y = event.x, event.y

        # Determine which card/zone was clicked
        zone_id, zone = self.get_clicked_card(x, y)

        if zone_id is None:
            print(f"Click at ({x}, {y}) - No card")
            return

        print(f"Click at ({x}, {y}) - Zone: {zone_id}, Type: {zone['type']}")

        # Handle click based on zone type
        if zone["type"] == "stock":
            self.game.draw_from_stock()
            self.draw_game()

        elif zone["type"] == "discard":
            if zone.get("is_last", False):
                print(f"Discard card selected (index {zone['index']})")
                # Selection/movement logic

        elif zone["type"] == "tableau":
            pile_idx = zone["pile_index"]
            card_idx = zone["card_index"]

            if zone.get("is_empty", False):
                print(f"Tableau pile {pile_idx} empty - can receive a King")
            elif zone.get("is_last", False):
                print(f"Last card of pile {pile_idx} selected")
                # Selection/movement logic
            else:
                print(f"Card {card_idx} of pile {pile_idx} (partially visible)")
                # Calculate how many cards from this one to the end
                pile = self.game.grid.game[pile_idx]
                num_cards = len(list(pile.items)) - card_idx
                print(f"  -> Can move {num_cards} card(s)")

        elif zone["type"] == "final":
            print(f"Foundation pile {zone['index']} clicked")


if __name__ == "__main__":
    root = tk.Tk()
    app = SolitaireApp(root)
    root.mainloop()
