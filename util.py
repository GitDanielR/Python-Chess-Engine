def squareIndexToRelativeCoordinate(index):
    rank = int(index / 8)
    file = index % 8

    return (file, rank)

def mousePositionToRelativeCoordinate(position, tileSize):
    file = position[0] // tileSize
    rank = position[1] // tileSize

    return (file, rank)

def relativeCoordinatesToSquareIndex(coords):
    file,rank = coords
    return rank*8 + file

def mousePositionToSquareIndex(position, tileSize):
    coords = mousePositionToRelativeCoordinate(position, tileSize)
    return relativeCoordinatesToSquareIndex(coords)

def fileRankInbounds(file, rank):
    return (0 <= file < 8 and 0 <= rank < 8)

def dFdRtoType(df, dr):
    horizontalSliding = abs(df)
    verticalSliding = abs(dr)
    if horizontalSliding and verticalSliding:
        return 'diagonal'
    elif horizontalSliding:
        return 'horizontal'
    return 'vertical'

def getFenRepresentationOfPiece(pieceType, pieceColor):
    if pieceType == 0: return ''

    if pieceType == 1: p = 'k'
    elif pieceType == 2: p = 'p'
    elif pieceType == 3: p = 'n'
    elif pieceType == 4: p = 'b'
    elif pieceType == 5: p = 'r'
    else: p = 'q'

    if pieceColor: p = p.upper()
    return p

def printSquareIndexAsFileRank(squareIndexList):
    for s in squareIndexList:
        file, rank = squareIndexToRelativeCoordinate(s)
        print(f"File: {file}, Rank: {rank}")