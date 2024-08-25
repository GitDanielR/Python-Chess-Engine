none = 0
king = 1
pawn = 2
knight = 3
bishop = 4
rook = 5
queen = 6

white = 8
black = 16

knightMovementDirections = [(-2,1),(-2,-1),(2,1),(2,-1),(-1,2),(-1,-2),(1,2),(1,-2)]

pieceMap = {
    0: 'none',
    1: 'king',
    2: 'pawn',
    3: 'knight',
    4: 'bishop',
    5: 'rook',
    6: 'queen',  
}

values = {
    0: 0,
    1: 0,
    2: 1,
    3: 3,
    4: 3,
    5: 5,
    6: 9
}

def isWhite(piece):
    return piece >> 3 == 1

def pieceToPieceType(piece):
        return piece & 0b00111