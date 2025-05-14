import os
from PIL import Image

def list_files_in_directory(directory):
    """列出指定資料夾中的所有檔案"""
    for root, dirs, files in os.walk(directory):
        for file in files:
            yield os.path.join(root, file)

for f in list_files_in_directory('./rotated_images'):
    if os.path.isfile(f):
        img = Image.open(f)
        print(f, img.size)
