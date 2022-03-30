# from numpy import ndarray
# import numpy as np
# import cv2

import sys
import json

# when the entry point is invoked then we have to have the following arguments!
WORKING_DIR = sys.argv[1]
CONFIG_PATH = sys.argv[2]
# INPUT_IMAGE_PATH = sys.argv[2]
# OUTPUT_IMAGE_PATH = sys.argv[3]
# TODO: add normals paths

import cv2
# from skimage import io

try:
	from pyxelatecore import Pyx, Pal
except Exception as e:    
	with open(WORKING_DIR + "/ext.log", "w") as log:
		log.write("err {}\n".format(str(e)))
finally:
	pass

def main():
	try:
		cfg = None
		with open(CONFIG_PATH, 'r') as f:
			cfg = json.load(f)

		paths_cfg = cfg["paths"]
		pyxelate_cfg = cfg["pyxelate"]

		# TODO: generate the normals

		# pixelated the normals and image
		high_res_img = cv2.imread(paths_cfg["input_path"])
		pyx = Pyx(
			height=pyxelate_cfg["height"],
			width=pyxelate_cfg["width"],
			factor=pyxelate_cfg["factor"],
			upscale=pyxelate_cfg["upscale"],
			depth=pyxelate_cfg["depth"],
			palette=pyxelate_cfg["palette"],
			dither=pyxelate_cfg["dither"],
			sobel=pyxelate_cfg["sobel"],
			svd=pyxelate_cfg["svd"],
			alpha=pyxelate_cfg["alpha"])
		pyx.fit(high_res_img)

		# write the results back
		cv2.imwrite(paths_cfg["output_pix_path"], pyx.transform(high_res_img))
	except Exception as e:
		with open(WORKING_DIR + "/ext.log", "w") as log:
			log.write("err {}\n".format(str(e)))

main()
