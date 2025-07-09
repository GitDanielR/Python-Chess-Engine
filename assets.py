import constants
import piece

pieces_img = None
piece_number_to_image = {}

def init(pygame):
    global pieces_img, piece_number_to_image
    
    pieces_img = pygame.image.load("chess_pieces.png")
    
    image_width = image_height = 333
    white_king   = pieces_img.subsurface((0 * image_width, 0 * image_height, image_width, image_height))
    white_pawn   = pieces_img.subsurface((5 * image_width, 0 * image_height, image_width, image_height))
    white_knight = pieces_img.subsurface((3 * image_width, 0 * image_height, image_width, image_height))
    white_bishop = pieces_img.subsurface((2 * image_width, 0 * image_height, image_width, image_height))
    white_rook   = pieces_img.subsurface((4 * image_width, 0 * image_height, image_width, image_height))
    white_queen  = pieces_img.subsurface((1 * image_width, 0 * image_height, image_width, image_height))
    black_king   = pieces_img.subsurface((0 * image_width, 1 * image_height, image_width, image_height))
    black_pawn   = pieces_img.subsurface((5 * image_width, 1 * image_height, image_width, image_height))
    black_knight = pieces_img.subsurface((3 * image_width, 1 * image_height, image_width, image_height))
    black_bishop = pieces_img.subsurface((2 * image_width, 1 * image_height, image_width, image_height))
    black_rook   = pieces_img.subsurface((4 * image_width, 1 * image_height, image_width, image_height))
    black_queen  = pieces_img.subsurface((1 * image_width, 1 * image_height, image_width, image_height))
    
    piece_number_to_image = {
        (piece.WHITE | piece.KING): white_king,
        (piece.WHITE | piece.PAWN): white_pawn,
        (piece.WHITE | piece.KNIGHT): white_knight,
        (piece.WHITE | piece.BISHOP): white_bishop,
        (piece.WHITE | piece.ROOK): white_rook,
        (piece.WHITE | piece.QUEEN): white_queen,
        (piece.BLACK | piece.KING): black_king,
        (piece.BLACK | piece.PAWN): black_pawn,
        (piece.BLACK | piece.KNIGHT): black_knight,
        (piece.BLACK | piece.BISHOP): black_bishop,
        (piece.BLACK | piece.ROOK): black_rook,
        (piece.BLACK | piece.QUEEN): black_queen
    }
    
    size_images(pygame)
    
def size_images(pygame):
    global piece_number_to_image
    
    for piece_value in piece_number_to_image:
        piece_number_to_image[piece_value] = pygame.transform.scale(piece_number_to_image[piece_value], (constants.TILE_SIZE, constants.TILE_SIZE))
        