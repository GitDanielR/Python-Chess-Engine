from dataclasses import dataclass
import piece
import util

class moveData:
    def __init__(self, startSquare, endSquare, capturedPiece, capturedPieceSquare):
        self.startSquare = startSquare
        self.endSquare = endSquare
        self.capturedPiece: capturedPiece
        self.capturedPieceSquare: capturedPieceSquare

class move:
    def __init__(self, board, pieceList):
        self.legalMoves = [list() for _ in range(12)]
        self.sudoLegalMoves = []
        self.generateLegalMoves(board, pieceList)

    def generateLegalMoves(self, board, pieceList):
        self.legalMoves = [list() for _ in range(12)]
        for pieceType in pieceList:
            for pieceSquareIndex in pieceType:
                self.getLegalMovesForPiece(pieceSquareIndex, board, pieceList)

    def getLegalMovesForPiece(self, squareIndex, board, pieceList):
        self.sudoLegalMoves = []
        currentPiece = board[squareIndex]
        pieceType = util.pieceToPieceType(currentPiece)
        legalMovesIndex = util.pieceToListIndex(currentPiece)

        if pieceType == piece.pawn:
            self.generatePawnMoves(squareIndex, board)
            return
        elif pieceType == piece.knight:
            self.generateKnightMoves(squareIndex, board)
            return
        elif pieceType == piece.king:
            self.generateKingMoves(squareIndex, board)

        if pieceType == piece.bishop or pieceType == piece.queen:
            self.addDiagonalSliding(squareIndex, board)
        if pieceType == piece.queen or pieceType == piece.rook:
            self.addSliding(squareIndex, board)

        self.filterMoves(squareIndex, board)
        pieceListIndex = pieceList[legalMovesIndex].index(squareIndex)
        print(pieceListIndex)
        while pieceListIndex+1 > len(self.legalMoves[legalMovesIndex]):
            self.legalMoves[legalMovesIndex].append(list())
        print(self.legalMoves[legalMovesIndex])
        self.legalMoves[legalMovesIndex][pieceListIndex] = self.sudoLegalMoves

    def generatePawnMoves(self, squareIndex, board):
        movementDirection = -8 if piece.isWhite(board[squareIndex]) else 8
        file,rank = util.squareIndexToRelativeCoordinate(squareIndex)
        
        newSquareIndex = squareIndex+movementDirection
        if (board[squareIndex+movementDirection] == piece.none):
            self.addMoveData(squareIndex, newSquareIndex, board[newSquareIndex], newSquareIndex)

        newSquareIndex += movementDirection
        if ((rank == 1 and movementDirection == 8) or (rank == 6 and movementDirection == -8)):
            self.addMoveData(squareIndex, newSquareIndex, board[newSquareIndex], newSquareIndex)

        # captures
        newRank = rank + (1 if movementDirection == 8 else -1)
        if (file > 0):
            newSquareIndex = util.relativeCoordinatesToSquareIndex((file-1, newRank))
            if (util.isOpponent(squareIndex, newSquareIndex, board)):
                self.addMoveData(squareIndex, newSquareIndex, board[newSquareIndex], newSquareIndex)
        if (file < 7):
            newSquareIndex = util.relativeCoordinatesToSquareIndex((file+1, newRank))
            if (util.isOpponent(squareIndex, newSquareIndex, board)):
                self.addMoveData(squareIndex, newSquareIndex, board[newSquareIndex], newSquareIndex)

        # en passant
        if (rank == 3 and movementDirection == -8):
            if (board[squareIndex+1] == (piece.pawn | piece.black) and file < 7):
                self.addMoveData(squareIndex, squareIndex+movementDirection+1, board[squareIndex+1], squareIndex+1)
                self.sudoLegalMoves.append(squareIndex+movementDirection+1)
            elif (board[squareIndex-1] == (piece.pawn | piece.black) and file > 0):
                self.addMoveData(squareIndex, squareIndex+movementDirection-1, board[squareIndex-1], squareIndex-1)
        if (rank == 4 and movementDirection == 8):
            if (board[squareIndex+1] == (piece.pawn | piece.white) and file < 7):
                self.addMoveData(squareIndex, squareIndex+movementDirection+1, board[squareIndex+1], squareIndex+1)
            elif (board[squareIndex-1] == (piece.pawn | piece.white) and file > 0):
                self.addMoveData(squareIndex, squareIndex+movementDirection-1, board[squareIndex+1], squareIndex-1)

    def generateKnightMoves(self, squareIndex, board):
        file,rank = util.squareIndexToRelativeCoordinate(squareIndex)

        if (file > 1):
            if (rank < 7):
                newSquare = util.relativeCoordinatesToSquareIndex((file-2, rank+1))
                self.addMoveData(squareIndex, newSquare, board[newSquare], newSquare)
            if (rank > 0):
                newSquare = util.relativeCoordinatesToSquareIndex((file-2, rank-1))
                self.addMoveData(squareIndex, newSquare, board[newSquare], newSquare)
        if (file < 6):
            if (rank < 7):
                newSquare = util.relativeCoordinatesToSquareIndex((file+2, rank+1))
                self.addMoveData(squareIndex, newSquare, board[newSquare], newSquare)
            if (rank > 0):
                newSquare = util.relativeCoordinatesToSquareIndex((file+2, rank-1))
                self.addMoveData(squareIndex, newSquare, board[newSquare], newSquare)
        if (rank > 1):
            if (file < 7):
                newSquare = util.relativeCoordinatesToSquareIndex((file+1, rank-2))
                self.addMoveData(squareIndex, newSquare, board[newSquare], newSquare)
            if (file > 0):
                newSquare = util.relativeCoordinatesToSquareIndex((file-1, rank-2))
                self.addMoveData(squareIndex, newSquare, board[newSquare], newSquare)
        if (rank < 6):
            if (file < 7):
                newSquare = util.relativeCoordinatesToSquareIndex((file+1, rank+2))
                self.addMoveData(squareIndex, newSquare, board[newSquare], newSquare)
            if (file > 0):
                newSquare = util.relativeCoordinatesToSquareIndex((file-1, rank+2))
                self.addMoveData(squareIndex, newSquare, board[newSquare], newSquare)
    
    def generateKingMoves(self, squareIndex, board):
        file,rank = util.squareIndexToRelativeCoordinate(squareIndex)
        for df in range(-1,2):
            for dr in range(-1,2):
                if (df == 0 and dr == 0):
                    continue
                
                newFile = file+df
                newRank = rank+dr
                if (not util.fileRankInbounds(newFile, newRank)):
                    continue
                newSquareIndex = util.relativeCoordinatesToSquareIndex((newFile, newRank))
                self.addMoveData(squareIndex, newSquareIndex, board[newSquareIndex], newSquareIndex)
    
    def addDiagonalSliding(self, squareIndex, board):
        file,rank = util.squareIndexToRelativeCoordinate(squareIndex)
        for df in range(-1,2,2):
            for dr in range(-1,2,2):
                currentFile,currentRank = file,rank
                while (True):
                    currentFile += df
                    currentRank += dr
                    if (not util.fileRankInbounds(currentFile, currentRank)): 
                        break
                    currentSquare = util.relativeCoordinatesToSquareIndex((currentFile, currentRank))
                    pieceInPath = board[currentSquare]
                    self.addMoveData(squareIndex, currentSquare, pieceInPath, currentSquare)
                    if pieceInPath:
                        break
    
    def addSliding(self, squareIndex, board):
        file,rank = util.squareIndexToRelativeCoordinate(squareIndex)
        for movementDirection in range(-1,2,2):
            currentFile = file
            while (True):
                currentFile += movementDirection
                if (not util.fileRankInbounds(currentFile, rank)):
                    break
                currentSquare = util.relativeCoordinatesToSquareIndex((currentFile, rank))
                pieceInPath = board[currentSquare]
                self.addMoveData(squareIndex, currentSquare, pieceInPath, currentSquare)
                if pieceInPath:
                    break
        
        for movementDirection in range(-1,2,2):
            currentRank = rank
            while (True):
                currentRank += movementDirection
                if (not util.fileRankInbounds(file, currentRank)):
                    break
                currentSquare = util.relativeCoordinatesToSquareIndex((file, currentRank))
                pieceInPath = board[currentSquare]
                self.addMoveData(squareIndex, currentSquare, pieceInPath, currentSquare)
                if pieceInPath:
                    break
    
    def filterMoves(self, squareIndex, board):
        for moveSquare in self.sudoLegalMoves:
            pieceAtSquare = board[moveSquare.startSquare]
            if (pieceAtSquare != piece.none):
                if (piece.isWhite(pieceAtSquare) == piece.isWhite(board[squareIndex])):
                    self.sudoLegalMoves.remove(moveSquare)

    def addMoveData(self, squareIndex, newSquareIndex, capturedPiece, capturedPieceSquare):
        self.sudoLegalMoves.append(moveData(squareIndex, newSquareIndex, capturedPiece, capturedPieceSquare))