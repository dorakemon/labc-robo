from enum import IntEnum, auto

import serial_lib as ser

# 状態遷移クラスはカメラのみ動かせる
class BaseState():
    class STATE(IntEnum):
        FRONT = auto()
        RIGHT = auto()
        LEFT = auto()
    
    def __init__(self):
        self.state = self.STATE.FRONT
        ser.camera_horizontal(90)

    def reset(self):
        self.state = self.STATE.FRONT
        ser.camera_horizontal(90)
    
    def update(self):
        pass

    def lookingRight(self):
        return self.state == self.STATE.RIGHT
    
    def lookingLeft(self):
        return self.state == self.STATE.LEFT

class Search(BaseState):
    """
    初めての探索
    """
    def __init__(self):
        super().__init__()
        self.state = self.STATE.FRONT
        self.move_forward = False
        self.move_count = 0
    
    def reset(self):
        self.state = self.STATE.FRONT
        self.move_forward = False
        self.move_count = 0
        ser.camera_horizontal(90)
    
    def update(self):
        if self.state == self.STATE.FRONT:
            ser.camera_horizontal(110)
            self.move_forward = False
            self.state = self.STATE.RIGHT
        elif self.state == self.STATE.RIGHT:
            ser.camera_horizontal(70) 
            self.state = self.STATE.LEFT
        elif self.state == self.STATE.LEFT:
            ser.camera_horizontal(90)
            self.state = self.STATE.FRONT
            self.move_forward = True
            self.move_count += 1

class Search2(Search):
    """
    2回目以降の探索
    """
    def __init__(self):
        super().__init__()
        self.do_rotate = False
        self.rotate_count = 0
        self.move_ratio = 0.5
    
    def reset(self):
        super().reset()
        self.do_rotate = False
        self.rotate_count = 0
        self.move_ratio = 0.5
    
    def update(self):
        if self.state == self.STATE.FRONT:
            ser.camera_horizontal(110)
            self.move_forward = False
            self.do_rotate = False
            self.move_forward = False
            self.state = self.STATE.RIGHT
        elif self.state == self.STATE.RIGHT:
            ser.camera_horizontal(70)
            self.state = self.STATE.LEFT
        elif self.state == self.STATE.LEFT:
            ser.camera_horizontal(90)
            self.state = self.STATE.FRONT
            self.do_rotate = True
            self.rotate_count += 1
            # 4回まわったら直進する
            # 直進する距離は比例的に増加
            if self.rotate_count % 4 == 0:
                self.move_forward = True
                self.move_ratio += 0.5
                

class FindPart(BaseState):
    def __init__(self) -> None:
        super().__init__()
        self.move_forward = False

    def reset(self):
        super().reset()
        self.move_forward = False

    def update(self):
        if self.state == self.STATE.FRONT:
            ser.camera_horizontal(100)
            self.move_forward = False
            self.state = self.STATE.RIGHT
        elif self.state == self.STATE.RIGHT:
            ser.camera_horizontal(80) 
            self.state = self.STATE.LEFT
        elif self.state == self.STATE.LEFT:
            ser.camera_horizontal(90)
            self.state = self.STATE.FRONT
            self.move_forward = True

class AngleAdjust(BaseState):
    def __init__(self) -> None:
        super().__init__()
    
    def reset(self):
        super().reset()

    def update(self):
        if self.state == self.STATE.FRONT:
            ser.camera_horizontal(110)
            self.state = self.STATE.RIGHT
        elif self.state == self.STATE.RIGHT:
            ser.camera_horizontal(70) 
            self.state = self.STATE.LEFT
        elif self.state == self.STATE.LEFT:
            ser.camera_horizontal(90)
            self.state = self.STATE.FRONT