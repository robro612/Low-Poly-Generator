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
        self.scroll = 0
        self.margin = 10
        self.selected = (-1,-1)
        self.selectedFile = ""
        self.previewSize = 800
        self.path = os.getcwd() + "/Images/catalina.jpg"
        self.directory = os.getcwd() + "/Images"
        self.thumbnailSize = 250
        self.lowPolyGenerator = LowPolyGenerator(self.path)
        self.lowPolyGenerator.generateTriangulation()
        self.lowPolyImage = LowPolyImage(self.lowPolyGenerator, self.path)
        self.directoryList = self.generateFileGrid()


    def generateFileGrid(self):
        thumbnailSize = self.thumbnailSize
        files, directories = [],[]
        path = self.directory
        for file in os.listdir(path):
            if file.endswith(".jpg"):
                files.append(path + "/" + file)
            elif not file.startswith("."):
                directories.append(file)
        directoryThumbnails = [("directory", path + "/" + dir) for dir in directories]
        backDirectory = "/".join(path.split("/")[:-1])
        directoryThumbnails.insert(0, ("directory", backDirectory))
        thumbnails = []
        for file in files:
            thumbnail = Image.open(file)
            thumbnail.thumbnail((self.thumbnailSize*0.8, self.thumbnailSize*0.8),
            Image.ANTIALIAS)
            thumbnails.append((thumbnail,file))
        self.thumbnails = directoryThumbnails + thumbnails
        maxC = (self.width - self.previewSize)//self.thumbnailSize
        self.thumbnailArray = [[None]*maxC for _ in range(len(self.thumbnails)//maxC + 1)]
        r,c = 0,0
        for i in range(len(self.thumbnails)):
            self.thumbnailArray[r][c] = self.thumbnails[i]
            c += 1
            if c > maxC - 1:
                r += 1
                c = 0

    def getRowCol(self, mx, my):
        for r in range(len(self.thumbnailArray)):
            for c in range(len(self.thumbnailArray[0])):
                if my > r*self.thumbnailSize + (r+1)*self.margin - self.scroll and \
                my < (r+1)*self.thumbnailSize + (r+2)*self.margin - self.scroll and \
                mx > c*self.thumbnailSize + (c+1)*self.margin and \
                mx < (c+1)*self.thumbnailSize + (c+2)*self.margin and \
                self.thumbnailArray[r][c] != None:
                    return (r,c)
        return (-1,-1)

    def mousePressed(self, event):
        print("click")
        self.selected = self.getRowCol(event.x, event.y)
        r,c = self.selected
        if (r,c) != (-1,-1):
            self.selectedFile = self.thumbnailArray[r][c][1]
            print("SELECTED: ", self.selectedFile)


    def drawGrid(self, canvas):
        thumbnailSize = self.thumbnailSize
        folderIconColor = LowPolyGenerator.rgbString(120,180,210)
        captionColor = LowPolyGenerator.rgbString(180,180,180)
        lighterBackgroundColor = LowPolyGenerator.rgbString(78,78,78)
        backgroundColor = LowPolyGenerator.rgbString(50,50,50)
        darkerBackgroundColor = LowPolyGenerator.rgbString(38,38,38)
        outlineBlue = LowPolyGenerator.rgbString(38,101,203)

        canvas.create_rectangle(0,0, self.width, self.height, fill=backgroundColor)
        availableLength = self.width - self.previewSize
        canvas.create_line(self.width - self.previewSize, 0, self.width - 800, self.height)
        maxC = availableLength//thumbnailSize

        r,c = 0,0
        for i in range(len(self.thumbnails)):
            if (r,c) == self.selected:
                boxColor = lighterBackgroundColor
                outlineColor = outlineBlue
            else:
                boxColor = darkerBackgroundColor
                outlineColor = "black"
            canvas.create_rectangle(
            c*thumbnailSize + (c+1)*self.margin,
            r*thumbnailSize + (r+1)*self.margin - self.scroll,
            c*thumbnailSize + self.thumbnailSize + (c+1)*self.margin,
            r*thumbnailSize + self.thumbnailSize + (r+1)*self.margin - self.scroll,
            fill = boxColor, outline = outlineColor)
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
            if imgName == self.directory.split("/")[-2]:
                imgName = ".."
            canvas.create_text(c*thumbnailSize + self.thumbnailSize//2 + (c+1)*self.margin,
            r*thumbnailSize + thumbnailSize - self.scroll - 5 + (r+1)*self.margin,
            text=imgName, anchor="s", font="Arial 12", fill=captionColor)
            c += 1
            if c > maxC - 1:
                r += 1
                c = 0

    def keyPressed(self, event):
        scrollDelta = 20
        thumbnailDelta = 10
        if event.key == "Down":
            self.scroll += scrollDelta
        if event.key == "Up":
            self.scroll -= scrollDelta
            self.scroll = max(self.scroll, 0)
        if event.key == "Left":
            self.thumbnailSize -= thumbnailDelta
            self.directoryList = self.generateFileGrid()
        if event.key == "Right":
            self.thumbnailSize += thumbnailDelta
            self.directoryList = self.generateFileGrid()

    def redrawAll(self, canvas):
        self.drawGrid(canvas)

        # poly image canvas saving from https://stackoverflow.com/questions/34777676/how-to-convert-a-python-tkinter-canvas-postscript-file-to-an-image-file-readable
        # self.ps = canvas.postscript(colormode='color')
        # image = Image.open(io.BytesIO(self.ps.encode('utf-8')))
        # image.save('./Images/poly.jpg')



app = PolyBridge(width=1920, height=1080)
