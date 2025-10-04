from tkinter import Tk, Label
from PIL import Image, ImageTk
import random

#definition des cartes
famile = ('pique', 'trefle', 'carreau', 'coeur')
hauteur = ('as', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'valet', 'dame', 'roi')
root = Tk()

class cCard():

    def __init__(self,c,h):
        self.famile = c
        self.valeur = h
        self.face=False

    def afficher_carte(self):
        unecarteopif = Image.open("cartes/"+self.valeur+"_"+self.famile+".gif")
        photo=ImageTk.PhotoImage(unecarteopif)
        label = Label(root, image=photo)
        label.pack


class cPaquet():

    def __init__(self):
        self.cartes = [] #un paquet est un tableau de 52 cartes (4x13)
        for c in range(4):
            for h in range(13):
                nouvelle_carte = cCard(famile[c], hauteur[h]) #la hauteur commence à 1
                self.cartes.append(nouvelle_carte)
                
    def melange(self):
        t = len(self.cartes)
        for i in range(t):
            h1, h2 = random.randint(t), random.randint(t)
            self.cartes[h1], self.cartes[h2] = self.cartes[h2], self.cartes[h1]

    def tirage(self):  #depile
        t = len(self.cartes)
        res=[]
        if t>=3:
            carte1,carte2,carte3 = self.cartes[0],self.cartes[1],self.cartes[2]
            del(self.cartes[0],self.cartes[0],self.cartes[0]) 
            return [carte1,carte2,carte3]
        elif t>0:
            for i in range (t):
                carte=self.carte[0]
                del(self.cartes[0])
                res.append(carte)
            return res
        else:
            return None
        
    def empiler(self,elem):
        self.cartes.append(elem)
        
class Defausse(cPaquet):
    def tirage(self):
        t = len(self.cartes)
        if t>0:
            carte=self.carte[0]
            del(self.cartes[0])
            return carte
        else:
            return None
        
    def tete(self):
        return self.cartes[0]
    
    def visibles(self):
        t=len(self.cartes)
        res=[]
        if t>=3:
            e1,e2,e3=self.cartes.tirage(),self.cartes.tirage(),self.cartes.tirage()
            self.cartes.empiler(e3)
            self.cartes.empiler(e2)
            self.cartes.empiler(e1)
            return [e1,e2,e3]
        elif t>0:
            for i in range (t):
                elem=self.cartes.tirage()
                self.cartes.empiler(elem)
                res.append(elem)
            return res
        else:
            return None


class Pile_finale(cPaquet):
