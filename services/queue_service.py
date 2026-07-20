from models.song_model import Song
from utils.constante import *
import services.player_service as player_service

queue: list[Song] = []
current_index: int = -1
current_song: Song | None = None


def add_song(song: Song):
    global current_index, current_song
    if song in queue:
        remove_song(song)
    queue.append(song)
    if current_song is None:
        current_index = 0
        current_song = song


def remove_song(song: Song):
    global current_index, current_song
    if song not in queue:
        return
    if current_song is not None and current_song.id == song.id:
        queue.remove(song)
        if not queue:
            current_index = -1
            current_song = None
            player_service.stop_song()
            return
        current_index %= len(queue)
        current_song = queue[current_index]
    else:
        index_before = queue.index(song)
        queue.remove(song)
        if index_before < current_index:
            current_index -= 1
        if current_index >= len(queue):
            current_index = len(queue) - 1


def clear_queue():
    global current_index, current_song
    player_service.stop_song()
    current_index = -1
    current_song = None
    queue.clear()


