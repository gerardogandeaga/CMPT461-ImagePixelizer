
import sys
import cv2
import numpy as np
from PIL import Image
from skimage import io
from pyxelatecore import Pyx, Pal

def pixelate_image(input, output):
	# im = io.imread(input)
	im = cv2.imread(input)
	
	downsample_by = 10
	palette = 7 

	pyx = Pyx(factor=downsample_by, palette=palette, dither="none")
	
	pyx.fit(im)
	
	pixelized_im = pyx.transform(im)
	# io.imsave(output, pixelized_im)
	cv2.imwrite(output, pixelized_im)

	print(pixelized_im.shape)

# pixelate_image(
# 	sys.argv[1],
# 	sys.argv[2])

from pprint import pprint
def numpy_to_pil():
	np_im = cv2.imread("../test-images/output/pix-teddy.png")

	rgba_im = cv2.cvtColor(np_im, cv2.COLOR_RGB2RGBA)

	print(rgba_im.shape)
	print(rgba_im[:10,:10,3])

	cv2.imshow("Demo", rgba_im)

	cv2.waitKey(0)
	cv2.destroyAllWindows()

	# pil_im = Image.fromarray(np_im, "RGB")

numpy_to_pil()
