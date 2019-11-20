import numpy as np
import matplotlib.pyplot as plt
from matplotlib.image import imread
from scipy.spatial import Delaunay
from tkinter import *
import cv2, random, time, os


# FILE LOADING
print(os.getcwd())

for file in os.listdir(os.getcwd() + "/images"):
    if file != ".DS_Store":
        print(file)

# I use matplotlib's imageread to read an image into a numpy array
im = plt.imread(os.getcwd()+"/images/rafa.jpg")


kernel = np.array([[-1,-1,-1], [-1, 9,-1], [-1,-1,-1]])
bim = cv2.blur(im,(30,30))
sim = cv2.filter2D(im,-1, kernel)


cim = (cv2.Canny(im, 10, 120))


x = [1,2,30,4,5,3,40,7,5,3]
y = [2,5,9,14,43,4,7,9,50,60]

print(cim.shape)

f, ax = plt.subplots(2,2)
ax[0,0].imshow(im)
ax[1,0].imshow(sim, cmap = "gray")
ax[1,1].imshow(bim, cmap = "gray")
ax[0,1].imshow(cim, cmap = "gray")
plt.show()

A = np.array([1,2,3])
B = np.array([1,4,6])
print(np.dot(A,B))



# Delaunay method works by taking in a list of coordinates (vertices)
# outputs simplices, an array of 3-lists that contain the indices of the points that
# create each triangle in the Delaunay triangulation



# from https://stackoverflow.com/questions/34588464/python-how-to-capture-image-from-webcam-on-click-using-opencv
# messing around with webcam, wont actually use in project
# cam = cv2.VideoCapture(0)
#
# cv2.namedWindow("test")
#
# img_counter = 0
#
# while True:
#     ret, frame = cam.read()
#     cv2.imshow("test", frame)
#     if not ret:
#         break
#     k = cv2.waitKey(1)
#
#     if k%256 == 27:
#         # ESC pressed
#         print("Escape hit, closing...")
#         break
#     elif k%256 == 32:
#         # SPACE pressed
#         img_name = "opencv_frame_{}.png".format(img_counter)
#         cv2.imwrite(img_name, frame)
#         print("{} written!".format(img_name))
#         img_counter += 1
#
# cam.release()
#
# cv2.destroyAllWindows()
