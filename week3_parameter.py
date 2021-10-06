from enums import Paper

# 探索純
COLOR_ORDER = [Paper.RED, Paper.BLUE, Paper.GREEN]

# １秒間に何ピクセル分進むことができるか
MOVE_VELOCITY = 43
# 移動速度

# 一周にかかる時間
ROTATE_SOCOND = 6.7
# 回転速度

# カメラの映っているそこの点への移動にかかる時間
INIT_MOVE_TIME = 2.3

# 透視変換後の画像のロボットの中心座標
# ロボットの中心座標をカーソル出さして計測
CAMERA_X = 120
CAMERA_Y = 260


# 紙がすべて映ったと判断する閾値
#  1700近辺
MIN_FULL_AREA = 1650
MAX_FULL_AREA = 3000

# 紙が少なくとも一部映ったと判断する
MIN_PART_AREA = 1000
MAX_PART_AREA = MIN_FULL_AREA

CLOSE_D = 80
# 初めに紙を検知して、それくらい近づいて回り込むか
# ピクセル指定
# 初めは遠くて何回か同じ処理を繰り返し正確にまっすぐに

SEARCH_MOVE_FORWARD_SEC = 1.2      
# 探索をするうえで前に進む秒数

# cf) https://shikaku-mafia.com/cv2-houghcircles/
HOUGH_PARA = {"dp":0.8, "minDist":3, "param1":20, 
            "param2":70, "minRadius":15, "maxRadius":max(240,320)}
# 円検出の際のパラメータ

ADJUST_ALLOW_PIXEL = 12
# 何ピクセル分ずれていても角度調整で許容できるかのピクセル

ADJUST_ANGLE = 2
# 角度微調整の際に何度ずつずらすか

APPROACH_MOVE_SEC = 2.5

MOTOR_DEFAULT_L = 122
MOTOR_DEFAULT_R = 133
SERVO_DEFAULT_V = 90
SERVO_DEFAULT_H = 99
