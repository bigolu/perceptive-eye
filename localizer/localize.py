import numpy as np
from numpy.linalg import norm
from numpy.matlib import repmat
import cv2
import math
from chili import find

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
      distCoeffs=np.array([1, 0, 0, 0, 0])):
        self.landmarks = {}
        self.objects = {}
        self.camera_mat = cameraMat
        self.dist_coeffs = distCoeffs

    def load_img(self, path):
        self.img = cv2.imread(path)
        self.img_grey = cv2.imread(path, cv2.IMREAD_GRAYSCALE)

    def find_chili(self):
        return find(self.img_grey)

    def pnp(self, img_points):
        chili_tag_locations = np.array(
                [
                    [0, 0, 0],
                    [0, 0.029, 0],
                    [0.029, 0.029, 0],
                    [0.029, 0, 0] ,
                ]
            )
        print(np.array(img_points[3][0]))
        _, rvec, tvec = cv2.solvePnP(
            chili_tag_locations,
            np.array(img_points[3][0]),
            self.camera_mat,
            self.dist_coeffs
        )

        r, jacobian = cv2.Rodrigues(rvec)
        r = r.T

        t = np.dot(-r, tvec)

        return (r, t)

    def display_img(self):
        cv2.imshow('image', self.img_grey)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

if __name__ == "__main__":
    path = "foo.jpeg"
    cl = ChiliLocalizer()
    cl.load_img(path)
    chili_tags = cl.find_chili()
    r, t = cl.pnp(chili_tags)
    
