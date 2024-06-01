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