

from krita import *
import numpy as np
import cv2
from PIL import Image
import subprocess
import json

WORKING_DIR = os.path.join(str(Krita.instance().readSetting("", "ResourceDirectory", "")), "pykrita")
INPUT_IMAGE_PATH   = os.path.join(WORKING_DIR, "my_extension/INPUT_IMAGE.png")
INPUT_MASK_PATH   = os.path.join(WORKING_DIR, "my_extension/INPUT_MASK.png")
OUTPUT_IMAGE_PATH  = os.path.join(WORKING_DIR, "my_extension/OUTPUT_IMAGE.png")
ENGINE_PYTHON_PATH = os.path.join(WORKING_DIR, "deps/bin/python3.9")
ENGINE_ENTRY_POINT = os.path.join(WORKING_DIR, "my_extension/core/pixelizer.py")
CONFIG_PATH = os.path.join(WORKING_DIR, "my_extension/engine.cfg")

IM_MODE = "RGBA"

class Engine(object):
    @staticmethod
    def krita2numpy(pixel_data, size):
        pil_img = Image.frombytes(IM_MODE, size, pixel_data)
        return Engine.pil2numpy(pil_img=pil_img)

    @staticmethod
    def load_img(path):
        """
        returns and RGBA image from a specified path
        """
        img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        return cv2.cvtColor(img, cv2.COLOR_RGB2RGBA)

    @staticmethod
    def numpy2pil(np_img):
        return Image.fromarray(np_img, IM_MODE)

    @staticmethod
    def pil2numpy(pil_img):
        return np.array(pil_img, dtype=np.uint8)

    @staticmethod 
    def selection2mask(selection_arr, width, height):
        """
        Given a flattened of length = width * height
        return a numpy mask. selection_arr stores values between 0 and 255.
        """
        mask = np.frombuffer(selection_arr, dtype=np.uint8)
        mask = (mask > 0).astype(np.uint8) * 255;
        # reshape mask array to a rectangle
        mask = mask.reshape(height, width)

        return mask

    @staticmethod
    def export_config(
		input_path="", input_mask="", output_pix_path="", output_norm_path="", 
		xtc_path="", norm_scale_factor=4, norm_palette_size = 18,
		mask_region=None, 
		height=None, width=None, factor=None, upscale=1, depth=1, palette=8, dither="none", sobel=3, svd=True, alpha=.6):
        """
        Create a config file for the pixelizer containing the
        """
        config_map = {
            "paths": {
                "input_path":       input_path,
                "input_mask":       input_mask,
                "output_pix_path":  output_pix_path,
                "output_norm_path": output_norm_path,
				"xtc_path":          xtc_path,
            },
            "mask_region": {
                "x": mask_region[0],
                "y": mask_region[1],
                "w": mask_region[2],
                "h": mask_region[3],
            },
            "pyxelate": {
                "height":  height,
                "width":   width,
                "factor":  factor,
                "upscale": upscale,
                "depth":   depth,
                "palette": palette,
                "dither":  dither,
                "sobel":   sobel,
                "svd":     svd,
                "alpha":   alpha
            },
            "normal_gen": {
                "factor":  norm_scale_factor,
                "palette": norm_palette_size,
            }
        }

        with open(CONFIG_PATH, 'w') as f:
            json.dump(config_map, f)

    @staticmethod
    def create_new_documents(pix_img, norm_img, width, height):
        """
        Create new documents for the pixelized and normal images
        """

        # populate the pixelized document
        if pix_img != None:
            pix_document = Krita.instance().createDocument(width, height, "Pixelized", "RGBA", "U8", "", 300.0)
            pix_layer = pix_document.createNode("Pixelized", "paintlayer")
            pix_document.rootNode().removeChildNode(pix_document.nodeByName("Background"))
            pix_document.rootNode().addChildNode(pix_layer, None)

            pix_layer.setPixelData(pix_img, 0, 0, width, height)
            Krita.instance().activeWindow().addView(pix_document)
            pix_document.refreshProjection()


        if norm_img != None:
            # populate the normal map document
            norm_document = Krita.instance().createDocument(width, height, "Normal Map", "RGBA", "U8", "", 300.0)
            norm_layer = norm_document.createNode("Normal Map", "paintlayer")
            norm_document.rootNode().addChildNode(norm_layer, None)

            norm_layer.setPixelData(norm_img, 0, 0, width, height)
            Krita.instance().activeWindow().addView(norm_document)
            norm_document.refreshProjection()
