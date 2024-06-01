import game

WIDTH = HEIGHT = 800
assert(WIDTH % 8 == 0)
assert(HEIGHT % 8 == 0)

if __name__ == "__main__":
    chessGame = game.game(WIDTH,HEIGHT)
    while (chessGame.running):
        chessGame.playChess()