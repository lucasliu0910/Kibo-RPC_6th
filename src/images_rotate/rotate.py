import os
from PIL import Image

# 設定路徑 - 使用原始字串 r 前綴
# base_folder = r"/Users/lucas/Documents/GitHub/Kibo-RPC_6th/assets"  # 輸入圖片路徑
base_folder = r"../../assets"  # 輸入圖片路徑
image_folder = os.path.join(base_folder, "item_template_images")

# 設定輸出路徑 - 用於儲存處理後的圖片
# output_base = r"/Users/lucas/Documents/GitHub/Kibo-RPC_6th/src/images_rotate/rotated_images"  # 輸出圖片路徑
output_base = r"./rotated_images"  # 輸出圖片路徑

# 定義物品類型列表
image_types = ["coin", "compass", "coral", "crystal", "diamond", "emerald", "fossil", "key", "letter", "shell", "treasure_box"]

def setup_folders():
    """創建必要的資料夾"""
    # 確保輸入資料夾存在
    os.makedirs(image_folder, exist_ok=True)
    
    # 確保輸出基礎資料夾存在
    os.makedirs(output_base, exist_ok=True)
    
    # 為每種物品類型創建資料夾
    for image_type in image_types:
        item_folder = os.path.join(output_base, image_type)
        os.makedirs(item_folder, exist_ok=True)

def create_background_image(size):
    """創建白色背景圖片"""
    return Image.new('RGBA', size, (255, 255, 255, 255))

def resize_image(image, scale, original_size):
    """縮放圖片到指定比例並放置在白色背景上"""
    # 計算縮放後的新尺寸
    width, height = image.size
    new_width = int(width * scale)
    new_height = int(height * scale)
    
    # 縮放圖片
    resized_image = image.resize((new_width, new_height), Image.LANCZOS)
    
    # 創建與原始圖片相同大小的白色背景
    background = create_background_image(original_size)
    
    # 計算居中位置
    x = (original_size[0] - new_width) // 2
    y = (original_size[1] - new_height) // 2
    
    # 將縮放後的圖片貼到背景上
    background.paste(resized_image, (x, y), resized_image)
    
    return background

def rotate_and_save(image, image_name, scale, degree):
    """旋轉指定角度的圖片並保存"""
    output_folder = os.path.join(output_base, image_name)
    scale_percent = int(scale * 100)
    
    rotated_image = image.rotate(degree, expand=True, fillcolor=(0, 0, 0, 0))
    
    # 為每個角度生成5張圖片
    for k in range(1, 6):
        output_path = os.path.join(output_folder, f"{image_name}_{scale_percent}p_{degree}_{k}.png")
        rotated_image.save(output_path)

def process_image(image_name):
    """處理單個圖片的所有操作"""
    try:
        image_path = os.path.join(image_folder, f"{image_name}.png")
        img = Image.open(image_path).convert("RGBA")
        original_image = img.resize((512,512), Image.LANCZOS) #TensorFlow Lite image input size
        original_size = original_image.size
        print(f"處理圖片: {image_name}.png (原始尺寸: {original_size[0]}x{original_size[1]})")
        
        # 縮放圖片到不同比例
        image_30 = resize_image(original_image, 0.3, original_size)
        image_50 = resize_image(original_image, 0.5, original_size)
        image_80 = resize_image(original_image, 0.8, original_size)
        image_100 = original_image  # 原始尺寸 (100%)
        
        # 對各種比例的圖片進行旋轉處理
        scales = {1.0: image_100, 0.3: image_30, 0.5: image_50, 0.8: image_80}
        
        for scale, image in scales.items():
            scale_percent = int(scale * 100)
            print(f"  開始處理 {image_name} 的 {scale_percent}% 版本旋轉...")
            
            for degree in range(0, 331, 30):
                rotate_and_save(image, image_name, scale, degree)
        
        print(f"完成 {image_name} 的所有縮放和旋轉")
        
    except Exception as e:
        print(f"處理 {image_name} 時發生錯誤: {e}")

def main():
    """主函數"""
    # 設置資料夾
    setup_folders()
    
    # 處理每一個圖片
    for image_name in image_types:
        process_image(image_name)
    
    print("所有圖片處理完成！")

if __name__ == "__main__":
    main()