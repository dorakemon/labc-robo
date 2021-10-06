from enum import IntEnum, auto

class Paper(IntEnum):
    RED = auto()
    BLUE = auto()
    GREEN = auto()

class Mode(IntEnum):
    SEARCH = auto()
    SEARCH2 = auto()
    FIND_PARTIAL = auto()
    FIND_ALL = auto()
    ANGLE_ADJUST = auto()
    CHECK_CENTER = auto()
    APPROACH = auto()
