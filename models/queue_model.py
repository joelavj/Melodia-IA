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
<<<<<<< HEAD
    state_player: StatePlay = StatePlay.STOP

    
=======
    repeat_mode: RepeatMode = RepeatMode.REPEAT_ALL
    #repeat_mode = RepeatMode.NO_REPEAT
    state_player: StatePlay = StatePlay.STOP
>>>>>>> 2888ecd1a236c850e4c676fdc58a447724476148
