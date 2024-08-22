Python chess engine minus the engine part. Currently still working on getting move generation to work correctly. Have it most of the way there with
support for things like castling, pinned pieces (currently pinned pieces cannot move at all), check, and the basic moves. Also includes some quality of life features like undoing, resetting the board, 
partial FEN string support (pieces, side to move) loading and retrieving from a game state, and different title and pawn promotion screens.

Shortcuts:
z -> undo move
r -> reset game board
e -> print position as FEN string (pieces, side to move are accurate)
