import numpy as np, cv2, sympy as sp, pandas as pd

from enums import Paper
from parameter import (
    CAMERA_X, CAMERA_Y, 
    CLOSE_D, 
    HOUGH_PARA,
    ADJUST_ALLOW_PIXEL,
)

# 確認: 色紙のマスクのHSVの閾値に問題はないか
def getMask(color, framePTHSV):
    if color == Paper.RED:
        mask1 = cv2.inRange(framePTHSV, (0,100,100), (15,255,255))
        mask2 = cv2.inRange(framePTHSV, (170,100,100), (180,255,255))
        mask = mask1 + mask2
    elif color == Paper.BLUE:
        mask = cv2.inRange(framePTHSV, (90,70,50), (110,255,255))
    elif color == Paper.GREEN:
        mask = cv2.inRange(framePTHSV, (60,70,50), (80,230,255))
    return mask

def getLargestContour(contours, areas):
    max_index = np.argmax(areas)
    c = contours[max_index]
    top_oblique = cv2.minAreaRect(c)
    return top_oblique

def getNearestLongLine(contour, framePT):
    """
    ### 最も近い長辺を計算
    * 最も長くて近い辺の中心座標を取得
    * その反対にある中心座標も取得
    * その直線の傾きと、中心の座標を返す
    """
    # 枠の４辺中接する２辺
    line0 = np.linalg.norm(contour[0]-contour[1])
    line1 = np.linalg.norm(contour[1]-contour[2])
    # 長い辺を作る頂点のペア
    ps = [[0,1],[2,3]] if line0 > line1 else [[0,3],[1,2]]
    long_center0 = np.int0(1/2*(contour[ps[0][0]]+contour[ps[0][1]]))
    long_center1 = np.int0(1/2*(contour[ps[1][0]]+contour[ps[1][1]]))
    # 確認: カメラの中心座標を確認
    camera= np.array([CAMERA_X, CAMERA_Y])
    # カメラの位置から近い長い辺を取得
    line0 = np.linalg.norm(long_center0-camera)
    line1 = np.linalg.norm(long_center1-camera)
    if line0 < line1:
        nearest_long_center = long_center0
        opposit_long_center = long_center1
        tmp0 = 0
    else:
        nearest_long_center = long_center1
        opposit_long_center = long_center0
        tmp0 = 1
    tmp1 = contour[ps[tmp0][0]]-contour[ps[tmp0][1]]
    # zero divizion error
    if tmp1[0] == 0 or tmp1[0] is None:
        tmp1[0] = 1
    slope = tmp1[1]/tmp1[0]
    if slope == 0 or slope is None:
        slope = 0.0001
    cv2.circle(framePT, nearest_long_center, 4, (255,0,0), -1, 1, 0)
    cv2.circle(framePT, camera, 4, (255,255,255), -1, 2, 0)
    return nearest_long_center, opposit_long_center, slope

def getBisectorPoint(cp, op, slope, framePT):
    """ 
    ### 二等分線上の点を取得
    * 最も長い辺の中心座標と対辺の中心座標、長辺の傾きを取得 
    * 中心座標、傾きから、指定する距離の連立方程式を解き、点を取得  
    * 2点求まるがopに近い点を削除  
    """
    x = sp.Symbol('x')
    y = sp.Symbol('y')
    expr1 = (x-cp[0])**2+(y-cp[1])**2-CLOSE_D**2
    expr2 = -1/slope*(x-cp[0])-y+cp[1] 
    ans = sp.solve([expr1, expr2])
    if ans is not None and len(ans)==2:
        ans_point0 = (int(ans[0][x]),int(ans[0][y]))
        ans_point1 = (int(ans[1][x]),int(ans[1][y]))
        line0 = np.linalg.norm(ans_point0-op)
        line1 = np.linalg.norm(ans_point1-op)
        close_point = ans_point0 if line0 > line1 else ans_point1
        cv2.circle(framePT, close_point, 4, (133,21,199), -1, 1, 0)
        return close_point
    else:
        return None

def tangentAngle(u: np.array, v: np.array):
    """### 2つのベクトルがなす角度を取得"""
    i = np.inner(u, v)
    n = np.linalg.norm(u) * np.linalg.norm(v)
    c = i / n
    return np.rad2deg(np.arccos(np.clip(c, -1.0, 1.0)))

def getAngle(center, close):
    """
    ### 2箇所の回転の位置を取得
    * 時計回りの角度が正、反時計回りが負
    * x座標がcameraの方がcloseより左なら負
    """
    camera = np.array([CAMERA_X, CAMERA_Y])
    v_camera_vertival = np.array([0, -100])
    v_close_camera = close - camera
    angle0 = tangentAngle(v_camera_vertival, v_close_camera)
    if camera[0] > close[0]:
        angle0 = -angle0
    v_center_close = center - close
    angle1 = tangentAngle(v_center_close, v_close_camera)
    if close[0] > center[0]:
        angle1 = -angle1
    return angle0, angle1

def getDistance(center_point, close_point):
    """### cameraからclose, closeからcenterまでの距離"""
    camera = np.array([CAMERA_X, CAMERA_Y])
    d_close_camera = np.linalg.norm(close_point - camera)
    d_center_close = np.linalg.norm(center_point - close_point)
    return d_close_camera, d_center_close

def getHoughCircles(frame):
    frameGray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    frameGray = cv2.GaussianBlur(frameGray, (11,11), 0)
    # 確認: ハフ変換のパラメータはこのままでいいと思うがおかしければ修正
    circles = cv2.HoughCircles(frameGray, cv2.HOUGH_GRADIENT, **HOUGH_PARA)
    if circles is not None:
        circles = circles.squeeze(axis=0)
        for i in range(0, min(3, len(circles))):
            p = circles[i]
            cv2.circle(frame, (int(p[0]),int(p[1])), 4, (0,255,0), -1, 8, 0)
            cv2.circle(frame, (int(p[0]),int(p[1])), int(p[2]), (0,0,255), 6-2*i, 8, 0)
    return circles

def calcCirclesCenter(circles, frame):
    """
    複数の円を検知し、中心の点が密集している中心点と、認識した円の数を返す。
    * 外れ値を検出して排除する
    """
    center_x = []
    # https://qiita.com/papi_tokei/items/6f77a2a250752cfa850b
    # 誤検知の数を後で確認
    if circles is not None:
        for c in circles:
            center_x.append(int(c[0]))
        # 外れ値除去
        x_pd = pd.Series(center_x)
        Q1 = x_pd.quantile(0.25)
        Q3 = x_pd.quantile(0.75)
        IQR = Q3 - Q1
        LOWER_Q = Q1 - 1.5 * IQR
        HIGHER_Q = Q3 + 1.5 * IQR
        x_pd_iqr = x_pd[(LOWER_Q <= x_pd) & (x_pd <= HIGHER_Q)].dropna()
        circle_x = int(x_pd_iqr.mean())
        w = int(frame.shape[1]/2) - 40
        cv2.circle(frame, (circle_x,230), 4, (255,0,0), -1, 8, 0)
        cv2.circle(frame, (w,235), 4, (255,255), -1, 8, 0)
        cv2.circle(frame, (w-ADJUST_ALLOW_PIXEL,235), 4, (255,0,255), -1, 8, 0)
        cv2.circle(frame, (w+ADJUST_ALLOW_PIXEL,235), 4, (255,0,255), -1, 8, 0)
        return len(circles), circle_x, len(x_pd_iqr.tolist())
    return 0, 0, 0
