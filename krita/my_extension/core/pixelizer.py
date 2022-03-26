# from numpy import ndarray
# import numpy as np
# import cv2

import sys

# when the entry point is invoked then we have to have the following arguments!
WORKING_DIR = sys.argv[1]
INPUT_IMAGE_PATH = sys.argv[2]
OUTPUT_IMAGE_PATH = sys.argv[3]
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


try:
	im = cv2.imread(INPUT_IMAGE_PATH)

	downsample_by = 10
	palette = 7
	pyx = Pyx(factor=downsample_by, palette=palette, dither="none")
	pyx.fit(im)

	cv2.imwrite(OUTPUT_IMAGE_PATH, pyx.transform(im))
except Exception as e:
	with open(WORKING_DIR + "/ext.log", "w") as log:
		log.write("err {}\n".format(str(e)))



# def pilexate_image(img):
# 	# red, blk_wht_img = cv2.threshold(img, 128, 255, cv2.THRESH_BINARY)
# 	# return blk_wht_img

# 	im = io.imread(input)

	

	# io.imsave(output, pixelized_im)


