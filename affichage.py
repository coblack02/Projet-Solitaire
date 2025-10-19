import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageDraw
from audio import AudioManager
from game import GameController
from cartes import Card


class SolitaireApp:

    def __init__(self, root: tk.Tk, menu_root: tk.Tk = None):
        self.root = root
        self.root.title("Solitaire")
        self.root.geometry("1200x800")
        self.root.configure(bg="darkgreen")

        # Game initialization
        self.game = GameController()
        self.game._redraw_callback = self._redraw
        # store menu root to return to it on victory
        self._menu_root = menu_root
        try:
            self.game.on_victory = self._on_victory
        except Exception:
            pass

        self.audio = AudioManager()
        self.audio.play_music()
        self.audio.set_volume(0.1)

        # Main canvas
        self.canvas = tk.Canvas(
            root, width=1200, height=800, bg="darkgreen", highlightthickness=0
        )
        self.canvas.pack()

        # Buttons frame at the bottom left
        self.button_frame = tk.Frame(root, bg="darkgreen")
        self.button_frame.place(x=20, y=750)

        # Create rounded button images
        self.btn_images = {}
        self._create_button_images()

        # Reset button
        self.reset_button = tk.Button(
            self.button_frame,
            image=self.btn_images.get('reset_normal'),
            text="🔄 Nouvelle Partie",
            compound="center",
            font=("Arial", 11, "bold"),
            fg="white",
            bg="darkgreen",
            border=0,
            activebackground="darkgreen",
            activeforeground="white",
            padx=15,
            pady=8,
            command=self.reset_game,
            cursor="hand2",
            highlightthickness=0,
        )
        self.reset_button.pack(side=tk.LEFT, padx=5)

        # Undo button
        self.undo_button = tk.Button(
            self.button_frame,
            image=self.btn_images.get('undo_normal'),
            text="↶ Annuler",
            compound="center",
            font=("Arial", 11, "bold"),
            fg="white",
            bg="darkgreen",
            border=0,
            activebackground="darkgreen",
            activeforeground="white",
            padx=15,
            pady=8,
            command=self.undo_move,
            cursor="hand2",
            highlightthickness=0,
        )
        self.undo_button.pack(side=tk.LEFT, padx=5)

        # Hint button
        self.hint_button = tk.Button(
            self.button_frame,
            image=self.btn_images.get('hint_normal'),
            text="💡 Indice",
            compound="center",
            font=("Arial", 11, "bold"),
            fg="white",
            bg="darkgreen",
            border=0,
            activebackground="darkgreen",
            activeforeground="white",
            padx=15,
            pady=8,
            command=self.show_hint,
            cursor="hand2",
            highlightthickness=0,
        )
        self.hint_button.pack(side=tk.LEFT, padx=5)

        # Abandon button - return to menu
        self.abandon_button = tk.Button(
            self.button_frame,
            text="� Abandonner",
            font=("Arial", 11, "bold"),
            bg="#95a5a6",
            fg="white",
            padx=15,
            pady=8,
            command=self.abandon_game,
            cursor="hand2",
            highlightthickness=0,
        )
        self.abandon_button.pack(side=tk.LEFT, padx=5)

        # Bind hover effects
        self._bind_button_hover(self.reset_button, 'reset')
        self._bind_button_hover(self.undo_button, 'undo')
        self._bind_button_hover(self.hint_button, 'hint')

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
        self.selected_card = None
        self.selected_cards_count = 0
        self.selected_zone = None

        # Dictionary to store clickable zones for each card
        self.card_zones = {}

        # Variables pour le drag-and-drop
        self.dragging = False
        self.drag_start_zone = None
        self.drag_cards_images = []
        self.current_mouse_pos = (0, 0)

        # Bind mouse events
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_release)
        self.canvas.bind("<Motion>", self.on_mouse_motion)

        # First display
        self._redraw()

    def _create_button_images(self):
        """Create rounded button images with normal and hover states."""
        buttons_config = {
            'reset': {'normal': '#2ecc71', 'hover': '#27ae60'},
            'undo': {'normal': '#e74c3c', 'hover': '#c0392b'},
            'hint': {'normal': '#f39c12', 'hover': '#e67e22'},
        }

        for btn_name, colors in buttons_config.items():
            # Normal state
            img_normal = Image.new("RGBA", (150, 50), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img_normal)
            draw.rounded_rectangle([(0, 0), (150, 50)], radius=5, fill=colors['normal'])
            photo_normal = ImageTk.PhotoImage(img_normal)
            self.btn_images[f'{btn_name}_normal'] = photo_normal

            # Hover state
            img_hover = Image.new("RGBA", (150, 50), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img_hover)
            draw.rounded_rectangle([(0, 0), (150, 50)], radius=5, fill=colors['hover'])
            photo_hover = ImageTk.PhotoImage(img_hover)
            self.btn_images[f'{btn_name}_hover'] = photo_hover

    def _bind_button_hover(self, button, btn_name):
        """Bind hover effects to a button."""
        def on_enter(e):
            button.config(image=self.btn_images[f'{btn_name}_hover'])

        def on_leave(e):
            button.config(image=self.btn_images[f'{btn_name}_normal'])

        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)

    def reset_game(self):
        """Reset the game after confirmation."""
        if messagebox.askyesno(
            "Nouvelle Partie", "Voulez-vous vraiment recommencer une nouvelle partie ?"
        ):
            self.game = GameController()
            self.game._redraw_callback = self._redraw
            self.selected_card = None
            self.selected_cards_count = 0
            self.selected_zone = None
            self.card_zones.clear()
            self.image_refs.clear()
            self.dragging = False
            self.drag_cards_images.clear()
            self._redraw()

    def undo_move(self):
        """Undo the last move."""
        if self.game.save.history:
            self.game.undo_move()
            self._redraw()
        else:
            messagebox.showinfo("Annuler", "Aucun coup à annuler.")

    def abandon_game(self):
        """Abandon the current game and return to the main menu (if available)."""
        if messagebox.askyesno("Abandonner", "Voulez-vous vraiment abandonner et retourner au menu ?"):
            try:
                # destroy the game window and show menu if possible
                if getattr(self, '_menu_root', None):
                    self.root.destroy()
                    self._menu_root.deiconify()
                else:
                    self.root.destroy()
            except Exception:
                try:
                    self.root.destroy()
                except Exception:
                    pass

    def show_hint(self):
        """Show a hint to the player."""
        hint = self.game.get_hint_message()
        if hint:
            message = hint.get("message", "Aucun indice disponible")

            if hint.get("type") == "discard_to_foundation":
                title = "💡 Excellent coup !"
                detailed_message = (
                    f"✨ {message}\n\n🎯 C'est le meilleur coup à jouer !"
                )
            elif hint.get("type") == "tableau_to_foundation":
                title = "💡 Excellent coup !"
                detailed_message = (
                    f"✨ {message}\n\n🎯 C'est le meilleur coup à jouer !"
                )
            elif hint.get("type") == "tableau_to_tableau_reveal":
                title = "💡 Bon coup !"
                detailed_message = f"✨ {message}\n\n🔓 Cela révélera une carte cachée."
            elif hint.get("type") == "discard_to_tableau":
                title = "💡 Coup possible"
                detailed_message = f"✨ {message}\n\n📝 Un coup valide pour progresser."
            elif hint.get("type") == "tableau_to_tableau":
                title = "💡 Coup possible"
                num_cards = hint.get("num_cards", 1)
                if num_cards > 1:
                    detailed_message = (
                        f"✨ {message}\n\n📚 Déplacez {num_cards} cartes ensemble."
                    )
                else:
                    detailed_message = f"✨ {message}"
            elif hint.get("type") == "draw_stock":
                title = "💡 Action suggérée"
                detailed_message = "✨ Piochez 3 nouvelles cartes du stock\n\n🎴 Cela peut débloquer de nouvelles possibilités."
            elif hint.get("type") == "recycle_stock":
                title = "💡 Action suggérée"
                detailed_message = "✨ Recyclez la défausse vers le stock\n\n♻️ Pour continuer à piocher des cartes."
            else:
                title = "💡 Indice"
                detailed_message = message

            messagebox.showinfo(title, detailed_message)
        else:
            messagebox.showinfo(
                "💡 Indice",
                "Aucun coup évident disponible.\n\nEssayez de piocher ou de réorganiser les colonnes.",
            )

    def load_card_image(self, card: Card):
        """Load a card image (or back if face down)."""
        if not card.face:
            img = Image.open("assets/cartes/dos_de_carte.jpg")
        else:
            img = Image.open(f"assets/cartes/{card.value}_{card.family}.png")
        img = img.resize((100, 150))

        img = self._round_corners(img, radius=5)

        photo = ImageTk.PhotoImage(img)
        self.image_refs.append(photo)
        return photo

    def _round_corners(self, img: Image.Image, radius: int = 15):
        """Arrondir les coins d'une image."""
        # Créer un masque circulaire
        mask = Image.new("L", img.size, 0)
        draw = ImageDraw.Draw(mask)

        # Dessiner les coins arrondis
        draw.rounded_rectangle([(0, 0), img.size], radius=radius, fill=255)

        # Appliquer le masque
        img.putalpha(mask)
        return img

    def draw_game(self):
        """Update the entire graphical display of the game."""
        self._normalize_columns()
        self.canvas.delete("all")
        self.image_refs.clear()
        self.card_zones.clear()

        # Stock
        if not self.game.stock.is_empty():
            stock_img = Image.open("assets/cartes/dos_de_carte.jpg").resize((100, 150))
            stock_img = self._round_corners(stock_img, radius=5)
            stock_photo = ImageTk.PhotoImage(stock_img)
            self.image_refs.append(stock_photo)
            self.canvas.create_image(
                self.stock_position[0],
                self.stock_position[1],
                image=stock_photo,
                anchor="nw",
                tags="stock",
            )
            self.card_zones["stock"] = {
                "x1": self.stock_position[0],
                "y1": self.stock_position[1],
                "x2": self.stock_position[0] + 100,
                "y2": self.stock_position[1] + 150,
                "type": "stock",
            }
        else:
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
            self.card_zones["stock"] = {
                "x1": self.stock_position[0],
                "y1": self.stock_position[1],
                "x2": self.stock_position[0] + 100,
                "y2": self.stock_position[1] + 150,
                "type": "stock",
            }

        # Discard pile
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
                self.card_zones[f"final_{i}"] = {
                    "x1": x,
                    "y1": 100,
                    "x2": x + 100,
                    "y2": 250,
                    "type": "final",
                    "index": i,
                    "is_empty": True,
                }

        # Tableau piles
        for i, elem in enumerate(self.game.grid.game):
            queue = elem[0]
            stack = elem[1]
            x = 100 + i * self.column_spacing
            y = self.tableau_start_y
            offset = 30

            try:
                n_queue = queue.size()
            except:
                n_queue = len(list(queue.items))
            try:
                n_stack = stack.size()
            except:
                n_stack = len(list(stack.items))

            if n_queue == 0 and n_stack == 0:
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
                for j, card in enumerate(list(stack.items)):
                    card.face = False
                    img = self.load_card_image(card)
                    card_y = y + j * offset
                    if img:
                        self.canvas.create_image(
                            x, card_y, image=img, anchor="nw", tags=f"tableau_{i}_s_{j}"
                        )
                    is_top_stack = j == n_stack - 1
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

                for j, card in enumerate(list(queue.items)):
                    card.face = True
                    img = self.load_card_image(card)
                    card_y = y + (n_stack + j) * offset
                    if img:
                        self.canvas.create_image(
                            x, card_y, image=img, anchor="nw", tags=f"tableau_{i}_q_{j}"
                        )
                    is_last = j == n_queue - 1
                    clickable_height = 150 if is_last else offset
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

        # Display moves
        self.canvas.create_text(
            600,
            50,
            text=f"Coups: {self.game.turns}",
            fill="white",
            font=("Arial", 16, "bold"),
        )

    def get_clicked_card(self, x: float, y: float):
        """Determine which card was clicked."""
        clicked_zones = []
        for zone_id, zone in self.card_zones.items():
            if zone["x1"] <= x <= zone["x2"] and zone["y1"] <= y <= zone["y2"]:
                clicked_zones.append((zone_id, zone))
        if clicked_zones:
            clicked_zones.sort(key=lambda z: z[1]["y1"], reverse=True)
            return clicked_zones[0]
        return None, None

    def _pile_objects(self, pile_index: int):
        """Return (queue, stack) for a tableau pile."""
        elem = self.game.grid.game[pile_index]
        return elem[0], elem[1]

    def _normalize_columns(self):
        """Normalize columns."""
        pass

    def _redraw(self):
        """Redraw the GUI."""
        try:
            self._normalize_columns()
        except:
            pass
        try:
            self.draw_game()
        except:
            pass

    def _on_victory(self):
        """Display a victory overlay and return to the menu after a delay."""
        try:
            # Overlay frame covering the root
            overlay = tk.Toplevel(self.root)
            overlay.attributes("-fullscreen", True)
            overlay.config(bg="black")
            overlay.attributes("-alpha", 0.85)

            frame = tk.Frame(overlay, bg="black")
            frame.place(relx=0.5, rely=0.5, anchor="center")

            label = tk.Label(
                frame,
                text="Vous avez gagné!",
                font=("Arial", 48, "bold"),
                fg="white",
                bg="black",
            )
            label.pack(padx=20, pady=20)

            # After 4 seconds, close overlay and return to menu
            def finish():
                try:
                    overlay.destroy()
                except Exception:
                    pass
                try:
                    # destroy game window and show menu
                    self.root.destroy()
                    if self._menu_root:
                        self._menu_root.deiconify()
                except Exception:
                    pass

            overlay.after(4000, finish)
        except Exception:
            pass
        self.root.update_idletasks()
        self.root.update()

    def _prepare_dragged_cards(self, start_zone: dict):
        """Prepare card images for drag."""
        self.drag_cards_images = []
        if start_zone.get("type") == "discard":
            if start_zone.get("is_last", False):
                top_card = self.game.discard_pile.peek()
                if top_card:
                    top_card.face = True
                    img = self.load_card_image(top_card)
                    if img:
                        self.drag_cards_images.append(img)
        elif start_zone.get("type") == "tableau":
            queue, stack = self._pile_objects(start_zone["pile_index"])
            if not start_zone.get("is_stack", False):
                clicked_index = start_zone.get("card_index", 0)
                try:
                    cards = list(queue.items)[clicked_index:]
                except:
                    cards = []
                for card in cards:
                    card.face = True
                    img = self.load_card_image(card)
                    if img:
                        self.drag_cards_images.append(img)
        elif start_zone.get("type") == "final":
            fpile = self.game.final_piles[start_zone["index"]]
            if not fpile.is_empty():
                top_card = fpile.peek()
                if top_card:
                    top_card.face = True
                    img = self.load_card_image(top_card)
                    if img:
                        self.drag_cards_images.append(img)

    def on_mouse_press(self, event: tk.Event):
        """Handle mouse press."""
        x, y = event.x, event.y
        zone_id, zone = self.get_clicked_card(x, y)
        self.selected_zone = (zone_id, zone)
        if zone_id:
            self.dragging = True
            self.drag_start_zone = zone
            self._prepare_dragged_cards(zone)

    def on_mouse_motion(self, event: tk.Event):
        """Handle mouse motion during drag."""
        self.current_mouse_pos = (event.x, event.y)
        if not self.dragging or not self.drag_start_zone:
            return
        self.draw_game()
        offset_y = 0
        for img in self.drag_cards_images:
            self.canvas.create_image(
                event.x,
                event.y + offset_y,
                image=img,
                anchor="center",
                tags="dragged_card",
            )
            offset_y += 30

    def on_mouse_release(self, event: tk.Event):
        """Handle mouse release."""
        x, y = event.x, event.y
        start_zone_id, start_zone = (
            self.selected_zone if self.selected_zone else (None, None)
        )
        end_zone_id, end_zone = self.get_clicked_card(x, y)

        self.dragging = False
        self.drag_start_zone = None
        self.drag_cards_images.clear()
        self.selected_zone = None

        if not start_zone:
            start_zone_id, start_zone = end_zone_id, end_zone

        if end_zone and end_zone.get("type") == "stock":
            self.game.draw_from_stock()
            self._redraw()
            return

        if not start_zone or not end_zone:
            self._redraw()
            return

        # Discard to foundation/tableau
        if start_zone.get("type") == "discard":
            if not start_zone.get("is_last", False):
                self._redraw()
                return
            if end_zone.get("type") == "final":
                dest = self.game.final_piles[end_zone["index"]]
                self.game.move_from_discard(dest)
                self._redraw()
                return
            if end_zone.get("type") == "tableau":
                dest_idx = end_zone["pile_index"]
                dest_queue = self.game.grid.game[dest_idx][0]
                self.game.move_from_discard(dest_queue)
                self._redraw()
                return

        # Tableau to tableau
        if start_zone.get("type") == "tableau" and end_zone.get("type") == "tableau":
            src_idx = start_zone["pile_index"]
            dst_idx = end_zone["pile_index"]
            if src_idx == dst_idx:
                self._redraw()
                return
            src_queue, src_stack = self._pile_objects(src_idx)
            dst_queue, dst_stack = self._pile_objects(dst_idx)
            try:
                n_queue = src_queue.size()
            except:
                n_queue = len(list(getattr(src_queue, "items", [])))
            if start_zone.get("is_stack", False) or (
                start_zone_id and "_s_" in start_zone_id
            ):
                self._redraw()
                return
            clicked_card_index = start_zone.get("card_index")
            if clicked_card_index is None:
                self._redraw()
                return
            num_to_move = n_queue - clicked_card_index
            if num_to_move <= 0:
                self._redraw()
                return
            self.game.move_card(src_queue, dst_queue, num_to_move)
            self._redraw()
            return

        # Tableau to foundation
        if start_zone.get("type") == "tableau" and end_zone.get("type") == "final":
            src_idx = start_zone["pile_index"]
            fpile = self.game.final_piles[end_zone["index"]]
            src_queue, src_stack = self._pile_objects(src_idx)
            if start_zone.get("is_stack", False):
                self._redraw()
                return
            try:
                q_size = src_queue.size()
            except:
                q_size = len(list(getattr(src_queue, "items", [])))
            if q_size <= 0:
                self._redraw()
                return
            self.game.move_card(src_queue, fpile, 1)
            self._redraw()
            return

        # Foundation to tableau
        if start_zone.get("type") == "final" and end_zone.get("type") == "tableau":
            src_fpile = self.game.final_piles[start_zone["index"]]
            dst_idx = end_zone["pile_index"]
            dst_queue = self.game.grid.game[dst_idx][0]
            if src_fpile.is_empty():
                self._redraw()
                return
            self.game.move_card(src_fpile, dst_queue, 1)
            self._redraw()
            return

        self._redraw()
