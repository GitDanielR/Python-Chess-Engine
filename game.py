import assets
import events
import gameBoard
import pygame
import util

class game:
    def __init__(self, width, height):
        boardSize = max(width,height)
        self.tileSize = int(boardSize / 8)

        pygame.init()
        self.window = pygame.display.set_mode((width, height))
        pygame.display.set_caption('Chess')

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
                if (squareIndex in self.board.legalMoves):
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
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.updateMouseEvent()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_z:
                    self.board.unmakeMove()

    def updateMouseEvent(self):
        if (self.events.addClick(pygame.mouse.get_pos(), self.tileSize)):
            print(self.events.squareSelected)
            if (len(self.events.mouseClicks) == 2):
                self.board.makeMove(self.events.mouseClicks)
                self.clearUserInput()
            elif (not self.board.verifySelection(self.events.squareSelected)):
                self.clearUserInput()
            else:
                self.board.populatelegalMoves(self.events.squareSelected)
                print(self.board.legalMoves)
                if (self.board.legalMoves is not None):
                    return
        
        self.clearUserInput()

    def clearUserInput(self):
        self.events.resetMouseInput()
        self.board.legalMoves = []

class loadedAssets:
    def __init__(self, tileSize):
        self.images = []
        for i in range(12):
            self.images.append(pygame.transform.scale(assets.pieceNumberToImage[i], (tileSize, tileSize)))