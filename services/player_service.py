import pygame
from pathlib import Path
import services.queue_service as queue
from utils.constante import StatePlay, RepeatMode

SONG_END = pygame.USEREVENT + 1
repeat_mode: RepeatMode = RepeatMode.REPEAT_ALL
state_player: StatePlay = StatePlay.STOP


def _ensure_mixer_initialized():
    if not pygame.mixer.get_init():
        pygame.mixer.init()
        pygame.mixer.music.set_endevent(SONG_END)


def play(path: Path):
    _ensure_mixer_initialized()
    pygame.mixer.music.load(str(path))
    pygame.mixer.music.play()


def pause():
    if pygame.mixer.get_init():
        pygame.mixer.music.pause()


def stop():
    if pygame.mixer.get_init():
        pygame.mixer.music.stop()


def resume_play():
    if pygame.mixer.get_init():
        pygame.mixer.music.unpause()


def play_song():
    global state_player
    if not queue.queue:
        return
    if queue.current_song is None:
        queue.current_index = 0
        queue.current_song = queue.queue[0]
    if state_player == StatePlay.STOP:
        play(queue.current_song.path)
        state_player = StatePlay.PLAY
    elif state_player == StatePlay.PAUSE:
        resume_play()
        state_player = StatePlay.PLAY


def stop_song():
    global state_player
    stop()
    state_player = StatePlay.STOP


def pause_song():
    global state_player
    if state_player in (StatePlay.STOP, StatePlay.PAUSE):
        return
    pause()
    state_player = StatePlay.PAUSE


def next_song():
    if not queue.queue:
        return
    stop_song()
    if repeat_mode == RepeatMode.REPEAT_ALL:
        queue.current_index = (queue.current_index + 1) % len(queue.queue)
        queue.current_song = queue.queue[queue.current_index]
    elif repeat_mode == RepeatMode.NO_REPEAT:
        next_index = queue.current_index + 1
        if next_index < len(queue.queue):
            queue.current_index = next_index
            queue.current_song = queue.queue[next_index]
        else:
            queue.current_index = -1
            queue.current_song = None
            return
    elif repeat_mode == RepeatMode.REPEAT_ONE:
        if queue.current_song is None and queue.queue:
            queue.current_index = 0
            queue.current_song = queue.queue[0]
    play_song()


def previous_song():
    if not queue.queue:
        return
    if queue.current_index < 0:
        queue.current_index = 0
    queue.current_index = (queue.current_index - 1) % len(queue.queue)
    queue.current_song = queue.queue[queue.current_index]
    stop_song()
    play_song()


def checkLecture():
    if not pygame.mixer.get_init():
        return
    for event in pygame.event.get():
        if event.type == SONG_END and state_player == StatePlay.PLAY:
            next_song()
