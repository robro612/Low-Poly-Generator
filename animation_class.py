# The animation_class.py file houses the code for the actual animation:
# Button classes and subclasses, and ModalApp architecture
# Run this file as main to run actual experience.

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
import cv2, random, time, io

#Base Button Class
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

    def buttonFunction(self, mode):
        pass
# Skews of buttons with spcific methods (change parameters, go to Help screen)
class ParametersButton(Button):
    def buttonFunction(self, mode):
        mode.changeParameters()

class HelpButton(Button):
    def buttonFunction(self, mode):
        mode.selected = (-1,-1)
        mode.app.setActiveMode(mode.app.helpMode)

class ReturnButton(Button):
    def buttonFunction(self, mode):
        mode.app.setActiveMode(mode.app.bridgeMode)

class PathButton(Button):
    def __init__(self, x, y, width, height, color, text, path):
        super().__init__(x, y, width, height, color, text)
        self.path = path
    def buttonFunction(self, mode):
        mode.directory = self.path + "/" + self.text

class SplashButton(Button):
    def buttonFunction(self, app):
        # file dialog from https://stackoverflow.com/questions/11295917/how-to-select-a-directory-and-store-the-location-using-tkinter-in-python
        app.startPath = filedialog.askdirectory()

    def draw(self, canvas):
        canvas.create_rectangle(self.x - self.width//2, self.y - self.height//2,
        self.x + self.width//2, self.y + self.height//2, fill=self.color)
        canvas.create_text(self.x, self.y, text=self.text,
        fill=LowPolyGenerator.rgbString(180,180,180), font="Arial 30")

# CMU graphics package from http://www.cs.cmu.edu/~112/notes/notes-animations-part2.html
# Modified to allow for a crucial MVC violation
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
        self.bridgeMode = BridgeMode()
        self.renderMode = RenderMode()
        self.splashScreenMode = SplashScreenMode()
        self.helpMode = HelpMode()
        self.setActiveMode(self.splashScreenMode)

class SplashScreenMode(Mode):
    def appStarted(self):
        self.button = SplashButton(self.width//2, 3*self.height//4, 360, 100, LowPolyGenerator.rgbString(78,78,78), "Pick a starting directory")
        self.startPath = ""
    # Checks if buttons are pressed
    def mousePressed(self, event):
        mx, my = event.x, event.y
        button = self.button
        if mx > button.x - button.width//2 and \
        mx < button.x + button.width//2 and \
        my > button.y - button.height//2 and \
        my < button.y + button.height//2:
            button.buttonFunction(self)
        if self.startPath != "":
            self.app.setActiveMode(self.app.bridgeMode)

    def drawBridgeLogo(self, canvas):
        brown = LowPolyGenerator.rgbString(38,28,4)
        orange = LowPolyGenerator.rgbString(242,183,63)
        canvas.create_rectangle(100,100,self.width - 100, self.height//2 - 100, fill=orange, width=0)
        canvas.create_rectangle(110,110,self.width - 110, self.height//2 - 110, fill=brown, width=0)
        canvas.create_text(self.width//2, self.height//4, text="LowPolyGen", font="Arial 120", fill=orange)

    def redrawAll(self, canvas):
        canvas.create_rectangle(0, 0, self.width, self.height, fill=LowPolyGenerator.rgbString(50,50,50), width=0)
        self.drawBridgeLogo(canvas)
        self.button.draw(canvas)

# Help screen mode that demonstrates steps of rendering and the effects of
# each parameter on the image's render
class HelpMode(Mode):
    def appStarted(self):
        self.tipIndex = 0
        self.blurImage = Image.open(os.getcwd() + "/assets/cmuBS.jpg")
        self.cannyImage = Image.open(os.getcwd() + "/assets/cmuCanny.jpg")
        self.polyImage = Image.open(os.getcwd() + "/assets/cmuPoly.jpg")
        self.blurImage.thumbnail((self.width*0.3, self.width*0.3), Image.ANTIALIAS)
        self.cannyImage.thumbnail((self.width*0.3, self.width*0.3), Image.ANTIALIAS)
        self.polyImage.thumbnail((self.width*0.3, self.width*0.3), Image.ANTIALIAS)
        self.returnButton = ReturnButton(self.width//2, 9*self.height//10, 100, 30, LowPolyGenerator.rgbString(78,78,78), "Return")

        self.tips = ["Use the arrow keys to scroll and resize the file system.","Blur determines the size of blur filter applied to the image. \n Sharpen decides whether to then run a sharpen kernel that \n increases the number of edges detected.", "Edge detection bounds determine the lower and upper bounds of edges. \n Generally, higher and closer together is more selective, \n resulting in less nodes (white dots) detected.", "Random sample points and node sample rate \n determine how many pixel \"edges\" as well as random points \n are input into the algorithm.", "Node threshold distance is the minimum side length of the generated triangles. \n Threshold check rate determines how likely triangle sides are to be \n ensured to be the minimum length. 100% will yield all sides with that minimum.", "Note that increasing the number of nodes through node or \n random sample rate increases can have an adverse effect on render times."]

    # checks if buttons are pressed
    def mousePressed(self, event):
        mx, my = event.x, event.y
        button = self.returnButton
        if mx > button.x - button.width//2 and \
        mx < button.x + button.width//2 and \
        my > button.y - button.height//2 and \
        my < button.y + button.height//2:
            button.buttonFunction(self)

    def keyPressed(self, event):
        if event.key == "Right":
            self.tipIndex += 1
            self.tipIndex %= len(self.tips)
        elif event.key == "Left":
            self.tipIndex -= 1
            self.tipIndex %= len(self.tips)
        elif event.key == "h":
            self.app.setActiveMode(self.app.bridgeMode)

    def drawImages(self, canvas):
        canvas.create_image(self.width//6, self.height//3, image=ImageTk.PhotoImage(self.blurImage))
        canvas.create_image(self.width//2, self.height//3, image=ImageTk.PhotoImage(self.cannyImage))
        canvas.create_image(5*self.width//6, self.height//3, image=ImageTk.PhotoImage(self.polyImage))

    def drawTip(self, canvas):
        canvas.create_text(self.width//2, 2*self.height//3, text=self.tips[self.tipIndex], font="Arial 40", justify="center", fill=LowPolyGenerator.rgbString(180,180,180))
        canvas.create_text(self.width//2, self.height//16, text=f"Tip #{self.tipIndex + 1}", font="Arial 40", justify="center", fill=LowPolyGenerator.rgbString(180,180,180))

    def redrawAll(self, canvas):
        canvas.create_rectangle(0, 0, self.width, self.height, fill=LowPolyGenerator.rgbString(50,50,50), width=0)
        self.drawImages(canvas)
        self.drawTip(canvas)
        self.returnButton.draw(canvas)

# This is the ModalApp Mode that draws all of the triangles in a split second
# then immediately exits back to the bridge mode
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
            self.app.width, self.app.height = self.tempW, self.tempH
        self.app.setActiveMode(self.app.bridgeMode)
    def keyPressed(self, event):
        if event.key == "s":
            self.app.saveSnapshot()
        else:
            self.app.setActiveMode(self.app.bridgeMode)

# This is the mode where most of the UX is done. This is meant to mimic the
# Adobe Bridge aesthetic
class BridgeMode(Mode):
    def appStarted(self):
        self.width, self.height = self.app.width, self.app.height
        self.scroll = -40
        self.margin = 20
        self.selected = (-1,-1)
        self.selectedFile = ""
        self.previewSize = self.width//2
        self.previewImage = None
        self.showHidden = False
        self.mousePosition = (None, None)
        self.thumbnailSize = (self.width - self.previewSize - 4*self.margin)//3
        self.directory = self.app.splashScreenMode.startPath
        self.directoryList = self.generateFileGrid()
        self.parametersButton = ParametersButton(self.width - self.previewSize//2, self.height - 200, 200, 60, LowPolyGenerator.rgbString(78,78,78), "Change Parameters")
        self.helpButton = HelpButton(self.width - self.previewSize//2, self.height - 140, 100, 30, LowPolyGenerator.rgbString(78,78,78), "Help")
        self.pathButtons = []
        self.generateDirectoryButtons()
        self.folderIcon = Image.open(os.getcwd() + "/assets/folderIcon.jpg")
        self.fileIcon = Image.open(os.getcwd() + "/assets/fileIcon.jpg")

    # Generates the string of buttons at the top according to the current path
    # clicking on them is meant to bring
    def generateDirectoryButtons(self):
        self.pathButtons = []
        split = self.directory.split("/")
        for i in range(len(split)):
            name = split[i]
            if name != "":
                self.pathButtons.append(PathButton(60 + (100 + 5)*len(self.pathButtons), 30, 100, 30, LowPolyGenerator.rgbString(78,78,78), name, "/".join(split[:i])))
        while 105*len(self.pathButtons) > self.width - self.previewSize:
            self.pathButtons.pop(0)
            for button in self.pathButtons:
                button.x -= 105
        try:
            self.generateFileGrid()
        except:
            pass

    # generates a 2D list of thumbnails and paths to be displayed
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
            thumbnail.thumbnail((self.thumbnailSize*0.8, self.thumbnailSize*0.8), Image.ANTIALIAS)
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
    # checks for button clicks on mouse pressed event
    def checkButtonClicks(self, mx, my):
        for button in self.pathButtons + [self.parametersButton, self.helpButton]:
            if mx > button.x - button.width//2 and \
            mx < button.x + button.width//2 and \
            my > button.y - button.height//2 and \
            my < button.y + button.height//2:
                button.buttonFunction(self)
                return True
        return False

    # Returns the selected file in grid of click
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
    # trims whitespace from image capture
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
            # if the selection isnt empty/default, and its a JPEG, render it
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
                self.previewImage.thumbnail((2*self.previewSize//3, 2*self.previewSize//3))
                self.app.renderMode = RenderMode()
                self.generateFileGrid()
            #Otherwise, if its a directory, navigate to that
            elif os.path.isdir(self.selectedFile):
                self.directory = self.selectedFile
                self.generateFileGrid()
                self.scroll = -40
                self.selected = (-1,-1)
        self.generateDirectoryButtons()

    # draws grid of icons on left
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
            suffixes = (".jpg", ".JPG", ".jpeg", "JPEG")
            if self.thumbnails[i][1].endswith(suffixes):
                canvas.create_image(c*thumbnailSize + self.thumbnailSize//2 + (c+1)*self.margin,
                r*thumbnailSize + self.thumbnailSize//2 - self.scroll + (r+1)*self.margin,
                image=ImageTk.PhotoImage(self.thumbnails[i][0]))
            else:
                if os.path.isdir(self.thumbnails[i][1]):
                    iconThumbnail = self.folderIcon.copy()
                    iconThumbnail.thumbnail((self.thumbnailSize//2,self.thumbnailSize//2), Image.ANTIALIAS)
                else:
                    iconThumbnail = self.fileIcon.copy()
                    iconThumbnail.thumbnail((self.thumbnailSize//2,self.thumbnailSize//2), Image.ANTIALIAS)

                color = folderIconColor
                canvas.create_image(c*thumbnailSize + self.thumbnailSize//2 + (c+1)*self.margin,
                r*thumbnailSize + self.thumbnailSize//2 - self.scroll + (r+1)*self.margin,
                image=ImageTk.PhotoImage(iconThumbnail))
                # else:
                #     color = "green"
                #     canvas.create_rectangle(
                #     c*thumbnailSize + self.thumbnailSize//2 - self.thumbnailSize//4 + (c+1)*self.margin,
                #     r*thumbnailSize + self.thumbnailSize//2 - self.thumbnailSize//4 + (r+1)*self.margin - self.scroll,
                #     c*thumbnailSize + self.thumbnailSize//2 + self.thumbnailSize//4 + (c+1)*self.margin,
                #     r*thumbnailSize + self.thumbnailSize//2 + self.thumbnailSize//4 + (r+1)*self.margin - self.scroll,
                #     fill = color)
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
        if event.key == "Down":
            self.scroll += scrollDelta
        elif event.key == "Up":
            self.scroll -= scrollDelta
            self.scroll = max(self.scroll, -40)
        elif event.key == "Left":
            self.thumbnailSize -= thumbnailDelta
            self.thumbnailSize = max(self.thumbnailSize, 1)
            self.scrollDelta = int(0.7*scrollDelta)
            try:
                self.directoryList = self.generateFileGrid()
            except:
                pass
        elif event.key == "Right":
            self.thumbnailSize += thumbnailDelta
            self.scrollDelta = int(1.3*scrollDelta)
            try:
                self.directoryList = self.generateFileGrid()
            except:
                pass
        elif event.key == "h":
            self.app.setActiveMode(self.app.helpMode)
        elif event.key == "p":
            self.changeParameters()
        elif event.key == "s":
            self.saveImage()

    # Saves the current previewed image
    def saveImage(self):
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
            try:
                os.mkdir(os.path() + "/Saved")
            except:
                pass
            self.previewImage.save(f"./Saved/{name}Poly{hashStr}.jpg")
            print("Saved")
        elif event.key == ".":
            self.showHidden = not self.showHidden
            self.directoryList = self.generateFileGrid()

    # Displays Matplotlib sliders to change parameters
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
        Slider(blur, "Blur Size", valmin=1, valmax=9,
        valinit=self.app.blurSize, valstep=2)
        sharpen = \
        Slider(sharpenAx, "Sharpen", valmin=0, valmax=1,
        valinit=int(self.app.sharpen), valstep=1)
        cannyLow = \
        Slider(low, "Edge Low", valmin=1, valmax=1000,
        valinit=self.app.cannyLow, valstep=1)
        cannyHigh = \
        Slider(high, "Edge High", slidermin=cannyLow, valmin=1, valmax=1000,
        valinit=self.app.cannyHigh, valstep=1)
        noiseRate = \
        Slider(noise, "Noise Rate", valmin=0, valmax=5000,
        valinit=self.app.randomNoiseRate, valstep=100)
        nodeSampleDistanceThreshold = \
        Slider(threshold, "Threshold distance", valmin=0, valmax=100,
        valinit=self.app.nodeSampleDistanceThreshold, valstep=5)
        nodeSampleRate = \
        Slider(nodeSample, "Node Sample Rate", valmin=0, valmax=1,
        valinit=self.app.nodeSampleRate, valstep=0.01)
        nodeThresholdRate = \
        Slider(nodeThreshold, "Node Threshold Check Rate", valmin=0, valmax=1,
        valinit=self.app.nodeThresholdRate, valstep=0.01)
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

    # Checks if mouse is hovering over the parameters button
    def checkParametersHover(self, event):
        button = self.parametersButton
        mx, my = event.x, event.y
        if mx > button.x - button.width//2 and \
        mx < button.x + button.width//2 and \
        my > button.y - button.height//2 and \
        my < button.y + button.height//2:
            self.mousePosition = (mx, my)
        else:
            self.mousePosition = (None, None)

    def mouseMoved(self, event):
        self.checkParametersHover(event)

    # Draws box with current parameters on hover
    def drawParametersText(self, canvas, x, y):
        captionColor = LowPolyGenerator.rgbString(180,180,180)
        lighterBackgroundColor = LowPolyGenerator.rgbString(78,78,78)
        text = f" Blur size: {self.app.blurSize} \n Sharpen: {self.app.sharpen} \n Edge Detection Bounds: ({self.app.cannyLow} : {self.app.cannyHigh}) \n Approximate Randomly Sampled Points: {self.app.randomNoiseRate} \n Node Sample Rate: {self.app.nodeSampleRate} \n Node Threshold Distance and Check Rate: {(100*self.app.nodeSampleDistanceThreshold)//100}, {self.app.nodeThresholdRate}"
        canvas.create_rectangle(x - 175, y - 150, x + 175, y - 40, fill=lighterBackgroundColor)
        canvas.create_text(x - 175, y - 50, text=text, fill=captionColor, anchor="sw")

    def redrawAll(self, canvas):
        self.drawGrid(canvas)
        canvas.create_text(self.width - self.previewSize//2, 20,
        text = f"{self.selectedFile}", font="Arial 12", fill=LowPolyGenerator.rgbString(180,180,180))
        if self.previewImage != None:
            canvas.create_image(self.width - self.previewSize//2, self.height//3, image = ImageTk.PhotoImage(self.previewImage))
        canvas.create_rectangle(0,0,self.width-self.previewSize, 60, fill=LowPolyGenerator.rgbString(50,50,50), width=0)
        self.parametersButton.draw(canvas)
        self.helpButton.draw(canvas)
        for button in self.pathButtons:
            button.draw(canvas)
        if self.mousePosition != (None, None):
            self.drawParametersText(canvas, self.mousePosition[0], self.mousePosition[1])

if __name__ == "__main__":
    app = PolyBridge(width=1500, height=1000)
