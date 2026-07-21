from dataclasses import dataclass, field
from typing import Optional
from models.song_model import Song
from utils.constante import RepeatMode


@dataclass
class Queue:
    id:int = -1 
    name:str = ""
    current_index: int = -1
    current_song:Optional[Song] = None
    queue:list[Song] = field(default_factory=list)
    repeat_mode: RepeatMode = RepeatMode.REPEAT_ALL

    def add_song(self, morceau:Song):
        if not isinstance(morceau.id, int):
            return
        for song in list(self.queue):
            if isinstance(song.id, int) and song.id == morceau.id:
                self.queue.remove(song)
        self.queue.append(morceau)

    def remove_song(self, song:Song):
        if song not in self.queue:
            return
        self.queue.remove(song)
        if self.current_song is not None and self.current_song.id == song.id:
            if self.queue:
                self.current_index = min(self.current_index, len(self.queue) - 1)
                self.current_song = self.queue[self.current_index]
            else:
                self.clear_queue()
                return
    
    def clear_queue(self):
        self.queue.clear()
        self.current_song = None
        self.current_index = -1
                
    def play(self, song:Song):
        self.current_index = self.queue.index(song)
        self.current_song = self.queue[self.current_index]