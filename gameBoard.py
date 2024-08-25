from dataclasses import dataclass
from random import choice

import numpy as np
import piece
import promotionScreen
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
    piecePinnedFen = 'r3k2r/1pp2ppp/p1n1n3/3q2B1/3P4/2N5/PPP1QPPP/R3K2R w KQkq - 0 1'
    kingChecksHimselfWithPawnFen = 'r3k2r/1pp2ppp/p1n1b3/3P1q2/8/2N5/PPP1QPPP/R3K2R w KQkq - 0 1'
    checkmateFen = '6k1/5ppp/8/8/8/5Q2/5PPP/6K1 w - - 0 1'
    
    def __init__(self, AIMode):
        self.AIMode = AIMode
        self.board = np.zeros(64, dtype=np.uint8)
        self.bitboards = np.zeros(6, dtype=np.uint64)
        self.pieceLists = [list() for _ in range(12)]
        self.castlingRights = CastlingRights()
        self.whiteToMove = True
        self.checkedSquares = []
        self.moveLog = []
        self.legalMoves = {}
        self.piecesLegalMoves = []
        self.squaresEnemyAttacks = []
        self.initBoard()

    def initBoard(self):
        self.positionFromFen(self.startingFen)
        self.setupPieceInformation()
        self.getAllLegalMoves()
        self.updateAttackedSquares()
    
    def setupPieceInformation(self):
        for squareIndex in range(64): 
            currentPiece = self.board[squareIndex]

            if (currentPiece != piece.none):
                pieceType = piece.pieceToPieceType(currentPiece)
                pieceListIndex = board.pieceToListIndex(currentPiece)
                mask = 1 << squareIndex
                self.bitboards[pieceType-1] |= np.uint64(mask)
                self.pieceLists[pieceListIndex].append(squareIndex)

    def printPositionAsFen(self):
        fenString = ""
        nBlanks = 0
        for file in range(8):
            for rank in range(8):
                currentPiece = self.board[file*8 + rank]
                symbol = util.getFenRepresentationOfPiece(piece.pieceToPieceType(currentPiece), piece.isWhite(currentPiece))
                if symbol == '': 
                    nBlanks += 1
                else:
                    fenString += (str(nBlanks) if nBlanks > 0 else '') + symbol
                    nBlanks = 0
            fenString += (str(nBlanks) if nBlanks > 0 else '') + ('/' if file < 7 else '')
            nBlanks = 0
        fenString += ' w' if self.whiteToMove else ' b'

        fenString += ' KQkq'
        fenString += ' - 0 1'
        print(fenString)  

    def isOpponent(self, squareIndex, squareSelected):
        if (squareSelected is None or squareIndex is None or self.board[squareIndex] == piece.none or self.board[squareSelected] == piece.none):
            return False
        return piece.isWhite(self.board[squareIndex]) != piece.isWhite(self.board[squareSelected])

    def isPawnCapture(self, squareIndex, squareSelected):
        squareFile,squareRank = util.squareIndexToRelativeCoordinate(squareIndex)
        selectedFile,selectedRank = util.squareIndexToRelativeCoordinate(squareSelected)
        return (piece.pieceToPieceType(self.board[squareIndex]) == piece.pawn and squareFile != selectedFile)

    def positionFromFen(self, position):
        pieceTypeFromSymbol = {
            'k' : piece.king,
            'p' : piece.pawn,
            'n' : piece.knight,
            'b' : piece.bishop,
            'r' : piece.rook,
            'q' : piece.queen
        }

        fenSections = position.split(' ')
        fenBoard = fenSections[0]
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
        
        self.whiteToMove = True if fenSections[1] == 'w' else False

    def getAllLegalMoves(self):
        self.legalMoves = {}
        def getPiecesLegalMoves(pieceSquare):
            self.populateLegalMoves(pieceSquare)
            self.legalMoves[pieceSquare] = self.piecesLegalMoves

        self.iteratePieces(getPiecesLegalMoves)

    def iteratePieces(self, function):
        pieceListOffset = 0 if self.whiteToMove else 6
        for i in range(6):
            pieceListIndex = pieceListOffset + i
            for pieceList in self.pieceLists[pieceListIndex]:
                if isinstance(pieceList, int):
                    function(pieceList)
                else:
                    for pieceSquare in pieceList:
                        function(pieceSquare)

    def pieceIsPinned(self, squareIndex):
        kingPosition = np.argmax(self.board == (not self.whiteToMove) * 8 + 9)
        kingFile, kingRank = util.squareIndexToRelativeCoordinate(kingPosition)
        currentFile, currentRank = util.squareIndexToRelativeCoordinate(squareIndex)

        df, dr = kingFile-currentFile, kingRank-currentRank
        if (df == 0 and dr == 0) or (abs(df) != abs(dr) and not (df == 0 or dr == 0)): return False

        def clampValue(val):
            if val > 0: return 1
            elif val == 0: return 0
            else: return -1
        
        df = clampValue(df)
        dr = clampValue(dr)

        while True:
            currentFile += df
            currentRank += dr

            if currentFile == kingFile and currentRank == kingRank: 
                break
            if self.board[util.relativeCoordinatesToSquareIndex((currentFile, currentRank))] != piece.none: 
                return False
        
        currentFile, currentRank = util.squareIndexToRelativeCoordinate(squareIndex)
        df, dr = -df, -dr
        currentFile += df
        currentRank += dr
        
        while util.fileRankInbounds(currentFile, currentRank):
            pieceInPath = self.board[util.relativeCoordinatesToSquareIndex((currentFile, currentRank))]
            if pieceInPath:
                return (-df, -dr) if self.checkIfPieceCanPin(pieceInPath, -df, -dr) else False
            
            currentFile += df
            currentRank += dr

        return False
    
    def checkIfPieceCanPin(self, pieceInPath, df, dr):
        if piece.isWhite(pieceInPath) == self.whiteToMove: return False     # can't pin yourself
        
        pieceInPathType = piece.pieceToPieceType(pieceInPath)
        if pieceInPathType == piece.queen: return True
        if pieceInPathType in [piece.pawn, piece.king]: return False  # these pieces can't pin, note knight's have already been returned false

        if (abs(df) ^ abs(dr)): return pieceInPathType == piece.rook
        if (abs(df) and abs(dr)): return pieceInPathType == piece.bishop

    def populateLegalMoves(self, squareIndex):
        self.piecesLegalMoves = []

        currentPiece = self.board[squareIndex]
        pieceType = piece.pieceToPieceType(currentPiece)

        if pieceType == piece.pawn:
            self.generatePawnMoves(squareIndex)
        elif pieceType == piece.knight:
            self.generateKnightMoves(squareIndex)
        elif pieceType == piece.king:
            self.generateKingMoves(squareIndex)

        if pieceType == piece.bishop or pieceType == piece.queen:
            self.addDiagonalSliding(squareIndex)
        if pieceType == piece.queen or pieceType == piece.rook:
            self.addSliding(squareIndex)

        if pinInformation := self.pieceIsPinned(squareIndex):
            self.filterPins(pinInformation)

    # pinInformation = (df, dr) for line from pinnedPiece to pinningPiece where -1 <= df,dr <= 1 and df,dr are integers
    def filterPins(self, pinInformation):
        def inlineMove(moveData):
            startFile, startRank = util.squareIndexToRelativeCoordinate(moveData.startSquare)
            endFile, endRank = util.squareIndexToRelativeCoordinate(moveData.endSquare)
            df = endFile - startFile
            dr = endRank - startRank
            df = cap(df)
            dr = cap(dr)

            return abs(df) == abs(pinInformation[0]) and abs(dr) == abs(pinInformation[1])
        
        def cap(x):
            if x == 0:
                return 0
            elif x < 0:
                return -1
            return 1
        
        self.piecesLegalMoves = [m for m in self.piecesLegalMoves if inlineMove(m)]

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
        def addCaptureData(newSquareIndex):
            if (self.isOpponent(squareIndex, newSquareIndex)):
                self.addMoveData(squareIndex, newSquareIndex, self.board[newSquareIndex], newSquareIndex)
        
        if (file > 0):
            addCaptureData(util.relativeCoordinatesToSquareIndex((file-1, newRank)))
        if (file < 7):
            addCaptureData(util.relativeCoordinatesToSquareIndex((file+1, newRank)))

        # en passant 
        def checkEnpassant(subtracting, shouldBeWhite):
            enemySquare = squareIndex + (-1 if subtracting else 1)
            if self.board[enemySquare] == (piece.pawn | (piece.white if shouldBeWhite else piece.black)) and (file > 0 if subtracting else file < 7) and self.moveLog and self.moveLog[-1].endSquare == enemySquare:
                self.addMoveData(squareIndex, enemySquare + movementDirection, self.board[enemySquare], enemySquare)
                return True
            return False

        if (rank == 3 and movementDirection == -8):
            if not checkEnpassant(False, False):
                checkEnpassant(True, False)
        elif (rank == 4 and movementDirection == 8):
            if not checkEnpassant(False, True):
                checkEnpassant(True, True)

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
                if not newSquareIndex in self.squaresEnemyAttacks: 
                    self.addMoveData(squareIndex, newSquareIndex, self.board[newSquareIndex], newSquareIndex)

        kingColor = 'white' if self.whiteToMove else 'black'
        # have castling rights
        if self.castlingRights.possibleCastles[kingColor + 'QueenSide']: 
            # castling path not attacked by enemy pieces
            if util.fileRankInbounds(file-3, rank) and ((squareIndex - 1) not in self.squaresEnemyAttacks) and ((squareIndex - 2) not in self.squaresEnemyAttacks): 
                # castling path doesn't have pieces in the way
                if (self.board[squareIndex-1] == piece.none and self.board[squareIndex-2] == piece.none and self.board[squareIndex-3] == piece.none):
                    self.addMoveData(squareIndex, squareIndex-2, piece.none, squareIndex-2, True)
        if self.castlingRights.possibleCastles[kingColor + 'KingSide']: 
            if util.fileRankInbounds(file+2, rank) and ((squareIndex + 1) not in self.squaresEnemyAttacks) and ((squareIndex + 2) not in self.squaresEnemyAttacks):
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
    # returns if checkmate
    def makeMove(self, chosenMove):
        self.castlingRights.saveCastleState()
        self.moveLog.append(chosenMove)

        self.updateBoardWithMove(chosenMove)
        self.checkedSquares = self.checkForCheck()
        self.updateMoveInformation()

        if self.checkedSquares: 
            self.filterSudoLegalMoves()
            if len([m for sublist in self.legalMoves.values() for m in sublist]) == 0:
                return True # checkmate
        return False

    def updateMoveInformation(self):
        self.getAllLegalMoves()
        self.updateAttackedSquares()
        self.whiteToMove = not self.whiteToMove
        self.getAllLegalMoves()

    def filterSudoLegalMoves(self):
        def validateMoves(pieceSquare):
            self.legalMoves[pieceSquare] = [m for m in self.legalMoves[pieceSquare] if m.endSquare in self.checkedSquares]
        self.iteratePieces(validateMoves)

    def updateAttackedSquares(self):
        def addPawnMoveToList(p):
            movementDirection = -8 if self.whiteToMove else 8
            rankDir = -1 if self.whiteToMove else 1
            for dir in [-1,1]:
                file,rank = util.squareIndexToRelativeCoordinate(p)
                if not util.fileRankInbounds(file + dir, rank + rankDir):
                    continue
                
                pieceInPath = self.board[p + movementDirection + dir]
                if pieceInPath == piece.none or piece.isWhite(pieceInPath) != self.whiteToMove:
                    self.squaresEnemyAttacks.append(p + movementDirection + dir)

        self.squaresEnemyAttacks = [
            item.endSquare
            for sublist in self.legalMoves.values() 
            for item in sublist
            if piece.pieceToPieceType(self.board[item.startSquare]) != piece.pawn
        ]

        # check the current team's pawns moves to see what they could attack but aren't
        pieceListIndex = board.pieceToListIndex((piece.white if self.whiteToMove else piece.black) | piece.pawn)
        pieceList = self.pieceLists[pieceListIndex]
        if isinstance(pieceList, int):
            addPawnMoveToList(pieceList)
        else:
            for p in pieceList:
                addPawnMoveToList(p)

    def checkForCheck(self):
        self.checkedSquares = []
        kingSquare = self.findCurrentPlayersKingSquareIndex()
        file,rank = util.squareIndexToRelativeCoordinate(kingSquare)

        kingIsWhite = piece.isWhite(self.board[kingSquare])
        oppositeColor = piece.black if kingIsWhite else piece.white
        
        movementDirection = -8 if kingIsWhite else 8
        for dir in [-1,1]:
            pawnSquare = kingSquare + movementDirection + dir
            if self.board[pawnSquare] == (piece.pawn | oppositeColor):
                return [pawnSquare]
        
        for knightMovementDirection in piece.knightMovementDirections:  # knights
            knightFile,knightRank = file+knightMovementDirection[0],rank+knightMovementDirection[1]
            if not util.fileRankInbounds(knightFile,knightRank): 
                continue
            knightSquare = util.relativeCoordinatesToSquareIndex((knightFile, knightRank))
            if self.board[knightSquare] == (piece.knight | oppositeColor): 
                return [knightSquare]

        allPaths = []
        closestPiecesSquare = []
        attackType = []    
        # queen, rook, bishop
        for df in [-1,0,1]:
            for dr in [-1,0,1]:
                currentPath = []
                if (df == dr == 0): 
                    continue

                currentFile, currentRank = file,rank
                while True:
                    currentFile += df
                    currentRank += dr
                    if (not util.fileRankInbounds(currentFile,currentRank)): 
                        break

                    currentSquare = util.relativeCoordinatesToSquareIndex((currentFile,currentRank))
                    currentPath.append(currentSquare)
                    pieceInPath = self.board[currentSquare]
                    if pieceInPath:
                        allPaths.append(currentPath)
                        closestPiecesSquare.append(currentSquare)
                        attackType.append(util.dFdRtoType(df, dr))
                        break
        
        possiblePieceMatches = [piece.queen | oppositeColor, piece.rook | oppositeColor, piece.bishop | oppositeColor]
        for index,blockingPieceSquare in enumerate(closestPiecesSquare):
            blockingPiece = self.board[blockingPieceSquare]
            if blockingPiece not in possiblePieceMatches: 
                continue

            blockingPieceType = piece.pieceToPieceType(blockingPiece)
            attackDirection = attackType[index]
            if ((blockingPieceType == piece.rook and (attackDirection == 'horizontal' or attackDirection == 'vertical')) or
                (blockingPieceType == piece.bishop and attackDirection == 'diagonal') or
                (blockingPieceType == piece.queen)):
                return allPaths[index]

        return []

    def unmakeMove(self):
        if (len(self.moveLog) == 0): 
            return
        undoneMove = self.moveLog.pop()
        self.castlingRights.undoCastleMove()
        
        self.updateBoardWithMove(move(undoneMove.endSquare, undoneMove.startSquare, piece.none, None, undoneMove.isCastle), True)
        if undoneMove.capturedPiece:
            self.setPieceInformationAtIndex(undoneMove.capturedPiece, undoneMove.capturedPieceSquare)
        self.updateMoveInformation()

    def updateBoardWithMove(self, chosenMove, undoing=False):
        if (chosenMove.capturedPiece != piece.none):
            self.setPieceInformationAtIndex(piece.none, chosenMove.capturedPieceSquare)

        currentPiece = self.board[chosenMove.startSquare]
        currentPieceType = piece.pieceToPieceType(currentPiece)
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
        pieceType = piece.pieceToPieceType(currentPiece)
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
    
    def pieceToListIndex(currentPiece):
        pieceType = piece.pieceToPieceType(currentPiece)
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
        pieceType = piece.pieceToPieceType(currentPiece)
        pieceColor = 'none ' if currentPiece == 0 else 'white ' if piece.isWhite(currentPiece) else 'black '
        file,rank = util.squareIndexToRelativeCoordinate(pieceSquare)
        return pieceColor + piece.pieceMap[pieceType] + ' at file ' + str(file) + ', rank ' + str(rank)

    def makeAIMove(self):
        aiMove = self.getBestMove()
        return self.makeMove(aiMove)

    def findCurrentPlayersKingSquareIndex(self):
        return np.argmax(self.board == (self.whiteToMove * 8) + 9)
    
    def getRandomMove(self):
        aiMoves = []
        while len(aiMoves) == 0:
            chosenPiece = choice(list(self.legalMoves.keys()))
            aiMoves = self.legalMoves[chosenPiece]
        return choice(aiMoves)

    def getBestMove(self):
        bestMove = None
        bestPieceCapture = -1

        def searchForBestMove(squareIndex):
            nonlocal bestMove, bestPieceCapture

            possibleMoves = self.legalMoves[squareIndex]
            for possibleMove in possibleMoves:
                capturedPieceValue = piece.values[piece.pieceToPieceType(possibleMove.capturedPiece)]
                if capturedPieceValue > bestPieceCapture:
                    bestMove = possibleMove
                    bestPieceCapture = capturedPieceValue
        
        self.iteratePieces(searchForBestMove)
        return bestMove
    
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
        if len(self.savedStates) == 0: 
            return
        self.possibleCastles = self.savedStates.pop()