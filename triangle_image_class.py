import numpy as np
import matplotlib.pyplot as plt
from matplotlib.image import imread
from scipy.spatial import Delaunay
from tkinter import *
from cmu_112_graphics import *
from triangulator_class import *
from PIL import Image
import cv2, random, time, io
# DELETE LIBRARIES NOT NEEDED IN THIS FILE

# This class will hold the image, both in its triangulated and regular forms
# and will have an option to save it as a scaleable static image from TK render
# rather than trying to animate real time every vertex and such

class LowPolyImage:
    def __init__(self, generator, path):
        self.lowPolyGenerator = generator
        self.pilImage = Image.open(path)
        self.tkImage = ImageTk.PhotoImage(self.pilImage)
        self.path = path
        self.imageSize = self.lowPolyGenerator.image.shape[:-1]
        self.triangles = self.lowPolyGenerator.triangles

    def drawImage(self, canvas, width, height):
        draw(canvas, width, height, self.lowPolyGenerator.triangles,
        self.lowPolyGenerator.nodes)

    def createThumbnail(self, thumbnailSize):
        w, h = self.pilImage.size
        app = ThumbnailRender(width = w, height = h, lowPolyImage = self, thumbnailSize = thumbnailSize)
        app.quit()



class ThumbnailRender(App):
    def appStarted(self):
        self.timerDelay = 100
        self.lowPolyImage = None

    def loadParams(self, lowPolyImage, thumbnailSize):
        self.lowPolyImage = lowPolyImage
        self.thumbnailSize = thumbnailSize
        return self

    def redrawAll(self, canvas):
        if self.lowPolyImage != None:
            self.lowPolyImage.drawImage(canvas, self.width//2, self.height//2)
            draw(canvas, self.width, self.height, self.lowPolyGenerator.triangles,
            self.lowPolyGenerator.nodes)
            # poly image canvas saving from https://stackoverflow.com/questions/34777676/how-to-convert-a-python-tkinter-canvas-postscript-file-to-an-image-file-readable
            ps = canvas.postscript(colormode='color')
            #print(self.ps)
            image = Image.open(io.BytesIO(ps.encode('utf-8')))
            image.save('./Images/thumbnail.jpg')
            self.quit()
