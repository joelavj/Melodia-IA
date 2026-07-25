from enum import Enum
from models.queue_model import Queue

class StatePlay(Enum):
    PLAY = "lecture"
    PAUSE = "pause"
    STOP = "stop"

class RepeatMode(Enum):
    NO_REPEAT = "aucun répetition"
    REPEAT_ALL = "répéter tout"
    REPEAT_ONE = "répéter un seul"

queue = Queue()