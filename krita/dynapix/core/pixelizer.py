import sys
import json

# when the entry point is invoked then we have to have the following arguments!
WORKING_DIR = sys.argv[1]
CONFIG_PATH = sys.argv[2]

import cv2
import numpy as np

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
		high_res_mask = cv2.imread(paths_cfg["input_mask"])

		high_rez_size = high_res_img.shape

		# run the images under the engines
		scale_factor = pyxelate_cfg["factor"]
		pyx = Pyx(
			height=pyxelate_cfg["height"],
			width=pyxelate_cfg["width"],
			factor=scale_factor,
			upscale=pyxelate_cfg["upscale"],
			depth=pyxelate_cfg["depth"],
			palette=pyxelate_cfg["palette"],
			dither=pyxelate_cfg["dither"],
			sobel=pyxelate_cfg["sobel"],
			svd=pyxelate_cfg["svd"],
			alpha=pyxelate_cfg["alpha"])
		pyx.fit(high_res_img)

		pix_img = pyx.transform(high_res_img)

		# mask the image out
		mask_region = cfg["mask_region"] # get the coordinate map of the mask
		pix_mask = cv2.cvtColor(high_res_mask, cv2.COLOR_BGR2GRAY)
		# pix_mask = (pix_mask > 0).astype(np.uint8)
		# pix_mask = np.repeat(pix_mask[..., np.newaxis], 3, axis=2) # convert it to a 3 channel mask
		# resize mask to the scaled output image
		pix_mask = cv2.resize(pix_mask, dsize=(high_rez_size[1] // scale_factor, high_rez_size[0] // scale_factor), interpolation=cv2.INTER_NEAREST)

		# apply mask
		# First create the image with alpha channel
		rgba_pix_img = cv2.cvtColor(pix_img, cv2.COLOR_RGB2RGBA)
		rgba_pix_img[:, :, 3] = pix_mask # add the alpha mask
		# masked_pix_img = np.multiply(pix_img, pix_mask)

		# crop selected portion
		x, y, w, h = mask_region["x"] // scale_factor, mask_region["y"] // scale_factor, mask_region["w"] // scale_factor, mask_region["h"] // scale_factor
		rgba_pix_img = rgba_pix_img[y:y+h, x:x+w, :]

		# write the results back
		cv2.imwrite(paths_cfg["output_pix_path"], rgba_pix_img)
	except Exception as e:
		with open(WORKING_DIR + "/ext.log", "w") as log:
			log.write("err {}\n".format(str(e)))

main()
