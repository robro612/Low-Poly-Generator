import numpy as np
import matplotlib.pyplot as plt
from matplotlib.image import imread
from scipy.spatial import Delaunay
from tkinter import *
from cmu_112_graphics import *
from triangle_image_class import *
from triangulator_class import *
from PIL import Image
import cv2, random, time, io, fitz

class MyModalApp(ModalApp):
    def appStarted(self):
        self.drawMode = BridgeMode()
        self.setActiveMode(self.drawMode)
        self.timerDelay = 100

class BridgeMode(Mode):
    def appStarted(self):
        self.path = os.getcwd() + "/Images/obama.jpg"
        self.directory = os.getcwd()
        self.lowPolyGenerator = LowPolyGenerator(self.path)
        self.lowPolyGenerator.generateTriangulation()
        self.lowPolyImage = LowPolyImage(self.lowPolyGenerator, self.path)
        self.ps = None
        self.generateFileGrid()

    def generateFileGrid(self):
        files, directories = [],[]
        for file in os.listdir(self.directory):
            if os.path.isfile(file):
                files.append(file)
            elif not file.startswith("."):
                directories.append(file)
            print(directories)


    def drawTemplate(self, canvas):
        pass

    def redrawAll(self, canvas):
        self.lowPolyImage.drawImage(canvas, self.width//2, self.height//2)
        draw(canvas, self.width, self.height, self.lowPolyGenerator.triangles,
        self.lowPolyGenerator.nodes)
        canvas.create_rectangle(0,0, 300, 300)
        # file saving from https://stackoverflow.com/questions/34777676/how-to-convert-a-python-tkinter-canvas-postscript-file-to-an-image-file-readable
        if self.ps == None:
            self.ps = canvas.postscript(file = './Images/new.ps', colormode='color')
            print(self.ps)
            print("saved")
            pix = fitz.Pixmap("./Images/new.ps")      # input.xxx: a file in any of the supported input formats
            pix.writeImage('./Images/new.jpg')



app = MyModalApp(width=1920, height=1080)
