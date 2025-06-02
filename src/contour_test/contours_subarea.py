import cv2
import numpy as np
from enum import Enum


class Hierarchy(Enum):
    Next = 0
    Previous = 1
    First_Child = 2
    Parent = 3

black = (0, 0, 0)
white = (255, 255, 255)
red = (0,0,255)
green = (0,255,0)
blue = (255,0,0)

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


def create_blank(width, height, rgb_color=black):
    """Create new image(numpy array) filled with certain color in RGB"""
    # Create black blank image
    image = np.zeros((height, width, 3), np.uint8)

    # Since OpenCV uses BGR, convert the color first
    color = tuple(reversed(rgb_color))
    # Fill image with color
    image[:] = color

    return image


def show_image(img, title, width):
    ratio =  img.shape[0] / img.shape[1]

    cv2.namedWindow(title, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(title, width, int(width * ratio))
    cv2.imshow(title, img)


def get_mask(shape, pts):
    # width, height = 300, 300
    (height, width) = shape[:2]
    # red = (255, 0, 0)
    # black = (0, 0, 0)
    # white = (255, 255, 255)
    mask = create_blank(width, height, rgb_color=black)

    cv2.fillPoly(mask, [pts], white) 
    # cv2.fillPoly(mask, pts, white) 

    return mask


def get_paper_corners(marker_corners, shape):
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


def find_parent(hierarchy, index):
    # print("index:",index)
    # print("hierarchy[index]:",hierarchy[index])
    if hierarchy[index][Hierarchy.Parent.value] == -1:
        return index
        # return hierarchy[index][2]
    else:
        return find_parent(hierarchy, hierarchy[index][Hierarchy.Parent.value])


def get_corners_area(corners):
    top_left = corners[0]
    top_right = corners[1]
    bottom_right = corners[2]
    bottom_left = corners[3]

    # paper_width_ratio = 27.0 / 4.5
    # paper_height_ratio = 15.0 / 4.5
    
    x_vec = top_right - top_left
    y_vec = bottom_left - top_left
    
    x_vec_length = np.linalg.norm(x_vec)
    y_vec_length = np.linalg.norm(y_vec)

    return x_vec_length*y_vec_length


def draw_all_contours(img, contours):
    # cnt = contours[1]
    # x, y, w, h = cv2.boundingRect(cnt)
    # cv2.rectangle(img, (x, y), (x + w, y + h), red, 2)
    i = 0
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        cv2.rectangle(img, (x, y), (x + w, y + h), red, 2)
        # cv2.putText(img, f"{i}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, blue, 2)
        # print(f"draw_all_contours| Contour {i},x:{x},y:{y},w:{w},h:{h},area: {cv2.contourArea(cnt)}")
        i += 1

    show_image(img, 'draw_all_contours', 720)


def draw_only_parent_contours(img, contours, hierarchys):
    hierarchy = hierarchys[0]
    headi = find_parent(hierarchy, 0)
    childi = hierarchy[headi][Hierarchy.First_Child.value]

    # i = 0
    # for cnt in contours:
    #     x, y, w, h = cv2.boundingRect(cnt)
    #     print(f"draw_only_parent_contours| Contour {i},x:{x},y:{y},w:{w},h:{h},area: {cv2.contourArea(cnt)},parent_id:{hierarchy[i][Hierarchy.Parent.value]}")
    #     i += 1

    while childi != -1:
        cnt = contours[childi]
        x, y, w, h = cv2.boundingRect(cnt)
        cv2.rectangle(img, (x, y), (x + w, y + h), red, 2)
        # cv2.putText(img, str(cv2.contourArea(cnt)), (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, blue, 2)
        # cv2.putText(img, str(childi), (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, blue, 2)
        childi = hierarchy[childi][Hierarchy.Next.value]
        
        area = cv2.contourArea(cnt)
        # print(f"draw_only_parent_contours Contour {childi} area: {area}")

    show_image(img, 'draw_only_parent_contours', 720)


def draw_only_parent_contours_minum_area(img, contours, hierarchys, min_area=100):
    hierarchy = hierarchys[0]
    headi = find_parent(hierarchy, 0)
    childi = hierarchy[headi][Hierarchy.First_Child.value]

    while childi != -1:
        cnt = contours[childi]
        x, y, w, h = cv2.boundingRect(cnt)
        area = cv2.contourArea(cnt)
        ratio = area / min_area
        # print(f"draw_only_parent_contours_minum_area contour {childi} area: {area}, ratio: {area/min_area:.3f}")
        if ratio > 0.08:
            cv2.rectangle(img, (x, y), (x + w, y + h), red, 2)
            # cv2.putText(img, str(cv2.contourArea(cnt)), (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, blue, 2)
            cv2.putText(img, str(childi), (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, blue, 2)
            # print(f"draw_only_parent_contours_minum_area| Contour {childi} area: {area}, ratio: {ratio:.2f}")
        # else:
        #     print(f"draw_only_parent_contours_minum_area| Contour {childi} area: {area}, ratio: {ratio} is too small, not drawn")
        childi = hierarchy[childi][Hierarchy.Next.value]

    show_image(img, 'draw_only_parent_contours_minum_area', 720)


def draw_contours_ratio(img, contours, min_area=100, r=0.05, range=1):
    id=0
    for cnt in contours:
        area = cv2.contourArea(cnt)
        ratio = area / min_area
        # if 2 > ratio and ratio > 0.05:
        # if 1.5 > ratio and ratio > 0.5:
        if r + range > ratio and ratio > r:
        # if True:
            # x, y, w, h = cv2.boundingRect(cnt)
            # cv2.rectangle(img, (x, y), (x + w, y + h), red, 2)

            rect = cv2.minAreaRect(cnt)
            box = cv2.boxPoints(rect)
            box = box.astype(int) #np.int0(box)
            cv2.drawContours(img,[box],0,red,2)

            # cv2.putText(img, f"{id}:{cv2.contourArea(cnt)}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, blue, 2)
            # cv2.putText(img, f"{id}:{ratio:.1f}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, blue, 2)
        # else:
        #     print(f"draw_contours_ratio Contour {id} area: {area}, ratio: {ratio} is too small, not drawn")

        id=id+1

    show_image(img, f"draw_contours_ratio: ratio {r}", 720)


def draw_contours_minum_area_by_ratio(img, contours, min_area=100):
    for r in range(0, 10):
        temp_img = img.copy()
        draw_contours_ratio(temp_img, contours, min_area, r/10.0, 0.1)


def draw_label(img, text, x, y, color=black, background=white, font=cv2.FONT_HERSHEY_SIMPLEX, scale=1, thickness=2):
    size, _ = cv2.getTextSize(text, font, scale, thickness)
    # size = cv2.getTextSize(text, font, scale, thickness)
    width, height = size
    pos1 = (x, y)
    pos2 = (x + width, y - height)
    # print(f"draw_label: label:{text}, x:{x}, y:{y}, width:{width}, height:{height}")
    cv2.rectangle(img, pos1, pos2, background, -1)
    cv2.putText(img, text, pos1, font, scale, color, thickness)    


def draw_contours_minum_area(img, contours, min_area=100):
    # print(f"draw_contours_minum_area min_area: {min_area}")
    id=0
    labels=0
    for cnt in contours:
        area = cv2.contourArea(cnt)
        ratio = area / min_area
        # if True:
        # if 1.5 > ratio and ratio > 0.5:
        if 2 > ratio and ratio > 0.05:
            x, y, w, h = cv2.boundingRect(cnt)
            cv2.rectangle(img, (x, y), (x + w, y + h), red, 2)

            # rect = cv2.minAreaRect(cnt)
            # box = cv2.boxPoints(rect)
            # box = box.astype(int) #np.int0(box)
            # cv2.drawContours(img,[box],0,red,2)

            if labels < 8:
                # x, y, w, h = cv2.boundingRect(cnt)
                # cv2.putText(img, f"{id}:{cv2.contourArea(cnt)}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, blue, 2)
                # size, _ = cv2.getTextSize(f"{id}:{ratio:.1f}", cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
                # width, height = size
                # cv2.rectangle(img, (x, y), (x + width, y + height), white, 2)
                # cv2.putText(img, f"{id}:{ratio:.1f}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, blue, 2)
                draw_label(img, f"{id}:{ratio:.1f}", x, y-10, color=blue)
                labels += 1
            # print(f"draw_contours_minum_area| Contour {id} area: {area}, ratio: {ratio:.3f}")
        # else:
            # print(f"draw_contours_minum_area Contour {id} area: {area}, ratio: {ratio:.3f} is too small, not drawn")

        id=id+1

    show_image(img, 'draw_contours_minum_area', 720)


# def get_max_iou(cnt, cons, self_id=0):
#     # print(f"get_my_iou id: {id}")
#     iou = 0.0
#     for i in range(0, len(cons)):
#         if i == self_id:
#             continue
#         c = cons[i]
#         iou = max(iou, contours_get_iou(cnt, c))
#         # print(f"get_my_iou id: {id}, i: {i}, iou: {iou}")

#     return iou

# def draw_contours_by_iou(img, contours, iou_limit=1.0):
#     id=0
#     labels=0
#     cons = []
    
#     for cnt in contours:
#         cons.append(cnt)

#     for cnt in contours:
#         # area = cv2.contourArea(cnt)
#         # ratio = area / min_area
#         # if True:
#         # if 1.5 > ratio and ratio > 0.5:

#         max_iou = get_max_iou(cnt, cons, id)
#         print(f"draw_contours_by_iou id: {id}, max_iou: {max_iou:.2f}")

#         # if iou_limit >= max_iou:
#         if True:
#             x, y, w, h = cv2.boundingRect(cnt)
#             cv2.rectangle(img, (x, y), (x + w, y + h), red, 2)

#             # if labels < 8:
#             if True:
#                 # x, y, w, h = cv2.boundingRect(cnt)
#                 # cv2.putText(img, f"{id}:{cv2.contourArea(cnt)}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, blue, 2)
#                 cv2.putText(img, f"{id}:{max_iou:.2f}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, blue, 2)
#                 labels += 1
#         # else:
#             # print(f"draw_contours_minum_area Contour {id} area: {area}, ratio: {ratio} is too small, not drawn")

#         id=id+1

#     show_image(img, f'draw_contours_by_iou: {max_iou}', 720)


def calculate_contour_iou(cnt1, cnt2):
    """
    計算兩個輪廓的 IOU (Intersection over Union)
    
    Args:
        cnt1: 第一個輪廓
        cnt2: 第二個輪廓
        
    Returns:
        float: IOU 值 (0~1 之間)
    """
    # 建立空白遮罩
    x1, y1, w1, h1 = cv2.boundingRect(cnt1)
    x2, y2, w2, h2 = cv2.boundingRect(cnt2)
    
    # 計算遮罩大小
    xmin = min(x1, x2)
    ymin = min(y1, y2)
    xmax = max(x1 + w1, x2 + w2)
    ymax = max(y1 + h1, y2 + h2)
    
    width = xmax - xmin
    height = ymax - ymin
    
    # 創建遮罩
    mask1 = np.zeros((height, width), dtype=np.uint8)
    mask2 = np.zeros((height, width), dtype=np.uint8)
    
    # 繪製輪廓到遮罩上
    cv2.drawContours(mask1, [cnt1], 0, 255, -1, offset=(-xmin, -ymin))
    cv2.drawContours(mask2, [cnt2], 0, 255, -1, offset=(-xmin, -ymin))
    
    # 計算交集和聯集
    intersection = cv2.bitwise_and(mask1, mask2)
    union = cv2.bitwise_or(mask1, mask2)
    
    # 計算面積
    intersection_area = cv2.countNonZero(intersection)
    union_area = cv2.countNonZero(union)
    
    area1 = cv2.countNonZero(mask1)
    area2 = cv2.countNonZero(mask2)

    # if area1 == 207553 or area2 == 207553:
    #     print(f"calculate_contour_iou: cnt1 area: {area1}, cnt2 area: {area2}, intersection_area: {intersection_area}, union_area: {union_area}")

    if union_area == area1 or union_area == area2:
        return 1.0

    # 計算 IOU
    if union_area == 0:
        return 0.0
    
    iou = intersection_area / union_area
    return iou


def find_parent_by_iou(contours, iou_threshold=0.7):
    """
    使用 IOU 找出可能的父輪廓
    回傳父輪廓的索引列表
    """
    n = len(contours)
    is_parent = [True] * n  # 預設所有輪廓都是父輪廓
    # is_parent = [False] * n  # 預設所有輪廓都是父輪廓
    
    # 比較所有輪廓對
    for i in range(n):
        for j in range(n):
            if i != j:
                # iou = contours_get_iou(contours[i], contours[j])
                iou = calculate_contour_iou(contours[i], contours[j])
                # print(f"Comparing contours {i} and {j}, IOU: {iou:.2f}")
                # 如果兩個輪廓的 IOU 大於閾值，面積較小的為子輪廓
                if iou > iou_threshold:
                    area_i = cv2.contourArea(contours[i])
                    area_j = cv2.contourArea(contours[j])
                    if area_i < area_j:
                        is_parent[i] = False
                    else:
                        is_parent[j] = False
                    # if area_i < area_j:
                    #     is_parent[j] = True
                    # else:
                    #     is_parent[i] = True
    
    # 回傳父輪廓的索引
    return [i for i in range(n) if is_parent[i]]


def draw_contours_by_iou_minum_area(img, paper_dimensions, contours, iou_threshold=0.7, min_area=100):
    # print(f"draw_contours_by_iou_minum_area| paper_dimensions: {paper_dimensions}")
    cons = []
    # papar_width = img.shape[1]
    # papar_height = img.shape[0]
    for i in range(len(contours)):
        cnt = contours[i]
        x, y, w, h = cv2.boundingRect(cnt)
        w_ratio = w / paper_dimensions[2]
        h_ratio = h / paper_dimensions[3]
        area = cv2.contourArea(cnt)
        area_ratio = area / min_area
        # print(f"draw_contours_by_iou: Contour {i}, bounding box: ({x}, {y}, {w}, {h}), ratio: {w/papar_width:.02f} {h/papar_height:.02f}")
        if h_ratio < 0.75 and w_ratio < 0.75 and area_ratio > 0.15:
            cons.append(cnt)

    contours = cons
    # for i in range(len(contours)):
    #     cnt = contours[i]
    #     x, y, w, h = cv2.boundingRect(cnt)
    #     print(f"draw_contours_by_iou: Contour {i}, bounding box: ({x}, {y}, {w}, {h})")

    # 找出父輪廓
    parent_indices = find_parent_by_iou(contours, iou_threshold)
    # print(f"draw_contours_by_iou| Found {len(parent_indices)} parent contours with IOU threshold {iou_threshold}")
    print(f"parent_indices {parent_indices}")

    # 繪製父輪廓
    for id in parent_indices:
        cnt = contours[id]
        x, y, w, h = cv2.boundingRect(cnt)
        cv2.rectangle(img, (x, y), (x + w, y + h), red, 2)
        
        # 顯示輪廓資訊
        area = cv2.contourArea(cnt)
        area_ratio = area / min_area
        # cv2.putText(img, f"{id}:{area:.0f}", (x+1, y - 10+1), cv2.FONT_HERSHEY_SIMPLEX, 0.5, white, 2)
        # cv2.putText(img, f"{id}:{area:.0f}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, blue, 2)
        draw_label(img, f"{id}:{area_ratio:.02f}", x, y-10, color=blue)
        print(f"draw_contours_by_iou_minum_area| Contour {id}, area_ratio {area_ratio:.03f}")

    show_image(img, f'draw_contours_by_iou_minum_area (threshold={iou_threshold} min_area={min_area})', 720)


def get_marker_corners(image):
    arucoDict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_5X5_1000)
    arucoParams = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(arucoDict, arucoParams)

    (corners, ids, rejected) = detector.detectMarkers(image)

    return corners, ids


# x, y, w, h = cv2.boundingRect(cnt)
def contours_get_iou(cnt1, cnt2):
    corners1 = cv2.boundingRect(cnt1)
    corners2 = cv2.boundingRect(cnt2)
    return get_iou(corners1, corners2)


def get_iou(bbox_ai, bbox_gt):
    iou_x = max(bbox_ai[0], bbox_gt[0]) # x
    iou_y = max(bbox_ai[1], bbox_gt[1]) # y
    iou_w = min(bbox_ai[2]+bbox_ai[0], bbox_gt[2]+bbox_gt[0]) - iou_x # w
    iou_w = max(iou_w, 0)
    # print(f'{iou_w=}')
    iou_h = min(bbox_ai[3]+bbox_ai[1], bbox_gt[3]+bbox_gt[1]) - iou_y # h
    iou_h = max(iou_h, 0)
    # print(f'{iou_h=}')

    iou_area = iou_w * iou_h
    # print(f'{iou_area=}')
    all_area = bbox_ai[2]*bbox_ai[3] + bbox_gt[2]*bbox_gt[3] - iou_area
    # print(f'{all_area=}')

    return max(iou_area/all_area, 0)


def get_contours_onpaper(paper_img):
    paper_gray_img = cv2.cvtColor(paper_img, cv2.COLOR_BGR2GRAY)
    # paper_color_img = cv2.cvtColor(paper_img, cv2.CV_32FC1, 1/255.0)
    # show_image(paper_img, f"ID {markerID} paper", 720)
    # paper_img.convertTo(paper_color_img, cv2.CV_32S)

    ret, thresh = cv2.threshold(paper_gray_img, 127, 255, cv2.THRESH_BINARY)
    # show_image(paper_img, f"ID {markerID} paper thresh", 720)
    # contours, hierarchys = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # contours, hierarchys = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    # contours, hierarchys = cv2.findContours(thresh, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    # contours, hierarchys = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    # contours, hierarchys = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # contours, hierarchys = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_TC89_L1)
    # contours, hierarchys = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_TC89_KCOS)

    # return contours, hierarchys, True

    # paper_gray_img_32bit = paper_gray_img.astype(np.int32)
    thresh_32bit = thresh.astype(np.int32)
    # contours, hierarchys = cv2.findContours(thresh_32bit, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    contours, hierarchys = cv2.findContours(thresh_32bit, cv2.RETR_FLOODFILL, cv2.CHAIN_APPROX_SIMPLE)

    return contours, hierarchys, False


def get_contours_tree(paper_img):
    gray = cv2.cvtColor(paper_img, cv2.COLOR_BGR2GRAY)
    # show_image(gray, f"gray {cv2.countNonZero(gray)}", 720)

    # blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    # sharp = sharpen(gray, 100)
    # show_image(sharp, f"sharp", 720)

    # ret, thresh = cv2.threshold(sharp, 127, 255, cv2.THRESH_BINARY)
    # ret, thresh = cv2.threshold(gray, 165, 255, cv2.THRESH_BINARY)
    # show_image(thresh, f"thresh {cv2.countNonZero(thresh)}", 720)
    # th2 = cv2.adaptiveThreshold(gray,255,cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY,11,2)
    # show_image(th2, f"MEAN thresh {cv2.countNonZero(th2)}", 720)
    th3 = cv2.adaptiveThreshold(gray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,11,2)
    show_image(th3, f"GAUSSIAN thresh {cv2.countNonZero(th3)}", 720)

    contours, hierarchys = cv2.findContours(th3, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    return contours, hierarchys, True


def get_contours_blur_tree(paper_img):
    gray = cv2.cvtColor(paper_img, cv2.COLOR_BGR2GRAY)

    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    ret, thresh = cv2.threshold(blurred, 127, 255, cv2.THRESH_BINARY)

    contours, hierarchys = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    return contours, hierarchys, True


def get_contours_sharpen_tree(paper_img):
    gray = cv2.cvtColor(paper_img, cv2.COLOR_BGR2GRAY)
    show_image(gray, f"gray", 720)

    # blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    sharp = sharpen(gray, 100)
    show_image(sharp, f"sharp", 720)

    # ret, thresh = cv2.threshold(sharp, 127, 255, cv2.THRESH_BINARY)
    ret, thresh = cv2.threshold(sharp, 160, 255, cv2.THRESH_BINARY)
    show_image(thresh, f"thresh", 720)

    contours, hierarchys = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    return contours, hierarchys, True


def get_contours_blur_floodfill(paper_img):
    gray = cv2.cvtColor(paper_img, cv2.COLOR_BGR2GRAY)

    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    ret, thresh = cv2.threshold(blurred, 127, 255, cv2.THRESH_BINARY)

    thresh_32bit = thresh.astype(np.int32)

    contours, hierarchys = cv2.findContours(thresh_32bit, cv2.RETR_FLOODFILL, cv2.CHAIN_APPROX_SIMPLE)

    return contours, hierarchys, False


def get_contours_sharpen_floodfill(paper_img):
    gray = cv2.cvtColor(paper_img, cv2.COLOR_BGR2GRAY)

    # blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    sharp = sharpen(gray, 100)

    ret, thresh = cv2.threshold(sharp, 127, 255, cv2.THRESH_BINARY)

    thresh_32bit = thresh.astype(np.int32)

    contours, hierarchys = cv2.findContours(thresh_32bit, cv2.RETR_FLOODFILL, cv2.CHAIN_APPROX_SIMPLE)

    return contours, hierarchys, False


def get_corners_bounding_box(paper_corners):
    """
    從四個角點取得邊界框
    
    Args:
        paper_corners: 紙張的四個角點座標 [top_left, top_right, bottom_right, bottom_left]
        
    Returns:
        tuple: (x, y, w, h) 邊界框的 x,y 座標及寬度和高度
    """
    # 將角點轉換為 numpy array 以便運算
    corners = np.array(paper_corners)
    
    # 取得最小和最大的 x,y 座標
    min_x = np.min(corners[:, 0])
    max_x = np.max(corners[:, 0])
    min_y = np.min(corners[:, 1])
    max_y = np.max(corners[:, 1])
    
    # 計算寬度和高度
    width = max_x - min_x
    height = max_y - min_y
    
    return (int(min_x), int(min_y), int(width), int(height))


def sharpen(img, sigma=100):    
    # sigma = 5、15、25
    blur_img = cv2.GaussianBlur(img, (0, 0), sigma)
    usm = cv2.addWeighted(img, 1.5, blur_img, -0.5, 0)
    
    return usm


def main():
    # raw_image = cv2.imread("./data/images/3c115d9c-8839-4ae8-9f3f-96d514dd5831.png")
    # raw_image = cv2.imread('./data/images/4b76e214-5bef-4adc-981f-ad6119932306.png')
    # raw_image = cv2.imread('./data/images/468070fc-23e0-4034-90ae-ca86b39935b7.png')
    # raw_image = cv2.imread('./data/images/c07d7f1c-581c-4b12-9105-9a131705f785.png')
    raw_image = cv2.imread('./data/images/482585764_1455590368759521_6647519779772489171_n.png')
    # raw_image = cv2.imread('./data/images/490238254_1842446786580514_8292045078609051837_n.png') #??
    # raw_image = cv2.imread('./data/images/490752727_3922194774688090_1916180895651358198_n.png')
    # raw_image = cv2.imread('./data/images/490797075_9500783306706076_2074756401633110199_n.png')
    # raw_image = cv2.imread('./data/images/490986346_1041000924540372_5860720053675956248_n.png')
    # raw_image = cv2.imread('./data/images/491008900_1819195295531383_8823035513900614833_n.png')

    image=undistort(raw_image)
    corners, ids = get_marker_corners(image)
    if len(corners) == 0:
        image=raw_image.copy()
        corners, ids = get_marker_corners(image)

    image2=image.copy()
    image3=image.copy()
    image4=image.copy()
    
    if len(corners) > 0:
        ids = ids.flatten()
        for markerCorner, markerID in zip(corners, ids):
            corners = markerCorner.reshape((4, 2))
            # (topLeft, topRight, bottomRight, bottomLeft) = corners

            paper_corners = get_paper_corners(corners, image.shape)

            # mask_img = get_mask(image.shape, corners.astype(int))
            mask_img = get_mask(image.shape, np.array(paper_corners).astype(int))
            mask_img = cv2.cvtColor(mask_img, cv2.COLOR_BGR2GRAY)
            # show_image(mask_img, f"ID {markerID} mask", 720)

            paper_img = cv2.bitwise_and(image, image, mask=mask_img)

            contours, hierarchys, hasParents = get_contours_onpaper(paper_img)

            area = get_corners_area(corners)
            # print(f"Marker ID: {markerID}, Area: {area}")
            
            draw_all_contours(image, contours)
            draw_contours_minum_area(image2, contours, area)
            if hasParents:
                draw_only_parent_contours(image3, contours, hierarchys)
                draw_only_parent_contours_minum_area(image4, contours, hierarchys, area)


    # show_image(raw_image, 'Raw Image', 720)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def main2():
    # raw_image = cv2.imread("../../assets/item_template_images/coin.png")
    # raw_image = cv2.imread("../../assets/item_template_images/compass.png")
    # raw_image = cv2.imread("../../assets/item_template_images/coral.png")
    # raw_image = cv2.imread("../../assets/item_template_images/crystal.png")
    # raw_image = cv2.imread("../../assets/item_template_images/diamond.png")
    # raw_image = cv2.imread("../../assets/item_template_images/emerald.png")
    # raw_image = cv2.imread("../../assets/item_template_images/fossil.png")
    # raw_image = cv2.imread("../../assets/item_template_images/key.png")
    # raw_image = cv2.imread("../../assets/item_template_images/letter.png")
    # raw_image = cv2.imread("../../assets/item_template_images/shell.png")
    # raw_image = cv2.imread("../../assets/item_template_images/treasure_box.png")
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
    
    # image=undistort(raw_image)
    image=raw_image.copy()

    corners, ids = get_marker_corners(image)
    if len(corners) == 0:
        image=raw_image.copy()
        corners, ids = get_marker_corners(image)

    image2=image.copy()
    image3=image.copy()
    image4=image.copy()
    image5=image.copy()

    if len(corners) > 0:
        ids = ids.flatten()
        for markerCorner, markerID in zip(corners, ids):
            corners = markerCorner.reshape((4, 2))
            # (topLeft, topRight, bottomRight, bottomLeft) = corners

            paper_corners = get_paper_corners(corners, image.shape)
            paper_dimensions = get_corners_bounding_box(paper_corners)
    
            mask_img = get_mask(image.shape, np.array(paper_corners).astype(int))
            mask_img = cv2.cvtColor(mask_img, cv2.COLOR_BGR2GRAY)
            # show_image(mask_img, f"ID {markerID} mask", 720)

            paper_img = cv2.bitwise_and(image, image, mask=mask_img)
            # show_image(paper_img, f"ID {markerID} paper_img", 720)

            # contours, hierarchys, hasParents = get_contours_onpaper(paper_img)
            contours, hierarchys, hasParents = get_contours_tree(paper_img)
            # contours, hierarchys, hasParents = get_contours_blur_tree(paper_img)
            # contours, hierarchys, hasParents = get_contours_sharpen_tree(paper_img)
            # contours, hierarchys, hasParents = get_contours_blur_floodfill(paper_img)
            # contours, hierarchys, hasParents = get_contours_sharpen_floodfill(paper_img)

            area = get_corners_area(corners)
            
            draw_all_contours(image, contours)
            draw_contours_minum_area(image2, contours, area)
            draw_contours_by_iou_minum_area(image3, paper_dimensions, contours, 0.7, area)
            if hasParents:
                draw_only_parent_contours(image4, contours, hierarchys)
                draw_only_parent_contours_minum_area(image5, contours, hierarchys, area)

    else:
        paper_img = image.copy()
        paper_dimensions = (0, 0, paper_img.shape[1], paper_img.shape[0])

        # contours, hierarchys, hasParents = get_contours_onpaper(paper_img)
        contours, hierarchys, hasParents = get_contours_tree(paper_img)

        area = paper_img.shape[0] * paper_img.shape[1] / 4
        
        draw_all_contours(image, contours)
        draw_contours_minum_area(image2, contours, area)
        draw_contours_by_iou_minum_area(image3, paper_dimensions, contours, 0.7, area)
        if hasParents:
            draw_only_parent_contours(image4, contours, hierarchys)
            draw_only_parent_contours_minum_area(image5, contours, hierarchys, area)
    
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # main()
    main2()
