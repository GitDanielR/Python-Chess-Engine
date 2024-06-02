import pygame

color = {
    'lightTile'     : (238,238,210),
    'darkTile'      : (118,150,86),
    'selected'      : (255, 255, 51),
    'legalMove'     : (108, 108, 108),
    'capture'       : (225, 95, 75)
}

piecesImg = pygame.image.load('chessPieces/pieces.png')
imageWidth = 333
imageHeight = 333

whiteKing   = piecesImg.subsurface((0 * imageWidth, 0 * imageHeight, imageWidth, imageHeight))
whitePawn   = piecesImg.subsurface((5 * imageWidth, 0 * imageHeight, imageWidth, imageHeight))
whiteKnight = piecesImg.subsurface((3 * imageWidth, 0 * imageHeight, imageWidth, imageHeight))
whiteBishop = piecesImg.subsurface((2 * imageWidth, 0 * imageHeight, imageWidth, imageHeight))
whiteRook   = piecesImg.subsurface((4 * imageWidth, 0 * imageHeight, imageWidth, imageHeight))
whiteQueen  = piecesImg.subsurface((1 * imageWidth, 0 * imageHeight, imageWidth, imageHeight))
blackKing   = piecesImg.subsurface((0 * imageWidth, 1 * imageHeight, imageWidth, imageHeight))
blackPawn   = piecesImg.subsurface((5 * imageWidth, 1 * imageHeight, imageWidth, imageHeight))
blackKnight = piecesImg.subsurface((3 * imageWidth, 1 * imageHeight, imageWidth, imageHeight))
blackBishop = piecesImg.subsurface((2 * imageWidth, 1 * imageHeight, imageWidth, imageHeight))
blackRook   = piecesImg.subsurface((4 * imageWidth, 1 * imageHeight, imageWidth, imageHeight))
blackQueen  = piecesImg.subsurface((1 * imageWidth, 1 * imageHeight, imageWidth, imageHeight))

pieceNumberToImage = {
    0: whiteKing,
    1: whitePawn,
    2: whiteKnight,
    3: whiteBishop,
    4: whiteRook,
    5: whiteQueen,
    6: blackKing,
    7: blackPawn,
    8: blackKnight,
    9: blackBishop,
    10: blackRook,
    11: blackQueen
}