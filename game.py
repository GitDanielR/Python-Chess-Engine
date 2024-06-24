import assets
import events
import gameBoard
import pygame
import titleScreen
import util

class game:
    def __init__(self, width, height):
        boardSize = min(width,height)
        self.tileSize = int(boardSize / 8)

        pygame.init()
        self.window = pygame.display.set_mode((width, height))
        pygame.display.set_caption('Chess')

        titleScreen.waitGameStart(self.window) # Wait for user to start the game 

        self.running = True
        self.board = gameBoard.board()
        self.events = events.events()
        self.loadedAssets = loadedAssets(self.tileSize)

    def __del__(self):
        pygame.quit()
    
    def playChess(self):
        self.handleInput()
        self.drawBoard()

    def drawBoard(self):
        for file in range(8):
            for rank in range(8):
                tileColor = assets.color['lightTile'] if (file + rank) % 2 != 0 else assets.color['darkTile']
                squareIndex = util.relativeCoordinatesToSquareIndex((file,rank))
                if (squareIndex == self.events.squareSelected):
                    tileColor = assets.color['selected']
                pygame.draw.rect(self.window, tileColor, (file*self.tileSize, rank*self.tileSize, self.tileSize, self.tileSize))
                if (self.board.legalMoves is not None and self.events.squareSelected in self.board.legalMoves):
                    if (squareIndex in [possibleMove.endSquare for possibleMove in self.board.legalMoves[self.events.squareSelected]]):
                        if (self.board.isOpponent(squareIndex, self.events.squareSelected) or self.board.isPawnCapture(self.events.squareSelected, squareIndex)):
                            pygame.draw.rect(self.window, assets.color['capture'], (file*self.tileSize, rank*self.tileSize, self.tileSize, self.tileSize))
                        else:
                            pygame.draw.circle(self.window, assets.color['legalMove'], (file*self.tileSize + self.tileSize//2, rank*self.tileSize + self.tileSize//2), self.tileSize//8)
            
        for index, pieceType in enumerate(self.board.pieceLists):
            for activePiecePosition in pieceType:
                # pieceImage = pygame.transform.scale(assets.pieceNumberToImage[index], (self.tileSize, self.tileSize))
                self.window.blit(self.loadedAssets.images[index], tuple(x * self.tileSize for x in util.squareIndexToRelativeCoordinate(activePiecePosition)))

        pygame.display.flip()

    def handleInput(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:  # any mouse buttons lol
                self.updateMouseEvent()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_z:
                    self.board.unmakeMove()
                elif event.key == pygame.K_r:   # reset
                    self.board = gameBoard.board()
                    self.events = events.events()

    def updateMouseEvent(self):
        if (self.events.addClick(pygame.mouse.get_pos(), self.tileSize)):   # there was a click that wasn't deselecting (either first or second)
            if (len(self.events.mouseClicks) == 2): # trying to make move
                startSquare = self.events.mouseClicks[0]
                endSquare = self.events.mouseClicks[1]
                chosenMove = next((possibleMove for possibleMove in self.board.legalMoves[startSquare] if possibleMove.endSquare == endSquare), None)
                if chosenMove is not None: self.board.makeMove(chosenMove)  # valid move chosen, make it
            elif (self.board.verifySelection(self.events.squareSelected)):  # first click, make sure can choose that square
                return
        
        self.events.resetMouseInput()   # clear user inputs (after move made or invalid piece chosen)

class loadedAssets:
    def __init__(self, tileSize):
        self.images = []
        for i in range(12):
            self.images.append(pygame.transform.scale(assets.pieceNumberToImage[i], (tileSize, tileSize)))