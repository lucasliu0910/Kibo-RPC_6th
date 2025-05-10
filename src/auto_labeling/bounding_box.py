# python labeling.py -i image.png -t 200 -o result.txt

import os
import sys
import argparse
import numpy as np
from PIL import Image
from typing import Tuple, Dict


def analyze_bw_image(image_path: str, threshold: int = 255) -> Dict[str, int]:
    """
    分析黑白圖片，找出黑色區域的邊界坐標和尺寸
    
    參數:
        image_path: 圖片檔案路徑
        threshold: 像素值閾值，小於此值被視為黑色 (預設255表示非純白即視為黑色)
        
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
    # 解析命令列參數
    parser = argparse.ArgumentParser(description='黑白圖片邊界檢測工具')
    parser.add_argument('--input', '-i', required=True, help='輸入圖片檔案路徑')
    parser.add_argument('--threshold', '-t', type=int, default=255, 
                        help='像素閾值，小於此值被視為黑色 (預設255，表示非純白即為黑色)')
    parser.add_argument('--output', '-o', default=None, help='輸出結果檔案路徑 (可選)')
    args = parser.parse_args()
    
    # 分析圖片
    result = analyze_bw_image(args.input, args.threshold)
    
    # 輸出結果
    print("\n分析結果:")
    print(f"x: {result['x']}  # 最左邊的黑色pixel的x座標")
    print(f"y: {result['y']}  # 最上面的黑色pixel的y座標")
    print(f"width: {result['width']}  # 黑色區域的寬度")
    print(f"height: {result['height']}  # 黑色區域的高度")
    
    # 保存結果 (如果指定了輸出檔案)
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(f"x: {result['x']}\n")
            f.write(f"y: {result['y']}\n")
            f.write(f"width: {result['width']}\n")
            f.write(f"height: {result['height']}\n")
        print(f"\n結果已保存至: {args.output}")


if __name__ == "__main__":
    main()