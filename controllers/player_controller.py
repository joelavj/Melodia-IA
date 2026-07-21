import services.player_service as player_service
from utils.constante import StatePlay
from models.queue_model import Queue
from models.song_model import Song
import services.queue_service as queue_service


def mode_play(queue:Queue):
    pass


def play(song:Song|None = None, queue:Queue|None = None):
    if song is None:
        active_queue = queue_service.get_active_queue()
        if not active_queue.queue:
            return None
        song = active_queue.queue[0]
    target_queue = queue_service.add_song(song=song, queue=queue)
    target_queue.play(song)
    if player_service.state_player != StatePlay.PAUSE:
        player_service.play_song(target_queue)
    else:
        player_service.pause_song(target_queue)
    return target_queue


def pause():
    player_service.state_player = StatePlay.PAUSE
    return player_service.pause_song()


def stop():
    player_service.stop_song()
    return None

