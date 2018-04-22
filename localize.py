import numpy as np
from numpy.linalg import norm
from numpy.matlib import repmat
import cv2
import math
from localizer.chili import find
import os

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

        return (rs, ts)

    def display_img(self):
        cv2.imshow('image', self.img_grey)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

orb = cv2.ORB_create()

def find_features(img):
  global orb
  kp = orb.detect(img, None)
  kp, des = orb.compute(img, kp)
  return kp, des

def find_campose_and_3dpts(dir_name):
  global c920K, c920D
  names = []
  i = 0
  while os.path.exists("{}/{}.jpg".format(dir_name, i)):
    names.append("{}/{}.jpg".format(dir_name, i))
    i += 1

  cl = ChiliLocalizer(cameraMat=c920K, distCoeffs=c920D)
  all_data = []

  for j in range(len(names) - 1):
    # load the images
    image1 = cv2.imread(names[j])
    image2 = cv2.imread(names[j+1])

    # find key features
    f1 = find_features(image1)
    f2 = find_features(image2)

    # match the features to each other
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(f1[1], f2[1])
    matches = sorted(matches, key=lambda x:x.distance)

    # load the images into the chilitag localizer
    cl.load_img(names[j])
    tags = cl.find_chili()
    r1, t1 = cl.pnp(tags)

    cl.load_img(names[j+1])
    tags = cl.find_chili()
    r2, t2 = cl.pnp(tags)

    if type(r1) == type(None) or type(r2) == type(None):
      continue

    # find the shift between the poses
    dt = t2 - t1
    dR = np.dot(r1.T, r2)
    dt = np.dot(-r1.T, t2)
    dR, J = cv2.Rodrigues(dR)

    # grab the projection matrices
    R1, R2, P1, P2, Q, roi1, roi2 = cv2.stereoRectify(
        cl.camera_mat, cl.dist_coeffs, cl.camera_mat, cl.dist_coeffs,
        (image1.shape[1], image1.shape[0]), dR, dt)

    # triangulate points given the projection matrices into cam 1's frame of ref
    pts1 = []
    pts2 = []

    for m in matches:
      pts1.append(f1[0][m.queryIdx].pt)
      pts2.append(f2[0][m.trainIdx].pt)
    X = cv2.triangulatePoints(P1, P2, np.array(pts1).T, np.array(pts2).T)
    X /= X[3] # div out 4th row to make homogeneous

    # get the actual 3d points by transforming cam 1's frame of ref to global
    pts3d = np.dot(r1, X[:3,:]) + t1
    pts3d_ = []
    for i in range(pts3d.shape[0]):
      if pts3d[:, i][0] < 0 or pts3d[:, i][0] > 18 or \
          pts3d[:, i][1] < 0 or pts3d[:, i][1] > 18 or \
          pts3d[:, i][2] < 0 or pts3d[:, i][2] > 18:
        continue
      else:
        pts3d_.append(pts3d[i, :])
    all_data.append({"campose": np.concatenate([r1, t1], axis=1),
                     "3dpoints": np.array(pts3d_).T})
  return all_data

"""
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
"""
