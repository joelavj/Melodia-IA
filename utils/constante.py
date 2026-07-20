from enum import Enum

class StatePlay(Enum):
    PLAY = "lecture"
    PAUSE = "pause"
    STOP = "stop"

class RepeatMode(Enum):
    NO_REPEAT = "aucun répetition"
    REPEAT_ALL = "répéter tout"
    REPEAT_ONE = "répéter un seul"