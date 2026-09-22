from enum import Enum
from pathlib import Path

class StatePlay(Enum):
    PLAY = "lecture"
    PAUSE = "pause"
    STOP = "stop"

class RepeatMode(Enum):
    NO_REPEAT = "aucun répetition"
    REPEAT_ALL = "répéter tout"
    REPEAT_ONE = "répéter un seul"

BASE_DIR = Path(r".\src\assets").resolve()