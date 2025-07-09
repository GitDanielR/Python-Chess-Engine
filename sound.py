from piece import NONE

sounds = []

def init(pygame):
    global sounds
    sounds = [
        pygame.mixer.Sound("sounds/move.mp3"),
        pygame.mixer.Sound("sounds/capture.mp3")
    ]

def play_sound(previous_move):
    is_capture = previous_move.captured_piece != NONE
    selected_sound = sounds[is_capture]
    selected_sound.play()
