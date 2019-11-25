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
        self.timerDelay = 100
        self.toRender = (None, None)
        self.rendered = None
        self.drawMode = BridgeMode()
        self.renderMode = RenderMode()
        self.setActiveMode(self.drawMode)

class RenderMode(Mode):
    def appStarted(self):
        self.lowPolyImage, self.renderSize = self.app.toRender
        self.tempW, self.tempH = self.app.width, self.app.height
        self.app.width, self.app.height = self.lowPolyImage.imageSize
        self.timerDelay = 0.1
    def redrawAll(self, canvas):
        if self.app.toRender != (None, None):
            self.lowPolyImage.drawImage(canvas, self.width, self.height)
            # poly image canvas saving from https://stackoverflow.com/questions/34777676/
            # how-to-convert-a-python-tkinter-canvas-postscript-file-to-an-image-file-readable
            ps = canvas.postscript(colormode='color')
            image = Image.open(io.BytesIO(ps.encode('utf-8')))

            self.app.rendered = image
            image.save("./Images/thumbnail.jpg")
            print("Done rnedering")
            self.app.width, self.app.height = self.tempW, self.tempH
        self.app.setActiveMode(self.app.drawMode)


class BridgeMode(Mode):
    def appStarted(self):
        self.width, self.height = self.app.width, self.app.height
        self.scroll = 0
        self.margin = 10
        self.selected = (-1,-1)
        self.selectedFile = ""
        self.previewSize = 600
        self.previewImage = None
        self.thumbnailSize = self.previewSize//2
        self.path = os.getcwd() + "/Images/catalina.jpg"
        self.directory = os.getcwd() + "/Images"
        self.directoryList = self.generateFileGrid()
        #self.lowPolyImage.createThumbnail(100)

    def generateFileGrid(self):
        thumbnailSize = self.thumbnailSize
        files, directories = [],[]
        path = self.directory
        for file in os.listdir(path):
            if file.endswith(".jpg") or \
            file.endswith(".JPG") or \
            file.endswith(".jpeg") or \
            file.endswith(".JPEG"):
                files.append(path + "/" + file)
            elif file.startswith(".b") or not file.startswith("."):
                directories.append(file)
        directoryThumbnails = [("directory", path + "/" + dir) for dir in directories]
        backDirectory = "/".join(path.split("/")[:-1])
        directoryThumbnails.insert(0, ("directory", backDirectory))
        thumbnails = []
        for file in files:
            thumbnail = Image.open(file)
            thumbnail.thumbnail((self.thumbnailSize*0.8, self.thumbnailSize*0.8), #magic number
            Image.ANTIALIAS)
            thumbnails.append((thumbnail,file))
        self.thumbnails = directoryThumbnails + thumbnails
        maxC = (self.width - self.previewSize - 4*self.margin)//self.thumbnailSize
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
        r,c = self.getRowCol(event.x, event.y)
        self.selected = (r,c)
        if (r,c) != (-1,-1):
            self.selectedFile = self.thumbnailArray[r][c][1]
            print("SELECTED: ", self.selectedFile)
            if self.selectedFile.endswith(".jpg") or \
            self.selectedFile.endswith(".JPG") or \
            self.selectedFile.endswith(".jpeg") or \
            self.selectedFile.endswith(".JPEG"):
                self.lowPolyGenerator = LowPolyGenerator(self.selectedFile)
                self.lowPolyGenerator.generateTriangulation()
                self.lowPolyImage = LowPolyImage(self.lowPolyGenerator, self.selectedFile)
                self.app.toRender = (self.lowPolyImage, self.selectedFile)
                self.app.setActiveMode(self.app.renderMode)
                self.previewImage = self.app.rendered
                self.previewImage = self.previewImage.crop((0,0,800,800)) #Magic Number
                self.previewImage.thumbnail((400,400)) #Magic Number
                print("Done setting", self.previewSize)
                self.app.renderMode = RenderMode()
                self.generateFileGrid()
            elif os.path.isdir(self.selectedFile):
                self.directory = self.selectedFile
                self.generateFileGrid()

    def drawGrid(self, canvas):
        thumbnailSize = self.thumbnailSize
        folderIconColor = LowPolyGenerator.rgbString(120,180,210)
        captionColor = LowPolyGenerator.rgbString(180,180,180)
        lighterBackgroundColor = LowPolyGenerator.rgbString(78,78,78)
        backgroundColor = LowPolyGenerator.rgbString(50,50,50)
        darkerBackgroundColor = LowPolyGenerator.rgbString(38,38,38)
        outlineBlue = LowPolyGenerator.rgbString(38,101,203)

        canvas.create_rectangle(0,0, self.width, self.height, fill=backgroundColor)
        availableLength = self.width - self.previewSize - 4*self.margin
        canvas.create_line(self.width - self.previewSize, 0,
        self.width - self.previewSize, self.height, fill = "black")
        maxC = availableLength//thumbnailSize
        # Draws images, boxes, and captions
        r,c = 0,0
        for i in range(len(self.thumbnails)):
            print(self.selected, (r,c))
            if (r,c) == self.selected:
                boxColor = lighterBackgroundColor
                outlineColor = outlineBlue
                print("yay")
            else:
                boxColor = darkerBackgroundColor
                outlineColor = "black"
                print("bleh")
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
        previewDelta = 20
        if event.key == "Down":
            self.scroll += scrollDelta
        elif event.key == "Up":
            self.scroll -= scrollDelta
            self.scroll = max(self.scroll, 0)
        elif event.key == "Left":
            self.thumbnailSize -= thumbnailDelta
            self.directoryList = self.generateFileGrid()
        elif event.key == "Right":
            self.thumbnailSize += thumbnailDelta
            self.directoryList = self.generateFileGrid()
        elif event.key == "g":
            self.previewSize += previewDelta
            self.thumbnailSize = self.previewSize//2
            self.directoryList = self.generateFileGrid()


    def drawCols(self, canvas):
        for i in range(self.width//100):
            if not (i*100 == self.previewSize):
                canvas.create_line(100*i, 0, 100*i, self.height)

    def redrawAll(self, canvas):
        self.drawGrid(canvas)
        canvas.create_text(self.width - 2*self.previewSize//3, 20, text = f"{self.previewSize}{self.selectedFile}")
        if self.previewImage != None:
            canvas.create_image(self.width - self.previewSize//2, self.height//4,
            image = ImageTk.PhotoImage(self.previewImage))
        #self.drawCols(canvas)

app = PolyBridge(width=1500, height=1000)
