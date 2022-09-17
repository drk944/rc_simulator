import cv2 as cv # Just for you Ashton
import numpy as np

img = cv.imread("images/oval_track_v1.png", cv.IMREAD_GRAYSCALE)
scale_percent = 140 # percent of original size
width = int(img.shape[1] * scale_percent / 100)
height = int(img.shape[0] * scale_percent / 100)
dim = (width, height)
  
# resize image
resized = cv.resize(img, dim, interpolation = cv.INTER_AREA)
cv.imwrite("images/oval_track_v1.png", resized)
cv.imshow("Track", img)
cv.imshow("Track1", resized)

cv.waitKey()