import subprocess
from os import system
import cv2

image = cv2.imread("./my_extension/INPUT_IMAGE.png")
height, width, dim = image.shape
if height > width:
	borderoutput = cv2.copyMakeBorder(image, 0, 0, 0, height - width, cv2.BORDER_CONSTANT, value=[255, 255, 255])
elif width > height:
	borderoutput = cv2.copyMakeBorder(image, width - height, 0, 0, 0, cv2.BORDER_CONSTANT, value=[255, 255, 255])
else:
	borderoutput = image
cv2.imwrite("./my_extension/BORDER_IMAGE.png", borderoutput)



subprocess.Popen(["../../deps/bin/python3.9", "demo.py", "--task", "normal", "--img_path", "../BORDER_IMAGE.png", "--output_path", "../"], cwd="./my_extension/XTConsistency-master").wait()

normal = 255 - cv2.imread("./my_extension/BORDER_IMAGE_normal_consistency.png")

if height > width:
	final = normal[:, 0:int(256 * width / height), :]
elif width > height:
	final = normal[int(256 * (width - height) / width):, :, :]
else:
	final = normal

final = cv2.resize(final, (width, height)) 
final = cv2.cvtColor(final, cv2.COLOR_RGB2RGBA)
mask = cv2.imread("./my_extension/INPUT_MASK.png")
mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
final[:, :, 3] = mask


cv2.imwrite("./my_extension/FINAL_NORMAL.png", final)