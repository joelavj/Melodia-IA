import pygame
from pathlib import Path
from utils.constante import StatePlay, RepeatMode
from models.song_model import Song
from models.queue_model import Queue

SONG_END = pygame.USEREVENT + 1
state_player: StatePlay = StatePlay.STOP


def _ensure_mixer_initialized():
    if not pygame.mixer.get_init():
        pygame.mixer.init()
        pygame.mixer.music.set_endevent(SONG_END)


def play(path: Path):
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


def play_song(queue:Queue):
    global state_player
    if not queue.queue:
        return
    if queue.current_song is None:
        queue.current_index = 0
        queue.current_song = queue.queue[0]
    if state_player == StatePlay.STOP and isinstance(queue.current_song, Song) and isinstance(queue.current_song.path, Path):
        if play(queue.current_song.path):
            state_player = StatePlay.PLAY
        else:
            state_player = StatePlay.STOP
    elif state_player == StatePlay.PAUSE:
        resume_play()
        state_player = StatePlay.PLAY


def stop_song():
    global state_player
    stop()
    state_player = StatePlay.STOP


def pause_song(queue:Queue|None = None):
    global state_player
    if state_player == StatePlay.PAUSE:
        return state_player
    if state_player == StatePlay.STOP:
        state_player = StatePlay.PAUSE
        return state_player
    pause()
    state_player = StatePlay.PAUSE
    return state_player


def next_song(queue:Queue|None = None):
    from services import queue_service

    active_queue = queue or queue_service.get_active_queue()
    if not active_queue.queue:
        return
    stop_song()
    if active_queue.repeat_mode == RepeatMode.REPEAT_ALL:
        active_queue.current_index = (active_queue.current_index + 1) % len(active_queue.queue)
        active_queue.current_song = active_queue.queue[active_queue.current_index]
    elif active_queue.repeat_mode == RepeatMode.NO_REPEAT:
        next_index = active_queue.current_index + 1
        if next_index < len(active_queue.queue):
            active_queue.current_index = next_index
            active_queue.current_song = active_queue.queue[next_index]
        else:
            active_queue.current_index = -1
            active_queue.current_song = None
            return
    elif active_queue.repeat_mode == RepeatMode.REPEAT_ONE:
        if active_queue.current_song is None and active_queue.queue:
            active_queue.current_index = 0
            active_queue.current_song = active_queue.queue[0]
    play_song(active_queue)


def previous_song(queue:Queue|None = None):
    from services import queue_service

    active_queue = queue or queue_service.get_active_queue()
    if not active_queue.queue:
        return
    if active_queue.current_index < 0:
        active_queue.current_index = 0
    active_queue.current_index = (active_queue.current_index - 1) % len(active_queue.queue)
    active_queue.current_song = active_queue.queue[active_queue.current_index]
    stop_song()
    play_song(active_queue)


def checkLecture(queue):
    if not pygame.mixer.get_init():
        return
    for event in pygame.event.get():
        if event.type == SONG_END and state_player == StatePlay.PLAY:
            next_song(queue)
