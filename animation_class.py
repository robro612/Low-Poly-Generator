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

class BridgeMode(Mode):
    def appStarted(self):
        self.path = os.getcwd() + "/Images/catalina.jpg"
        self.directory = os.getcwd()
        self.lowPolyGenerator = LowPolyGenerator(self.path)
        self.lowPolyGenerator.generateTriangulation()
        self.lowPolyImage = LowPolyImage(self.lowPolyGenerator, self.path)
        #self.lowPolyImage.createThumbnail()
        im = self.lowPolyImage.pilImage
        im.thumbnail((250,250))
        im.save('./Images/thumbnail.jpg')
        self.ps = None
        self.directoryList = self.generateFileGrid()


    def generateFileGrid(self):
        files, directories = [],[]
        path = self.directory + "/Images/"
        for file in os.listdir(path):
            if file.endswith(".jpg"):
                files.append(path + file)
            elif not file.startswith("."):
                directories.append(file)
        thumbnails = []
        for file in files:
            thumbnail = Image.open(file)
            thumbnail.thumbnail((200,200))
            thumbnails.append((thumbnail,file))

        self.thumbnails = thumbnails

    def drawTemplate(self, canvas):
        canvas.create_rectangle(0,0, self.width, self.height, fill=LowPolyGenerator.rgbString(50,50,50))
        availableLength = self.width - 500
        maxC = availableLength//250
        for r in range(self.height//250):
            canvas.create_line(0, r*250, maxC*250, r*250)
        for c in range(maxC + 1):
            canvas.create_line(c*250, 0, c*250, self.height)
        r,c = 0,0
        for i in range(len(self.thumbnails)):
            canvas.create_image(c*250 + 125, r*250 + 125, image=ImageTk.PhotoImage(self.thumbnails[i][0]))
            imgName = self.thumbnails[i][1].split("/")[-1]
            canvas.create_text(c*250 + 125, r*250 + 250 - 5, text=imgName,
            anchor="s", font="Arial 12",
            fill=LowPolyGenerator.rgbString(180,180,180))
            c += 1
            if c > maxC - 1:
                r += 1
                c = 0


        # for i in range(len(self.thumbnails)):
        #     canvas.create_image(i*250 + 75, 300, image = ImageTk.PhotoImage(self.thumbnails[i]))

    def redrawAll(self, canvas):
        #self.lowPolyImage.drawImage(canvas, self.width//2, self.height//2)
        # #draw(canvas, self.width, self.height, self.lowPolyGenerator.triangles,
        # self.lowPolyGenerator.nodes)
        self.drawTemplate(canvas)

        # poly image canvas saving from https://stackoverflow.com/questions/34777676/how-to-convert-a-python-tkinter-canvas-postscript-file-to-an-image-file-readable
        # self.ps = canvas.postscript(colormode='color')
        # image = Image.open(io.BytesIO(self.ps.encode('utf-8')))
        # image.save('./Images/poly.jpg')



app = MyModalApp(width=1920, height=1080)
