import numpy as np
import matplotlib.pyplot as plt
from matplotlib.image import imread
from scipy.spatial import Delaunay
from tkinter import *
from cmu_112_graphics import *
from triangle_image_class import *
from triangulator_class import *
from PIL import Image
import cv2, random, time

class MyModalApp(ModalApp):
    def appStarted(self):
        self.drawMode = BridgeMode()
        self.setActiveMode(self.drawMode)
        self.timerDelay = 100

class BridgeMode(Mode):
    def appStarted(self):
        self.path = os.getcwd() + "/Images/obama.jpg"
        self.lowPolyGenerator = LowPolyGenerator(self.path)
        self.lowPolyGenerator.generateTriangulation()
        self.lowPolyImage = LowPolyImage(self.lowPolyGenerator, self.path)

    def redrawAll(self, canvas):
        self.lowPolyImage.drawImage(canvas, self.width//2, self.height//2)

app = MyModalApp(width=500, height=500)
