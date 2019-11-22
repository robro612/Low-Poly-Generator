import numpy as np
import matplotlib.pyplot as plt
from matplotlib.image import imread
from scipy.spatial import Delaunay
from tkinter import *
from cmu_112_graphics import *
from PIL import Image
import cv2, random, time
# DELETE LIBRARIES NOT NEEDED IN THIS FILE

# This class will hold the image, both in its triangulated and regular forms
# and will have an option to save it as a scaleable static image from TK render
# rather than trying to animate real time every vertex and such

class LowPolyImage:
    def __init__(self, generator, path):
        self.lowPolyGenerator = generator
        self.pilImage = Image.open(path)
        self.tkImage = ImageTk.PhotoImage(self.pilImage)
        self.path = path
        self.triangles = self.lowPolyGenerator.triangles
    def drawImage(self, canvas, x, y):
        canvas.create_image(x, y, image = self.tkImage)
