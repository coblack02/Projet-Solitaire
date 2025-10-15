from tkinter import Tk, Label
from PIL import Image, ImageTk



class Card:
    def __init__(self, c: str, h: str):
        self.family = c
        self.value = h
        self.face = False
