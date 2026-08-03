from services.player_service import backend
from services.queue_service import queue

from utils.constante import StatePlay, RepeatMode
from models.song_model import Song

from pathlib import Path
from typing import cast

class PlayEngine:
    def __init__(self) -> None:
        self._state = StatePlay.STOP
        self._repeat_mode = RepeatMode.REPEAT_ALL

    def play(self,  song:Song | None = None)->bool:
        if song is not None:
            if not self._prepare_song(song):
                return False
        current_song = queue.current()
        if current_song is None:
            return False
        match self._state:
            case StatePlay.PLAY:
                self.pause()
                return False
            case StatePlay.PAUSE:
                return self._resume()
            case StatePlay.STOP:
                return self._play_current()
        return False

    def _prepare_song(self, song:Song)->bool:
        if not queue.contains(song):
            queue.clear()
            queue.add(song)
        return True if queue.select(song) is not None else False

    def _resume(self)->bool:
        backend.resume()
        self._state = StatePlay.PLAY
        return True

    def next(self):
        song = self._move_next()
        if song is None:
            return self.stop()
        return self._play_current()

    def _next_song(self):
        if queue.is_empty():
            return None
        match self._repeat_mode:
            case RepeatMode.NO_REPEAT:
                if queue.has_next():
                    return queue.next()
                return None
            case RepeatMode.REPEAT_ONE:
                return queue.current()
            case RepeatMode.REPEAT_ALL:
                if queue.has_next():
                    return queue.next()
                queue.select_first()
                return queue.current()

    def previous(self):
        self._move_previous()
        return self._play_current()

    def _previous_song(self):
        if queue.is_empty():
            return None
        if queue.has_previous():
            return queue.previous()
        queue.select_first()
        return queue.current()

    def stop(self):
        backend.stop()
        self._state = StatePlay.STOP

    def pause(self):
        if self._state != StatePlay.PLAY:
            return
        backend.pause()
        self._state = StatePlay.PAUSE

    def _handle_song_end(self):
        song = self._move_next()
        if song is None:
            self.stop()
            return
        self._play_current()

    def _handle_event(self, event)->None:
        if event.type == backend.SONG_END_EVENT:
            self._handle_song_end()

    def process_events(self):
        for event in backend.poll_events():
            self._handle_event(event)

    def _play_current(self):
        current = queue.current()
        if current is None:
            return False
        try:
            backend.stop()
            backend.load(cast(Path, current.path))
            backend.play()
            self._state = StatePlay.PLAY
            return True
        except Exception as error:
            print(error)
            self._state = StatePlay.STOP
            return False
        
    def _move_next(self)->Song|None:
        if queue.is_empty():
            return None
        repeat_mode = self._repeat_mode
        match repeat_mode:
            case RepeatMode.NO_REPEAT:
                if queue.has_next():
                    return queue.next()
                return None
            case RepeatMode.REPEAT_ONE:
                return queue.current()
            case RepeatMode.REPEAT_ALL:
                if queue.has_next():
                    return queue.next()
                return queue.select_first()
        return None

    def _move_previous(self)->Song|None:
        if queue.is_empty():
            return None
        match self._repeat_mode:
            case RepeatMode.NO_REPEAT:
                if queue.has_previous():
                    return queue.previous()
                return queue.current()
            case RepeatMode.REPEAT_ONE:
                return queue.current()
            case RepeatMode.REPEAT_ALL:
                if queue.has_previous():
                    return queue.previous()
                return queue.select_last()
        return None

    def current_song(self)->Song|None:
        return queue.current()

    def state(self)->StatePlay:
        return self._state

    def repeat_mode(self)->RepeatMode:
        return self._repeat_mode

    def change_repeat_mode(self)->RepeatMode:
        if self._repeat_mode == RepeatMode.REPEAT_ALL:
            self._repeat_mode = RepeatMode.REPEAT_ONE
        elif self._repeat_mode == RepeatMode.REPEAT_ONE:
            self._repeat_mode = RepeatMode.NO_REPEAT
        elif self._repeat_mode == RepeatMode.NO_REPEAT:
            self._repeat_mode = RepeatMode.REPEAT_ALL
        return self._repeat_mode


engine = PlayEngine()