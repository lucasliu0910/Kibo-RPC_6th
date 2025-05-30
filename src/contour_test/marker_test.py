# o3-mini
import numpy as np
import math

def convert_marker_to_object(marker_corners, margins):
    """
    根據 marker 在相機座標系中的四個角點及 marker 與物體固定的相對邊界距離，
    換算出物體（例如白紙）在相機座標系裡的四角座標。
    
    參數:
        marker_corners: tuple，依序包含 marker 的四個角點 (topLeft, topRight, bottomRight, bottomLeft)，
                        每個角點格式為 (x, y)
        margins: dict，包含 marker 與物體之間的邊界距離，
                 範例如: {'left': 2214, 'right': 257, 'top': 423, 'bottom': 1177}
                 
    回傳:
        object_corners: tuple，依序為物體在相機座標系中的四角點 (topLeft, topRight, bottomRight, bottomLeft)
    """
    # 解包 marker 四角點
    topLeft, topRight, bottomRight, bottomLeft = marker_corners

    # 計算 marker 的旋轉角度 (以 topLeft 到 topRight 的向量為基準)
    dx = topRight[0] - topLeft[0]
    dy = topRight[1] - topLeft[1]
    theta = math.atan2(dy, dx)

    # 建立旋轉矩陣：將 marker 座標系轉換到相機座標系
    R = np.array([[math.cos(theta), -math.sin(theta)],
                  [math.sin(theta),  math.cos(theta)]])

    # 計算物體（例如白紙）的每個角點
    obj_topLeft     = np.array(topLeft)     + R.dot(np.array([-margins['left'], -margins['top']]))
    obj_topRight    = np.array(topRight)    + R.dot(np.array([ margins['right'], -margins['top']]))
    obj_bottomRight = np.array(bottomRight) + R.dot(np.array([ margins['right'],  margins['bottom']]))
    obj_bottomLeft  = np.array(bottomLeft)  + R.dot(np.array([-margins['left'],  margins['bottom']]))

    return (obj_topLeft, obj_topRight, obj_bottomRight, obj_bottomLeft)


# 範例測試程式碼:
if __name__ == '__main__':
    # 假設 marker 的相機座標 (可從 aruco 檢測獲取)
    marker_corners = ((100, 100), (300, 120), (290, 250), (90, 230))
    # marker 與標記物體（例如白紙）的固定相對邊界距離
    margins = {'left': 2214, 'right': 257, 'top': 423, 'bottom': 1177}

    obj_corners = convert_marker_to_object(marker_corners, margins)
    print("物體四角座標：")
    print("Top Left:", obj_corners[0])
    print("Top Right:", obj_corners[1])
    print("Bottom Right:", obj_corners[2])
    print("Bottom Left:", obj_corners[3])
    