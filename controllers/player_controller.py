from utils.constante import StatePlay, queue
from models.queue_model import Queue
from models.song_model import Song
import services.player_service as player_service
import services.queue_service as queue_service

def play(song:Song|None = None):
    if not player_service.play_song(song):
        player_service.next_song()
    else:
        print("Erreur de lecture")

def pause():
    player_service.pause_song()

def stop():
    player_service.stop_song()

