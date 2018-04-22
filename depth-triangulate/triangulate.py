import cv2

def triangulate(image1, image2, Rvec1, tvec1, Rvec2, tvec2):
  rvec, tvec, a, b, c, d, e, f, g, h = cv2.composeRT(Rvec1, tvec1, Rvec2.T, np.dot(-Rvec2.T, tvec2))
  R, J = cv2.Rodrigues(rvec)
  Rt = np.concatenate([R, tvec])
  homo = cv2.triangulatePoints(np.concatenate([np.eye(3), np.zeros((3, 1))]), Rt, image1, image2)
  return homo[:, :3]
