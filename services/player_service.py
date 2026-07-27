import pygame
from pathlib import Path
from utils.constante import StatePlay, RepeatMode
from models.song_model import Song
from services.queue_service import queue
from typing import Optional,cast

SONG_END = pygame.USEREVENT + 1

def _ensure_mixer_initialized():
    if not pygame.mixer.get_init():
        pygame.mixer.init()
        pygame.mixer.music.set_endevent(SONG_END)

def play(path: Path)->bool:
    if not path or not Path(path).exists():
        return False
    _ensure_mixer_initialized()
    pygame.mixer.music.load(str(path))
    pygame.mixer.music.play()
    return True

def pause():
    if pygame.mixer.get_init():
        pygame.mixer.music.pause()

def stop():
    if pygame.mixer.get_init():
        pygame.mixer.music.stop()

def resume_play():
    if pygame.mixer.get_init():
        pygame.mixer.music.unpause()


def play_song(song:Optional[Song] = None)->bool:
    import services.queue_service as queue_service
    if song is not None:
        if queue_service.is_song_here(song):
            if queue.current_song != song:
                queue.current_index = (queue.queue).index(song)
                queue.current_song = queue.queue[queue.current_index]
        else:
            queue_service.clear_queue()
            queue_service.add_song(song)
    else:
        if queue.current_song is not None and queue.current_index != -1:
            return False
    if queue.state_player == StatePlay.PAUSE:
            resume_play()
            queue.state_player = StatePlay.PLAY
    elif queue.state_player == StatePlay.STOP:
        if isinstance(queue.current_song, Song) and isinstance(queue.current_song.path, Path) and play(queue.current_song.path):
            queue.state_player = StatePlay.PLAY
        else:
            return False
    return True
    
def stop_song():
    stop()
    queue.state_player = StatePlay.STOP
    queue.current_index = -1
    queue.current_song = None

def pause_song():
    if queue.state_player == StatePlay.PLAY:
        pause()
        queue.state_player = StatePlay.PAUSE

def next_song():
    if len(queue.queue) == 0:
        stop_song()
        return
    if queue.repeat_mode == RepeatMode.REPEAT_ALL:
        queue.current_index = (queue.current_index + 1) % len(queue.queue)
        queue.current_song = queue.queue[queue.current_index]
    elif queue.repeat_mode == RepeatMode.NO_REPEAT:
        next_index = queue.current_index + 1
        if next_index < len(queue.queue):
            queue.current_index = next_index
            queue.current_song = queue.queue[next_index]
        else:
            stop_song()
            return
    elif queue.repeat_mode == RepeatMode.REPEAT_ONE:
        if queue.current_song is None and queue.queue != []:
            queue.current_index = 0
            queue.current_song = queue.queue[0]
    stop()
    play_song()

def previous_song():
    if len(queue.queue) == 0:
        return
    if queue.current_index < 0:
        queue.current_index = 0
    queue.current_index = (queue.current_index - 1) % len(queue.queue)
    queue.current_song = queue.queue[queue.current_index]
    stop()
    play_song()

def checkLecture():
    if not pygame.mixer.get_init():
        return
    for event in pygame.event.get():
        if event.type == SONG_END and queue.state_player == StatePlay.PLAY:
            next_song()

def repeat_mode():
    if queue.repeat_mode == RepeatMode.REPEAT_ALL:
        queue.repeat_mode = RepeatMode.REPEAT_ONE
    elif queue.repeat_mode == RepeatMode.REPEAT_ONE:
        queue.repeat_mode = RepeatMode.NO_REPEAT
    elif queue.repeat_mode == RepeatMode.NO_REPEAT:
        queue.repeat_mode = RepeatMode.REPEAT_ALL