import numpy as np

class piece:
    none = 0
    king = 1
    pawn = 2
    knight = 3
    bishop = 4
    rook = 5
    queen = 6

    white = 8
    black = 16

    def isWhite(piece):
        return np.right_shift(piece,3) == 1

class board:
    startingFen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
    
    def __init__(self):
        self.board = np.zeros(64, dtype=np.uint8)
        self.bitboards = np.zeros(6, dtype=np.uint64)
        self.pieceLists = [list() for _ in range(12)]
        self.whiteToMove = True
        self.initBoard()

    def initBoard(self):
        self.positionFromFen(self.startingFen)
        self.setupPieceInformation()
    
    def setupPieceInformation(self):
        for squareIndex in range(64): 
            currentPiece = self.board[squareIndex]
            pieceType = board.pieceToPieceType(currentPiece)
            if (piece.isWhite(currentPiece)):
                pieceListIndex = pieceType-1
            else:
                pieceListIndex = pieceType+5

            if (currentPiece != piece.none):
                mask = 1 << squareIndex
                self.bitboards[pieceType-1] |= np.uint64(mask)
                self.pieceLists[pieceListIndex].append(squareIndex)

    def positionFromFen(self, position):
        pieceTypeFromSymbol = {
            'k' : piece.king,
            'p' : piece.pawn,
            'n' : piece.knight,
            'b' : piece.bishop,
            'r' : piece.rook,
            'q' : piece.queen
        }

        fenBoard = position.split(' ')[0]
        file = 0
        rank = 0

        for char in fenBoard:
            if (char == '/'):
                file = 0
                rank += 1
            else:
                if (char.isdigit()):
                    file += int(char)
                else:
                    pieceColor = piece.white if char.isupper() else piece.black
                    pieceType = pieceTypeFromSymbol[char.lower()]
                    self.board[rank*8 + file] = pieceColor | pieceType
                    file += 1
        print(self.board)

    # pieceToMove/endPosition = (file,rank)
    def makeMove(self, mouseClicks):
        activePieceBoardIndex = mouseClicks[0]
        endBoardIndex = mouseClicks[1]
        print('Making move from ', activePieceBoardIndex, ' to ', endBoardIndex)
        self.updatePieceInformation(activePieceBoardIndex, endBoardIndex)
        self.whiteToMove = not self.whiteToMove

    def pieceToPieceType(piece):
        return piece & 0b00111
    
    def updatePieceInformation(self, currentBoardIndex, endBoardIndex):
        piece = self.board[currentBoardIndex]
        pieceType = board.pieceToPieceType(piece)
        
        # Update bitboards
        self.bitboards[pieceType-1] ^= np.uint64(currentBoardIndex)
        self.bitboards[pieceType-1] |= np.uint64(endBoardIndex)

        # Update game board
        self.board[endBoardIndex] = piece
        self.board[currentBoardIndex] = 0

        # Update piece lists
        for pieceList in self.pieceLists:
            for index, val in enumerate(pieceList):
                if val == currentBoardIndex:
                    pieceList[index] = endBoardIndex
                    return
                
    def verifySelection(self, squareIndex):
        chosenPiece = self.board[squareIndex]
        if (chosenPiece == piece.none):
            return False
        return (piece.isWhite(chosenPiece) == self.whiteToMove)