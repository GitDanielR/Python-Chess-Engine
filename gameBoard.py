from dataclasses import dataclass
import numpy as np
import piece
import util

@dataclass
class move:
    startSquare: int
    endSquare: int
    capturedPiece: piece
    capturedPieceSquare: int

class board:
    startingFen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
    
    def __init__(self):
        self.board = np.zeros(64, dtype=np.uint8)
        self.bitboards = np.zeros(6, dtype=np.uint64)
        self.pieceLists = [list() for _ in range(12)]
        self.whiteToMove = True
        self.inCheck = False
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
        squareFile,squareRank = util.squareIndexToRelativeCoordinate(squareIndex)
        selectedFile,selectedRank = util.squareIndexToRelativeCoordinate(squareSelected)
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
        file,rank = util.squareIndexToRelativeCoordinate(squareIndex)
        
        if (self.board[squareIndex+movementDirection] == piece.none):
            self.addMoveData(squareIndex, squareIndex+movementDirection, piece.none, None)
            # self.legalMoves.append(squareIndex+movementDirection)

        if ((rank == 1 and movementDirection == 8) or (rank == 6 and movementDirection == -8)):
            newSquareIndex = squareIndex+(2*movementDirection)
            if (self.board[newSquareIndex] == piece.none):
                self.addMoveData(squareIndex, newSquareIndex, piece.none, None)
                # self.legalMoves.append(squareIndex+(2*movementDirection))
        
        # captures
        newRank = rank + (1 if movementDirection == 8 else -1)
        if (file > 0):
            newSquareIndex = util.relativeCoordinatesToSquareIndex((file-1, newRank))
            if (self.isOpponent(squareIndex, newSquareIndex)):
                self.addMoveData(squareIndex, newSquareIndex, self.board[newSquareIndex], newSquareIndex)
                # self.legalMoves.append(newSquareIndex)
        if (file < 7):
            newSquareIndex = util.relativeCoordinatesToSquareIndex((file+1, newRank))
            if (self.isOpponent(squareIndex, newSquareIndex)):
                self.addMoveData(squareIndex, newSquareIndex, self.board[newSquareIndex], newSquareIndex)
                # self.legalMoves.append(newSquareIndex)

        # en passant (up left of a piece doesn't work? movementDirection+1)
        if (rank == 3 and movementDirection == -8):
            if (self.board[squareIndex+1] == (piece.pawn | piece.black) and file < 7):
                self.addMoveData(squareIndex, squareIndex+movementDirection+1, self.board[squareIndex+1], squareIndex+1)
                # self.legalMoves.append(squareIndex+movementDirection+1)
            if (self.board[squareIndex-1] == (piece.pawn | piece.black) and file > 0):
                self.addMoveData(squareIndex, squareIndex+movementDirection-1, self.board[squareIndex-1], squareIndex-1)
                # self.legalMoves.append(squareIndex+movementDirection-1)
        if (rank == 4 and movementDirection == 8):
            if (self.board[squareIndex+1] == (piece.pawn | piece.white) and file < 7):
                self.addMoveData(squareIndex, squareIndex+movementDirection+1, self.board[squareIndex+1], squareIndex+1)
                # self.legalMoves.append(squareIndex+movementDirection+1)
            if (self.board[squareIndex-1] == (piece.pawn | piece.white) and file > 0):
                self.addMoveData(squareIndex, squareIndex+movementDirection-1, self.board[squareIndex-1], squareIndex-1)
                # self.legalMoves.append(squareIndex+movementDirection-1)

    def generateKnightMoves(self, squareIndex):
        file,rank = util.squareIndexToRelativeCoordinate(squareIndex)

        if (file > 1):
            if (rank < 7):
                newSquareIndex = util.relativeCoordinatesToSquareIndex((file-2, rank+1))
                self.addMoveData(squareIndex, newSquareIndex, self.board[newSquareIndex], newSquareIndex)
                # self.legalMoves.append(util.relativeCoordinatesToSquareIndex((file-2, rank+1)))
            if (rank > 0):
                newSquareIndex = util.relativeCoordinatesToSquareIndex((file-2, rank-1))
                self.addMoveData(squareIndex, newSquareIndex, self.board[newSquareIndex], newSquareIndex)
                # self.legalMoves.append(util.relativeCoordinatesToSquareIndex((file-2, rank-1)))
        if (file < 6):
            if (rank < 7):
                newSquareIndex = util.relativeCoordinatesToSquareIndex((file+2, rank+1))
                self.addMoveData(squareIndex, newSquareIndex, self.board[newSquareIndex], newSquareIndex)
                # self.legalMoves.append(util.relativeCoordinatesToSquareIndex((file+2, rank+1)))
            if (rank > 0):
                newSquareIndex = util.relativeCoordinatesToSquareIndex((file+2, rank-1))
                self.addMoveData(squareIndex, newSquareIndex, self.board[newSquareIndex], newSquareIndex)
                # self.legalMoves.append(util.relativeCoordinatesToSquareIndex((file+2, rank-1)))
        if (rank > 1):
            if (file < 7):
                newSquareIndex = util.relativeCoordinatesToSquareIndex((file+1, rank-2))
                self.addMoveData(squareIndex, newSquareIndex, self.board[newSquareIndex], newSquareIndex)
                # self.legalMoves.append(util.relativeCoordinatesToSquareIndex((file+1, rank-2)))
            if (file > 0):
                newSquareIndex = util.relativeCoordinatesToSquareIndex((file-1, rank-2))
                self.addMoveData(squareIndex, newSquareIndex, self.board[newSquareIndex], newSquareIndex)
                # self.legalMoves.append(util.relativeCoordinatesToSquareIndex((file-1, rank-2)))
        if (rank < 6):
            if (file < 7):
                newSquareIndex = util.relativeCoordinatesToSquareIndex((file+1, rank+2))
                self.addMoveData(squareIndex, newSquareIndex, self.board[newSquareIndex], newSquareIndex)
                # self.legalMoves.append(util.relativeCoordinatesToSquareIndex((file+1, rank+2)))
            if (file > 0):
                newSquareIndex = util.relativeCoordinatesToSquareIndex((file-1, rank+2))
                self.addMoveData(squareIndex, newSquareIndex, self.board[newSquareIndex], newSquareIndex)
                # self.legalMoves.append(util.relativeCoordinatesToSquareIndex((file-1, rank+2)))
    
    def generateKingMoves(self, squareIndex):
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
                self.addMoveData(squareIndex, newSquareIndex, self.board[newSquareIndex], newSquareIndex)
    
    def addDiagonalSliding(self, squareIndex):
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
                    pieceInPath = self.board[currentSquare]
                    self.addMoveData(squareIndex, currentSquare, pieceInPath, currentSquare)
                    if pieceInPath:
                        break
    
    def addSliding(self, squareIndex):
        file,rank = util.squareIndexToRelativeCoordinate(squareIndex)
        for movementDirection in range(-1,2,2):
            currentFile = file
            while (True):
                currentFile += movementDirection
                if (not util.fileRankInbounds(currentFile, rank)):
                    break
                currentSquare = util.relativeCoordinatesToSquareIndex((currentFile, rank))
                pieceInPath = self.board[currentSquare]
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
                pieceInPath = self.board[currentSquare]
                self.addMoveData(squareIndex, currentSquare, pieceInPath, currentSquare)
                if pieceInPath:
                    break
    
    # TO-DO: Filter moves that leave king in check
    def filterMoves(self, squareIndex):
        for move in self.legalMoves:
            pieceAtSquare = self.board[move.endSquare]
            if (pieceAtSquare != piece.none):
                if (piece.isWhite(pieceAtSquare) == piece.isWhite(self.board[squareIndex])):
                    self.legalMoves.remove(move)

    # pieceToMove/endPosition = (file,rank)
    def makeMove(self, chosenMove):
        self.updateBoardWithMove(chosenMove)
        self.moveLog.append(chosenMove)
        self.whiteToMove = not self.whiteToMove

        self.inCheck = self.moveCreatesCheck(self.moveLog[-1])
        if self.inCheck: self.checkCheckmate(self.moveLog[-1])

    def moveCreatesCheck(self, moveToCheck):
        # pieces at index 1-5
        self.populatelegalMoves(moveToCheck.endSquare)
        if any(board.pieceToPieceType(possibleMove.capturedPiece) == piece.king for possibleMove in self.legalMoves):
            return True
        else:
            return False

    def checkCheckmate(self, previousMove):
        # Check the current teams pieces and see if any of them can be moved such that no longer in check
        checkmateAvoidable = True
        pieceListOffset = 0 if self.whiteToMove else 6
        for i in range(6):
            pieceListIndex = pieceListOffset + i
            for pieceList in self.pieceLists[pieceListIndex]:
                if isinstance(pieceList, int):
                    checkmateAvoidable = self.pieceCanRemoveCheck(pieceList, previousMove)
                    if checkmateAvoidable:
                        print('Checkmate avoidable')
                        return
                else:
                    for pieceSquare in pieceList:
                        checkmateAvoidable = self.pieceCanRemoveCheck(pieceSquare, previousMove)
                        # Right now only considers the piece that was initally attacking, not all the pieces attacking
                        if checkmateAvoidable:
                            print('Checkmate avoidable')
                            return
        print('Checkmate')
    
    def pieceCanRemoveCheck(self, pieceSquare, pieceChecking):
        self.populatelegalMoves(pieceSquare)
        for possibleMove in self.legalMoves:
            self.makeMove(possibleMove)
            stillInCheck = self.moveCreatesCheck(pieceChecking)
            self.unmakeMove()
            if not stillInCheck:
                return True
        return False

    def unmakeMove(self):
        if (len(self.moveLog) == 0): return
        undoneMove = self.moveLog.pop()
        
        self.updateBoardWithMove(move(undoneMove.endSquare, undoneMove.startSquare, piece.none, None))
        if undoneMove.capturedPiece:
            self.setPieceInformationAtIndex(undoneMove.capturedPiece, undoneMove.capturedPieceSquare)
        self.whiteToMove = not self.whiteToMove

    def updateBoardWithMove(self, chosenMove):
        if (chosenMove.capturedPiece != piece.none):
            self.setPieceInformationAtIndex(piece.none, chosenMove.capturedPieceSquare)

        currentPiece = self.board[chosenMove.startSquare]
        self.setPieceInformationAtIndex(currentPiece, chosenMove.endSquare)
        self.setPieceInformationAtIndex(piece.none, chosenMove.startSquare)

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
        
    def addMoveData(self, squareIndex, newSquareIndex, capturedPiece, capturedPieceSquare):
        self.legalMoves.append(move(squareIndex, newSquareIndex, capturedPiece, capturedPieceSquare))