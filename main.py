import tkinter as tk
from tkinter import messagebox
from affichage import SolitaireApp


RULES_TEXT = (
    "Solitaire (Klondike) rules:\n\n"
    "- Build four foundation piles by suit from Ace to King.\n"
    "- On the tableau, build down by alternating colors.\n"
    "- You can move visible sequences between tableau piles if they follow the rules.\n"
    "- Click the stock to draw cards to the discard.\n"
    "- Only an Ace may start a foundation.\n"
    "- The goal is to move all cards to the four foundations."
)


def open_game_from_menu(root):
    # Open the game in a new window and hide the menu window
    root.withdraw()
    game_win = tk.Toplevel()
    # Start game in fullscreen
    game_win.attributes("-fullscreen", True)
    # Allow Escape to quit the game window and return to the menu
    game_win.bind("<Escape>", lambda e: (game_win.destroy(), root.deiconify()))
    game_win.protocol("WM_DELETE_WINDOW", lambda: (game_win.destroy(), root.deiconify()))
    SolitaireApp(game_win, menu_root=root)


def show_rules():
    messagebox.showinfo("Règles du Solitaire", RULES_TEXT)


def main_menu():
    root = tk.Tk()
    root.title("Solitaire - Menu")
    # Start menu in fullscreen mode
    root.geometry("400x300")
    root.attributes("-fullscreen", True)
    root.configure(bg="darkgreen")
    # Centered frame to hold title and buttons
    center_frame = tk.Frame(root, bg="darkgreen")
    center_frame.place(relx=0.5, rely=0.5, anchor="center")

    title = tk.Label(center_frame, text="Solitaire", font=("Arial", 40, "bold"), bg="darkgreen", fg="white")
    title.pack(pady=(0, 20))

    btn_font = ("Arial", 18)
    btn_kwargs = {"font": btn_font, "bg": "#2e8b57", "fg": "white", "activebackground": "#249150", "bd": 0}

    btn_play = tk.Button(center_frame, text="Jouer", width=20, command=lambda: open_game_from_menu(root), **btn_kwargs)
    btn_play.pack(pady=10, ipadx=20, ipady=8)

    btn_rules = tk.Button(center_frame, text="Règles", width=20, command=show_rules, **btn_kwargs)
    btn_rules.pack(pady=10, ipadx=20, ipady=8)

    btn_quit = tk.Button(center_frame, text="Quitter", width=20, command=root.destroy, **btn_kwargs)
    btn_quit.pack(pady=10, ipadx=20, ipady=8)

    root.mainloop()


if __name__ == "__main__":
    main_menu()
