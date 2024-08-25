import assets
import events
import gameBoard
import pygame
import titleScreen
import util

class game:
    def __init__(self, width, height):
        boardSize = min(width,height)
        self.tileSize = boardSize // 8

        pygame.init()
        self.window = pygame.display.set_mode((width, height), pygame.RESIZABLE)
        pygame.display.set_caption('Chess')
        pygame.event.set_allowed([pygame.QUIT, pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN, pygame.VIDEORESIZE])

        # Wait for game start, returns True if option to play vs AI selected, False otherwise
        playingAgainstAI = titleScreen.waitGameStart("Chess")

        self.board = gameBoard.board(playingAgainstAI)
        self.events = events.events()
        self.loadedAssets = self.loadAssets()
        self.sounds = {'pieceMove': pygame.mixer.Sound("sounds/move.mp3"),
                       'capture': pygame.mixer.Sound("sounds/capture.mp3")}
        self.running = True

    def __del__(self):
        pygame.quit()

    def playChess(self):
        self.drawBoard()
        self.handleInput()

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
                self.window.blit(self.loadedAssets[index], tuple(x * self.tileSize for x in util.squareIndexToRelativeCoordinate(activePiecePosition)))

        pygame.display.flip()

    def handleInput(self):
        event = pygame.event.wait()

        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:  # any mouse buttons lol
            self.updateMouseEvent()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_z:
                self.board.unmakeMove()
                if self.board.AIMode: 
                    self.board.unmakeMove()
            elif event.key == pygame.K_r:   # reset to starting fen
                self.resetBoard()
            elif event.key == pygame.K_e:
                self.board.printPositionAsFen()
            elif event.key == pygame.K_t:
                self.board.AIMode = not self.board.AIMode
                if self.board.AIMode:
                    self.board.makeAIMove()
        elif event.type == pygame.VIDEORESIZE:
            self.resizeWindow(event.size, event.w, event.h)

    def updateMouseEvent(self):
        if (self.events.addClick(pygame.mouse.get_pos(), self.tileSize)):   # there was a click that wasn't deselecting (either first or second)
            if (len(self.events.mouseClicks) == 2): # trying to make move
                startSquare = self.events.mouseClicks[0]
                endSquare = self.events.mouseClicks[1]
                
                chosenMove = next((possibleMove for possibleMove in self.board.legalMoves[startSquare] if possibleMove.endSquare == endSquare), None)
                if chosenMove is not None: 
                    soundEffect = self.sounds['capture'] if chosenMove.capturedPiece else self.sounds['pieceMove']
                    soundEffect.play()

                    self.processCheckmate(self.board.makeMove(chosenMove))  # valid move chosen, make it
                    if self.board.AIMode: 
                        self.processCheckmate(self.board.makeAIMove())

            elif (self.board.verifySelection(self.events.squareSelected)):  # first click, make sure can choose that square
                return  # avoid clearing input if valid first click made
        
        self.events.resetMouseInput()   # clear user inputs (after move made or invalid piece chosen)
    
    def resizeWindow(self, size, width, height):
        self.window.fill(assets.color['black'])
        self.tileSize = min(width, height) // 8
        self.loadedAssets = self.loadAssets()

    def loadAssets(self):
        images = []
        for i in range(12):
            images.append(pygame.transform.scale(assets.pieceNumberToImage[i], (self.tileSize, self.tileSize)))
        return images
    
    def processCheckmate(self, checkmate):
        if checkmate:
            self.board.AIMode = titleScreen.waitGameStart(f"{"You" if not self.board.whiteToMove else "AI"} win{"" if not self.board.whiteToMove else "s"}!")
            self.resetBoard()
    
    def resetBoard(self):
        self.board = gameBoard.board(self.board.AIMode)
        self.events = events.events()