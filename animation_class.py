import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from matplotlib.image import imread
from scipy.spatial import Delaunay
from tkinter import *
from cmu_112_graphics import *
from triangle_image_class import *
from triangulator_class import *
from PIL import Image, ImageChops
import cv2, random, time, io, easygui

class Button():
    def __init__(self, x, y, width, height, color, text):
        self.x, self.y = x, y
        self.width, self.height = width, height
        self.color = color
        self.text = text
    def draw(self, canvas):
        canvas.create_rectangle(self.x - self.width//2, self.y - self.height//2,
        self.x + self.width//2, self.y + self.height//2, fill=self.color)
        canvas.create_text(self.x, self.y, text=self.text,
        fill=LowPolyGenerator.rgbString(180,180,180), font="Arial 12")

class PolyBridge(ModalApp):
    def appStarted(self):
        self.timerDelay = 100
        self.toRender = (None, None)
        self.rendered = None
        self.blurSize = 3
        self.sharpen = True
        self.cannyLow = 100
        self.cannyHigh = 500
        self.randomNoiseRate = 500
        self.nodeSampleDistanceThreshold = 20
        self.nodeSampleRate = 0.1
        self.nodeThresholdRate = 0.2
        self.drawMode = BridgeMode()
        self.renderMode = RenderMode()
        self.setActiveMode(self.drawMode)

class RenderMode(Mode):
    def appStarted(self):
        self.lowPolyImage, self.renderSize = self.app.toRender
        self.tempW, self.tempH = self.app.width, self.app.height
        self.app.height, self.app.width = self.lowPolyImage.imageSize
        self.height, self.width = self.lowPolyImage.imageSize
        self.timerDelay = 0.1
    def redrawAll(self, canvas):
        if self.app.toRender != (None, None):
            self.lowPolyImage.drawImage(canvas, self.width, self.height)
            # poly image canvas saving from https://stackoverflow.com/questions/34777676/
            # how-to-convert-a-python-tkinter-canvas-postscript-file-to-an-image-file-readable
            ps = canvas.postscript(colormode='color')
            image = Image.open(io.BytesIO(ps.encode('utf-8')))

            self.app.rendered = image
            #image.save("./Images/thumbnail.jpg")
            self.app.width, self.app.height = self.tempW, self.tempH
        self.app.setActiveMode(self.app.drawMode)
    def keyPressed(self, event):
        if event.key == "s":
            self.app.saveSnapshot()
        else:
            self.app.setActiveMode(self.app.drawMode)

class BridgeMode(Mode):
    def appStarted(self):
        self.width, self.height = self.app.width, self.app.height
        self.scroll = 0
        self.margin = 20
        self.selected = (-1,-1)
        self.selectedFile = ""
        self.previewSize = 700
        self.previewImage = None
        self.showHidden = False
        self.thumbnailSize = (self.width - self.previewSize - 5*self.margin)//3
        self.directory = os.getcwd()
        self.directoryList = self.generateFileGrid()
        self.button = Button(self.width - self.previewSize//2, self.height - 200,
        200, 60, LowPolyGenerator.rgbString(78,78,78), "Change Parameters")
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
            elif self.showHidden or not file.startswith("."):
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
        maxC = (self.width - self.previewSize - 4*self.margin)//self.thumbnailSize #magic number
        self.thumbnailArray = [[None]*maxC for _ in range(len(self.thumbnails)//maxC + 1)]
        r,c = 0,0
        for i in range(len(self.thumbnails)):
            self.thumbnailArray[r][c] = self.thumbnails[i]
            c += 1
            if c > maxC - 1:
                r += 1
                c = 0

    def checkButtonClicks(self, mx, my):
        if mx > self.button.x - self.button.width//2 and \
        mx < self.button.x + self.button.width//2 and \
        my > self.button.y - self.button.height//2 and \
        my < self.button.y + self.button.height//2:
            self.changeParameters()
            return True
        return False

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
    # whitespace cropping from from https://stackoverflow.com/questions/10615901/trim-whitespace-using-pil
    def trim(self, im):
        bg = Image.new(im.mode, im.size, im.getpixel((im.size[0]-1,im.size[1]-1)))
        diff = ImageChops.difference(im, bg)
        diff = ImageChops.add(diff, diff, 2.0, -100)
        bbox = diff.getbbox()
        if bbox:
            return im.crop(bbox)

    def mousePressed(self, event):
        if self.checkButtonClicks(event.x, event.y):
            r,c = self.selected
        else:
            r,c = self.getRowCol(event.x, event.y)
        self.selected = (r,c)
        if (r,c) != (-1,-1):
            self.selectedFile = self.thumbnailArray[r][c][1]
            if self.selectedFile.endswith(".jpg") or \
            self.selectedFile.endswith(".JPG") or \
            self.selectedFile.endswith(".jpeg") or \
            self.selectedFile.endswith(".JPEG"):
                self.lowPolyGenerator = LowPolyGenerator(self.selectedFile,
                blurSize=self.app.blurSize, sharpen=self.app.sharpen,
                nodeSampleDistanceThreshold=self.app.nodeSampleDistanceThreshold,
                randomNoiseRate=self.app.randomNoiseRate,
                cannyLow=self.app.cannyLow, cannyHigh=self.app.cannyHigh,
                nodeSampleRate=self.app.nodeSampleRate,
                nodeThresholdRate=self.app.nodeThresholdRate)
                self.lowPolyGenerator.generateTriangulation()
                self.lowPolyImage = LowPolyImage(self.lowPolyGenerator, self.selectedFile)
                self.app.toRender = (self.lowPolyImage, self.selectedFile)
                self.app.setActiveMode(self.app.renderMode)
                self.previewImage = self.app.rendered
                self.previewImage = self.trim(self.previewImage)
                 #Magic Number
                self.previewImage.thumbnail((500,500)) #Magic Number
                self.app.renderMode = RenderMode()
                self.generateFileGrid()
            elif os.path.isdir(self.selectedFile):
                self.directory = self.selectedFile
                self.generateFileGrid()
                self.scroll = 0
                self.selected = (-1,-1)

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
            if self.thumbnails[i][1].endswith(".jpg") or \
            self.thumbnails[i][1].endswith(".JPG") or \
            self.thumbnails[i][1].endswith(".jpeg") or \
            self.thumbnails[i][1].endswith(".JPEG"):
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
            if len(imgName) > 2*thumbnailSize//12:
                imgName = "..."+imgName[-15:]
            canvas.create_text(c*thumbnailSize + self.thumbnailSize//2 + (c+1)*self.margin,
            r*thumbnailSize + thumbnailSize - self.scroll - 5 + (r+1)*self.margin,
            text=imgName, anchor="s", font="Arial 12", fill=captionColor)
            c += 1
            if c > maxC - 1:
                r += 1
                c = 0

    def keyPressed(self, event):
        scrollDelta = 40
        thumbnailDelta = 20
        previewDelta = 20
        if event.key == "Down":
            self.scroll += scrollDelta
        elif event.key == "Up":
            self.scroll -= scrollDelta
            self.scroll = max(self.scroll, 0)
        elif event.key == "Left":
            self.thumbnailSize -= thumbnailDelta
            self.thumbnailSize = max(self.thumbnailSize, 1)
            self.scrollDelta = int(0.7*scrollDelta)
            self.directoryList = self.generateFileGrid()
        elif event.key == "Right":
            self.thumbnailSize += thumbnailDelta
            self.scrollDelta = int(1.3*scrollDelta)
            self.directoryList = self.generateFileGrid()
        elif event.key == "g":
            self.previewSize += previewDelta
            self.thumbnailSize = self.previewSize//2
            self.directoryList = self.generateFileGrid()
        elif event.key == "p":
            self.changeParameters()
        elif event.key == "s":
            if self.previewImage != None:
                name = self.selectedFile.split("/")[-1]
                name = name.split(".")[0]
                hashStr = hash((self.app.blurSize,
                self.app.sharpen,
                self.app.cannyLow,
                self.app.cannyHigh,self.app.randomNoiseRate,
                self.app.nodeSampleDistanceThreshold,
                self.app.nodeSampleRate,
                self.app.nodeThresholdRate))
                hashStr = str(hashStr)[-4:]
                self.previewImage.save(f"./Saved/{name}Poly{hashStr}.jpg")
                print("Saved")


    def changeParameters(self):
        fig, ax = plt.subplots(figsize=(8.5, 3))
        plt.axis('off')
        high = plt.axes([0.25, 0.2, 0.65, 0.03])
        low = plt.axes([0.25, 0.3, 0.65, 0.03])
        blur = plt.axes([0.25, 0.4, 0.65, 0.03])
        sharpenAx = plt.axes([0.25, 0.5, 0.65, 0.03])
        noise = plt.axes([0.25, 0.6, 0.65, 0.03])
        threshold = plt.axes([0.25, 0.7, 0.65, 0.03])
        nodeSample = plt.axes([0.25, 0.8, 0.65, 0.03])
        nodeThreshold = plt.axes([0.25, 0.9, 0.65, 0.03])
        blurSize = \
        Slider(blur, "Blur Size", valmin=1, valmax=25, valinit=3, valstep=2)
        sharpen = \
        Slider(sharpenAx, "Sharpen", valmin=0, valmax=1, valinit=1, valstep=1)
        cannyLow = \
        Slider(low, "Edge Low", valmin=1, valmax=1000, valinit=100, valstep=1)
        cannyHigh = \
        Slider(high, "Edge High", slidermin=cannyLow, valmin=1, valmax=1000, valinit=500, valstep=1)
        noiseRate = \
        Slider(noise, "Noise Rate", valmin=0, valmax=10000, valinit=1000, valstep=100)
        nodeSampleDistanceThreshold = \
        Slider(threshold, "Threshold distance", valmin=0, valmax=100, valinit=20, valstep=5)
        nodeSampleRate = \
        Slider(nodeSample, "Node Sample Rate", valmin=0, valmax=1, valinit=0.1, valstep=0.01)
        nodeThresholdRate = \
        Slider(nodeThreshold, "Node Threshold Check Rate", valmin=0, valmax=1, valinit=0.2, valstep=0.01)
        plt.show()
        self.app.blurSize = int(blurSize.val)
        self.app.sharpen = bool(sharpen.val)
        self.app.cannyLow = int(cannyLow.val)
        self.app.cannyHigh = int(cannyHigh.val)
        self.app.randomNoiseRate = int(noiseRate.val)
        self.app.nodeSampleDistanceThreshold = int(nodeSampleDistanceThreshold.val)
        self.app.nodeSampleRate = nodeSampleRate.val
        self.app.nodeThresholdRate = nodeThresholdRate.val

    def drawCols(self, canvas):
        for i in range(self.width//100):
            if not (i*100 == self.previewSize):
                canvas.create_line(100*i, 0, 100*i, self.height)

    def redrawAll(self, canvas):
        self.drawGrid(canvas)
        canvas.create_text(self.width - self.previewSize//2, 20,
        text = f"{self.selectedFile}", font="Arial 12", fill="white")
        if self.previewImage != None:
            canvas.create_image(self.width - self.previewSize//2, self.height//3,
            image = ImageTk.PhotoImage(self.previewImage))
        self.button.draw(canvas)
        #self.drawCols(canvas)

app = PolyBridge(width=1500, height=1000)
