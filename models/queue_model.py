from dataclasses import dataclass, field
from typing import Optional
from models.song_model import Song
from utils.constante import RepeatMode, StatePlay
import repositories.queue_repository as queue_repository


@dataclass
class Queue:
    id:int = 0 
    name:str = "queue"
    current_index: int = -1
    current_song: Optional[Song] = None
    queue:list[Song] = queue_repository.find_all()
    repeat_mode: RepeatMode = RepeatMode.REPEAT_ALL
    state_player: StatePlay = StatePlay.STOP