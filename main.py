import tkinter as tk
from affichage import SolitaireApp


def main():
    """Main entry point for the Solitaire game."""
    root = tk.Tk()
    app = SolitaireApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
