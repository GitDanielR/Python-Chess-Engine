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