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
	# from modules.unet import UNet, UNetReshade
	from xt_consistency.modules.unet import UNet, UNetReshade
	import PIL
	from PIL import Image
	import cv2
except Exception as e:    
	with open(WORKING_DIR + "/normals.log", "w") as log:
		log.write("import error {}\n".format(str(e)))
		log.write(traceback.format_exc())
	sys.exit()
finally:
	pass

NORMAL_TASK = 0
# TODO: get the input image path from cfg
# TODO: get the output path from cfg

def load_image(input_path):
	img = cv2.imread(input_path)
	height, width, dim = img.shape
	if height > width:
		borderoutput = cv2.copyMakeBorder(img, 0, 0, 0, height - width, cv2.BORDER_CONSTANT, value=[255, 255, 255])
	elif width > height:
		borderoutput = cv2.copyMakeBorder(img, width - height, 0, 0, 0, cv2.BORDER_CONSTANT, value=[255, 255, 255])
	else:
		borderoutput = img

	return borderoutput, (height, width, dim)

	# cv2.imwrite("./my_extension/BORDER_IMAGE.png", borderoutput)


def generate_normals(pil_image, xtc_path, output_path):

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
	# TODO: add models path in the cfg file
	path = os.path.join(xtc_path, "models/rgb2normal_consistency.pth")
	model_state_dict = torch.load(path, map_location=map_location)
	model.load_state_dict(model_state_dict)
	baseline_output = model(img_tensor).clamp(min=0, max=1)
	trans_topil(baseline_output[0]).save(output_path)

	# re-read the image return it
	return cv2.imread(output_path)


def process_normals(normal_img, img_dims, mask_img):
	height, width = img_dims[0], img_dims[1]
	normal_img = 255 - normal_img

	if height > width:
		final_normal_img = normal_img[:, 0:int(256 * width / height), :]
	elif width > height:
		final_normal_img = normal_img[int(256 * (width - height) / width):, :, :]
	else:
		final_normal_img = normal_img

	final_normal_img = cv2.resize(final_normal_img, (width, height)) 
	final_normal_img = cv2.cvtColor(final_normal_img, cv2.COLOR_RGB2RGBA)
	final_normal_img[:, :, 3] = mask_img

	return final_normal_img

# def pixelate_normals():


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
		# TODO: pixelate normals

		cv2.imwrite(paths["output_norm_path"], normal_img)

	except Exception as e:
		with open(WORKING_DIR + "/normals.log", "w") as log:
			log.write("run error {}\n".format(str(e)))
			log.write(traceback.format_exc())

main()
