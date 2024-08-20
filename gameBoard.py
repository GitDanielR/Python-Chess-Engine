from dataclasses import dataclass
import numpy as np
import piece
import promotionScreen
import random
import util

@dataclass
class move:
    startSquare: int
    endSquare: int
    capturedPiece: piece
    capturedPieceSquare: int
    isCastle: bool

class board:
    startingFen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
    pawnPromotionFen = '8/P7/8/8/8/8/8/8 w - - 0 1'
    allCastlingPossibleFen = 'r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1'
    
    def __init__(self):
        self.board = np.zeros(64, dtype=np.uint8)
        self.bitboards = np.zeros(6, dtype=np.uint64)
        self.pieceLists = [list() for _ in range(12)]
        self.castlingRights = CastlingRights()
        self.whiteToMove = True
        self.check = False
        self.moveLog = []
        self.legalMoves = {}
        self.piecesLegalMoves = []
        self.squaresEnemyAttacks = []
        self.piecePinDirections = [[0 for _ in range(64)],[0 for _ in range(64)]]   # idx 0 is black pins, 1 is white pins 
        self.initBoard()

    def initBoard(self):
        self.positionFromFen(self.startingFen)
        self.setupPieceInformation()
        self.getAllLegalMoves()
    
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

    def getAllLegalMoves(self):
        self.legalMoves = {}
        pieceListOffset = 0 if self.whiteToMove else 6
        for i in range(6):
            pieceListIndex = pieceListOffset + i
            for pieceList in self.pieceLists[pieceListIndex]:
                if isinstance(pieceList, int):
                    # just one piece of type
                    self.populatelegalMoves(pieceList)
                    self.legalMoves[pieceList] = self.piecesLegalMoves
                else:
                    for pieceSquare in pieceList:
                        self.populatelegalMoves(pieceSquare)
                        self.legalMoves[pieceSquare] = self.piecesLegalMoves

    def populatelegalMoves(self, squareIndex):
        self.piecesLegalMoves = []
        currentPiece = self.board[squareIndex]
        pieceType = board.pieceToPieceType(currentPiece)

        if pieceType == piece.pawn:
            self.generatePawnMoves(squareIndex)
            return
        elif pieceType == piece.knight:
            self.generateKnightMoves(squareIndex)
        elif pieceType == piece.king:
            self.generateKingMoves(squareIndex)

        if pieceType == piece.bishop or pieceType == piece.queen:
            self.addDiagonalSliding(squareIndex)
        if pieceType == piece.queen or pieceType == piece.rook:
            self.addSliding(squareIndex)

        self.filterPins(squareIndex)

    def filterPins(self, squareIndex):
        if len(self.piecesLegalMoves) == 0: return

        pinType = self.piecePinDirections[self.whiteToMove][squareIndex]
        if pinType == 0: return

        startFile,startRank = util.squareIndexToRelativeCoordinate(squareIndex)
        for possibleMove in self.piecesLegalMoves:
            endFile,endRank = util.squareIndexToRelativeCoordinate(possibleMove.endSquare)
            df = max(-1, min(endFile-startFile, 1))
            dr = max(-1, min(endRank-startRank, 1))
            if df != pinType[0] or dr != pinType[1]:
                self.piecesLegalMoves.remove(possibleMove)

    def generatePawnMoves(self, squareIndex):
        movementDirection = -8 if piece.isWhite(self.board[squareIndex]) else 8
        file,rank = util.squareIndexToRelativeCoordinate(squareIndex)
        
        if (self.board[squareIndex+movementDirection] == piece.none):
            self.addMoveData(squareIndex, squareIndex+movementDirection, piece.none, None)

        if ((rank == 1 and movementDirection == 8) or (rank == 6 and movementDirection == -8)):
            newSquareIndex = squareIndex+(2*movementDirection)
            if (self.board[newSquareIndex] == piece.none):
                self.addMoveData(squareIndex, newSquareIndex, piece.none, None)
        
        # captures
        newRank = rank + (1 if movementDirection == 8 else -1)
        if (file > 0):
            newSquareIndex = util.relativeCoordinatesToSquareIndex((file-1, newRank))
            if (self.isOpponent(squareIndex, newSquareIndex)):
                self.addMoveData(squareIndex, newSquareIndex, self.board[newSquareIndex], newSquareIndex)
        if (file < 7):
            newSquareIndex = util.relativeCoordinatesToSquareIndex((file+1, newRank))
            if (self.isOpponent(squareIndex, newSquareIndex)):
                self.addMoveData(squareIndex, newSquareIndex, self.board[newSquareIndex], newSquareIndex)

        # en passant
        if (rank == 3 and movementDirection == -8):
            if (self.board[squareIndex+1] == (piece.pawn | piece.black) and file < 7):
                self.addMoveData(squareIndex, squareIndex+movementDirection+1, self.board[squareIndex+1], squareIndex+1)
            if (self.board[squareIndex-1] == (piece.pawn | piece.black) and file > 0):
                self.addMoveData(squareIndex, squareIndex+movementDirection-1, self.board[squareIndex-1], squareIndex-1)
        if (rank == 4 and movementDirection == 8):
            if (self.board[squareIndex+1] == (piece.pawn | piece.white) and file < 7):
                self.addMoveData(squareIndex, squareIndex+movementDirection+1, self.board[squareIndex+1], squareIndex+1)
            if (self.board[squareIndex-1] == (piece.pawn | piece.white) and file > 0):
                self.addMoveData(squareIndex, squareIndex+movementDirection-1, self.board[squareIndex-1], squareIndex-1)

    def generateKnightMoves(self, squareIndex):
        file,rank = util.squareIndexToRelativeCoordinate(squareIndex)

        for knightMove in piece.knightMovementDirections:
            newFile,newRank = file+knightMove[0],rank+knightMove[1]
            if (util.fileRankInbounds(newFile,newRank)): 
                newSquareIndex = util.relativeCoordinatesToSquareIndex((newFile,newRank))
                self.addMoveData(squareIndex, newSquareIndex, self.board[newSquareIndex], newSquareIndex)
    
    def generateKingMoves(self, squareIndex):
        file,rank = util.squareIndexToRelativeCoordinate(squareIndex)
        for df in [-1,0,1]:
            for dr in [-1,0,1]:
                if (df == dr == 0): continue
                
                newFile = file+df
                newRank = rank+dr
                if (not util.fileRankInbounds(newFile, newRank)):
                    continue
                newSquareIndex = util.relativeCoordinatesToSquareIndex((newFile, newRank))
                # can't put yourself in check
                if not newSquareIndex in self.squaresEnemyAttacks: self.addMoveData(squareIndex, newSquareIndex, self.board[newSquareIndex], newSquareIndex)

        kingColor = 'white' if self.whiteToMove else 'black'
        # have castling rights
        if self.castlingRights.possibleCastles[kingColor + 'QueenSide']: 
            # castling path not attacked by enemy pieces
            if ((squareIndex - 1) not in self.squaresEnemyAttacks) and ((squareIndex - 2) not in self.squaresEnemyAttacks): 
                # castling path doesn't have pieces in the way
                if (self.board[squareIndex-1] == piece.none and self.board[squareIndex-2] == piece.none and self.board[squareIndex-3] == piece.none):
                    self.addMoveData(squareIndex, squareIndex-2, piece.none, squareIndex-2, True)
        if self.castlingRights.possibleCastles[kingColor + 'KingSide']: 
            if ((squareIndex + 1) not in self.squaresEnemyAttacks) and ((squareIndex + 2) not in self.squaresEnemyAttacks):
                if (self.board[squareIndex+1] == piece.none and self.board[squareIndex+2] == piece.none):
                    self.addMoveData(squareIndex, squareIndex+2, piece.none, squareIndex+2, True)
    
    def addDiagonalSliding(self, squareIndex):
        file,rank = util.squareIndexToRelativeCoordinate(squareIndex)
        for df in [-1,1]:
            for dr in [-1,1]:
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
        for movementDirection in [-1,1]:
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
        
        for movementDirection in [-1,1]:
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
        
    # pieceToMove/endPosition = (file,rank)
    def makeMove(self, chosenMove):
        self.calculatePins()

        self.castlingRights.saveCastleState()
        self.moveLog.append(chosenMove)

        self.updateBoardWithMove(chosenMove)
        self.check = self.checkForCheck()

        if self.check: print('In check')
        self.getAllLegalMoves()     # update what the person who just moved can do
        # get all squares that the current (almost previous) team can attack - used for castling rights & pins
        self.squaresEnemyAttacks = [item.endSquare for sublist in self.legalMoves.values() for item in sublist] 
        self.whiteToMove = not self.whiteToMove
        self.getAllLegalMoves()

    def checkForCheck(self):
        foundKing = np.where(self.board == (self.whiteToMove * 8) + 9)
        kingSquare = foundKing[0][0] # where is opponents king
        file,rank = util.squareIndexToRelativeCoordinate(kingSquare)

        kingIsWhite = piece.isWhite(self.board[kingSquare])
        oppositeColor = piece.black if kingIsWhite else piece.white
        
        movementDirection = -8 if kingIsWhite else 8
        if self.board[kingSquare+movementDirection+1] == (piece.pawn | oppositeColor) or self.board[kingSquare+movementDirection-1] == (piece.pawn | oppositeColor): # pawns
            return True
        
        for knightMovementDirection in piece.knightMovementDirections:  # knights
            knightFile,knightRank = file+knightMovementDirection[0],rank+knightMovementDirection[1]
            if not util.fileRankInbounds(knightFile,knightRank): continue    # this should be in file,col -> can have weird knight checks?
            if self.board[util.relativeCoordinatesToSquareIndex((knightFile,knightRank))] == (piece.knight | oppositeColor): 
                return True

        closestPiecesSquare = []
        attackType = []    
        foundNearest = False
        # queen, rook, bishop
        for df in [-1,0,1]:
            for dr in [-1,0,1]:
                if (df == dr == 0): continue

                currentFile, currentRank = file,rank
                while True:
                    currentFile += df
                    currentRank += dr
                    if (not util.fileRankInbounds(currentFile,currentRank)): break

                    currentSquare = util.relativeCoordinatesToSquareIndex((currentFile,currentRank))
                    pieceInPath = self.board[currentSquare]
                    if pieceInPath:
                        if not foundNearest:closestPiecesSquare.append(currentSquare)
                        attackType.append(util.dFdRtoType(df, dr))
                        break
        
        possiblePieceMatches = [piece.queen | oppositeColor, piece.rook | oppositeColor, piece.bishop | oppositeColor]
        for index,blockingPieceSquare in enumerate(closestPiecesSquare):
            blockingPiece = self.board[blockingPieceSquare]
            if blockingPiece not in possiblePieceMatches: continue

            blockingPieceType = board.pieceToPieceType(blockingPiece)
            attackDirection = attackType[index]
            if blockingPieceType == piece.rook and (attackDirection == 'horizontal' or attackDirection == 'vertical'): return True
            elif blockingPieceType == piece.bishop and attackDirection == 'diagonal': return True
            elif blockingPieceType == piece.queen: return True   # queen can attack anything it wants to

        return False

    def unmakeMove(self):
        if (len(self.moveLog) == 0): return
        undoneMove = self.moveLog.pop()
        self.castlingRights.undoCastleMove()
        
        self.updateBoardWithMove(move(undoneMove.endSquare, undoneMove.startSquare, piece.none, None, undoneMove.isCastle), True)
        if undoneMove.capturedPiece:
            self.setPieceInformationAtIndex(undoneMove.capturedPiece, undoneMove.capturedPieceSquare)
        self.getAllLegalMoves()     # update what the person who just moved can do
        # get all squares that the current (almost previous) team can attack - used for castling rights & pins
        self.squaresEnemyAttacks = [item.endSquare for sublist in self.legalMoves.values() for item in sublist] 
        self.whiteToMove = not self.whiteToMove
        self.getAllLegalMoves()

    def updateBoardWithMove(self, chosenMove, undoing=False):
        if (chosenMove.capturedPiece != piece.none):
            self.setPieceInformationAtIndex(piece.none, chosenMove.capturedPieceSquare)

        currentPiece = self.board[chosenMove.startSquare]
        currentPieceType = board.pieceToPieceType(currentPiece)
        if currentPieceType == piece.pawn:  # pawn promotion
            file,rank = util.squareIndexToRelativeCoordinate(chosenMove.endSquare)
            if rank == 0 or rank == 7:  # update the pieceLists 
                chosenPiece = promotionScreen.choosePromotionForPawn()
                if chosenPiece == 'queen': currentPiece = piece.queen
                elif chosenPiece == 'rook': currentPiece = piece.rook
                elif chosenPiece == 'bishop': currentPiece = piece.bishop
                else: currentPiece = piece.knight
                currentPiece = currentPiece | (piece.white if self.whiteToMove else piece.black) 
        elif currentPieceType == piece.king and not undoing:    # moving king disables all castle rights
            kingColor = 'white' if self.whiteToMove else 'black'
            self.castlingRights.disableCastleMove([kingColor + 'QueenSide', kingColor + 'KingSide'])
        elif currentPieceType == piece.rook and not undoing:    # moving rook disables one side castle rights
            kingColor = 'white' if self.whiteToMove else 'black'
            castleSide = 'QueenSide' if chosenMove.startSquare % 8 == 0 else 'KingSide'
            self.castlingRights.disableCastleMove([kingColor + castleSide])

        self.setPieceInformationAtIndex(currentPiece, chosenMove.endSquare)
        self.setPieceInformationAtIndex(piece.none, chosenMove.startSquare)
        if chosenMove.isCastle:
            if not undoing:
                rookSide = 1 if chosenMove.endSquare < chosenMove.startSquare else -1
                rookSquare = chosenMove.endSquare + rookSide
                noPieceSquare = chosenMove.endSquare-2 if rookSide == 1 else chosenMove.endSquare+1
            else:
                rookSide = 1 if chosenMove.startSquare < chosenMove.endSquare else -1
                noPieceSquare = chosenMove.startSquare + rookSide 
                rookSquare = round(noPieceSquare/8)*8
                if rookSquare > noPieceSquare: rookSquare -= 1
        
            rookColor = piece.white if piece.isWhite(currentPiece) else piece.black
            self.setPieceInformationAtIndex(piece.rook | rookColor, rookSquare)
            self.setPieceInformationAtIndex(piece.none, noPieceSquare)

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
        offset = -1 if piece.isWhite(currentPiece) else 5
        return pieceType + offset
        
    def addMoveData(self, squareIndex, newSquareIndex, capturedPiece, capturedPieceSquare, isCastle=False):
        if capturedPiece != piece.none and (piece.isWhite(capturedPiece) == self.whiteToMove): return   # can't attack self

        self.piecesLegalMoves.append(move(squareIndex, newSquareIndex, capturedPiece, capturedPieceSquare, isCastle))

    def displayLegalMoves(self):
        for pieceSquare, moves in self.legalMoves.items():
            print('possible moves for : ' + self.pieceInformationString(pieceSquare))
            for move in moves:
                print('End Square: ' + self.pieceInformationString(move.endSquare))
                if move.capturedPiece != 0: print('Captured piece square: ' + self.pieceInformationString(move.capturedPieceSquare))

    def pieceInformationString(self, pieceSquare):
        currentPiece = self.board[pieceSquare]
        pieceType = board.pieceToPieceType(currentPiece)
        pieceColor = 'none ' if currentPiece == 0 else 'white ' if piece.isWhite(currentPiece) else 'black '
        file,rank = util.squareIndexToRelativeCoordinate(pieceSquare)
        return pieceColor + piece.pieceMap[pieceType] + ' at file ' + str(file) + ', rank ' + str(rank)
    
    def calculatePins(self):
        self.piecePinDirections = [[0 for _ in range(64)],[0 for _ in range(64)]]
        whiteKing = np.where(self.board == (piece.king | piece.white))[0][0]
        blackKing = np.where(self.board == (piece.king | piece.black))[0][0]

        # only sliding pieces can pin -> do like sliding
        whiteKingFile, whiteKingRank = util.squareIndexToRelativeCoordinate(whiteKing)
        blackKingFile, blackKingRank = util.squareIndexToRelativeCoordinate(blackKing)
        for df in [-1,0,1]:
            for dr in [-1,0,1]:
                if (df == dr == 0): continue

                solvingForWhite = solvingForBlack = True
                numWhiteEncountered = numBlackEncountered = 0
                currentWhiteFile, currentWhiteRank = whiteKingFile, whiteKingRank
                currentBlackFile, currentBlackRank = blackKingFile, blackKingRank
                while solvingForWhite or solvingForBlack:
                    if solvingForWhite:
                        currentWhiteFile += df
                        currentWhiteRank += dr
                        if not util.fileRankInbounds(currentWhiteFile, currentWhiteRank): 
                            solvingForWhite = False
                            continue

                        currentWhiteSquare = util.relativeCoordinatesToSquareIndex((currentWhiteFile, currentWhiteRank))
                        pieceInWhitePath = self.board[currentWhiteSquare]

                        if pieceInWhitePath and piece.isWhite(pieceInWhitePath): 
                            numWhiteEncountered += 1
                            if numWhiteEncountered == 2: solvingForWhite = False
                        elif pieceInWhitePath and numWhiteEncountered == 1: 
                            self.backtrackPin(currentWhiteSquare, df, dr, isWhite=True)
                            solvingForWhite = False

                    if solvingForBlack:
                        currentBlackFile += df
                        currentBlackRank += dr
                        if not util.fileRankInbounds(currentBlackFile, currentBlackRank):
                            solvingForBlack = False
                            continue
                        currentBlackSquare = util.relativeCoordinatesToSquareIndex((currentBlackFile,currentBlackRank))
                        pieceInBlackPath = self.board[currentBlackSquare]

                        if pieceInBlackPath and not piece.isWhite(pieceInBlackPath):
                            numBlackEncountered += 1
                            if numBlackEncountered == 2: solvingForBlack = False
                        elif pieceInBlackPath and numBlackEncountered == 1:
                            self.backtrackPin(currentBlackSquare, df, dr, isWhite=False)
                            solvingForBlack = False
    
    def backtrackPin(self, currentSquare, df, dr, isWhite):
        currentSquarePieceType = board.pieceToPieceType(currentSquare)
        if currentSquarePieceType not in [piece.queen, piece.rook, piece.bishop]: return
        file,rank = util.squareIndexToRelativeCoordinate(currentSquare)

        kingToFind = (piece.king | (piece.white if isWhite else piece.black))
        currentSquarePiece = piece.none
        while currentSquarePiece != kingToFind:
            file -= df
            rank -= dr

            currentSquare = util.relativeCoordinatesToSquareIndex((file,rank))
            self.piecePinDirections[isWhite][currentSquare] = [df,dr]
            currentSquarePiece = self.board[currentSquare]

    def makeAIMove(self):
        pieceMoves = []
        while len(pieceMoves) == 0: 
            chosenPiece = random.choice(list(self.legalMoves.keys()))
            pieceMoves = self.legalMoves[chosenPiece]
        self.makeMove(pieceMoves[0])

    
class CastlingRights:
    def __init__(self, whiteQueenSide=True, whiteKingSide=True, blackQueenSide=True, blackKingSide=True):
        self.possibleCastles = {
            'whiteQueenSide': whiteQueenSide,
            'whiteKingSide': whiteKingSide,
            'blackQueenSide': blackQueenSide,
            'blackKingSide': blackKingSide
        }
        self.savedStates = []

    def saveCastleState(self):
        self.savedStates.append(self.possibleCastles.copy())

    def disableCastleMove(self, moveTypeList):
        for moveType in moveTypeList:
            self.possibleCastles[moveType] = False

    def undoCastleMove(self):
        if len(self.savedStates) == 0: return
        self.possibleCastles = self.savedStates.pop()