import ctypes
import os
import numpy as np

path = "localizer/build/cc/libchili.so"
libchili = ctypes.cdll.LoadLibrary(path)
libchili.getNumDetect.resType = ctypes.c_int
libchili.getNumDetect.argTypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int]
libchili.copyAndClean.argTypes = [ctypes.c_void_p, ctypes.c_void_p]

def find(grayImage):
  assert(len(grayImage.shape) == 2)
  width = grayImage.shape[1]
  height = grayImage.shape[0]
  __grayImagePtr__ = ctypes.cast(
      (ctypes.c_ubyte * width * height)(),
      ctypes.POINTER(ctypes.c_ubyte))
  __grayImage__ = np.ctypeslib.as_array(__grayImagePtr__,
      shape=(height, width))
  np.copyto(__grayImage__, grayImage)
  n = libchili.getNumDetect(__grayImagePtr__, width, height)
  if n == 0:
    return {}
  ids = ctypes.cast((ctypes.c_int * n)(),
      ctypes.POINTER(ctypes.c_int))
  corners = ctypes.cast((ctypes.c_float * n * 8)(), 
      ctypes.POINTER(ctypes.c_float))
  libchili.copyAndClean(ids, corners)
  ids = list(np.ctypeslib.as_array(ids, shape=(n, )))
  corners = list(np.ctypeslib.as_array(corners, shape=(n * 8, )))
  tags = {}
  for i in range(n):
    tags[ids[i]] = [np.reshape(corners[i * 8 : (i + 1) * 8], (4, 2))]
  return tags
