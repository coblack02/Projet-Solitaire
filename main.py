import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageDraw, ImageTk
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


def create_rounded_button_image(width, height, radius, bg_color) -> Image.Image:
    """create a rounded rectangle button image."""
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([(0, 0), (width, height)], radius=radius, fill=bg_color)
    return img


def open_game_from_menu(root) -> None:
    # Open the game in a new window and hide the menu window
    root.withdraw()
    game_win = tk.Toplevel()
    # Start game in fullscreen
    game_win.attributes("-fullscreen", True)
    # Allow Escape to quit the game window and return to the menu
    game_win.bind("<Escape>", lambda e: (game_win.destroy(), root.deiconify()))
    game_win.protocol(
        "WM_DELETE_WINDOW", lambda: (game_win.destroy(), root.deiconify())
    )
    SolitaireApp(game_win, menu_root=root)


def show_rules() -> None:
    messagebox.showinfo("Règles du Solitaire", RULES_TEXT)


def main_menu() -> None:
    root = tk.Tk()
    root.title("Solitaire - Menu")
    root.geometry("400x300")
    root.attributes("-fullscreen", True)
    root.configure(bg="darkgreen")

    # Centered frame to hold title and buttons
    center_frame = tk.Frame(root, bg="darkgreen")
    center_frame.place(relx=0.5, rely=0.5, anchor="center")

    title = tk.Label(
        center_frame,
        text="Solitaire",
        font=("Arial", 40, "bold"),
        bg="darkgreen",
        fg="white",
    )
    title.pack(pady=(0, 20))

    btn_width, btn_height = 200, 50
    btn_radius = 15
    btn_bg_normal = "#2e8b57"
    btn_bg_hover = "#249150"

    img_normal = create_rounded_button_image(
        btn_width, btn_height, btn_radius, btn_bg_normal
    )
    img_hover = create_rounded_button_image(
        btn_width, btn_height, btn_radius, btn_bg_hover
    )

    photo_normal = ImageTk.PhotoImage(img_normal)
    photo_hover = ImageTk.PhotoImage(img_hover)

    def create_styled_button(parent, text, command) -> tk.Button:
        """Create a styled button with hover effect."""
        btn = tk.Button(
            parent,
            image=photo_normal,
            text=text,
            compound="center",
            command=command,
            font=("Arial", 18, "bold"),
            fg="white",
            bg="darkgreen",
            border=0,
            activebackground="darkgreen",
            activeforeground="white",
            cursor="hand2",
            relief="flat",
            highlightthickness=0,
        )

        # hover effect
        def on_enter(e) -> None:
            btn.config(image=photo_hover)

        def on_leave(e) -> None:
            btn.config(image=photo_normal)

        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

        return btn

    btn_play = create_styled_button(
        center_frame, "Jouer", lambda: open_game_from_menu(root)
    )
    btn_play.pack(pady=10)

    btn_rules = create_styled_button(center_frame, "Règles", show_rules)
    btn_rules.pack(pady=10)

    btn_quit = create_styled_button(center_frame, "Quitter", root.destroy)
    btn_quit.pack(pady=10)

    # Keep references to the images
    root.photo_normal = photo_normal
    root.photo_hover = photo_hover

    root.mainloop()


if __name__ == "__main__":
    main_menu()
