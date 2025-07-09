import constants

running = True
highlight_best_move = False
resize_pending = False
move_pending = False
piece_chosen_pending = False
undo_pending = False
restart_pending = False
print_fen_pending = False
start_tile = None
end_tile = None

def handle_input(pygame, event, is_checkmate):
    global running, resize_pending, start_tile, end_tile, move_pending, piece_chosen_pending, restart_pending, undo_pending, print_fen_pending, highlight_best_move
    
    if event.type == pygame.QUIT:
        running = False
    elif event.type == pygame.VIDEORESIZE:
        resize_pending = True
    elif event.type == pygame.MOUSEBUTTONDOWN and not is_checkmate:
        if event.button == pygame.BUTTON_LEFT:
            if start_tile is None:
                start_tile = get_tile(pygame)
                piece_chosen_pending = True
            else:
                end_tile = get_tile(pygame)
                if start_tile == end_tile:
                    clear_selected()
                else:
                    move_pending = True
    elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_r:
            restart_pending = True
        elif event.key == pygame.K_z:
            undo_pending = True
        elif event.key == pygame.K_p:
            print_fen_pending = True
        elif event.key == pygame.K_h and not is_checkmate:
            highlight_best_move = not highlight_best_move
        
def clear_selected():
    global start_tile, end_tile, move_pending
    
    start_tile = None
    end_tile = None
    move_pending = False
    
def get_tile(pygame):
    mouse_x, mouse_y = pygame.mouse.get_pos()
    
    file = (mouse_x - constants.X_OFFSET) // constants.TILE_SIZE
    rank = (mouse_y - constants.Y_OFFSET) // constants.TILE_SIZE
    return (file,rank)
