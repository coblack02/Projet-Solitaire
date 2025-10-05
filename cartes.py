from tkinter import Tk, Label
from PIL import Image, ImageTk
import random

#cards defini
family = ('pique', 'trefle', 'carreau', 'coeur')
height = ('as', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'valet', 'dame', 'roi')
root = Tk()

class cCard():

    def __init__(self,c,h):
        self.family = c
        self.value = h
        self.face=False

    def afficher_carte(self):
        randcard = Image.open("cartes/"+self.value+"_"+self.family+".gif")
        photo=ImageTk.PhotoImage(randcard)
        label = Label(root, image=photo)
        label.pack()


class cPaquet():

    def __init__(self):
        self.deck = [] #the deck is an array of 52 cards (4x13)
        for c in range(4):
            for h in range(13):
                new_card = cCard(family[c], height[h]) #height starts at 1
                self.deck.append(new_card)

    def Shuffle(self):
        t = len(self.deck)
        for i in range(t):
            h1, h2 = random.randint(t), random.randint(t)
            self.deck[h1], self.deck[h2] = self.deck[h2], self.deck[h1]

    def draw(self):  #depile
        t = len(self.deck)
        res=[]
        if t>=3:
            carte1,carte2,carte3 = self.deck[0],self.deck[1],self.deck[2]
            del(self.deck[0],self.deck[0],self.deck[0]) 
            return [carte1,carte2,carte3]
        elif t>0:
            for i in range (t):
                carte=self.carte[0]
                del(self.deck[0])
                res.append(carte)
            return res
        else:
            return None
        
    def stack(self,elem):
        self.deck.append(elem)

class DiscardPile(cPaquet):
    def draw(self):
        t = len(self.deck)
        if t>0:
            card=self.deck[0]
            del(self.deck[0])
            return card
        else:
            return None
        
    def top(self):
        return self.deck[0]
    
    def visible(self):
        t=len(self.deck)
        res=[]
        if t>=3:
            e1,e2,e3=self.deck.draw(),self.deck.draw(),self.deck.draw()
            self.deck.stack(e3)
            self.deck.stack(e2)
            self.deck.stack(e1)
            return [e1,e2,e3]
        elif t>0:
            for i in range (t):
                elem=self.deck.draw()
                self.deck.stack(elem)
                res.append(elem)
            return res
        else:
            return None


class FinalPile(cPaquet):
    def __init__(self):
        super().__init__()
        self.deck = []  #start with an empty deck