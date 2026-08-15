import pygame
from pathlib import Path

class AudioBackend:
    SONG_END_EVENT = pygame.USEREVENT + 1
    def __init__(self) -> None:
        pygame.mixer.init()
        pygame.mixer.music.set_endevent(self.SONG_END_EVENT)

    def load(self, path:Path):
        pygame.mixer.music.load(str(path))

    def play(self):
        pygame.mixer.music.play()

    def pause(self):
        pygame.mixer.music.pause()

    def resume(self):
        pygame.mixer.music.unpause()

    def stop(self):
        pygame.mixer.music.stop()

    # Lecture en cours ?
    def is_busy(self):
        return pygame.mixer.music.get_busy()

    # Retourne les évènements
    def poll_events(self):
        return pygame.event.get()

backend = AudioBackend()