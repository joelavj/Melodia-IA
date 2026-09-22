from services.queue_service import queue
from services.player_service import engine
from models.song_model import Song
from typing import Optional

class QueueController :
    def add_song(self, id_song:int):
        queue.add(id_song)


    def remove_song(self, id_song:int):
        was_current = queue.remove(id_song)
        if was_current:
            # Le morceau retiré était en cours de lecture : auparavant rien
            # ne prévenait le moteur audio, qui continuait de jouer un
            # morceau qui n'existait plus dans la file d'attente. On enchaîne
            # maintenant sur le morceau qui a pris sa place, ou on arrête la
            # lecture si la file est désormais vide.
            current = queue.current()
            if current is not None:
                engine.play(current.id)
            else:
                engine.stop()

    def clear_queue(self):
        queue.clear()
        # Idem : vider la file pendant une lecture ne devait pas laisser le
        # morceau courant continuer à jouer dans le vide.
        engine.stop()


    def move_song(self, id_song:int, pos_init:int, pos_target:int):
        queue.change_order_song(id_song, pos_init, pos_target)


queue_controller = QueueController()
