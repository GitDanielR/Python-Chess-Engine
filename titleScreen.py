from assets import color
from sys import exit

import pygame

def waitGameStart(context):
    window = pygame.display.get_surface()
    
    def drawScreen():
        displayInfo = pygame.display.Info()
        screenWidth = displayInfo.current_w
        screenHeight = displayInfo.current_h
        tileSize = max(screenWidth, screenHeight) // 8
        titleFont = pygame.font.SysFont(None, int(tileSize*2))
        subheadingFont = pygame.font.SysFont(None, int(tileSize/2))

        title = titleFont.render(context, True, color['black'])
        titlePosition = title.get_rect(center=(screenWidth//2, screenHeight//2-tileSize//2))

        soloplayerInstruction = subheadingFont.render("Press enter to play solo", True, color['black'])
        soloplayerInstructionPosition = soloplayerInstruction.get_rect(center=(screenWidth//2, screenHeight//2+tileSize//3))

        botInstructions = subheadingFont.render("Press shift to play vs. AI", True, color['black'])
        botInstructionsPosition = botInstructions.get_rect(center=(screenWidth//2, screenHeight//2+2*tileSize//3))

        hotkeys = subheadingFont.render("Z to undo & R to reset", True, color['black'])
        hotkeysPosition = hotkeys.get_rect(center=(screenWidth//2, screenHeight//2+3*tileSize//3))

        # Draw the title screen
        for file in range(8):
            for rank in range(8):
                tileColor = color['lightTile'] if (file + rank) % 2 != 0 else color['darkTile']
                pygame.draw.rect(window, tileColor, (file * tileSize, rank * tileSize, tileSize, tileSize))
        window.blit(title, titlePosition)
        window.blit(soloplayerInstruction, soloplayerInstructionPosition)
        window.blit(botInstructions, botInstructionsPosition)
        window.blit(hotkeys, hotkeysPosition)
        pygame.display.flip()
    
    # Wait for the game to start
    drawScreen()
    while True:
        event = pygame.event.wait()

        if event.type == pygame.QUIT:
            exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                window.fill(color['black'])
                return False
            elif event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                window.fill(color['black'])
                return True
        elif event.type == pygame.VIDEORESIZE:
            drawScreen()