import numpy as np
import matplotlib.pyplot as plt
from matplotlib.image import imread
from scipy.spatial import Delaunay
from tkinter import *
import cv2, random, time
# DELETE LIBRARIES NOT NEEDED IN THIS FILE

# This class will hold the image, both in its triangulated and regular forms
# and will have an option to save it as a scaleable static image from TK render
# rather than trying to animate real time every vertex and such

class LowPolyImage:
    def __init__(self, image, path, triangles):
        self.image = image
        self.path = path
        self.triangles = triangles
        self.trianglesImage = None
    def drawImage(self, x, y, longestSide):
        currentLongestSide = max(self.image.shape)
