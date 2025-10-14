import tkinter as tk
from PIL import Image, ImageTk
from game import GameController


class SolitaireApp:

    def __init__(self, root):

        self.root = root
        self.root.title("Solitaire")
        self.root.geometry("1200x800")
        self.root.configure(bg="darkgreen")

        # Initialisation du jeu
        self.game = GameController()

        # Canvas principal
        self.canvas = tk.Canvas(root, width=1200, height=800, bg="darkgreen", highlightthickness=0)
        self.canvas.pack()

        # Positions de base
        self.position_pioche = (100, 100)
        self.position_defausse = (250, 100)
        self.fondation_depart_x = 600
        self.espacement_fondations = 150
        self.tableau_depart_y = 300
        self.espacement_colonnes = 150

        # Liste pour garder les références d'images 
        self.image_refs = []

        # Bind clic sur le stock
        self.canvas.tag_bind("stock", "<Button-1>", self.draw_from_stock)

        # Premier affichage
        self.draw_game()

    def load_card_image(self, card):

        """Charge une image de carte (ou le dos si face cachée)."""
  
        if not card.face:
                
                img = Image.open("cartes/dos_de_carte.webp")

        else:

            img = Image.open(f"cartes/{card.value}_{card.family}.gif")

        img = img.resize((100, 150))
        photo = ImageTk.PhotoImage(img)
        self.image_refs.append(photo)
        return photo
        

    def draw_game(self):

        """Met à jour tout l'affichage graphique du jeu."""

        self.canvas.delete("all")
        self.image_refs.clear()

        # Pioche (stock)
        if not self.game.stock.is_empty():
                
                stock_img = Image.open("cartes/dos_de_carte.webp").resize((100, 150))
                stock_photo = ImageTk.PhotoImage(stock_img)
                self.image_refs.append(stock_photo)
                self.canvas.create_image(
                    self.position_pioche[0], self.position_pioche[1],
                    image=stock_photo, anchor="nw", tags="stock"
                )

        else:

            # Stock vide
            self.canvas.create_rectangle(
                self.position_pioche[0], self.position_pioche[1],
                self.position_pioche[0] + 100, self.position_pioche[1] + 150,
                outline="white", width=2, dash=(5, 5)
            )
            self.canvas.create_text(
                self.position_pioche[0] + 50, self.position_pioche[1] + 75,
                text="Vide", fill="white", font=("Arial", 12)
            )

        # Défausse Afficher les 3 dernières cartes
        if not self.game.discard_pile.is_empty():
            visible_cards = self.game.discard_pile.visible()
            if visible_cards:
                # Espacement horizontal entre les cartes visibles
                card_offset = 30
                for i, card in enumerate(visible_cards):
                    card.face = True
                    img = self.load_card_image(card)
                    if img:
                        x_pos = self.position_defausse[0] + (i * card_offset)
                        self.canvas.create_image(
                            x_pos, self.position_defausse[1],
                            image=img, anchor="nw", tags=f"discard_{i}"
                        )

        else:

            self.canvas.create_rectangle(
                self.position_defausse[0], self.position_defausse[1],
                self.position_defausse[0] + 100, self.position_defausse[1] + 150,
                outline="white", width=2
            )

        # Piles finales 
        for i, pile in enumerate(self.game.final_piles):

            x = self.fondation_depart_x + i * self.espacement_fondations

            if not pile.is_empty():

                top_card = pile.peek()
                top_card.face = True
                img = self.load_card_image(top_card)

                if img:

                    self.canvas.create_image(x, 100, image=img, anchor="nw")
            else:

                self.canvas.create_rectangle(x, 100, x + 100, 250, outline="white", width=2)

        # Piles du tableau (7 colonnes)
        for i, pile in enumerate(self.game.grid.piles):

            x = 100 + i * self.espacement_colonnes
            y = self.tableau_depart_y
            offset = 30
            pile_cards = list(pile.items)  
            
            if len(pile_cards) == 0:

                # Pile vide
                self.canvas.create_rectangle(
                    x, y, x + 100, y + 150,
                    outline="white", width=2, dash=(5, 5)
                )

            else:

                for j, card in enumerate(pile_cards):
                    # Seule la dernière carte est visible
                    card.face = (j == len(pile_cards) - 1)
                    img = self.load_card_image(card)

                    if img:

                        self.canvas.create_image(x, y + j * offset, image=img, anchor="nw")

        # Afficher le nombre de coups
        self.canvas.create_text(
            600, 50, text=f"Coups: {self.game.turns}", 
            fill="white", font=("Arial", 16, "bold")
        )

    def draw_from_stock(self, event=None):

        """Quand on clique sur le paquet, tirer 3 cartes."""

        self.game.draw_from_stock()
        self.draw_game()
       

if __name__ == "__main__":
    root = tk.Tk()
    app = SolitaireApp(root)
    root.mainloop()