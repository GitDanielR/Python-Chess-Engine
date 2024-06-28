import pygame
from assets import color
import button
from piece import pieceMap

# there are 4 choices for promotion
def choosePromotionForPawn():
    window = pygame.display.get_surface()

    displayInfo = pygame.display.Info()
    screenWidth = displayInfo.current_w
    screenHeight = displayInfo.current_h
    dx = screenWidth // 6   # 1/6 width
    dy = screenHeight // 6  # height of button
    xPadding = dx // 2
    yPos = screenHeight // (6/2.5)

    buttons = []
    pieceMapIndex = 3
    # buttons for knight, bishop, rook, queen
    for x in range(xPadding, xPadding*5, dx):
        buttons.append(button.Button(color['darkTile'], x, yPos, dx, dy, pieceMap[pieceMapIndex]))
        pieceMapIndex += 1

    window.fill(color['white'])
    for button in buttons:
        button.draw(window, outline=(0,0,0))
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                for button in buttons:
                    if button.isOver(pos): 
                        return button.text