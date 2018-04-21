#!/usr/bin/env python3
import pyrealsense2 as rs
import cv2
import numpy as np

def main():
  counter = 1440 # set based on the directory of images
  try:
    # Create a context object.
    # This object owns the handles to all connected realsense devices
    pipeline = rs.pipeline()

    config = rs.config()
    config.enable_stream(rs.stream.depth, 640, 360, rs.format.z16, 30)
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

    profile = pipeline.start(config)

    depth_sensor = profile.get_device().first_depth_sensor()
    depth_scale = depth_sensor.get_depth_scale()
    print("Depth scale is:", depth_scale)

    clipping_distance_in_meters = 1
    clipping_distance = clipping_distance_in_meters / depth_scale

    # create an align object
    align_to = rs.stream.color
    align = rs.align(align_to)

    while True:
      # This call waits until a new coherent set of frames is available on a device
      # Calls to get_frame_data(...) and get_frame_timestamp(...) on a device will return stable values until wait_for_frames(...) is called
      frames = pipeline.wait_for_frames()

      aligned_frames = align.process(frames)
      
      # get aligned frames
      depth_frame = aligned_frames.get_depth_frame()
      color_frame = aligned_frames.get_color_frame()
      if not depth_frame or not color_frame:
        continue

      depth_image = np.asanyarray(depth_frame.get_data())
      color_image = np.asanyarray(color_frame.get_data())

      # remove background
      grey_color = 250 # just an arbitrary color, doesn't really matter
      depth_image_3d = np.dstack((depth_image, depth_image, depth_image))
      bg_removed = np.where((depth_image_3d > clipping_distance) | (depth_image_3d <= 0),
          grey_color, color_image)

      #depth_frame = depth_frame * depth_scale
      # render
      #depth_cm = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
      #images = np.hstack((bg_removed, depth_cm))
      cv2.imshow("depth", bg_removed)
      cv2.waitKey(1)

      # save images in a folder
      cv2.imwrite("color_images/%05d.png" % counter, color_image)
      with open("depth_images/%05d.npy" % counter, "wb") as fp:
        np.save(fp, depth_image.astype(np.float32) * depth_scale)
      counter += 1

  finally:
    pipeline.stop()

if __name__ == "__main__":
  main()
