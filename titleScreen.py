import pygame
from assets import color

def waitGameStart(window):
    displayInfo = pygame.display.Info()
    screenWidth = displayInfo.current_w
    screenHeight = displayInfo.current_h
    tileSize = max(screenWidth, screenHeight) // 8
    titleFont = pygame.font.SysFont(None, int(tileSize*2))
    subheadingFont = pygame.font.SysFont(None, int(tileSize/2))

    title = titleFont.render("Chess", True, color['black'])
    titlePosition = title.get_rect(center=(screenWidth//2, screenHeight//2-tileSize//2))
    instructions = subheadingFont.render("Press enter to continue", True, color['black'])
    instructionsPosition = instructions.get_rect(center=(screenWidth//2, screenHeight//2+tileSize//3))
    hotkeys = subheadingFont.render("Z to undo & R to reset", True, color['black'])
    hotkeysPosition = hotkeys.get_rect(center=(screenWidth//2, screenHeight//2+2*tileSize//3))

    # Draw the title screen
    for file in range(8):
        for rank in range(8):
            tileColor = color['lightTile'] if (file + rank) % 2 != 0 else color['darkTile']
            pygame.draw.rect(window, tileColor, (file * tileSize, rank * tileSize, tileSize, tileSize))
    window.blit(title, titlePosition)
    window.blit(instructions, instructionsPosition)
    window.blit(hotkeys, hotkeysPosition)
    pygame.display.flip()
    
    # Wait for the game to start
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    window.fill(color['black'])
                    return