import os
import sys
import traceback
from io import BytesIO
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


# 在這裡設定輸入圖片路徑 - 使用r前綴的原始字串避免Unicode轉義問題
IMAGE_PATH = r"D:/Users/lucas/LocalFiles/Github/Kibo-RPC_6th/src/auto_labeling/examples/coin_30p_30_1.png"
# 閾值設定 (小於此值的像素被視為黑色)
THRESHOLD = 150
# 是否輸出結果到文件
OUTPUT_TO_FILE = True
# 輸出文件路徑
OUTPUT_PATH = r"D:/Users/lucas/LocalFiles/Github/Kibo-RPC_6th/src/auto_labeling/examples/bounding_box_result.txt"
# 調試模式 - 啟用會輸出更多信息
DEBUG_MODE = True


def analyze_image(image_path, threshold=200):
    """
    分析圖片，找出黑色區域的邊界坐標和尺寸
    支援多種圖片格式，包括PNG
    """
    try:
        print(f"嘗試讀取圖片: {image_path}")
        if not os.path.exists(image_path):
            print(f"錯誤: 找不到圖片 '{image_path}'")
            return {
                "error": "找不到圖片",
                "x": -1,
                "y": -1,
                "width": 0,
                "height": 0
            }
        
        # 獲取檔案大小
        file_size = os.path.getsize(image_path)
        print(f"圖片檔案大小: {file_size} 字節")
        
        # 檢查PIL庫是否可用
        if not PIL_AVAILABLE:
            print("錯誤: 處理PNG圖片需要PIL庫。請使用以下命令安裝:")
            print("pip install pillow")
            return {
                "error": "缺少PIL庫，無法處理PNG圖片",
                "x": -1,
                "y": -1,
                "width": 0,
                "height": 0
            }
        
        # 使用PIL庫讀取圖片
        try:
            img = Image.open(image_path)
            print(f"已成功開啟圖片。格式: {img.format}, 尺寸: {img.size}, 模式: {img.mode}")
            
            # 轉換為灰度圖
            if img.mode != 'L':
                print(f"將圖片從 {img.mode} 模式轉換為灰度模式")
                img = img.convert('L')
            
            width, height = img.size
            
            # 獲取像素數據
            pixels = list(img.getdata())
            pixels = [pixels[i * width:(i + 1) * width] for i in range(height)]
            
            # 如果有透明通道，單獨獲取透明度資訊
            has_alpha = 'A' in img.mode
            alpha_mask = None
            
            if has_alpha:
                print("圖片包含透明通道")
                alpha_img = Image.open(image_path)
                # 提取透明通道
                _, _, _, alpha = alpha_img.split()
                alpha_data = list(alpha.getdata())
                alpha_mask = [alpha_data[i * width:(i + 1) * width] for i in range(height)]
            
            # 輸出像素值分佈情況
            if DEBUG_MODE:
                pixel_values = [p for row in pixels for p in row]
                min_val = min(pixel_values)
                max_val = max(pixel_values)
                avg_val = sum(pixel_values) / len(pixel_values)
                print(f"像素值範圍: {min_val} - {max_val}, 平均值: {avg_val:.2f}")
                
                # 統計像素值分佈
                value_counts = {}
                for val in pixel_values:
                    if val in value_counts:
                        value_counts[val] += 1
                    else:
                        value_counts[val] = 1
                
                print("像素值分佈 (取樣):")
                sorted_values = sorted(value_counts.keys())
                for i, val in enumerate(sorted_values):
                    if i % 10 == 0 or i == len(sorted_values) - 1:  # 只顯示每10個值和最後一個值
                        count = value_counts[val]
                        percentage = count / len(pixel_values) * 100
                        print(f"  像素值 {val}: {count} 個像素 ({percentage:.2f}%)")
            
            # 初始化邊界值
            min_x, min_y = width, height
            max_x, max_y = -1, -1
            
            # 計算邊界
            black_pixel_count = 0
            for y in range(height):
                for x in range(width):
                    # 檢查像素是否透明
                    is_transparent = False
                    if alpha_mask:
                        is_transparent = alpha_mask[y][x] == 0
                    
                    # 只考慮非透明且像素值小於閾值的像素為黑色
                    if not is_transparent and pixels[y][x] < threshold:
                        black_pixel_count += 1
                        min_x = min(min_x, x)
                        min_y = min(min_y, y)
                        max_x = max(max_x, x)
                        max_y = max(max_y, y)
                        
                        # 在調試模式下輸出前10個被判定為黑色的像素
                        if DEBUG_MODE and black_pixel_count <= 10:
                            print(f"找到黑色像素 #{black_pixel_count}: 位置({x},{y}), 值={pixels[y][x]}")
            
            print(f"找到 {black_pixel_count} 個黑色像素")
            
            # 如果沒有找到黑色像素
            if black_pixel_count == 0 or min_x > max_x or min_y > max_y:
                print(f"警告：使用閾值 {threshold} 未找到黑色像素")
                
                # 嘗試採用自適應閾值
                if DEBUG_MODE:
                    print("嘗試採用自適應閾值...")
                    adaptive_threshold = 240  # 嘗試一個更高的閾值
                    print(f"自適應閾值: {adaptive_threshold}")
                    
                    # 使用自適應閾值重新檢測
                    min_x, min_y = width, height
                    max_x, max_y = -1, -1
                    black_pixel_count = 0
                    
                    for y in range(height):
                        for x in range(width):
                            is_transparent = False
                            if alpha_mask:
                                is_transparent = alpha_mask[y][x] == 0
                            
                            if not is_transparent and pixels[y][x] < adaptive_threshold:
                                black_pixel_count += 1
                                min_x = min(min_x, x)
                                min_y = min(min_y, y)
                                max_x = max(max_x, x)
                                max_y = max(max_y, y)
                    
                    print(f"使用自適應閾值 {adaptive_threshold} 找到 {black_pixel_count} 個黑色像素")
                    
                    if black_pixel_count > 0:
                        print(f"自適應邊界坐標: 左({min_x}), 上({min_y}), 右({max_x}), 下({max_y})")
                        width = max_x - min_x + 1
                        height = max_y - min_y + 1
                        return {
                            "x": min_x,
                            "y": min_y,
                            "width": width,
                            "height": height,
                            "note": f"使用自適應閾值 {adaptive_threshold}"
                        }
                
                return {
                    "error": "未找到黑色像素",
                    "x": -1,
                    "y": -1,
                    "width": 0,
                    "height": 0
                }
            
            print(f"邊界坐標: 左({min_x}), 上({min_y}), 右({max_x}), 下({max_y})")
            
            # 計算寬度和高度
            width = max_x - min_x + 1
            height = max_y - min_y + 1
            
            result = {
                "x": min_x,
                "y": min_y,
                "width": width,
                "height": height
            }
            
            print(f"計算結果: x={min_x}, y={min_y}, width={width}, height={height}")
            
            return result
            
        except Exception as img_error:
            print(f"處理圖片時出錯: {str(img_error)}")
            traceback.print_exc()
            return {
                "error": f"處理圖片時出錯: {str(img_error)}",
                "x": -1,
                "y": -1,
                "width": 0,
                "height": 0
            }
            
    except Exception as e:
        print(f"分析圖片時出錯: {str(e)}")
        print("詳細錯誤訊息:")
        traceback.print_exc()
        return {
            "error": str(e),
            "x": -1,
            "y": -1,
            "width": 0,
            "height": 0
        }


def main():
    """主程式入口點"""
    try:
        print("=== 邊界框提取器開始執行（PNG 支援版） ===")
        print(f"Python版本: {sys.version}")
        print(f"工作目錄: {os.getcwd()}")
        print(f"圖片路徑: {IMAGE_PATH}")
        print(f"閾值設定: {THRESHOLD}")
        print(f"調試模式: {'開啟' if DEBUG_MODE else '關閉'}")
        print(f"PIL庫: {'可用' if PIL_AVAILABLE else '不可用'}")
        
        # 分析圖片
        result = analyze_image(IMAGE_PATH, THRESHOLD)
        
        # 輸出結果
        print("\n=== 最終分析結果 ===")
        if "error" in result and result["error"]:
            print(f"錯誤: {result['error']}")
        print(f"x: {result['x']}  # 最左邊的黑色pixel的x座標")
        print(f"y: {result['y']}  # 最上面的黑色pixel的y座標")
        print(f"width: {result['width']}  # 黑色區域的寬度")
        print(f"height: {result['height']}  # 黑色區域的高度")
        if "note" in result:
            print(f"注意: {result['note']}")
        
        # 保存結果至文件
        if OUTPUT_TO_FILE:
            try:
                with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
                    f.write(f"x: {result['x']}\n")
                    f.write(f"y: {result['y']}\n")
                    f.write(f"width: {result['width']}\n")
                    f.write(f"height: {result['height']}\n")
                    if "note" in result:
                        f.write(f"note: {result['note']}\n")
                print(f"\n結果已保存至: {OUTPUT_PATH}")
            except Exception as e:
                print(f"寫入結果檔案時出錯: {str(e)}")
        
        print("=== 程式執行完畢 ===")
        
        # 保持視窗開啟直到按下任意鍵 (Windows系統)
        if os.name == 'nt':  # Windows
            print("\n按下Enter鍵結束...")
            input()
    
    except Exception as e:
        print(f"主程式執行時出錯: {str(e)}")
        print("詳細錯誤訊息:")
        traceback.print_exc()
        
        if os.name == 'nt':  # Windows
            print("\n按下Enter鍵結束...")
            input()


if __name__ == "__main__":
    main()