import services.player_service as player_service
from utils.constante import StatePlay

def mode_play():
    pass

def play():
    if player_service.state_player != StatePlay.PAUSE:
        player_service.play_song()
    else: 
        player_service.pause_song()

def stop():
    player_service.stop_song()

