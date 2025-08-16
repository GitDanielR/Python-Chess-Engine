import assets
import board
import constants
import events
import pygame
#from pyperclip import copy
import renderer
import sound

def play_chess():
    pygame.init()
    window = pygame.display.set_mode((constants.WIDTH, constants.HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Chess")
    pygame.event.set_blocked([pygame.MOUSEMOTION])

    constants.calculate_tile_size()
    board.init()
    assets.init(pygame)
    sound.init(pygame)
    
    while events.running:
        event = pygame.event.wait()
        events.handle_input(pygame, event, board.is_checkmate)
        
        if not events.running:
            pygame.quit()
            break
        elif events.resize_pending:
            resize(event.w, event.h)
        elif events.restart_pending:
            restart()
        elif events.undo_pending:
            undo_move()
        elif events.print_fen_pending:
            print_board_fen()
        elif not board.is_checkmate:
            if events.piece_chosen_pending:
                validate_start_tile()
            elif events.move_pending:
                move()
            
        draw(window)
        pygame.display.flip()
    
def resize(width, height):
    constants.set_width_height(width, height)
    assets.size_images(pygame)
    events.resize_pending = False

def move():
    move_made = board.make_player_move(events.start_tile, events.end_tile)
    
    events.clear_selected()
    if move_made:
        play_sound()
        process_player_move()

def process_player_move(): 
    if not board.white_to_move and constants.IS_AI_MODE:
        board.make_ai_move()
        play_sound()

def play_sound():
    last_move = board.move_log[-1]
    sound.play_sound(last_move)

def draw(window):
    renderer.clear_window(window)

    if not board.is_checkmate:
        piece_chosen = events.start_tile is not None
        
        renderer.draw_checkerboard(pygame, window)
        if piece_chosen:
            renderer.highlight_tile(pygame, events.start_tile, window)
        renderer.draw_pieces(board.board, assets.piece_number_to_image, window)
        if piece_chosen:
            start_square = board.file_rank_to_square_index(events.start_tile)
            renderer.highlight_legal_moves(pygame, board.legal_moves[start_square], window)
        if events.highlight_best_move:
            best_move = board.get_current_player_best_move()
            renderer.highlight_move(pygame, best_move, window)
    else:
        renderer.show_end_screen(pygame, not board.white_to_move, window)
    
def validate_start_tile():
    valid_piece_chosen = board.validate_start_tile(events.start_tile)
    if not valid_piece_chosen:
        events.clear_selected()
    events.piece_chosen_pending = False
    
def restart():
    board.init()
    events.restart_pending = False

def undo_move():
    board.undo_last_move()
    if constants.IS_AI_MODE:
        board.undo_last_move()
    events.undo_pending = False
    
def print_board_fen():
    fen_string = board.get_position_as_fen()
    #copy(fen_string)
    print(fen_string)
    events.print_fen_pending = False
