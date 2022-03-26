
import sys
import cv2
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

pixelate_image(
	sys.argv[1],
	sys.argv[2])
