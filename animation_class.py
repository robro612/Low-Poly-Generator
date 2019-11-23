import numpy as np
import matplotlib.pyplot as plt
from matplotlib.image import imread
from scipy.spatial import Delaunay
from tkinter import *
from cmu_112_graphics import *
from triangle_image_class import *
from triangulator_class import *
from PIL import Image
import cv2, random, time, io

class MyModalApp(ModalApp):
    def appStarted(self):
        self.drawMode = BridgeMode()
        self.setActiveMode(self.drawMode)
        self.timerDelay = 100
        self.ps = None

class BridgeMode(Mode):
    def appStarted(self):
        self.path = os.getcwd() + "/Images/nico.jpg"
        self.lowPolyGenerator = LowPolyGenerator(self.path)
        self.lowPolyGenerator.generateTriangulation()
        self.lowPolyImage = LowPolyImage(self.lowPolyGenerator, self.path)

    def keyPressed(self, event):
        if event.key == "Space":
            # saving from https://stackoverflow.com/questions/34777676/how-to-convert-a-python-tkinter-canvas-postscript-file-to-an-image-file-readable
            ps = self.canvas.postscript(colormode='color')
            img = Image.open(io.BytesIO(ps.encode('utf-8')))
            img.save('./Images/test.jpg')

    def drawTemplate(self, canvas):
        pass

    def redrawAll(self, canvas):
        self.lowPolyImage.drawImage(canvas, self.width//2, self.height//2)
        draw(canvas, self.width, self.height, self.lowPolyGenerator.triangles,
        self.lowPolyGenerator.nodes)
        self.ps = canvas.postscript(colormode='color')
        img = Image.open(io.BytesIO(self.ps.encode('utf-8')))
        img.save('./Images/test.jpg')

app = MyModalApp(width=1800, height=1000)
