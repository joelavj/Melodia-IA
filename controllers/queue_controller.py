from services.queue_service import queue
from models.song_model import Song
from typing import Optional

class QueueController :
    def add_song(self, id_song:int):
        queue.add(id_song)

    def remove_song(self, id_song:int):
        queue.remove(id_song)

    def clear_queue(self):
        queue.clear()

    
    def move_song(self, id_song:int, pos_init:int, pos_target:int):
        queue.change_order_song(id_song, pos_init, pos_target)
    

queue_controller = QueueController()

