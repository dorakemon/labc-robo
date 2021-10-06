from enum import IntEnum, auto

"""import serial_lib as ser"""

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


# 状態遷移クラスはカメラのみ動かせる
class Search():
    class STATE(IntEnum):
        FRONT = auto()
        RIGHT = auto()
        LEFT = auto()
    
    def __init__(self):
        self.state = self.STATE.FRONT
        self.move_forward = False
        self.move_forward_count = 0
    
    def reset(self):
        self.state = self.STATE.FRONT
        self.move_forward = False
        self.move_forward_count = 0
        """ser.camera_horizontal(90)"""
    
    def update(self):
        if self.state == self.STATE.FRONT:
            """ser.camera_horizontal(110)"""
            self.move_forward = False
            self.state = self.STATE.RIGHT
        elif self.state == self.STATE.RIGHT:
            """ser.camera_horizontal(70)""" 
            self.state = self.STATE.LEFT
        elif self.state == self.STATE.LEFT:
            """ser.camera_horizontal(90)"""
            self.state = self.STATE.FRONT
            self.move_forward = True
            self.move_forward_count += 1
    
    def lookingRight(self):
        return self.state == self.STATE.RIGHT
    
    def lookingLeft(self):
        return self.state == self.STATE.LEFT

class FindPart():
    class STATE(IntEnum):
        FRONT = auto()
        RIGHT = auto()
        LEFT = auto()

    def __init__(self) -> None:
        self.state = self.STATE.INIT
        self.move_forward = False

    def reset(self):
        self.state = self.STATE.INIT
        self.move_forward = False
        """ ser.camera_horizontal(90) """

    def update(self):
        if self.state == self.STATE.FRONT:
            """ser.camera_horizontal(100)"""
            self.move_forward = False
            self.state = self.STATE.RIGHT
        elif self.state == self.STATE.RIGHT:
            """ser.camera_horizontal(80)""" 
            self.state = self.STATE.LEFT
        elif self.state == self.STATE.LEFT:
            """ser.camera_horizontal(90)"""
            self.state = self.STATE.FRONT
            self.move_forward = True

    def lookingRight(self):
        return self.state == self.STATE.RIGHT
    
    def lookingLeft(self):
        return self.state == self.STATE.LEFT

class AngleAdjust():
    class STATE(IntEnum):
        FRONT = auto()
        RIGHT = auto()
        LEFT = auto()

    def __init__(self) -> None:
        self.state = self.STATE.FRONT
    
    def reset(self):
        self.state = self.STATE.FRONT
        """ser.camera_horizontal(90)"""

    def update(self):
        if self.state == self.STATE.FRONT:
            """ser.camera_horizontal(110)"""
            self.state = self.STATE.RIGHT
        elif self.state == self.STATE.RIGHT:
            """ser.camera_horizontal(70)""" 
            self.state = self.STATE.LEFT
        elif self.state == self.STATE.LEFT:
            """ser.camera_horizontal(90)"""
            self.state = self.STATE.FRONT
    
    def lookingRight(self):
        return self.state == self.STATE.RIGHT
    
    def lookingLeft(self):
        return self.state == self.STATE.LEFT
