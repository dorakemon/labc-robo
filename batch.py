from asciimatics.screen import ManagedScreen

from enums import Mode
from state import Search, FindPart, AngleAdjust

# 出力する際に毎回print_atいろんなところですると、追加時に大変
class Batch:
    def __init__(self, _s:ManagedScreen) -> None:
        self.s = _s
        self.p = {
            'oblique_x': 0, 'oblique_y': 0, 'oblique_w': 0, 'oblique_h': 0,
            'oblique_angle': 0, 'oblique_area': 0,
            'slope': 0, 'close_point': 0, 'angle0': 0, 'angle1': 0,
            'd_close_camera': 0, 'd_center_close': 0,
            'len_circles': 0, 'circle_x': 0, 'len_circles_iqr': 0,
            'status': "stop", 'pixel': 0, 'angle': 0, 'time': 0,
            'finished_count': 0, 
            'current_status': Mode(1).name, 
            'se_state': Search.STATE(1).name,
            'fp_state': FindPart.STATE(1).name, 
            'aa_state': AngleAdjust.STATE(1).name,
            'move_record': {}
        }

    # oblique=None, slope=0, close_point=0,
    # angle0=0, angle1=0, d_close_camera=0, d_center_close=0,
    # len_circles=0, circle_x=0, len_circles_iqr=0,
    # status="stop", pixel=0, angle=0, time=0,
    # finished_count=0, current_status=0, se_state=0, 
    # fp_state=0, aa_state=0, move_record=0
    def update(self, **kwargs):
        for k, v in kwargs.items():
            if k == 'top_oblique':
                self.p['oblique_x'] = int(v[0][0])  #   中心 x 座標
                self.p['oblique_y'] = int(v[0][1])  #   中心 y 座標
                self.p['oblique_w'] = int(v[1][0])  #   幅
                self.p['oblique_h'] = int(v[1][1])  #   高さ
                self.p['oblique_angle'] = int(v[2]) #   傾き角
                self.p['oblique_area'] = int(v[1][0]) * int(v[1][1])   # 面積
            elif k == 'current_status':
                self.p['current_status'] = Mode(v).name
            elif k == 'se_state':
                self.p['se_state'] = Search.STATE(v).name
            elif k == 'fp_state':
                self.p['fp_state'] = FindPart.STATE(v).name
            elif k == 'aa_state':
                self.p['aa_state'] = AngleAdjust.STATE(v).name
            elif k not in self.p:
                raise KeyError(f"{k}のキーはself.pに存在しない")
            else: 
                self.p[k] = v

    def print(self):
        self.s.print_at(f"Yellow contour:",0,0,3,3)
        self.s.print_at(f"center : ({self.p['oblique_x']:3}, {self.p['oblique_y']:3})", 2,1)
        self.s.print_at(f"width  :{self.p['oblique_w']:6}", 2,2)
        self.s.print_at(f"height :{self.p['oblique_h']:6}", 2,3)
        self.s.print_at(f"angle  :{self.p['oblique_angle']:6}", 2,4)
        self.s.print_at(f"area   :{self.p['oblique_area']:6}", 2,5)

        self.s.print_at(f"APPROACH LINE", 0,7,1,3)
        self.s.print_at(f"slope      :{self.p['slope']:8.2f}", 2,8)
        self.s.print_at(f"close point: {self.p['close_point']}", 2,9)

        self.s.print_at(f"POINT INFO",0,11,5,3)
        self.s.print_at(f"angle0         : {self.p['angle0']:8.2f}°", 2,12)
        self.s.print_at(f"angle1         : {self.p['angle1']:8.2f}°", 2,13)
        self.s.print_at(f"d_close_camera : {self.p['d_close_camera']:8.2f} pixl", 2,14)
        self.s.print_at(f"d_center_close : {self.p['d_center_close']:8.2f} pixl", 2,15)

        self.s.print_at(f"HOUGH CIRCLES", 0,17,2,3)
        self.s.print_at(f"len(circles)   : {self.p['len_circles']:4}", 2,18)
        self.s.print_at(f"len(cir_iqr)   : {self.p['len_circles_iqr']:4}", 2,19)
        self.s.print_at(f"circle_x       : {self.p['circle_x']:4} pixl", 2,20)

        # self.s.print_at(f"CAR MOVE INFO",0,22,6,3)
        # self.s.print_at(f"status     : {self.p['status']}   ", 2,23)
        # self.s.print_at(f"pixel      : {self.p['pixel']:7.3f}", 2,24)
        # self.s.print_at(f"angle      : {self.p['angle']:7.3f}", 2,25)
        # self.s.print_at(f"time       : {self.p['time']:6.2f}", 2,26)
        self.s.refresh()

    def print_car_info(self):
        self.s.print_at(f"CAR MOVE INFO",0,22,6,3)
        self.s.print_at(f"status     : {self.p['status']}   ", 2,23)
        self.s.print_at(f"pixel      : {self.p['pixel']:7.3f}", 2,24)
        self.s.print_at(f"angle      : {self.p['angle']:7.3f}", 2,25)
        self.s.print_at(f"time       : {self.p['time']: 7.3f}", 2,26)
        self.s.refresh()

    def print_state(self):
        self.s.print_at(f"finished count : {self.p['finished_count']}", 2,33, 2, 2)
        self.s.print_at(f"current_status : {self.p['current_status']}", 2,34, 2, 2)
        self.s.print_at(f"SE_state : {self.p['se_state']       }", 2,35)
        self.s.print_at(f"FP_state : {self.p['fp_state']       }", 2,36)
        self.s.print_at(f"AA_state : {self.p['aa_state']       }", 2,37)
        # s.print_at(f"MOVE_RECORD    : {move_record}", 2,39)
        self.s.refresh()

    def print_color(self, pixel_value_str: str) -> None:
        self.s.print_at(pixel_value_str, 0, 31)
        self.s.refresh()

    def print_error(self, error_msg: str) -> None:
        self.s.print_at(f"{error_msg}", 0, 40, 1, 2)
        self.s.refresh()
    
    def print_record(self):
        self.s.print_at(f"MOVE_RECORD    : {len(self.p['move_record'])}", 2,38)
        line = 39
        for e in self.p['move_record']:
            self.s.print_at(f"MOVE_RECORD    : {e}", 2,line)
            line += 1
        for i in range(10):
            self.s.print_at(f"MOVE_RECORD    : ================================", 2,line+i)
            