from tkinter import Tk, Label
from PIL import Image, ImageTk

root = Tk()


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
