# gemini 2.0 flash
import cv2
import numpy as np

def calculate_paper_coordinates(marker_coordinates, marker_to_paper_transform):
  """
  根據 marker 座標和 marker 到白紙的轉換，計算白紙座標。

  Args:
    marker_coordinates: Marker 在相機視角中的座標 (x, y)。
    marker_to_paper_transform: 將 marker 座標轉換為白紙座標的轉換矩陣。

  Returns:
    白紙在相機視角中的座標 (x, y)。
  """

  # 將 marker 座標轉換為齊次座標
  marker_homogeneous = np.array([marker_coordinates[0], marker_coordinates[1], 1])

  # 應用轉換
  paper_homogeneous = np.dot(marker_to_paper_transform, marker_homogeneous)

  # 將齊次座標轉換為笛卡爾座標
  paper_coordinates = (paper_homogeneous[0] / paper_homogeneous[2], paper_homogeneous[1] / paper_homogeneous[2])

  return paper_coordinates

# 範例用法
# 假設您已經檢測到 marker 並獲得了其座標
marker_coordinates = (100, 200)

# 假設您已經確定了 marker 到白紙的轉換矩陣
# 這是一個 3x3 的矩陣，描述了 marker 和白紙之間的旋轉和平移
marker_to_paper_transform = np.array([[1, 0, 10],
                                      [0, 1, 20],
                                      [0, 0, 1]])

# 計算白紙座標
paper_coordinates = calculate_paper_coordinates(marker_coordinates, marker_to_paper_transform)

# 打印結果
print("Marker 座標:", marker_coordinates)
print("白紙座標:", paper_coordinates)