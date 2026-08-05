from services.engine_service import engine
from typing import Optional
from models.song_model import Song
from utils.constante import StatePlay

class PlayerController :

    def play_pause(self, song:Optional[Song]=None):
        if engine.play(song):
            print("Morceau en cours de lecture")
        else:
            print("Morceau en pause")


    def player_status(self):
        return {
            "song": engine.current_song(),
            "state": engine.state(),
            "repeat": engine.repeat_mode()
        }


    def next_song(self):
        engine.next()


    def previous_song(self):
        engine.previous()

    def stop_play(self):
        engine.stop()

    def change_repeat_mode(self):
        return engine.change_repeat_mode()

    def process_event(self):
        engine.process_events()

player_controller = PlayerController()