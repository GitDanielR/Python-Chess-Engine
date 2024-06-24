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
def isWhite(piece):
    return piece >> 3 == 1