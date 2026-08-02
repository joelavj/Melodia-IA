from services.player_manager import engine
from typing import Optional
from models.song_model import Song
from utils.constante import StatePlay

def play_song(song:Optional[Song]=None):
    engine.play(song)

def current_song()->Song|None:
    return engine.current_song()

def state()->StatePlay:
    return engine.state()

def player_status():
    return {
        "song": engine.current_song(),
        "state": engine.state(),
        "repeat": engine.repeat_mode()
    }