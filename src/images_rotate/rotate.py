import os
from PIL import Image

# 設定本地路徑，請根據您的本地資料夾結構調整
base_folder = "D:\\Users\\lucas\\LocalFiles\\Github\\Kibo-RPC_6th\\assets"  # 替換為您電腦上的資料夾路徑
image_folder = os.path.join(base_folder, "item_template_images")

# 確保輸出資料夾存在
os.makedirs(image_folder, exist_ok=True)
os.makedirs(os.path.join(base_folder, "rotated_images"), exist_ok=True)

# 為所有圖片生成不同角度的旋轉版本
image_types = ["coin", "compass", "coral", "crystal", "diamond", 
               "emerald", "fossil", "key", "letter", "shell","treasure_box"]

# 主要圖片旋轉處理
for i in range(0, 10):
    image_name = image_types[i]
    image_path = os.path.join(image_folder, f"{image_name}.png")
    image = Image.open(image_path).convert("RGBA")
    
    print(f"處理圖片: {image_name}.png")
    
    # 每5度旋轉一次，從0度到355度
    for degree in range(0, 331, 30):
        # 旋轉圖片
        rotated_image = image.rotate(degree, expand=True, fillcolor=(0, 0, 0, 0))
        
        # 為每個角度生成5張圖片
        for k in range(1, 6):
            output_path = os.path.join(base_folder, "rotated_images", f"{image_name}_{degree}_{k}.png")
            rotated_image.save(output_path)
    
    print(f"完成 {image_name} 的所有旋轉")

# 生成原始圖片的副本
for i in range(0, 10):
    image_name = image_types[i]
    image_path = os.path.join(image_folder, f"{image_name}.png")
    image = Image.open(image_path)
    
    # 旋轉圖片(0度，等同於原圖)
    rotated_image = image.rotate(0, expand=True)
    
    # 為每個原始圖片生成5個副本
    for k in range(1, 6):
        output_path = os.path.join(base_folder, f"{image_name}_{k}.png")
        rotated_image.save(output_path)
    
    print(f"已為 {image_name} 生成5個副本")