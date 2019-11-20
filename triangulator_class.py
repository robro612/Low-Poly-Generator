import numpy as np
import matplotlib.pyplot as plt
from matplotlib.image import imread
from scipy.spatial import Delaunay
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
    def __init__(self, imagePath, blurSize=3, sharpen=True,
                nodeSampleDistanceThreshold=10, randomNoiseRate=400,
                cannyLow=50, cannyHigh=100, verbose=False,
                saveResults=False):
        self.path = imagePath
        self.blurSize = blurSize
        self.sharpen = sharpen
        self.nodeSampleDistanceThreshold = nodeSampleDistanceThreshold
        self.randomNoiseRate = randomNoiseRate
        self.cannyLow = cannyLow
        self.cannyHigh = cannyHigh
        self.verbose = verbose
        self.saveResults = saveResults
        self.image = self.loadImage()

    #Loads image using matplotlib's imread method
    def loadImage(self):
        try:
            image = imread(self.path)
        except:
            print("Image was not found in directory")
            return
        if self.verbose:
            fileName = self.path.split("/")[-1]
            print(f"Loading Image: {fileName}")
        return image

    # preprocesses image using grayscale and blur for speed, and a sharpen
    # filter for increased edge detection
    def preProcessImage(self):
        message = ""
        preProcessed = np.dot(self.image[:, :, :3], [0.3, 0.6, 0.1])
        message += "Converting to grayscale \n"
        if self.blurSize > 0:
            preProcessed = cv2.blur(self.image,
            (self.blurSize, self.blurSize))
            message += \
            f"Blurring with a normalized box filter of size {self.blurSize} \n"
        else:
            preProcessed = cv2.blur(self.image,
            (1, 1))
        if self.sharpen:
            preProcessed = cv2.filter2D(preProcessed, -1,
            kernel = np.array([[-1,-1,-1], [-1, 9,-1], [-1,-1,-1]]))
            message += "Sharpening \n"
        if self.verbose:
            print(message)
        # print("BRUH", preProcessed.shape, preProcessed)
        return preProcessed

    # takes in two tuples, returns euclidean distance
    @staticmethod
    def distance(point1, point2):
        x1, y1 = point1
        x2, y2 = point2
        return ((x2-x1)**2 + (y2-y1)**2)**0.5

    # Uses Canny edge detection to get all nodes, then pares them down by
    # removing all withing a given radius of another
    # returns a list of nodes in tuple form
    def edgeDetection(self):
        # uses cv2's canny edge detection filter
        #CHANGE THESE PARAMETERS BACK TO CANNYLOW AND HIGH
        canny = cv2.Canny(self.preProcessed, self.cannyLow, self.cannyHigh)
        nodes = []
        threshold = self.nodeSampleDistanceThreshold
        noiseProbability = self.randomNoiseRate / \
        (canny.shape[0]*canny.shape[1])
        for row in range(canny.shape[0]):
            for col in range(canny.shape[1]):
                if canny[row, col] == 255 and random.random() < 100000/(self.image.shape[0]*self.image.shape[1]):
                    nodes.append((col, row))
                elif random.random() < noiseProbability:
                    nodes.append((col, row))
        # removes nodes in nodeSampleDistanceThreshold distance
        i = 0
        count = 0
        threshold = 2
        while i < len(nodes):
            j = i + 1
            while j < len(nodes):
                if random.random() > .99 and LowPolyGenerator.distance(nodes[i], nodes[j]) < threshold:
                    count += 1
                    nodes.pop(j)
                else:
                    j += 1
            if i % 100 == 0:
            i += 1
        print(f"{count} nodes were within {threshold} of each other")
        # adds the corners to ensure the complete space
        for point in [(0,0), (0,self.image.shape[0]), (self.image.shape[1],0),
        (self.image.shape[1], self.image.shape[0])]:
            if point not in nodes:
                nodes.append(point)
        return nodes, canny

    def getAverageColor(self, simplex):
        # each simplex is a three-list of the indices of points from the passed
        # point array that make a given triangle
        nodes = self.nodes
        image = self.image
        vertices = [nodes[i] for i in simplex]
        points = [(vertex[0], vertex[1]) for vertex in vertices]
        row,col = 0,0
        for point in points:
            row += point[0]
            col += point[1]
        row //= 3
        col //= 3
        return image[col][row]

    # RGB conversion formula from
    # http://www.cs.cmu.edu/~112/notes/notes-graphics-part2.html
    @staticmethod
    def rgbString(r,g,b):
        return "#%02x%02x%02x" % (r, g, b)

    # uses scipy's implementation of Delaunay triangulation
    def triangulate(self):
        delaunay = Delaunay(self.nodes)
        simplices = delaunay.simplices
        triangles = dict()
        # iterates for each triple vertices of a given triangle
        for simplex in simplices:
            r,g,b = self.getAverageColor(simplex)
            triangles[tuple(simplex)] = self.rgbString(r,g,b)
        return triangles, delaunay

    # Wrapper method call that returns all relevant information including
    # triangle dict that defines lowPoly image, delaunay object for new changes,
    # and the original image and its path
    def generateTriangulation(self):
        start = time.time()
        self.preProcessed = self.preProcessImage()
        self.nodes, self.canny = self.edgeDetection()
        self.triangles, self.delaunay = self.triangulate()
        end = time.time()
        if self.verbose:
            print(f"Time to generate: {end-start}")
        return self.triangles, self.delaunay, self.image, self.path

lowPolyGenerator = LowPolyGenerator("/Users/rohanmjha/Desktop/College/15-112/term-project/images/nico.jpg")

def draw(canvas, width, height, triangles, nodes):
    canvas.create_rectangle(0,0, width, height, fill = "black")
    for simplex in triangles:
        x0,y0 = nodes[simplex[0]][0], nodes[simplex[0]][1]
        x1,y1 = nodes[simplex[1]][0], nodes[simplex[1]][1]
        x2,y2 = nodes[simplex[2]][0], nodes[simplex[2]][1]
        canvas.create_polygon(x0,y0,x1,y1,x2,y2, fill = triangles[simplex],
        width = 0)
        # add outline = colorString to get rid of thin black outlines

def runDrawing(lowPolyGenerator):
    root = Tk()
    root.resizable(width=False, height=False) # prevents resizing window
    canvas = Canvas(root, width = lowPolyGenerator.image.shape[1],
    height = lowPolyGenerator.image.shape[0])
    canvas.configure(bd=0, highlightthickness=0)
    canvas.pack()
    draw(canvas, lowPolyGenerator.image.shape[1],
    lowPolyGenerator.image.shape[0], lowPolyGenerator.triangles,
    lowPolyGenerator.nodes)
    root.mainloop()
    print("bye!")

path = "/Users/rohanmjha/Desktop/College/15-112/term-project/images/nico.jpg"
lowPolyGenerator = LowPolyGenerator(path)
lowPolyGenerator.generateTriangulation()
runDrawing(lowPolyGenerator)

plt.imshow(lowPolyGenerator.canny)
plt.show()
