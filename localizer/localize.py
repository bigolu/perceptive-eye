import numpy as np
from numpy.linalg import norm
from numpy.matlib import repmat
import cv2
import math
from chili import find

c920K = np.array(
    [[ 450.88974675  , 0.   ,      299.54114384],
 [   0.         ,455.04038717, 225.93263983],
 [   0.         ,  0.        ,   1.        ]])
c920D = np.array([[-0.07893157, 0.21037218, 0.02158169, 0.02398847,-0.23897265]])


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
        p0 = 0
        p1 = 0.029
        p2 = 0.175
        p3 = 0.204
        chili_tag_locations = {
            
            "0": np.array(
                [
                    [0, p3, 0],
                    [p1, p3, 0],
                    [p1, p2, 0],
                    [0, p2, 0]
                ]
            ), "1": np.array(
                [
                  [p2, p3, 0],
                  [p3, p3, 0],
                  [p3, p2, 0],
                  [p2, p2, 0]
                  ]
                ), "2": np.array(
                [
                  [p2, p1, 0],
                  [p3, p1, 0],
                  [p3, 0, 0],
                  [p2, 0, 0]
                ]
              ), "3": np.array(
                [
                  [0, p1, 0],
                  [p1, p1, 0],
                  [p1, 0, 0],
                  [0, 0, 0]
                ]
              )
            }
        rs = None
        ts = None
        for i in range(4):
          if i in img_points:
            _, rvec, tvec = cv2.solvePnP(
                chili_tag_locations[str(i)],
                np.array(img_points[i][0]),
                self.camera_mat,
                self.dist_coeffs
            )

            r, jacobian = cv2.Rodrigues(rvec)
            r = r.T

            t = np.dot(-r, tvec)
            rs = r
            ts = t

        return (r, t)

    def display_img(self):
        cv2.imshow('image', self.img_grey)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

if __name__ == "__main__":
    path = "img00206.png"
    cl = ChiliLocalizer(cameraMat=c920K, distCoeffs=c920D)
    cl.load_img(path)
    chili_tags = cl.find_chili()
    r, t = cl.pnp(chili_tags)
    print(np.degrees(toEuler(r)), t)

    cl.load_img("img00352.png")
    chili_tags = cl.find_chili()
    r, t = cl.pnp(chili_tags)
    print(np.degrees(toEuler(r)), t)
