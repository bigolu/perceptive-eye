import cv2

c920K = np.array(
    [[ 450.88974675,   0.        , 299.54114384]
     [   0.        , 455.04038717, 225.93263983]
     [   0.        ,   0.        ,   1.        ]])
c920D = np.array([[-0.07893157, 0.21037218, 0.02158169, 0.02398847,-0.23897265]])

d415K = np.array(
    [[ 462.13868987,   0.        , 320.        ]
     [   0.        , 462.86923212, 180.        ]
     [   0.        ,   0.        ,   1.        ]]
d415D = np.array([[0, 0, 0, 0, 0]])

def triangulate(image1, image2, Rvec1, tvec1, Rvec2, tvec2):
  R1, J1 = cv2.Rodrigues(Rvec1)
  R2, J2 = cv2.Rodrigues(Rvec2)

  R1 = R1.T
  R2 = R2.T
  t1 = np.dot(-R1, tvec1)
  t2 = np.dot(-R2, tvec2)

  Rt1 = np.concatenate([R1, t1])
  Rt2 = np.concatenate([R2, t2])

  homo = cv2.triangulatePoints(Rt1, Rt2, image1, image2)
  cv2.triangulatePoints
  return homo[:, :3]

#cam = cv2.VideoCapture(1)
#cam.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc("Y", "U", "Y", "V"))
#cam.set(cv2.CAP_PROP_AUTOFOCUS, False)
#cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
#cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)


