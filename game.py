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

    def __del__(self):
        pygame.quit()
    
    def playChess(self):
        self.handleInput()
        self.drawBoard()

    def drawBoard(self):
        for file in range(8):
            for rank in range(8):
                tileColor = assets.color['lightTile'] if (file + rank) % 2 != 0 else assets.color['darkTile']
                if (self.events.squareSelected == util.relativeCoordinatesToSquareIndex((file,rank))):
                    tileColor = tuple(int(x * 0.7) for x in tileColor)
                pygame.draw.rect(self.window, tileColor, (file*self.tileSize, rank*self.tileSize, self.tileSize, self.tileSize))
        
        for index, pieceType in enumerate(self.board.pieceLists):
            for activePiecePosition in pieceType:
                pieceImage = pygame.transform.scale(assets.pieceNumberToImage[index], (self.tileSize, self.tileSize))
                self.window.blit(pieceImage, tuple(x * self.tileSize for x in util.squareIndexToRelativeCoordinate(activePiecePosition)))

        pygame.display.flip()

    def handleInput(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.updateMouseEvent()

    def updateMouseEvent(self):
        if (self.events.addClick(pygame.mouse.get_pos(), self.tileSize)):
            if (len(self.events.mouseClicks) == 2):
                self.board.makeMove(self.events.mouseClicks)
                self.events.resetMouseInput()
            elif (not self.board.verifySelection(self.events.squareSelected)):
                self.events.resetMouseInput()