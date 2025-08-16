# Python Chess Engine

A feature-rich chess engine implemented in Python with a graphical interface. This engine supports all standard chess rules, including special moves, and offers a simple AI opponent.

## Features

- **Complete Chess Rules Implementation**:
  - Castling (both kingside and queenside)
  - En passant (double pawn pushes)
  - Pawn promotion
  - Check/checkmate detection
  - Pin detection
  - Move validation according to all chess rules

- **FEN String Support**:
  - Load games from FEN strings
  - Export current board position to FEN notation

- **Game Features**:
  - Undo moves
  - Resizable game window
  - Sound effects for moves, captures, and checks
  - Simple AI that evaluates future moves
  - End game screen displaying winner

- **Game Modes**
  - AI Mode: Play against a computer opponent that evaluates moves ahead
  - Two-Player Mode: Disable the AI to control both sides (ideal for local multiplayer or testing positions)
  - Configurable in constants.py (IS_AI_MODE flag)

- **Visual Interface**:
  - Clean board representation
  - Legal move highlighting
  - Piece selection visuals

## Requirements

- Python
- Pygame library

## Installation

1. Clone the repository or download the source files
2. Install the required dependencies:
   ```
   pip install pygame
   ```

## Usage

Run the main game file:
```
python main.py
```

### Controls
- Left-click to select and move pieces
- 'Z' key to undo the last move
- 'R' to reset the board to initial position
- 'H' to highlight the "best" move found by bot
- 'P' to print the current board state as a FEN string

### AI Options
The AI strength can be adjusted by modifying the search depth in the engine parameters (default looks ahead 2 moves).

## FEN Support

You can load specific positions using FEN notation. Example starting position:
```
rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1
```

The current position FEN can be accessed through the engine interface.

## Gameplay

Pinned bishop:   
<img width="800" height="800" alt="Bishop Pinned Moves" src="https://github.com/user-attachments/assets/f7960d7a-52e9-4481-87d3-5c5d96446232" />

Castling:  
<img width="800" height="800" alt="Castle Moves" src="https://github.com/user-attachments/assets/bd344ed6-8120-4a20-9035-125725930416" />

En Passant:   
<img width="800" height="800" alt="En Passant Moves" src="https://github.com/user-attachments/assets/61687712-c86f-4eb1-82fd-6f61f620724a" />

King Moves:   
<img width="800" height="800" alt="King Moves" src="https://github.com/user-attachments/assets/954bd039-440d-44e9-9f70-09ed7f3e400e" />

