import cv2
import numpy as np
import math
import os
from typing import Tuple, Optional, Dict, Any

class PaperCropper:
    def __init__(self):
        self.ar_dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_5X5_1000)
        self.detector_params = cv2.aruco.DetectorParameters()
        self._opencv_version = 'new'
        
        self.area_tag_id = {
            "area1": 101,
            "area2": 102,
            "area3": 103,
            "area4": 104
        }
        
        self.crop_img_counter = 0
        
        self.camera_matrix = np.array([
            [523.105750, 0, 635.434258],
            [0, 534.765913, 500.335102],
            [0, 0, 1]
        ], dtype=np.float32)
        
        self.dist_coeffs = np.array([-0.164787, 0.020375, -0.001572, -0.000369, 0.000000], dtype=np.float32)
        
    def undistort(self, image: np.ndarray) -> np.ndarray:
        h, w = image.shape[:2]
        new_camera_matrix, roi = cv2.getOptimalNewCameraMatrix(
            self.camera_matrix, self.dist_coeffs, (w, h), 1, (w, h)
        )
        
        undistorted = cv2.undistort(image, self.camera_matrix, self.dist_coeffs, 
                                   None, new_camera_matrix)
        return undistorted
    
    def save_debug_image(self, image: np.ndarray, filename: str):
        debug_dir = "debug_images"
        if not os.path.exists(debug_dir):
            os.makedirs(debug_dir)
        
        filepath = os.path.join(debug_dir, filename)
        cv2.imwrite(filepath, image)
        print(f"Debug image saved: {filepath}")
    
    def crop_paper(self, input_image: np.ndarray, area: str) -> np.ndarray:
        undistorted_img = self.undistort(input_image)
        
        if len(undistorted_img.shape) > 2 and undistorted_img.shape[2] > 1:
            gray_img = cv2.cvtColor(undistorted_img, cv2.COLOR_BGR2GRAY)
        else:
            gray_img = undistorted_img.copy()
        
        self.detector_params.minMarkerPerimeterRate = 0.01
        self.detector_params.maxMarkerPerimeterRate = 0.5

        detector = cv2.aruco.ArucoDetector(self.ar_dictionary, self.detector_params)
        corners, ids, _ = detector.detectMarkers(gray_img)
        
        
        
        if area not in self.area_tag_id:
            print(f"Unknown area: {area}")
            return self._default_crop(gray_img, area)
        
        target_id = self.area_tag_id[area]
        found_target_marker = False
        marker_index = -1
        
        if ids is not None and len(ids) > 0:
            for i, marker_id in enumerate(ids.flatten()):
                if marker_id == target_id:
                    marker_index = i
                    found_target_marker = True
                    break
        
        if found_target_marker:
            corner = corners[marker_index][0]
            
            top_left = corner[0]
            top_right = corner[1]
            bottom_right = corner[2]
            bottom_left = corner[3]
            
            paper_width_ratio = 27.0 / 4.5
            paper_height_ratio = 15.0 / 4.5
            
            x_vec = top_right - top_left
            y_vec = bottom_left - top_left
            
            x_vec_length = np.linalg.norm(x_vec)
            y_vec_length = np.linalg.norm(y_vec)
            
            x_vec_norm = x_vec / x_vec_length
            y_vec_norm = y_vec / y_vec_length
            
            marker_center = np.mean(corner, axis=0)
            
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
            end_x = min(gray_img.shape[1] - 1, int(np.ceil(max_x)))
            end_y = min(gray_img.shape[0] - 1, int(np.ceil(max_y)))
            
            width = end_x - start_x
            height = end_y - start_y
            
            if width <= 0 or height <= 0:
                print(f"Wrong cropping area, use default. Area: {area}")
                return self._default_crop(gray_img, area)
            
            cropped_img = gray_img[start_y:end_y, start_x:end_x]
            
            if self.crop_img_counter < 10:
                debug_img = undistorted_img.copy()
                if len(debug_img.shape) == 2:
                    debug_img = cv2.cvtColor(debug_img, cv2.COLOR_GRAY2BGR)
                
                cv2.circle(debug_img, tuple(top_left.astype(int)), 5, (255, 0, 0), 2)
                cv2.circle(debug_img, tuple(top_right.astype(int)), 5, (0, 255, 0), 2)
                cv2.circle(debug_img, tuple(bottom_right.astype(int)), 5, (0, 0, 255), 2)
                cv2.circle(debug_img, tuple(bottom_left.astype(int)), 5, (255, 255, 0), 2)
                
                cv2.circle(debug_img, tuple(paper_top_left.astype(int)), 8, (255, 0, 255), 2)
                cv2.circle(debug_img, tuple(paper_top_right.astype(int)), 8, (255, 0, 255), 2)
                cv2.circle(debug_img, tuple(paper_bottom_right.astype(int)), 8, (255, 0, 255), 2)
                cv2.circle(debug_img, tuple(paper_bottom_left.astype(int)), 8, (255, 0, 255), 2)
                
                cv2.rectangle(debug_img, (start_x, start_y), (end_x, end_y), (0, 255, 255), 2)
                
                self.save_debug_image(debug_img, f"paper_debug_{area}_{self.crop_img_counter}.jpg")
            
            self.save_debug_image(cropped_img, f"paper_crop_{area}_{self.crop_img_counter}.jpg")
            self.crop_img_counter += 1
            
            return cropped_img
            
        else:
            print(f"Unable to find tag of '{area}' (ID: {target_id})")
            return self._default_crop(gray_img, area)
    
    def _default_crop(self, gray_img: np.ndarray, area: str) -> np.ndarray:
        img_height, img_width = gray_img.shape
        
        width = int(img_width * 0.8)
        height = int(width * 15.0 / 27.0)
        
        start_x = int(img_width * 0.1)
        start_y = (img_height - height) // 2
        
        end_x = min(start_x + width, img_width)
        end_y = min(start_y + height, img_height)
        
        cropped_img = gray_img[start_y:end_y, start_x:end_x]
        
        self.save_debug_image(cropped_img, f"paper_crop_{area}_{self.crop_img_counter}.jpg")
        self.crop_img_counter += 1
        
        return cropped_img


def main():
    cropper = PaperCropper()
    
    test_image_path = "Sample4.jpg"
    
    if not os.path.exists(test_image_path):
        print(f"Image not exists: {test_image_path}")
        return
    
    image = cv2.imread(test_image_path)
    if image is None:
        print(f"Failed to read image: {test_image_path}")
        return
    
    print(f"Read image: {test_image_path}")
    print(f"Img size: {image.shape}")
    
    areas = ["area1", "area2", "area3", "area4"]
    
    for area in areas:
        print(f"\nProcessing area: {area}")
        try:
            cropped = cropper.crop_paper(image, area)
            print(f"Cropping finished, size: {cropped.shape}")
        except Exception as e:
            print(f"Failed to crop area '{area}': {e}")
    
    print("\nComplete!")


if __name__ == "__main__":
    main()
