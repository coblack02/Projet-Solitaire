import tkinter as tk
import tkinter.ttk as ttk

def afficher_position(evt):
    # l'objet evt a deux propriétés x et y qui sont les coordonnées du clic
    pos_x, pos_y = evt.x, evt.y
    affichage = f"Position : abscisse = {pos_x} ; ordonnées = {pos_y}"
    strvar_position.set(affichage)

appli = tk.Tk()
appli.title("Position de la souris dans un Canvas")

can = tk.Canvas(appli, width=500, height=300, bg='pink')
can.grid(row=10, column=10)

# création d'une StringVar pour pouvoir actualiser la position de la souris dans le Label
strvar_position = tk.StringVar()
strvar_position.set('Position de la souris')
ttk.Label(appli, textvariable=strvar_position).grid(row=20, column=10)

# gestionnaire d'événement (clic gauche) lié au Canvas pour appeler fonction afficher_position
can.bind("<Button-1>", afficher_position)

appli.mainloop()