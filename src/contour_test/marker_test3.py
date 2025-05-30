# gpt 4o
import numpy as np

def calculate_paper_coordinates(marker_coords, marker_to_paper_offset, rotation_angle):
    """
    根據 marker 的相機視角座標計算白紙的相機視角座標。

    :param marker_coords: numpy array, marker 的相機視角座標 (x, y, z)
    :param marker_to_paper_offset: numpy array, marker 到白紙中心的偏移量 (dx, dy, dz)
    :param rotation_angle: float, marker 到白紙的旋轉角度（以弧度為單位）
    :return: numpy array, 白紙的相機視角座標 (x, y, z)
    """
    # 創建旋轉矩陣（假設只有 Z 軸旋轉）
    rotation_matrix = np.array([
        [np.cos(rotation_angle), -np.sin(rotation_angle), 0],
        [np.sin(rotation_angle), np.cos(rotation_angle), 0],
        [0, 0, 1]
    ])

    # 計算白紙的相機視角座標
    paper_coords = marker_coords + rotation_matrix @ marker_to_paper_offset
    return paper_coords

# 範例數據
marker_coords = np.array([1.0, 2.0, 3.0])  # marker 的相機視角座標
marker_to_paper_offset = np.array([0.5, 0.5, 0.0])  # marker 到白紙的偏移量
rotation_angle = np.radians(30)  # 旋轉角度（30 度轉為弧度）

# 計算白紙的相機視角座標
paper_coords = calculate_paper_coordinates(marker_coords, marker_to_paper_offset, rotation_angle)
print("白紙的相機視角座標:", paper_coords)