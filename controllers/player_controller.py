from utils.constante import StatePlay
from models.queue_model import Queue
from models.song_model import Song
import services.player_service as player_service
import services.queue_service as queue_service
from services.queue_service import queue

def play_pause(song:Song|None = None):
    if song is None:
        if queue.state_player == StatePlay.PLAY:
            player_service.pause_song()
        elif queue.state_player == StatePlay.PAUSE:
            player_service.play_song()
        elif queue.state_player == StatePlay.STOP:
            player_service.play_song()
    else:
        if not player_service.play_song(song):
            player_service.next_song()
        else:
            player_service.stop_song()
            print("Erreur de lecture")

def stop():
    player_service.stop_song()

def change_repeat_mode():
    player_service.repeat_mode()
    print(queue.repeat_mode)

def next_song():
    player_service.next_song()

def previous_song():
    player_service.previous_song()
