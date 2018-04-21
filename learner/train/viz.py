#!/usr/bin/env python3
import mxnet as mx
import numpy as np
import math
import glob
import os
import h5py
import cv2
import logging
logging.basicConfig(level=logging.INFO)

root_dir = "../capture/"
colors = []
depths = []

all_color_paths = glob.glob(os.path.join(root_dir + "color_images/*.png"))
#all_depth_paths = glob.glob(os.path.join(root_dir + "depth_images/*.npy"))
num_items = min(len(all_color_paths), 100)

all_color_images = [cv2.imread(root_dir + "color_images/%05d.png" % i) \
    for i in range(num_items)]
all_depth_images = []
for i in range(num_items):
  with open(root_dir + "depth_images/%05d.npy" % i, "rb") as fp:
    all_depth_images.append(np.load(fp))

for i in range(num_items):
  depth_image = all_depth_images[i]
  depth_image_3d = np.dstack((depth_image, depth_image, depth_image))
  #bg_removed = np.where((depth_image_3d > 1.0) | (depth_image_3d <= 0), \
  #    153, depth_image_3d)
  #depth_cm = cv2.applyColorMap(
  #    cv2.convertScaleAbs(bg_removed, alpha=0.03), cv2.COLORMAP_JET)
  color_image = all_color_images[i] / 255.0
  images = np.hstack((color_image, depth_image_3d))
  cv2.imshow("depth-and-color", images)
  cv2.waitKey(0)
