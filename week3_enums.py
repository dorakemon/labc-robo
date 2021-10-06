from enum import IntEnum, auto

class Paper(IntEnum):
    RED = auto()
    BLUE = auto()
    GREEN = auto()

class Mode(IntEnum):
    SEARCH = auto()
    FIND_PARTIAL = auto()
    FIND_ALL = auto()
    ANGLE_ADJUST = auto()
    CHECK_CENTER = auto()
    APPROACH = auto()
    PENDING = auto()

# 角度調整のための状態
class AA_STATE(IntEnum):
    INIT = auto()
    S_FRONT = auto()
    S_RIGHT = auto()
    S_LEFT = auto()

class SE_STATE(IntEnum):
    S_FRONT = auto()
    S_RIGHT = auto()
    S_LEFT = auto()

class FP_STATE(IntEnum):
    INIT = auto()
    S_FRONT = auto()
    S_RIGHT = auto()
    S_LEFT = auto()

class FIND_PART():
    def __init__(self) -> None:
        self.state = FP_STATE.INIT
        self.moved_1sec = False

    def update(self, update_state):
        self.state = update_state
    
    def move_forward(self):
        self.moved_1sec = True
    
    def reset(self):
        self.state = FP_STATE.INIT
        self.moved_1sec = False
