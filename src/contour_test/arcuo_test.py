import math
import cv2
import numpy as np


"""
Function Description of findHMatrix:
    @param pts1: source points. 
    @param pts2: Destination points. 

    @return b: 3x3 Homography matrix 

    @brief :This function finds the homography between two
           points pts1 and pts2 using svd method
"""


def findHMatrix(pts1, pts2):
    A = []
    # Image coordinates
    xc1, yc1 = pts1[0]
    xc2, yc2 = pts1[1]
    xc3, yc3 = pts1[2]
    xc4, yc4 = pts1[3]

    # World Coordinates
    xw1, yw1 = pts2[0]
    xw2, yw2 = pts2[1]
    xw3, yw3 = pts2[2]
    xw4, yw4 = pts2[3]

    # Transforming World to Image coordinates
    A = [
        [xw1, yw1, 1, 0, 0, 0, -xc1 * xw1, -xc1 * yw1, -xc1],
        [0, 0, 0, xw1, yw1, 1, -yc1 * xw1, -yc1 * yw1, -yc1],
        [xw2, yw2, 1, 0, 0, 0, -xc2 * xw2, -xc2 * yw2, -xc2],
        [0, 0, 0, xw2, yw2, 1, -yc2 * xw2, -yc2 * yw2, -yc2],
        [xw3, yw3, 1, 0, 0, 0, -xc3 * xw3, -xc3 * yw3, -xc3],  # pdf
        [0, 0, 0, xw3, yw3, 1, -yc3 * xw3, -yc3 * yw3, -yc3],
        [xw4, yw4, 1, 0, 0, 0, -xc4 * xw4, -xc4 * yw4, -xc4],
        [0, 0, 0, xw4, yw4, 1, -yc4 * xw4, -yc4 * yw4, -yc4],
    ]
    u, s, V = np.linalg.svd(A, full_matrices=True)

    # Converting to Hommogeneous coordinates
    a = []
    if V[8][8] == 1:
        for i in range(0, 9):
            a.append(V[8][i])
    else:
        for i in range(0, 9):
            a.append(V[8][i] / V[8][8])

    # H matrix in 3X3 shape
    b = np.reshape(a, (3, 3))
    return b


def show_image(img, title, width):
    ratio =  img.shape[0] / img.shape[1]

    cv2.namedWindow(title, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(title, width, int(width * ratio))
    cv2.imshow(title, img)


def undistort(image):
    h = image.shape[0]
    w = image.shape[1]

    camera_matrix = np.array([
            [523.105750, 0, 635.434258],
            [0, 534.765913, 500.335102],
            [0, 0, 1]
        ], dtype=np.float32)

    dist_coeffs = np.array([-0.164787, 0.020375, -0.001572, -0.000369, 0.000000], dtype=np.float32)
        
    new_camera_matrix, roi = cv2.getOptimalNewCameraMatrix(
            camera_matrix, dist_coeffs, (w, h), 1, (w, h)
        )

    undistorted = cv2.undistort(image, camera_matrix, dist_coeffs, None, new_camera_matrix)

    return undistorted

def drawCorners(image, corners):
    (topLeft, topRight, bottomRight, bottomLeft) = corners

    # convert each of the (x, y)-coordinate pairs to integers
    topRight = (int(topRight[0]), int(topRight[1]))
    bottomRight = (int(bottomRight[0]), int(bottomRight[1]))
    bottomLeft = (int(bottomLeft[0]), int(bottomLeft[1]))
    topLeft = (int(topLeft[0]), int(topLeft[1]))

    cv2.putText(image, "TL", topLeft, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
    cv2.putText(image, "TR", topRight, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
    cv2.putText(image, "BR", bottomRight, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
    cv2.putText(image, "BL", bottomLeft, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

    cv2.circle(image, topLeft, 5, (255, 0, 0), 2)
    cv2.circle(image, topRight, 5, (255, 0, 0), 2)
    cv2.circle(image, bottomRight, 5, (255, 0, 0), 2)
    cv2.circle(image, bottomLeft, 5, (255, 0, 0), 2)

def get_warp_image_0(image, pts1, pts2):
    w = int(abs(topRight[0] - topLeft[0]))
    h = int(abs(topLeft[1] - bottomLeft[1]))

    pts1 = np.zeros([4, 2], dtype="float32")
    n = 0
    # put the image points in an array
    for j in corners:
        if n < 4:
            pts1[n][0] = j[0]
            pts1[n][1] = j[1]
        n += 1

    # points of upright tag
    pts2 = np.float32([[0, 0], [w - 1, 0], [w - 1, h - 1], [0, h - 1]])

    # find the H matrix
    H = findHMatrix(pts2, pts1)  # Transforming second to first
    RevH = findHMatrix(pts1,pts2)  # Transforming second to first

    # H=cv2.Rodrigues(pts2,pts1)

    # Make the tag upright
    uprightTag = cv2.warpPerspective(img2, H, (w - 1, h - 1))
    # show_image(uprightTag, f"{markerID}: uprightTag", 720)


def get_warp_image_1(image, pts1, pts2):
    
    (topLeft, topRight, bottomRight, bottomLeft) = pts1

    # convert each of the (x, y)-coordinate pairs to integers
    topRight = (int(topRight[0]), int(topRight[1]))
    bottomRight = (int(bottomRight[0]), int(bottomRight[1]))
    bottomLeft = (int(bottomLeft[0]), int(bottomLeft[1]))
    topLeft = (int(topLeft[0]), int(topLeft[1]))

    w = int(abs(topRight[0] - topLeft[0]))
    h = int(abs(topLeft[1] - bottomLeft[1]))

    p1 = np.float32([topLeft,topRight,bottomRight,bottomLeft])
    # p2 = np.float32([[0, 0], [w - 1, 0], [w - 1, h - 1], [0, h - 1]])
    m = cv2.getPerspectiveTransform(p1,pts2)

    # img = cv2.imread('meme.jpg')
    tag = cv2.warpPerspective(image, m, (w - 1, h - 1))
    # cv2.imshow('oxxostudio', output)
    # show_image(tag, f"{markerID}: tag", 720)

    return tag

def getWarpImage(image, pts1):
    
    (topLeft, topRight, bottomRight, bottomLeft) = pts1

    # convert each of the (x, y)-coordinate pairs to integers
    topRight = (int(topRight[0]), int(topRight[1]))
    bottomRight = (int(bottomRight[0]), int(bottomRight[1]))
    bottomLeft = (int(bottomLeft[0]), int(bottomLeft[1]))
    topLeft = (int(topLeft[0]), int(topLeft[1]))

    w = int(abs(topRight[0] - topLeft[0]))
    h = int(abs(topLeft[1] - bottomLeft[1]))

    p1 = np.float32([topLeft,topRight,bottomRight,bottomLeft])
    p2 = np.float32([[0, 0], [w - 1, 0], [w - 1, h - 1], [0, h - 1]])
    m = cv2.getPerspectiveTransform(p1,p2)

    print(f"Warping: topLeft {topLeft} topRight {topRight} bottomRight {bottomRight} bottomLeft {bottomLeft}")

    # img = cv2.imread('meme.jpg')
    warped_img = cv2.warpPerspective(image, m, (w - 1, h - 1))
    # cv2.imshow('oxxostudio', output)
    # show_image(tag, f"{markerID}: tag", 720)

    return warped_img

def get_paper_corners_0(image, topLeft, topRight, bottomRight, bottomLeft, w, h, pts1):
    wt = image.shape[1]
    ht = image.shape[0]
    print(f"image width {wt} height {ht}")
    print(f"arTag width {w} height {h}")
    print(f"width ratio {wt / w} height ratio {ht / h}")
                        
            # 範例: 計算 marker 周圍的白紙位置
            # 假設你有 marker 的四個角點 pts1（順序: TL, TR, BR, BL）
            # margin_left = topLeft[0]
            # margin_right = image.shape[0] - topRight[0]
            # margin_top = topLeft[1]
            # margin_bottom = image.shape[1] - bottomLeft[1]
    margin_left = 2214
    margin_right = 257
    margin_top = 423
    margin_bottom = 1177

    print(f"margin_left {margin_left} margin_right {margin_right} margin_top {margin_top} margin_bottom {margin_bottom}")

    paper_topLeft     = [pts1[0][0] - margin_left, pts1[0][1] - margin_top]
    paper_topRight    = [pts1[1][0] + margin_right, pts1[1][1] - margin_top]
    paper_bottomRight = [pts1[2][0] + margin_right, pts1[2][1] + margin_bottom]
    paper_bottomLeft  = [pts1[3][0] - margin_left, pts1[3][1] + margin_bottom]

    white_paper_pos = (paper_topLeft, paper_topRight, paper_bottomRight, paper_bottomLeft)

    print(f"paper_topLeft {paper_topLeft} paper_topRight {paper_topRight} paper_bottomRight {paper_bottomRight} paper_bottomLeft {paper_bottomLeft}")

            # 若要在圖上繪製出來，可使用 cv2.polylines
            # paper_corners = np.array([paper_topLeft, paper_topRight, paper_bottomRight, paper_bottomLeft], dtype=np.int32)
            # cv2.polylines(image, [paper_corners], isClosed=True, color=(255,255,255), thickness=2)

            # r_pts1 = np.zeros([4, 2], dtype="float32")
            # n = 0
            # # put the image points in an array
            # for j in white_paper_pos:
            #     if n < 4:
            #         r_pts1[n][0] = j[0]
            #         r_pts1[n][1] = j[1]
            #     n += 1

            # paper_img = cv2.warpPerspective(img2, RevH, (wt - 1, ht - 1))
            # paper_img = cv2.warpPerspective(img2, H, (wt - 1, ht - 1))
            # show_image(paper_img, f"paper_img", 720)


            # 計算 marker 的旋轉角度（以 topLeft 到 topRight 的向量為基準）
    dx = topRight[0] - topLeft[0]
    dy = topRight[1] - topLeft[1]
    theta = math.atan2(dy, dx)

            # 建立將 marker 坐標系轉換到相機視角的旋轉矩陣
    R = np.array([[math.cos(theta), -math.sin(theta)],
                        [math.sin(theta),  math.cos(theta)]])

            # 定義 marker 與白紙的邊界距離（依 marker 座標系定義的 margin）
    margin_left   = 2214   # marker 與白紙左邊距離
    margin_right  = 257    # marker 與白紙右邊距離
    margin_top    = 423    # marker 與白紙上邊距離
    margin_bottom = 1177   # marker 與白紙下邊距離

            # 計算白紙的四個角點
    paper_topLeft     = topLeft     + R.dot(np.array([-margin_left, -margin_top]))
    paper_topRight    = topRight    + R.dot(np.array([ margin_right, -margin_top]))
    paper_bottomRight = bottomRight + R.dot(np.array([ margin_right,  margin_bottom]))
    paper_bottomLeft  = bottomLeft  + R.dot(np.array([-margin_left,  margin_bottom]))

    print("paper_topLeft:", paper_topLeft)
    print("paper_topRight:", paper_topRight)
    print("paper_bottomRight:", paper_bottomRight)
    print("paper_bottomLeft:", paper_bottomLeft)

    cv2.putText(
                image, "WTL", (int(paper_topLeft[0]),int(paper_topLeft[1])), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1
            )
    cv2.putText(
                image, "WTR", (int(paper_topRight[0]),int(paper_topRight[1])), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1
            )
    cv2.putText(
                image, "WBR", (int(paper_bottomRight[0]),int(paper_bottomRight[1])), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1
            )
    cv2.putText(
                image, "WBL", (int(paper_bottomLeft[0]),int(paper_bottomLeft[1])), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1
            )

def getPaperCorners(marker_corners, shape):
    top_left = marker_corners[0]
    top_right = marker_corners[1]
    bottom_right = marker_corners[2]
    bottom_left = marker_corners[3]

    paper_width_ratio = 27.0 / 4.5
    paper_height_ratio = 15.0 / 4.5
    
    x_vec = top_right - top_left
    y_vec = bottom_left - top_left
    
    x_vec_length = np.linalg.norm(x_vec)
    y_vec_length = np.linalg.norm(y_vec)
    
    x_vec_norm = x_vec / x_vec_length
    y_vec_norm = y_vec / y_vec_length
    
    marker_center = np.mean(marker_corners, axis=0)
    
    marker_size = (x_vec_length + y_vec_length) / 2
    
    scale = marker_size / 4.5
    
    tag_to_paper_left_distance = 20.0 + 2.25
    tag_to_paper_top_distance = 3.75
    
    paper_top_left = (marker_center - 
                    tag_to_paper_left_distance * scale * x_vec_norm - 
                    tag_to_paper_top_distance * scale * y_vec_norm)
    
    paper_top_right = paper_top_left + paper_width_ratio * marker_size * x_vec_norm
    
    paper_bottom_left = paper_top_left + paper_height_ratio * marker_size * y_vec_norm
    
    paper_bottom_right = paper_top_right + paper_height_ratio * marker_size * y_vec_norm
    
    all_points = np.array([paper_top_left, paper_top_right, 
                            paper_bottom_left, paper_bottom_right])
    
    min_x = np.min(all_points[:, 0])
    max_x = np.max(all_points[:, 0])
    min_y = np.min(all_points[:, 1])
    max_y = np.max(all_points[:, 1])
    
    start_x = max(0, int(np.floor(min_x)))
    start_y = max(0, int(np.floor(min_y)))
    end_x = min(shape[1] - 1, int(np.ceil(max_x)))
    end_y = min(shape[0] - 1, int(np.ceil(max_y)))
    
    width = end_x - start_x
    height = end_y - start_y
    
    if width <= 0 or height <= 0:
        print(f"Wrong cropping area, use default. Area: {area}")
        return marker_corners
    
    return [paper_top_left, paper_top_right, paper_bottom_right, paper_bottom_left]

def main():
    # raw_image = cv2.imread("./data/images/3c115d9c-8839-4ae8-9f3f-96d514dd5831.png")
    # raw_image = cv2.imread('./data/images/4b76e214-5bef-4adc-981f-ad6119932306.png')
    # raw_image = cv2.imread('./data/images/468070fc-23e0-4034-90ae-ca86b39935b7.png')
    # raw_image = cv2.imread('./data/images/c07d7f1c-581c-4b12-9105-9a131705f785.png')
    # raw_image = cv2.imread('./data/images/482585764_1455590368759521_6647519779772489171_n.png')
    # raw_image = cv2.imread('./data/images/490238254_1842446786580514_8292045078609051837_n.png') #??
    # raw_image = cv2.imread('./data/images/490752727_3922194774688090_1916180895651358198_n.png')
    # raw_image = cv2.imread('./data/images/490797075_9500783306706076_2074756401633110199_n.png')
    # raw_image = cv2.imread('./data/images/490986346_1041000924540372_5860720053675956248_n.png')
    raw_image = cv2.imread('./data/images/491008900_1819195295531383_8823035513900614833_n.png')

    image = raw_image.copy()
    # image = undistort(raw_image)

    img2=image.copy()

    arucoDict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_5X5_1000)
    arucoParams = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(arucoDict, arucoParams)

    (corners, ids, rejected) = detector.detectMarkers(image)

    print(f"corners are {len(corners)}")
    # if ids: print (f"ids are {len(ids)}")
    print(f"rejected are {len(rejected)}")

    ratio = image.shape[1] / image.shape[0]

    cv2.namedWindow("Image", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Image", int(720 * ratio), 720)

    for i in range(len(corners)):
        print(f"ids {i} are {ids[i]}")
        cv2.aruco.drawDetectedMarkers(image, corners, ids)

    if len(corners) > 0:
        ids = ids.flatten()
        for markerCorner, markerID in zip(corners, ids):
            corners = markerCorner.reshape((4, 2))
            (topLeft, topRight, bottomRight, bottomLeft) = corners

            # convert each of the (x, y)-coordinate pairs to integers
            topRight = (int(topRight[0]), int(topRight[1]))
            bottomRight = (int(bottomRight[0]), int(bottomRight[1]))
            bottomLeft = (int(bottomLeft[0]), int(bottomLeft[1]))
            topLeft = (int(topLeft[0]), int(topLeft[1]))

            print(f"id {markerID}: topLeft {topLeft} topRight {topRight} bottomRight {bottomRight} bottomLeft {bottomLeft}")

            # drawCorners(image, corners)

            # get_warp_image_0(image, corners, new_corners)

            # get_paper_corners_0(image, topLeft, topRight, bottomRight, bottomLeft, w, h, pts1)

            # w = int(abs(topRight[0] - topLeft[0]))
            # h = int(abs(topLeft[1] - bottomLeft[1]))
            # p2 = np.float32([[0, 0], [w - 1, 0], [w - 1, h - 1], [0, h - 1]])
            # tag = get_warp_image_1(img2, corners, p2)
            # tag = getWarpImage(img2, corners)
            # show_image(tag, f"{markerID}: tag", 720)
            
            paper_corners = getPaperCorners(corners, image.shape)
            drawCorners(image, paper_corners)
            paper_img = getWarpImage(img2, paper_corners)
            show_image(paper_img, f"Paper ID {markerID}", 512)


    cv2.imshow("Image", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


main()
