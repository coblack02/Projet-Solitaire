# Solitaire (Klondike) Game

A Python implementation of the classic Klondike Solitaire card game with a graphical user interface built using Tkinter.

## Features

- **Full Klondike Solitaire gameplay** with standard rules
- **Interactive GUI** with drag-and-drop card movement
- **Game mechanics** including stock pile, discard pile, tableau, and foundation piles
- **Move history** with undo functionality
- **Hint system** that suggests the best moves with priority levels
- **Auto-complete** that automatically places cards on foundations when all tableau cards are revealed
- **Background music** with volume control
- **Main menu** with game rules and options

## Project Structure

The codebase is organized into several modules:

- **cartes.py** - Card class representing individual playing cards
- **piles.py** - Data structures for different pile types (Stock, Stack, DiscardPile, FinalPile)
- **files.py** - Queue and tableau management (Game_queue, GameStack, Grid)
- **game.py** - Game logic and controller (Game, Save, GameController)
- **affichage.py** - GUI and rendering (SolitaireApp)
- **audio.py** - Audio management (AudioManager)
- **main.py** - Entry point with main menu

## How to Play

### Objective

Move all 52 cards to the four foundation piles, building each suit from Ace to King.

### Rules

- **Foundation piles**: Build up by suit, starting with an Ace
- **Tableau piles**: Build down by alternating colors (red on black, black on red)
- **Stock pile**: Draw up to three cards at a time
- **Discard pile**: Cards drawn from the stock go here; recycle back to stock when empty
- **Sequences**: Move visible sequences between tableau piles if they follow the alternating color rule

### Controls

- **Left-click and drag** to move cards between piles
- **New Game**: Start a fresh game
- **Undo**: Revert the last move
- **Hint**: Get a suggested move based on priority rules
- **Stock pile**: Click to draw cards

## Game Logic

### Priority System for Hints

The hint system prioritizes moves as follows:

1. **Priority 1** - Moves to foundation (highest priority)
2. **Priority 2** - Tableau moves that reveal hidden cards
3. **Priority 3** - Moves from discard to tableau
4. **Priority 4** - General tableau-to-tableau moves
5. **Priority 5** - Draw from stock or recycle discard

### Move Validation

Each move type has specific validation:
- Foundation moves check for correct suit and ascending order
- Tableau moves validate alternating colors and descending sequence
- Card sequences can be moved as a group if valid

### Game State Management

The game maintains full move history using the Save class, allowing players to undo moves back to the start of the game.

## Requirements

- Python 3.7+
- tkinter (usually included with Python)
- Pillow (PIL) - for image handling
- pygame - for audio playback

## Installation

```bash
pip install Pillow pygame
```

## Running the Game

```bash
python main.py
```

This will launch the main menu from which you can start a new game, view rules, or quit.

## Assets Required

The game expects the following asset structure:

```
assets/
├── cartes/
│   ├── dos_de_carte.jpg (card back)
│   └── {value}_{suit}.png (individual cards)
└── musique/
    └── musique_balatro.mp3 (background music)
```

Card values: as, 2, 3, 4, 5, 6, 7, 8, 9, 10, valet, dame, roi
Suit names: pique, trefle, carreau, coeur

## Game State

The game tracks:
- Current turn count
- Stock pile remaining cards
- Discard pile contents
- Four foundation piles
- Seven tableau piles with both visible and hidden cards
- Move history for undo functionality

## Notes

- Normalization of columns is disabled as hidden stack cards are intentionally static
- The UI handles both normal and fallback implementations for queue operations
- Auto-complete triggers when all tableau cards are revealed and runs automatically
