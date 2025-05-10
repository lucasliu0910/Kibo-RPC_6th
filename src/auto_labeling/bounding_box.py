import os
import sys
import numpy as np
from PIL import Image
from typing import Dict


# 在這裡設定輸入圖片路徑
IMAGE_PATH = "D:\\Users\\lucas\\LocalFiles\\Github\\Kibo-RPC_6th\\src\\auto_labeling\\examples\\coin_30p_30_1.png"  # 請將這裡改為您實際的圖片路徑
# 閾值設定 (小於此值的像素被視為黑色，預設255表示任何非純白都視為黑色)
THRESHOLD = 255


def analyze_bw_image(image_path: str, threshold: int = 255) -> Dict[str, int]:
    """
    分析黑白圖片，找出黑色區域的邊界坐標和尺寸
    
    參數:
        image_path: 圖片檔案路徑
        threshold: 像素值閾值，小於此值被視為黑色
        
    回傳:
        包含x, y, width, height的字典
    """
    try:
        # 載入圖片
        img = Image.open(image_path).convert('L')  # 轉換為灰度圖
        img_array = np.array(img)
        
        # 找出所有非白色(黑色)的像素
        black_pixels = np.where(img_array < threshold)
        
        # 如果沒有找到黑色像素
        if len(black_pixels[0]) == 0 or len(black_pixels[1]) == 0:
            print("警告：圖片中沒有找到黑色像素")
            return {
                "x": -1,
                "y": -1,
                "width": 0,
                "height": 0
            }
            
        # 找出邊界
        min_y = int(np.min(black_pixels[0]))  # 最上面的黑色pixel的y座標
        max_y = int(np.max(black_pixels[0]))  # 最下面的黑色pixel的y座標
        min_x = int(np.min(black_pixels[1]))  # 最左邊的黑色pixel的x座標
        max_x = int(np.max(black_pixels[1]))  # 最右邊的黑色pixel的x座標
        
        # 計算寬度和高度
        width = max_x - min_x + 1
        height = max_y - min_y + 1
        
        result = {
            "x": min_x,
            "y": min_y,
            "width": width,
            "height": height
        }
        
        return result
        
    except Exception as e:
        print(f"分析圖片時出錯: {e}")
        return {
            "x": -1,
            "y": -1,
            "width": 0,
            "height": 0
        }


def main():
    """主程式入口點"""
    print(f"正在分析圖片: {IMAGE_PATH}")
    print(f"閾值設定: {THRESHOLD} (小於此值的像素被視為黑色)")
    
    # 檢查檔案是否存在
    if not os.path.exists(IMAGE_PATH):
        print(f"錯誤: 找不到圖片 '{IMAGE_PATH}'")
        return
    
    # 分析圖片
    result = analyze_bw_image(IMAGE_PATH, THRESHOLD)
    
    # 輸出結果
    print("\n分析結果:")
    print(f"x: {result['x']}  # 最左邊的黑色pixel的x座標")
    print(f"y: {result['y']}  # 最上面的黑色pixel的y座標")
    print(f"width: {result['width']}  # 黑色區域的寬度")
    print(f"height: {result['height']}  # 黑色區域的高度")
    
    # 保持視窗開啟直到按下任意鍵 (Windows系統)
    if os.name == 'nt':  # Windows
        print("\n按下任意鍵結束...")
        os.system('pause')


if __name__ == "__main__":
    main()