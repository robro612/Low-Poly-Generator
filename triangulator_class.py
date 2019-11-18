import numpy as np
import matplotlib.pyplot as plt
from matplotlib.image import imread
from tkinter import *
import cv2, random, time
# Uses numpy for storage of images
# matplot lib to plot intermediate renders of edge detected nodes
# and triangle vertices as well as load jpegs as image ndarrays
# tkinter for rendering final image and sliders to alter paramerters
# cv2 for canny and delaunay
# random for random noise to break up sparse areas (will try sparse gaussian
# noise as well for efficiency)
# time to test runtime during testing

class LowPolyGenerator():
    def __init__(self, imagePath, blurSize=3, grayScale=False,
                nodeSampleRate=0.01, randomNoiseRate=0.0001, verbose = False,
                saveResults = False):
        self.path = imagePath
        self.blurSize = blurSize
        self.nodeSampleRate = nodeSampleRate
        self.randomNoiseRate = randomNoiseRate
        self.verbose = verbose
        self.saveResults = saveResults
        self.img = self.loadImage()


    def loadImage(self):
        try:
            img = imread(self.path)
        except:
            print("Image was not found in directory")
            return
        if self.verbose:
            fileName = self.path.split("/")[-1]
            print(f"Loading Image: {fileName}")
        return image

    def preProcessImage(self, img, blurSize, grayScale):
        msg = ""
        if grayScale:
            preProcessed= np.dot(img[...,:3], [.3, .6, .1])
            mgs += "Converting to grayscale \n"
        if blurSize > 0:
            preProcessed = cv2.blur(img, (blurSize, blurSize))
            msg += f"blurring with a normalized box filter of size {blurSize}"
        if self.verbose:
            print(msg)
        return preProcessed
