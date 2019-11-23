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
        self.ps = canvas.postscript(colormode='color')
        img = Image.open(io.BytesIO(self.ps.encode('utf-8')))
        img.save('./Images/test.jpg')



app = MyModalApp(width=1920, height=1080)
