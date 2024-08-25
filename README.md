# Python Chess Engine

## Chess engine developed using python, pygame, and numpy

Python chess engine minus the smart engine part (currently just greedy). Have move generation most of the way there, with a small known bug where some pins work and others don't. Also includes some quality of life features like undoing, resetting the board, FEN string support, and different title and pawn promotion screens.

To use different FEN starting positions, go to the gameBoard.py file and find the initBoard function. Swap the input to whatever FEN you want to play with. There are a few FENs already avaiable located at the top of the board class in gameBoard.py. But any FEN can be added and used. Though the way the bot is currently setup relies on previous moves to calculate legal moves on the next turn. So loading in a FEN that isn't the starting FEN might give different moves than if you reached that position from the move before. So best to find a position you want, then have a move undone and remake that move to get to the position of interest. 

Shortcuts:
* z -> undo
* t -> toggle between AI & solo play
* r -> reset board to starting position

<img src="./images/chessTitleScreen.png" alt="Chess title screen" width="800" height="800" border="10" />
<img src="./images/chessGameState.png" alt="Chess game" width="800" height="800" border="10" />
<img src="./images/chessCheckState.png" alt="Knight moves in checked position" width="800" height="800" border="10" />