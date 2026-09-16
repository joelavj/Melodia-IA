from services.player_service import engine
from typing import Optional
from models.song_model import Song
from utils.constante import StatePlay
from controllers.lyrics_controller import lyrics_controller

class PlayerController :

    def play_song(self, id_song:Optional[int]=None):
        
        if engine.play(id_song):
            print("Morceau en cours de lecture")
        else:
            print("Morceau en pause")


    def player_status(self):
        return {
            "song": engine.current_song(),
            "state": engine.state(),
            "repeat": engine.repeat_mode(),
            "is_playing" : True if engine.state() == StatePlay.PLAY else False
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

    def seek(self,pos:int):
        if engine.seek(pos):
            print(f"temps de lecture actuelle {pos//60}:{pos%60} ")
        else:
            print(f"Erreur du temps {pos//60}:{pos%60} ")

    def current_position(self)->float:
        return engine.current_position()

    def current_lyric(self, id_song:Optional[int]=None, current_time:Optional[float]=None):
        return lyrics_controller.sync_current_lyrics(id_song=id_song, current_time=current_time)

    def change_volume(self, val:int):
        if engine.change_volume(val):
            print(f"Volume changé en {val}")
        else:
            print("Volume inchangée")

player_controller = PlayerController()