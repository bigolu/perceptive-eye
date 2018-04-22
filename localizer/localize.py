import numpy as np
from numpy.linalg import norm
from numpy.matlib import repmat
import cv2
import math

def toEuler(R):
  theta1 = math.atan2(R[1, 2], R[2, 2])
  c2 = math.sqrt(R[0, 0] ** 2 + R[0, 1] ** 2)
  theta2 = math.atan2(-R[0, 2], c2)
  s1 = math.sin(theta1)
  c1 = math.cos(theta1)
  theta3 = math.atan2(s1 * R[2, 0] - c1 * R[1, 0], c1 * R[1, 1] - s1 * R[2, 1])
  return np.array([theta1, theta2, theta3])

class ChiliLocalizer(object):
  def __init__(self,
      cameraMat=np.array([[1360.4, 0, 960], [0, 1360.4, 540], [0, 0, 1]]),
      distCoeffs=np.array([0, 0, 0, 0, 0])):
    self.landmarks = {}
    self.objects = {}
    self.res = 
