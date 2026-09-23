from services.player_service import engine
from typing import Optional
from models.song_model import Song
from utils.constante import StatePlay
from controllers.lyrics_controller import lyrics_controller
from utils.logger import get_logger

logger = get_logger(__name__)


class PlayerController :

    def play_song(self, id_song:Optional[int]=None):

        is_playing = engine.play(id_song)
        if is_playing:
            logger.debug("Morceau en cours de lecture")
        else:
            logger.debug("Morceau en pause")
        return is_playing

    def toggle_play_pause(self):
        """Alterne lecture/pause du morceau courant. Utilisé par la barre de lecture (PlayerBar)."""
        return self.play_song()

    def player_status(self):
        return {
            "song": engine.current_song(),
            "state": engine.state(),
            "repeat": engine.repeat_mode(),
            "is_playing" : True if engine.state() == StatePlay.PLAY else False
        }

    def is_playing(self) -> bool:
        """Etat de lecture courant, sous forme de booléen. Utilisé par la barre de lecture."""
        return self.player_status()["is_playing"]

    def current_song(self):
        """Morceau actuellement chargé dans le moteur. Utilisé par la barre de lecture."""
        return engine.current_song()

    def next_song(self):
        engine.next()

    def next(self):
        """Alias attendu par la barre de lecture."""
        self.next_song()

    def previous_song(self):
        return engine.previous()

    def previous(self):
        """Alias attendu par la barre de lecture."""
        self.previous_song()

    def stop_play(self):
        engine.stop()

    def stop(self):
        """Alias attendu par la barre de lecture."""
        self.stop_play()

    def change_repeat_mode(self):
        return engine.change_repeat_mode()

    def get_repeat_mode(self):
        """Mode de répétition courant renvoyé par le backend."""
        return engine.repeat_mode()

    def process_event(self):
        engine.process_events()

    def seek(self,pos:int):
        pos = int(pos)
        if engine.seek(pos):
            logger.debug("temps de lecture actuelle %d:%02d", pos // 60, pos % 60)
        else:
            logger.warning("Erreur du temps %d:%02d", pos // 60, pos % 60)

    def current_position(self)->float:
        return engine.current_position()

    def get_playback_position(self) -> float:
        """Alias attendu par la barre de lecture."""
        return self.current_position()

    def current_lyric(self, id_song:Optional[int]=None, current_time:Optional[float]=None):
        return lyrics_controller.sync_current_lyrics(id_song=id_song, current_time=current_time)

    def change_volume(self, val:int):
        if engine.change_volume(val):
            logger.debug("Volume changé en %s", val)
        else:
            logger.debug("Volume inchangée")

    def set_volume(self, val:float):
        """La vue (PlayerBar) envoie un volume normalisé entre 0 et 1 ;
        on le convertit vers l'échelle 0-100 attendue par le backend."""
        self.change_volume(int(round(val * 100)))

player_controller = PlayerController()
