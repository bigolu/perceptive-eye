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
num_items = len(all_color_paths)
#num_items = 100

all_color_images = np.array([np.rollaxis( \
  cv2.imread(root_dir + "color_images/%05d.png" % i), -1) \
    for i in range(num_items)])
all_depth_images = []
for i in range(num_items):
  with open(root_dir + "depth_images/%05d.npy" % i, "rb") as fp:
    depth_image = np.load(fp)
    all_depth_images.append(depth_image.reshape([1] + list(depth_image.shape)))
all_depth_images = np.array(all_depth_images)

print(all_color_images.shape, all_depth_images.shape)

batch_size = 2
train_iter = mx.io.NDArrayIter(data=all_color_images, label=all_depth_images, batch_size=batch_size, data_name="color", label_name="depth_label")


data = mx.sym.Variable("color")

conv1 = mx.sym.Convolution(data=data, name="conv1", num_filter=64, kernel=(3, 3), pad=(1, 1))
relu1 = mx.sym.Activation(data=conv1, name="relu1", act_type="relu")
pool1 = mx.sym.Pooling(data=relu1, name="pool1", pool_type="max", kernel=(2, 2), stride=(2, 2))

conv2 = mx.sym.Convolution(data=pool1, name="conv2", num_filter=64, kernel=(3, 3), pad=(1, 1))
relu2 = mx.sym.Activation(data=conv2, name="relu2", act_type="relu")
pool2 = mx.sym.Pooling(data=relu2, name="pool2", pool_type="max", kernel=(2, 2), stride=(2, 2))

conv3 = mx.sym.Convolution(data=pool2, name="conv3", num_filter=64, kernel=(3, 3), pad=(1, 1))
relu3 = mx.sym.Activation(data=conv3, name="relu3", act_type="relu")
pool3 = mx.sym.Pooling(data=relu3, name="pool3", pool_type="max", kernel=(2, 2), stride=(2, 2))

conv4 = mx.sym.Convolution(data=pool3, name="conv4", num_filter=64, kernel=(3, 3), pad=(1, 1))
relu7 = mx.sym.Activation(data=conv4, name="relu7", act_type="relu")
pool4 = mx.sym.Pooling(data=relu7, name="pool4", pool_type="max", kernel=(2, 2), stride=(2, 2))

flat1 = mx.sym.Flatten(data=pool4, name="flat1")
fc1 = mx.sym.FullyConnected(data=flat1, name="fc1", num_hidden=2048)
relu4 = mx.sym.Activation(data=fc1, name="relu4", act_type="relu")

fc2 = mx.sym.FullyConnected(data=relu4, name="fc2", num_hidden=2048)
relu5 = mx.sym.Activation(data=fc2, name="relu5", act_type="relu")

fc3 = mx.sym.FullyConnected(data=relu5, name="fc3", num_hidden=3600)
relu6 = mx.sym.Activation(data=fc3, name="relu6", act_type="relu")

reshaped = mx.sym.reshape(name="reshaped", data=relu6, shape=(batch_size, 3, 30, 40))

dec1 = mx.sym.Deconvolution(data=reshaped, kernel=(4, 4), stride=(2, 2), pad=(1, 1), num_filter=64, no_bias=True, name="dec1")
conv5 = mx.sym.Convolution(data=dec1, name="conv5", num_filter=64, kernel=(3, 3), pad=(1, 1))
relu8 = mx.sym.Activation(data=conv5, name="relu8", act_type="relu")

dec2 = mx.sym.Deconvolution(data=relu8, kernel=(4, 4), stride=(2, 2), pad=(1, 1), num_filter=64, no_bias=True, name="dec2")
conv6 = mx.sym.Convolution(data=dec2, name="conv6", num_filter=64, kernel=(3, 3), pad=(1, 1))
relu9 = mx.sym.Activation(data=conv6, name="relu9", act_type="relu")

dec3 = mx.sym.Deconvolution(data=relu9, kernel=(4, 4), stride=(2, 2), pad=(1, 1), num_filter=64, no_bias=True, name="dec3")
conv7 = mx.sym.Convolution(data=dec3, name="conv7", num_filter=64, kernel=(3, 3), pad=(1, 1))
relu10 = mx.sym.Activation(data=conv7, name="relu10", act_type="relu")

dec4 = mx.sym.Deconvolution(data=relu10, kernel=(4, 4), stride=(2, 2), pad=(1, 1), num_filter=64, no_bias=True, name="dec4")
conv8 = mx.sym.Convolution(data=dec4, name="conv8", num_filter=1, kernel=(3, 3), pad=(1, 1))

depth = mx.sym.LinearRegressionOutput(data=conv8, name="depth")


mod = mx.mod.Module(depth, context=mx.gpu(0), data_names=['color'], label_names=['depth_label'])
mod.bind(
    data_shapes=train_iter.provide_data,
    label_shapes=train_iter.provide_label,
)
mod.init_params(initializer=mx.init.Uniform(0.01))
mod.init_optimizer(
    optimizer="nag",
    optimizer_params=(
      ("learning_rate", 0.01),
      ("momentum", 0.9)))

nb_epoch = 50
mod.fit(train_iter, num_epoch=nb_epoch)#, \
#    batch_end_callback=mx.callback.ProgressBar(all_color_images.shape[0] / batch_size))

mod.save_params("v1.model")

"""
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
  cv2.waitKey(0)"""
