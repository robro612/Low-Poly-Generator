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

class PolyBridge(ModalApp):
    def appStarted(self):
        self.drawMode = BridgeMode()
        self.setActiveMode(self.drawMode)
        self.timerDelay = 100

class BridgeMode(Mode):
    def appStarted(self):
        self.path = os.getcwd() + "/Images/catalina.jpg"
        self.directory = os.getcwd()
        self.thumbnailSize = 250
        self.lowPolyGenerator = LowPolyGenerator(self.path)
        self.lowPolyGenerator.generateTriangulation()
        self.lowPolyImage = LowPolyImage(self.lowPolyGenerator, self.path)
        #self.lowPolyImage.createThumbnail(self.thumbnailSize)
        self.directoryList = self.generateFileGrid(self.thumbnailSize)
        self.scroll = 0
        self.margin = 10


    def generateFileGrid(self, thumbnailSize):
        files, directories = [],[]
        path = self.directory + "/Images/"
        for file in os.listdir(path):
            if file.endswith(".jpg"):
                files.append(path + file)
            elif not file.startswith("."):
                directories.append(file)
        directoryThumbnails = [("directory", dir) for dir in directories]
        thumbnails = []
        for file in files:
            thumbnail = Image.open(file)
            thumbnail.thumbnail((self.thumbnailSize*0.8, self.thumbnailSize*0.8))
            thumbnails.append((thumbnail,file))

        self.thumbnails = directoryThumbnails + thumbnails

    def drawTemplate(self, canvas):
        thumbnailSize = self.thumbnailSize
        folderIconColor = LowPolyGenerator.rgbString(120,180,210)
        captionColor = LowPolyGenerator.rgbString(180,180,180)
        backgroundColor = LowPolyGenerator.rgbString(50,50,50)
        darkerBackgroundColor = LowPolyGenerator.rgbString(38,38,38)

        canvas.create_rectangle(0,0, self.width, self.height, fill=backgroundColor)
        availableLength = self.width - 3*self.thumbnailSize
        maxC = availableLength//thumbnailSize
        # for r in range(len(self.thumbnails)):
        #     canvas.create_line(0, r*thumbnailSize-self.scroll,
        #      maxC*thumbnailSize, r*thumbnailSize-self.scroll)
        # for c in range(maxC + 1):
        #     canvas.create_line(c*thumbnailSize, 0-self.scroll,
        #     c*thumbnailSize, self.height)
        r,c = 0,0
        for i in range(len(self.thumbnails)):
            canvas.create_rectangle(
            c*thumbnailSize + (c+1)*self.margin,
            r*thumbnailSize + (r+1)*self.margin - self.scroll,
            c*thumbnailSize + self.thumbnailSize + (c+1)*self.margin,
            r*thumbnailSize + self.thumbnailSize + (r+1)*self.margin - self.scroll,
            fill = darkerBackgroundColor)
            if self.thumbnails[i][1].endswith(".jpg"):
                canvas.create_image(c*thumbnailSize + self.thumbnailSize//2 + (c+1)*self.margin,
                r*thumbnailSize + self.thumbnailSize//2 - self.scroll + (r+1)*self.margin,
                image=ImageTk.PhotoImage(self.thumbnails[i][0]))
            else:
                canvas.create_rectangle(
                c*thumbnailSize + self.thumbnailSize//2 - self.thumbnailSize//4 + (c+1)*self.margin,
                r*thumbnailSize + self.thumbnailSize//2 - self.thumbnailSize//4 + (r+1)*self.margin - self.scroll,
                c*thumbnailSize + self.thumbnailSize//2 + self.thumbnailSize//4 + (c+1)*self.margin,
                r*thumbnailSize + self.thumbnailSize//2 + self.thumbnailSize//4 + (r+1)*self.margin - self.scroll,
                fill = folderIconColor)
            imgName = self.thumbnails[i][1].split("/")[-1]
            canvas.create_text(c*thumbnailSize + self.thumbnailSize//2 + (c+1)*self.margin,
            r*thumbnailSize + thumbnailSize - self.scroll - 5 + (r+1)*self.margin,
            text=imgName, anchor="s", font="Arial 12", fill=captionColor)
            c += 1
            if c > maxC - 1:
                r += 1
                c = 0

    def keyPressed(self, event):
        scrollDelta = 20
        if event.key == "Down":
            self.scroll += scrollDelta
        if event.key == "Up":
            self.scroll -= scrollDelta
            self.scroll = max(self.scroll, 0)


    def redrawAll(self, canvas):
        #self.lowPolyImage.drawImage(canvas, self.width//2, self.height//2)
        # #draw(canvas, self.width, self.height, self.lowPolyGenerator.triangles,
        # self.lowPolyGenerator.nodes)
        self.drawTemplate(canvas)

        # poly image canvas saving from https://stackoverflow.com/questions/34777676/how-to-convert-a-python-tkinter-canvas-postscript-file-to-an-image-file-readable
        # self.ps = canvas.postscript(colormode='color')
        # image = Image.open(io.BytesIO(self.ps.encode('utf-8')))
        # image.save('./Images/poly.jpg')



app = PolyBridge(width=1920, height=1080)
