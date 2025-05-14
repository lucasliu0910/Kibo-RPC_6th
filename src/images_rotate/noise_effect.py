import os
import shutil
import sys
from PIL import Image

def list_files_in_directory(directory):
    """列出指定資料夾中的所有檔案"""
    for root, dirs, files in os.walk(directory):
        for file in files:
            yield os.path.join(root, file)

# for f in list_files_in_directory('./rotated_images'):
#     if os.path.isfile(f):
#         img = Image.open(f)
#         print(f, img.size)

def main():
    if len(sys.argv) < 2:
        print("Usage: python noise_effect.py <image_directory>")
        return
    
    img_folder = sys.argv[1]
    # img_folder = './rotated_images'

    for f in list_files_in_directory(img_folder):
        if os.path.isfile(f):
            oldpath=f.split('\\')
            # print(oldpath)
            oldpath[-2]=oldpath[-2]+'-noised'
            newpath='\\'.join(oldpath)
            # print(newpath)
            newdir=os.path.dirname(newpath)
            # print(newdir)
            os.makedirs(newdir, exist_ok=True)
            # break
            try:
                img = Image.open(f).convert("RGBA")
                noise_img = Image.effect_noise(img.size, 100).convert("RGBA")
                # final_img = Image.alpha_composite(noise_img, img)
                blended_image = Image.blend(img, noise_img, alpha=0.3)
                # noise_img.show()
                # final_img.show()
                # blended_image.show()
                print("  Saving noised image:", os.path.basename(newpath))
                blended_image.save(newpath)
            except:
                print("Moving non-image file:", os.path.basename(f))
                shutil.move(f, newpath)
            # break

if __name__ == "__main__":
    main()
    