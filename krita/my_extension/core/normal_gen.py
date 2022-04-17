import sys
import json
import traceback
import os

# when the entry point is invoked then we have to have the following arguments!
WORKING_DIR = sys.argv[1]
CONFIG_PATH = sys.argv[2]
sys.path.append(WORKING_DIR+"/core/xt_consistency")

try:
	import torch
	from torchvision import transforms
	from xt_consistency.modules.unet import UNet, UNetReshade
	import PIL
	from PIL import Image, ImageOps
	import cv2
	from pyxelatecore import Pyx, Pal
	import numpy as np
except Exception as e:    
	with open(WORKING_DIR + "/normals.log", "w") as log:
		log.write("import error {}\n".format(str(e)))
		log.write(traceback.format_exc())
	sys.exit()
finally:
	pass

NORMAL_TASK = 0
KERN_SHARPEN = np.array([
	[0, -1, 0],
	[-1, 5, -1],
	[0, -1, 0],
])

def load_image(input_path):
	"""
	Loads an image from the input path and then resizes it to be a square image.
	Returns resized image and original image dimensions
	"""
	img = cv2.imread(input_path)
	height, width, dim = img.shape
	if height > width:
		borderoutput = cv2.copyMakeBorder(img, 0, 0, 0, height - width, cv2.BORDER_CONSTANT, value=[255, 255, 255])
	elif width > height:
		borderoutput = cv2.copyMakeBorder(img, width - height, 0, 0, 0, cv2.BORDER_CONSTANT, value=[255, 255, 255])
	else:
		borderoutput = img

	return borderoutput, (height, width, dim)


def generate_normals(pil_image, xtc_path, output_path):
	"""
	Uses XTC to generate a normal map of the image and saves it to the output path.
	Returns normal image
	"""
	trans_totensor = transforms.Compose([transforms.Resize(256, interpolation=PIL.Image.BILINEAR),
										transforms.CenterCrop(256),
										transforms.ToTensor()])
	trans_topil = transforms.ToPILImage()

	# get target task and model
	models = [UNet(), UNet(downsample=6, out_channels=1), UNetReshade(downsample=5)]
	model = models[NORMAL_TASK]

	map_location = (lambda storage, loc: storage.cuda()) if torch.cuda.is_available() else torch.device('cpu')

	img_tensor = trans_totensor(pil_image)[:3].unsqueeze(0)

	# compute baseline and consistency output
	path = os.path.join(xtc_path, "models/rgb2normal_consistency.pth")
	model_state_dict = torch.load(path, map_location=map_location)
	model.load_state_dict(model_state_dict)
	baseline_output = model(img_tensor).clamp(min=0, max=1)
	trans_topil(baseline_output[0]).save(output_path)

	# re-read the image return it
	return cv2.imread(output_path)


def process_normals(normal_img, img_dims, mask_img):
	"""
	Resized the normals to match input image dimensions
	"""
	height, width = img_dims[0], img_dims[1]
	normal_img = 255 - normal_img

	# resize if needed
	if height > width:
		final_normal_img = normal_img[:, 0:int(256 * width / height), :]
	elif width > height:
		final_normal_img = normal_img[int(256 * (width - height) / width):, :, :]
	else:
		final_normal_img = normal_img

	# mask the image
	final_normal_img = cv2.resize(final_normal_img, (width, height), interpolation=cv2.INTER_NEAREST)
	# final_normal_img = cv2.cvtColor(final_normal_img, cv2.COLOR_RGB2RGBA)
	# final_normal_img[:, :, 3] = mask_img

	return final_normal_img

def pixelate_normals(normal_img, mask_img, scale_factor, palette_size):
	"""
	Pixelates the normal map image
	"""

	# sharpen the image
	# pix_normal_img = cv2.filter2D(src=normal_img, ddepth=-1, kernel=KERN_SHARPEN)

	# reduce the colours by posterizing
	pix_normal_img = Image.fromarray(normal_img, mode="RGB") # to PIL
	pix_normal_img = ImageOps.posterize(pix_normal_img, 5)

	# back to numpy image
	pix_normal_img = np.array(pix_normal_img, dtype=np.uint8)

	# mask out the image, setting the alpha=0 points to black
	bin_mask_img = (mask_img > 0).astype(np.uint8)
	pix_normal_img[:,:,0] = np.multiply(pix_normal_img[:,:,0], bin_mask_img)
	pix_normal_img[:,:,1] = np.multiply(pix_normal_img[:,:,1], bin_mask_img)
	pix_normal_img[:,:,2] = np.multiply(pix_normal_img[:,:,2], bin_mask_img)

	# pixelate normals
	pyx = Pyx(factor=scale_factor, palette=palette_size)
	pyx.fit(pix_normal_img)

	return pyx.transform(pix_normal_img)

def mask_and_crop(pix_normal_img, mask_img, mask_region, scale_factor):
	mask_img = cv2.resize(mask_img, dsize=(pix_normal_img.shape[1], pix_normal_img.shape[0]), interpolation=cv2.INTER_NEAREST)
	pix_normal_img[:,:,3] = mask_img

	# crop selected portion
	x, y, w, h = mask_region["x"] // scale_factor, mask_region["y"] // scale_factor, mask_region["w"] // scale_factor, mask_region["h"] // scale_factor
	return pix_normal_img[y:y+h, x:x+w, :]

def main():
	try:
		cfg = None
		with open(CONFIG_PATH, 'r') as f:
			cfg = json.load(f)
		paths = cfg["paths"]

		mask_img = cv2.cvtColor(cv2.imread(paths["input_mask"]), cv2.COLOR_BGR2GRAY)
		
		img, original_dims = load_image(paths["input_path"])
		normal_img = generate_normals(Image.fromarray(img), paths["xtc_path"], paths["output_norm_path"])
		normal_img = process_normals(normal_img, original_dims, mask_img)
		pix_normal_img = pixelate_normals(normal_img, mask_img, cfg["pyxelate"]["factor"], cfg["normal_gen"]["palette"])

		# fixing red channel
		pix_normal_img[:,:,2] = 255 - pix_normal_img[:,:,2]
		
		# convert to RGBA and mask out the image
		pix_normal_img = cv2.cvtColor(pix_normal_img, cv2.COLOR_RGB2RGBA)
		pix_normal_img = mask_and_crop(pix_normal_img, mask_img, cfg["mask_region"], cfg["pyxelate"]["factor"])


		cv2.imwrite(paths["output_norm_path"], pix_normal_img)

	except Exception as e:
		with open(WORKING_DIR + "/normals.log", "w") as log:
			log.write("run error {}\n".format(str(e)))
			log.write(traceback.format_exc())

main()
