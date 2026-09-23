import pygame
from pathlib import Path

class AudioBackend:
    SONG_END_EVENT = pygame.USEREVENT + 1
    def __init__(self) -> None:
        pygame.init()
        pygame.mixer.init()
        pygame.mixer.music.set_endevent(self.SONG_END_EVENT)
        self.current_track_elapsed = 0

    def load(self, path:Path):
        self.current_track_elapsed = 0
        # SDL_mixer garde en interne la position atteinte par le morceau
        # précédent (surtout après un seek()) ; sans unload() explicite,
        # le prochain play() pouvait repartir de cette ancienne position
        # au lieu de 0, donnant l'impression que "suivant" reprenait là
        # où le morceau précédent s'était arrêté.
        pygame.mixer.music.unload()
        pygame.mixer.music.load(str(path))
        # SDL_mixer poste parfois un SONG_END_EVENT juste après un load()
        # explicite (même quand aucun morceau n'était réellement fini). Sans
        # purge, cet évènement fantôme est traité au prochain poll comme une
        # vraie fin de morceau -> avance automatique et intempestive vers le
        # morceau suivant (c'est ce qui causait le "next" qui n'arrêtait
        # plus de nexter).
        pygame.event.clear(self.SONG_END_EVENT)

    def play(self):
        pygame.mixer.music.play(loops=0, start=0.0)

    def pause(self):
        pygame.mixer.music.pause()

    def resume(self):
        pygame.mixer.music.unpause()

    def stop(self):
        pygame.mixer.music.stop()
        # Même remarque que pour load() : stop() peut lui aussi poster un
        # SONG_END_EVENT fantôme. Sans cette purge, ce faux évènement était
        # traité juste après par le poller -> le moteur relançait aussitôt
        # le morceau suivant, donnant l'impression que "stop" ne stoppait
        # pas la lecture.
        pygame.event.clear(self.SONG_END_EVENT)

    # Lecture en cours ?
    def is_busy(self):
        return pygame.mixer.music.get_busy()

    def seek(self,pos:int):
        self.current_track_elapsed = pos
        pygame.mixer.music.set_pos(pos)
        

    def current_position(self) -> float:
        return max(self.current_track_elapsed,pygame.mixer.music.get_pos() / 1000.0)

    # Retourne les évènements
    def poll_events(self):
        return pygame.event.get()

    def volume(self, val:float):
        pygame.mixer.music.set_volume(val)

backend = AudioBackend()