import constants
import piece

colors = {
    "DARK_GREEN": (118,150,86),
    "CREAM": (238,238,210),
    "BLACK": (0,0,0),
    "HIGHLIGHT": (219,195,0),
    "CAPTURE_INDICATOR": (245,139,139),
    "BEST_MOVE_INDICATOR": (125,0,125),
    "WHITE": (255,255,255)
}
highlight_best_move = False

def get_screen_pos_from_square_index(square_index):
    return ((square_index % constants.NUM_TILES) * constants.TILE_SIZE + constants.X_OFFSET, (square_index // 8) * constants.TILE_SIZE + constants.Y_OFFSET)
    
def get_square_screen_pos_from_tile(tile):
    screen_x = tile[0] * constants.TILE_SIZE + constants.X_OFFSET
    screen_y = tile[1] * constants.TILE_SIZE + constants.Y_OFFSET
    return (screen_x, screen_y)

def get_circle_screen_pos_from_tile(tile):
    screen_x, screen_y = get_square_screen_pos_from_tile(tile)
    return (screen_x + constants.TILE_SIZE // 2, screen_y + constants.TILE_SIZE // 2)

def clear_window(window):
    window.fill(colors["BLACK"])

def draw_checkerboard(pygame, window):
    for rank in range(constants.NUM_TILES):
        for file in range(constants.NUM_TILES):        
            color = colors["DARK_GREEN"] if (file+rank) % 2 == 0 else colors["CREAM"]
            pygame.draw.rect(window, color, (file * constants.TILE_SIZE + constants.X_OFFSET, rank * constants.TILE_SIZE + constants.Y_OFFSET, constants.TILE_SIZE, constants.TILE_SIZE))
    
def draw_pieces(board, assets, window):
    for square_index, piece_at_square in enumerate(board):
        if piece.get_piece_type(piece_at_square) != piece.NONE:
            window.blit(assets[piece_at_square], get_screen_pos_from_square_index(square_index))
            
def highlight_tile(pygame, tile, window):
    screen_x, screen_y = get_square_screen_pos_from_tile(tile)
    pygame.draw.rect(window, colors["HIGHLIGHT"], (screen_x, screen_y, constants.TILE_SIZE, constants.TILE_SIZE))

def highlight_legal_moves(pygame, legal_moves, window):
    for legal_move in legal_moves:
        move_indicator_color = colors["CAPTURE_INDICATOR"] if legal_move.captured_piece != piece.NONE else colors["HIGHLIGHT"]
        draw_circle_on_tile(pygame, move_indicator_color, legal_move.end_tile, window)

def highlight_move(pygame, best_move, window):
    draw_circle_on_tile(pygame, colors["BEST_MOVE_INDICATOR"], best_move.start_tile, window)
    draw_circle_on_tile(pygame, colors["BEST_MOVE_INDICATOR"], best_move.end_tile, window)

def draw_circle_on_tile(pygame, color, tile, window):
    screen_position = get_circle_screen_pos_from_tile(tile)
    pygame.draw.circle(window, color, screen_position, constants.TILE_SIZE // 8)

def show_end_screen(pygame, white_won, window):
    end_game_text = ("White" if white_won else "Black") + " wins\nPress R to reset\nPress Z to undo" 
    show_screen(pygame, end_game_text, window)

def show_screen(pygame, text, window):
    lines = text.split("\n")

    font_size = 36
    font = pygame.font.Font(None, font_size)
    for index, line in enumerate(lines):
        text = font.render(line, True, colors["WHITE"])
        text_rect = text.get_rect(center=(constants.WIDTH // 2, constants.HEIGHT // 2 + index * font_size))
        window.blit(text, text_rect)