import tkinter as tk
from tkinter import messagebox
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
        
        # Connecter le callback pour l'animation de l'auto-complétion
        self.game._redraw_callback = self._redraw

        # Main canvas
        self.canvas = tk.Canvas(
            root, width=1200, height=800, bg="darkgreen", highlightthickness=0
        )
        self.canvas.pack()

        # Buttons frame at the bottom left
        self.button_frame = tk.Frame(root, bg="darkgreen")
        self.button_frame.place(x=20, y=750)  # Position en bas à gauche

        # Reset button
        self.reset_button = tk.Button(
            self.button_frame,
            text="🔄 Nouvelle Partie",
            font=("Arial", 11, "bold"),
            bg="#2ecc71",
            fg="white",
            padx=15,
            pady=8,
            command=self.reset_game,
            cursor="hand2"
        )
        self.reset_button.pack(side=tk.LEFT, padx=5)

        # Undo button
        self.undo_button = tk.Button(
            self.button_frame,
            text="↶ Annuler",
            font=("Arial", 11, "bold"),
            bg="#e74c3c",
            fg="white",
            padx=15,
            pady=8,
            command=self.undo_move,
            cursor="hand2"
        )
        self.undo_button.pack(side=tk.LEFT, padx=5)

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
        self.selected_zone = None  # (zone_id, zone) stored on mouse press for drag/drop

        # Dictionary to store clickable zones for each card
        self.card_zones = {}

        # Bind mouse events: press/release for drag-drop
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_release)

        # First display
        self._redraw()

    def reset_game(self):
        """Recommencer une nouvelle partie."""
        if messagebox.askyesno("Nouvelle Partie", "Voulez-vous vraiment recommencer une nouvelle partie ?"):
            # Réinitialiser le jeu
            self.game = GameController()
            # Reconnecter le callback
            self.game._redraw_callback = self._redraw
            self.selected_card = None
            self.selected_cards_count = 0
            self.selected_zone = None
            self.card_zones.clear()
            self.image_refs.clear()
            # Redessiner
            self._redraw()
            print("✅ Nouvelle partie démarrée !")

    def undo_move(self):
        """Annuler le dernier coup."""
        if self.game.save.history:
            self.game.undo_move()
            self._redraw()
            print("↶ Coup annulé !")
        else:
            messagebox.showinfo("Annuler", "Aucun coup à annuler.")

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
        # Normalize columns: if a queue is empty but its stack has cards,
        # move the top card from the stack back into the queue (face-down).
        self._normalize_columns()

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
                text="♻️\nRecycler",
                fill="white",
                font=("Arial", 10),
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
                    # Clickable zone for empty foundation pile so we can drop Aces there
                    self.card_zones[f"final_{i}"] = {
                        "x1": x,
                        "y1": 100,
                        "x2": x + 100,
                        "y2": 250,
                        "type": "final",
                        "index": i,
                        "is_empty": True,
                    }

        # Tableau piles (7 columns)
        for i, elem in enumerate(self.game.grid.game):
            # elem is [Game_queue (face-down), GameStack (face-up)]
            queue = elem[0]
            stack = elem[1]

            x = 100 + i * self.column_spacing
            y = self.tableau_start_y
            offset = 30

            # Support both size() method and direct len access
            try:
                n_queue = queue.size()
            except Exception:
                n_queue = len(list(queue.items))

            try:
                n_stack = stack.size()
            except Exception:
                n_stack = len(list(stack.items))

            if n_queue == 0 and n_stack == 0:
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
                # Draw face-down cards (stack) first
                for j, card in enumerate(list(stack.items)):
                    # stack cards are face-down
                    card.face = False
                    img = self.load_card_image(card)
                    card_y = y + j * offset
                    if img:
                        self.canvas.create_image(
                            x, card_y, image=img, anchor="nw", tags=f"tableau_{i}_s_{j}"
                        )

                    # Only the topmost stack card might be interactive (to flip)
                    is_top_stack = (j == n_stack - 1)
                    clickable_height = 150 if is_top_stack and n_queue == 0 else offset
                    self.card_zones[f"tableau_{i}_s_{j}"] = {
                        "x1": x,
                        "y1": card_y,
                        "x2": x + 100,
                        "y2": card_y + clickable_height,
                        "type": "tableau",
                        "pile_index": i,
                        "card_index": j,
                        "is_stack": True,
                        "is_top_stack": is_top_stack,
                    }

                # Draw face-up cards (queue)
                for j, card in enumerate(list(queue.items)):
                    card.face = True
                    img = self.load_card_image(card)
                    card_y = y + (n_stack + j) * offset
                    if img:
                        self.canvas.create_image(
                            x, card_y, image=img, anchor="nw", tags=f"tableau_{i}_q_{j}"
                        )

                    is_last = (j == n_queue - 1)
                    clickable_height = 150 if is_last else offset
                    # card_index refers to index within queue (visible cards)
                    self.card_zones[f"tableau_{i}_q_{j}"] = {
                        "x1": x,
                        "y1": card_y,
                        "x2": x + 100,
                        "y2": card_y + clickable_height,
                        "type": "tableau",
                        "pile_index": i,
                        "card_index": j,
                        "is_stack": False,
                        "is_last": is_last,
                    }


        # Display number of moves
        self.canvas.create_text(
            600,
            50,
            text=f"Coups: {self.game.turns}",
            fill="white",
            font=("Arial", 16, "bold"),
        )

    def get_clicked_card(self, x, y):
        """Determine which card was clicked based on coordinates."""
        clicked_zones = []

        for zone_id, zone in self.card_zones.items():
            if zone["x1"] <= x <= zone["x2"] and zone["y1"] <= y <= zone["y2"]:
                clicked_zones.append((zone_id, zone))

        # If multiple zones match, take the one with highest y
        if clicked_zones:
            clicked_zones.sort(key=lambda z: z[1]["y1"], reverse=True)
            return clicked_zones[0]

        return None, None

    # Helper methods to access pile structure
    def _pile_objects(self, pile_index):
        """Return (queue, stack) for a tableau pile index."""
        elem = self.game.grid.game[pile_index]
        return elem[0], elem[1]

    def _pile_top_card(self, pile_index):
        """Return the top visible card of a pile or None."""
        queue, stack = self._pile_objects(pile_index)
        try:
            if stack.size() > 0:
                return stack.peek()
        except Exception:
            if len(list(stack.items)) > 0:
                return list(stack.items)[-1]

        try:
            return queue.peek()
        except Exception:
            items = list(queue.items)
            return items[-1] if items else None

    def _rank(self, card):
        """Return numeric rank for comparison using piles.height from piles module."""
        try:
            from piles import height
            return height.index(card.value)
        except Exception:
            order = ["as", "2", "3", "4", "5", "6", "7", "8", "9", "10", "valet", "dame", "roi"]
            return order.index(card.value)

    def _normalize_columns(self):
        """Ensure that for each tableau column, if the queue is empty and the stack has cards,
        move the top card from the stack into the queue (and mark it face-down)."""
        for i, elem in enumerate(self.game.grid.game):
            queue, stack = elem[0], elem[1]
            try:
                q_size = queue.size()
            except Exception:
                q_size = len(list(getattr(queue, 'items', [])))
            try:
                s_size = stack.size()
            except Exception:
                s_size = len(list(getattr(stack, 'items', [])))

            if q_size == 0 and s_size > 0:
                pass
                
    def _redraw(self):
        """Normalize columns and redraw the GUI."""
        try:
            self._normalize_columns()
        except Exception:
            pass
        try:
            self.draw_game()
        except Exception:
            pass
        # Forcer la mise à jour de l'affichage
        self.root.update_idletasks()
        self.root.update()

    def on_mouse_press(self, event):
        """Store the zone where the mouse press occurred (start of potential move)."""
        x, y = event.x, event.y
        zone_id, zone = self.get_clicked_card(x, y)
        self.selected_zone = (zone_id, zone)
        if zone_id:
            print(f"Press at ({x},{y}) -> {zone_id}")

    def on_mouse_release(self, event):
        """On release, try to move selected cards from start zone to release zone."""
        x, y = event.x, event.y
        start_zone_id, start_zone = self.selected_zone if self.selected_zone else (None, None)
        end_zone_id, end_zone = self.get_clicked_card(x, y)

        # Clear selection
        self.selected_zone = None

        # If no start zone (press not captured), fall back to using end zone as start
        if not start_zone:
            start_zone_id, start_zone = end_zone_id, end_zone

        # If release happened on the stock, perform draw (pioche)
        if end_zone and end_zone.get("type") == "stock":
            self.game.draw_from_stock()
            try:
                self.draw_game()
            except Exception:
                pass
            self.selected_zone = None
            return

        if not start_zone or not end_zone:
            print(f"Release at ({x},{y}) - no valid start or end zone")
            return

        print(f"Release at ({x},{y}) - start: {start_zone_id}, end: {end_zone_id}")

        # Handle moves from discard
        if start_zone.get("type") == "discard":
            if not start_zone.get("is_last", False):
                print("Can't move a non-last discard card")
                return

            if end_zone.get("type") == "final":
                dest = self.game.final_piles[end_zone["index"]]
                success = self.game.move_from_discard(dest)
                if success:
                    self._redraw()
                return

            if end_zone.get("type") == "tableau":
                dest_idx = end_zone["pile_index"]
                dest_queue = self.game.grid.game[dest_idx][0]
                success = self.game.move_from_discard(dest_queue)
                if success:
                    self._redraw()
                return

        # Handle moves between tableau piles
        if start_zone.get("type") == "tableau" and end_zone.get("type") == "tableau":
            src_idx = start_zone["pile_index"]
            dst_idx = end_zone["pile_index"]
            if src_idx == dst_idx:
                print("Released on same pile - no move")
                return
            
            src_queue, src_stack = self._pile_objects(src_idx)
            dst_queue, dst_stack = self._pile_objects(dst_idx)
            
            try:
                n_queue = src_queue.size()
            except Exception:
                n_queue = len(list(getattr(src_queue, 'items', [])))
            try:
                n_stack = src_stack.size()
            except Exception:
                n_stack = len(list(getattr(src_stack, 'items', [])))

            if start_zone.get("is_stack", False) or (start_zone_id and "_s_" in start_zone_id):
                print("Hidden stack cards cannot be moved or flipped via the UI.")
                return

            clicked_card_index = start_zone.get("card_index")
            if start_zone_id and "_s_" in start_zone_id:
                print("Cannot start a move from a hidden stack zone. Flip the card first.")
                return
            if clicked_card_index is None:
                print("No card index on start zone")
                return

            num_to_move = n_queue - clicked_card_index
            if num_to_move <= 0:
                print("Nothing to move")
                return

            success = self.game.move_card(src_queue, dst_queue, num_to_move)
            if success:
                self._redraw()
            else:
                print("Invalid move between tableaus")
            return

        # Handle moves to foundation
        if start_zone.get("type") == "tableau" and end_zone.get("type") == "final":
            src_idx = start_zone["pile_index"]
            fpile = self.game.final_piles[end_zone["index"]]
            src_queue, src_stack = self._pile_objects(src_idx)

            if start_zone.get("is_stack", False):
                print("Cannot move a hidden card to foundation. Flip it first.")
                return

            try:
                q_size = src_queue.size()
            except Exception:
                q_size = len(list(getattr(src_queue, 'items', [])))

            if q_size <= 0:
                print("No visible card to move to foundation.")
                return

            success = self.game.move_card(src_queue, fpile, 1)
            if success:
                self._redraw()
            else:
                print("Invalid move to foundation")
            return

        # Handle moves FROM foundation TO tableau (NOUVEAU)
        if start_zone.get("type") == "final" and end_zone.get("type") == "tableau":
            src_fpile = self.game.final_piles[start_zone["index"]]
            dst_idx = end_zone["pile_index"]
            dst_queue = self.game.grid.game[dst_idx][0]

            # Vérifier qu'il y a une carte dans la fondation
            if src_fpile.is_empty():
                print("Foundation pile is empty.")
                return

            success = self.game.move_card(src_fpile, dst_queue, 1)
            if success:
                self._redraw()
                print("✅ Carte déplacée de la fondation vers le tableau")
            else:
                print("Invalid move from foundation to tableau")
            return


if __name__ == "__main__":
    root = tk.Tk()
    app = SolitaireApp(root)
    root.mainloop()
