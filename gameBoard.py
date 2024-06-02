from dataclasses import dataclass
import numpy as np
from util import squareIndexToRelativeCoordinate, relativeCoordinatesToSquareIndex, fileRankInbounds

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

@dataclass
class move:
    startSquare: int
    endSquare: int
    capturedPiece: piece.none

class board:
    startingFen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
    
    def __init__(self):
        self.board = np.zeros(64, dtype=np.uint8)
        self.bitboards = np.zeros(6, dtype=np.uint64)
        self.pieceLists = [list() for _ in range(12)]
        self.whiteToMove = True
        self.moveLog = []
        self.legalMoves = []
        self.initBoard()

    def initBoard(self):
        self.positionFromFen(self.startingFen)
        self.setupPieceInformation()
    
    def setupPieceInformation(self):
        for squareIndex in range(64): 
            currentPiece = self.board[squareIndex]

            if (currentPiece != piece.none):
                pieceType = board.pieceToPieceType(currentPiece)
                pieceListIndex = board.pieceToListIndex(currentPiece)
                mask = 1 << squareIndex
                self.bitboards[pieceType-1] |= np.uint64(mask)
                self.pieceLists[pieceListIndex].append(squareIndex)

    def isOpponent(self, squareIndex, squareSelected):
        if (squareSelected is None or squareIndex is None or self.board[squareIndex] == piece.none or self.board[squareSelected] == piece.none):
            return False
        return piece.isWhite(self.board[squareIndex]) != piece.isWhite(self.board[squareSelected])

    def isPawnCapture(self, squareIndex, squareSelected):
        squareFile,squareRank = squareIndexToRelativeCoordinate(squareIndex)
        selectedFile,selectedRank = squareIndexToRelativeCoordinate(squareSelected)
        return (board.pieceToPieceType(self.board[squareIndex]) == piece.pawn and squareFile != selectedFile)

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

    def populatelegalMoves(self, squareIndex):
        self.legalMoves = []
        currentPiece = self.board[squareIndex]
        pieceType = board.pieceToPieceType(currentPiece)

        if pieceType == piece.pawn:
            self.generatePawnMoves(squareIndex)
            return
        elif pieceType == piece.knight:
            self.generateKnightMoves(squareIndex)
            return
        elif pieceType == piece.king:
            self.generateKingMoves(squareIndex)

        if pieceType == piece.bishop or pieceType == piece.queen:
            self.addDiagonalSliding(squareIndex)
        if pieceType == piece.queen or pieceType == piece.rook:
            self.addSliding(squareIndex)

        self.filterMoves(squareIndex)

    def generatePawnMoves(self, squareIndex):
        movementDirection = -8 if piece.isWhite(self.board[squareIndex]) else 8
        file,rank = squareIndexToRelativeCoordinate(squareIndex)
        
        if (self.board[squareIndex+movementDirection] == piece.none):
            self.legalMoves.append(squareIndex+movementDirection)

        if ((rank == 1 and movementDirection == 8) or (rank == 6 and movementDirection == -8)):
            self.legalMoves.append(squareIndex+(2*movementDirection))
        
        # captures
        newRank = rank + (1 if movementDirection == 8 else -1)
        if (file > 0):
            newSquareIndex = relativeCoordinatesToSquareIndex((file-1, newRank))
            if (self.isOpponent(squareIndex, newSquareIndex)):
                self.legalMoves.append(newSquareIndex)
        if (file < 7):
            newSquareIndex = relativeCoordinatesToSquareIndex((file+1, newRank))
            if (self.isOpponent(squareIndex, newSquareIndex)):
                self.legalMoves.append(newSquareIndex)

        # en passant
        if (rank == 3 and movementDirection == -8):
            if (self.board[squareIndex+1] == (piece.pawn | piece.black) and file < 7):
                self.legalMoves.append(squareIndex+movementDirection+1)
            elif (self.board[squareIndex-1] == (piece.pawn | piece.black) and file > 0):
                self.legalMoves.append(squareIndex+movementDirection-1)
        if (rank == 4 and movementDirection == 8):
            if (self.board[squareIndex+1] == (piece.pawn | piece.white) and file < 7):
                self.legalMoves.append(squareIndex+movementDirection+1)
            elif (self.board[squareIndex-1] == (piece.pawn | piece.white) and file > 0):
                self.legalMoves.append(squareIndex+movementDirection-1)


    def generateKnightMoves(self, squareIndex):
        file,rank = squareIndexToRelativeCoordinate(squareIndex)

        if (file > 1):
            if (rank < 7):
                self.legalMoves.append(relativeCoordinatesToSquareIndex((file-2, rank+1)))
            if (rank > 0):
                self.legalMoves.append(relativeCoordinatesToSquareIndex((file-2, rank-1)))
        if (file < 6):
            if (rank < 7):
                self.legalMoves.append(relativeCoordinatesToSquareIndex((file+2, rank+1)))
            if (rank > 0):
                self.legalMoves.append(relativeCoordinatesToSquareIndex((file+2, rank-1)))
        if (rank > 1):
            if (file < 7):
                self.legalMoves.append(relativeCoordinatesToSquareIndex((file+1, rank-2)))
            if (file > 0):
                self.legalMoves.append(relativeCoordinatesToSquareIndex((file-1, rank-2)))
        if (rank < 6):
            if (file < 7):
                self.legalMoves.append(relativeCoordinatesToSquareIndex((file+1, rank+2)))
            if (file > 0):
                self.legalMoves.append(relativeCoordinatesToSquareIndex((file-1, rank+2)))
    
    def generateKingMoves(self, squareIndex):
        file,rank = squareIndexToRelativeCoordinate(squareIndex)
        for df in range(-1,2):
            for dr in range(-1,2):
                if (df == 0 and dr == 0):
                    continue
                
                newFile = file+df
                newRank = rank+dr
                if (not fileRankInbounds(newFile, newRank)):
                    continue
                self.legalMoves.append(relativeCoordinatesToSquareIndex((newFile, newRank)))
    
    def addDiagonalSliding(self, squareIndex):
        file,rank = squareIndexToRelativeCoordinate(squareIndex)
        for df in range(-1,2,2):
            for dr in range(-1,2,2):
                currentFile,currentRank = file,rank
                while (True):
                    currentFile += df
                    currentRank += dr
                    if (not fileRankInbounds(currentFile, currentRank)): 
                        break
                    currentSquare = relativeCoordinatesToSquareIndex((currentFile, currentRank))
                    self.legalMoves.append(currentSquare)
                    pieceInPath = self.board[currentSquare]
                    if pieceInPath:
                        break
    
    def addSliding(self, squareIndex):
        file,rank = squareIndexToRelativeCoordinate(squareIndex)
        for movementDirection in range(-1,2,2):
            currentFile = file
            while (True):
                currentFile += movementDirection
                if (not fileRankInbounds(currentFile, rank)):
                    break
                currentSquare = relativeCoordinatesToSquareIndex((currentFile, rank))
                self.legalMoves.append(currentSquare)
                pieceInPath = self.board[currentSquare]
                if pieceInPath:
                    break
        
        for movementDirection in range(-1,2,2):
            currentRank = rank
            while (True):
                currentRank += movementDirection
                if (not fileRankInbounds(file, currentRank)):
                    break
                currentSquare = relativeCoordinatesToSquareIndex((file, currentRank))
                self.legalMoves.append(currentSquare)
                pieceInPath = self.board[currentSquare]
                if pieceInPath:
                    break
    
    def filterMoves(self, squareIndex):
        for move in self.legalMoves:
            pieceAtSquare = self.board[move]
            if (pieceAtSquare != piece.none):
                if (piece.isWhite(pieceAtSquare) == piece.isWhite(self.board[squareIndex])):
                    self.legalMoves.remove(move)

    # pieceToMove/endPosition = (file,rank)
    def makeMove(self, mouseClicks):
        activePieceBoardIndex = mouseClicks[0]
        endBoardIndex = mouseClicks[1]
        if (endBoardIndex not in self.legalMoves):
            return
        
        capturedPiece = self.board[endBoardIndex]
        if (capturedPiece != piece.none and piece.isWhite(self.board[activePieceBoardIndex]) == piece.isWhite(capturedPiece)): return

        self.updatePieceInformation(activePieceBoardIndex, endBoardIndex)
        self.moveLog.append(move(activePieceBoardIndex, endBoardIndex, capturedPiece))
        self.whiteToMove = not self.whiteToMove

    def unmakeMove(self):
        if (len(self.moveLog) == 0): return
        move = self.moveLog.pop()
        self.updatePieceInformation(move.endSquare, move.startSquare)
        self.setPieceInformationAtIndex(move.capturedPiece, move.endSquare)
        self.whiteToMove = not self.whiteToMove

    def updatePieceInformation(self, currentBoardIndex, endBoardIndex):
        if (self.board[endBoardIndex]):
            self.setPieceInformationAtIndex(piece.none, endBoardIndex)

        currentPiece = self.board[currentBoardIndex]
        self.setPieceInformationAtIndex(currentPiece, endBoardIndex)
        self.setPieceInformationAtIndex(piece.none, currentBoardIndex)

    def setPieceInformationAtIndex(self, currentPiece, squareIndex):
        pieceType = board.pieceToPieceType(currentPiece)
        pieceListIndex = board.pieceToListIndex(currentPiece)
        self.bitboards[pieceType-1] ^= np.uint64(squareIndex)
        self.board[squareIndex] = currentPiece

        if currentPiece != piece.none:
            self.pieceLists[pieceListIndex].append(squareIndex)
        else:
            for pieceList in self.pieceLists:
                if squareIndex in pieceList:
                    pieceList.remove(squareIndex)
                    return
                
    def verifySelection(self, squareIndex):
        chosenPiece = self.board[squareIndex]
        if (chosenPiece == piece.none):
            return False
        return (piece.isWhite(chosenPiece) == self.whiteToMove)
    
    def pieceToPieceType(piece):
        return piece & 0b00111
    
    def pieceToListIndex(currentPiece):
        pieceType = board.pieceToPieceType(currentPiece)
        if (piece.isWhite(currentPiece)):
            return pieceType-1
        else:
            return pieceType+5