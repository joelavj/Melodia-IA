from dataclasses import dataclass, field
from typing import Optional
from models.song_model import Song
from utils.constante import RepeatMode, StatePlay

@dataclass
class Queue:
    id:int = 0 
    name:str = "queue"
    current_index: int = -1
    current_song: Optional[Song] = None
    queue:list[Song] = field(default_factory=list)