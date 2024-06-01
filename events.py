from util import mousePositionToSquareIndex

class events:
    def __init__(self):
        self.squareSelected = ()
        self.mouseClicks = []

    def addClick(self, position, tileSize):
        position = mousePositionToSquareIndex(position, tileSize)
        if (self.squareSelected == position):
            self.squareSelected = ()
            self.mouseClicks = []
            return False
        
        self.squareSelected = position
        self.mouseClicks.append(position)
        return True

    def resetMouseInput(self):
        self.squareSelected = ()
        self.mouseClicks = []