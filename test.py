import numpy as np
import matplotlib.pyplot as plt
from matplotlib.image import imread
from scipy.spatial import Delaunay
from cmu_112_graphics import *
from tkinter import *
from PIL import Image
import cv2, random, time, os


def plot(filepath):
    im = plt.imread(filepath)
    im = im[: , : , :]
    plt.imshow(im)
    plt.show()



file = "/Users/rohanmjha/Desktop/College/15-112/term-project/images/rafa.jpg"

g = file.split("/")[-1]



t = time.time()
img = imread(file)
print(img.shape)
print("read",(time.time() - t) * 1000)


t = time.time()
gr_img = np.dot(img[:,:,:3], [.3, .6, .1])
print("BROSBNSFBNSB,", gr_img)
# plt.imshow(gr_img, cmap = "gray")
# plt.show()
#gr_img = img
# print("NOJOKE" , gr_img.shape)
gr_img = cv2.blur(img,(3,3))
# print("blurred,", gr_img)
gr_img = cv2.filter2D(gr_img,-1,kernel = np.array([[-1,-1,-1], [-1, 9,-1], [-1,-1,-1]]))
# print("HOW", gr_img)
edges = cv2.Canny(gr_img,1,100)
# print("BRO SRSYLT", type(gr_img))
# print(img.shape,edges.shape)
# print(type(edges))
print("AHOY", edges[190,565])

print("Canny",(time.time() - t) * 1000)

points = []
points.append([0,0])
points.append([gr_img.shape[1],gr_img.shape[0]])
points.append([0,gr_img.shape[0]])
points.append([gr_img.shape[1],0])

sampleRate = edges.shape[0]*edges.shape[1]
print(400/sampleRate)
t = time.time()
for row in range(edges.shape[0]):
    for col in range(edges.shape[1]):

        if edges[row, col] == 255:
            # actual points
            if random.random() > 0.93:
                # edges[row][col] = 0
                points.append((col,row))
        elif random.random() < 400/sampleRate:
            # extra noise
            points.append((col,row))



points = np.array(points)
print("adding points to list",(time.time() - t) * 1000)

tri = Delaunay(points)
print(len(tri.simplices))
# tri.simplices = tri.simplices[50:100]
colorTri = dict()

def getAverageTriangleColor(simplex, points, image):
    # each simplex is a three-list of the indices of points from the passed
    # point array that make a given triangle
    vertices = [points[i] for i in simplex]
    xys = [(arr[0], arr[1]) for arr in vertices]
    r,c = 0,0
    for xy in xys:
        r += xy[0]
        c += xy[1]
    r //= 3
    c //= 3
    return image[c][r]

# from http://www.cs.cmu.edu/~112/notes/notes-graphics-part2.html
def rgbString(red, green, blue):
    return "#%02x%02x%02x" % (red, green, blue)

# Tkinter grpahics starter from
# http://www.cs.cmu.edu/~112/notes/notes-graphics-part1.html


def draw(canvas, width, height):
    canvas.create_rectangle(0,0, width, height, fill = "blue")
    canvas.create_image(width//2, height//2, image = ImageTk.PhotoImage(pilImage))
    # for simplex in tri.simplices:
    #     vertices = [points[i] for i in simplex]
    #     xys = [(arr[0], arr[1]) for arr in vertices]
    #     x0,y0 = xys[0][0],xys[0][1]
    #     x1,y1 = xys[1][0],xys[1][1]
    #     x2,y2 = xys[2][0],xys[2][1]
    #     color = getAverageTriangleColor(simplex, points, img)
    #     red, green, blue = color
    #     colorString = rgbString(red, green, blue)
    #     #print("BRUH", colorString)
    #     canvas.create_polygon(x0,y0,x1,y1,x2,y2, fill = colorString,
    #     width = 0) #add outline = colorString to get rid of thin black outlines

def runDrawing(width=img.shape[1], height=img.shape[0]):
    root = Tk()
    root.resizable(width=False, height=False) # prevents resizing window
    canvas = Canvas(root, width=width, height=height)
    canvas.configure(bd=0, highlightthickness=0)
    canvas.pack()
    draw(canvas, width, height)
    pilImage = Image.open(file)
    root.mainloop()
    print("bye!")

runDrawing()

# print(type(tri))
# print(tri.simplices[0])
# print("delaunay",(time.time() - t) * 1000)
# print(points[tri.simplices[5]])
#
# f = plt.figure()
# f.add_subplot(1,2,1)
# plt.imshow(edges, cmap = 'gray')
# f.add_subplot(1,2,2)
# plt.imshow(gr_img, cmap = 'gray')
# plt.show()
#
# print(edges[0][0])
#
# print(points[:,0].shape)
# #plt.triplot(points[:,0], points[:,1], tri.simplices.copy(), zorder=2)
#
# plt.scatter(points[:,0], points[:,1], zorder=2)
# plt.imshow(img, cmap = "gray", zorder=1)
# plt.show()
#
#
# print(type(img))

"""
Workflow:

Imports
file input
image structuring
image preprocessing (blur, grayscale if appropriate)
edge detection
node deletion based on proximity
add some nodes in super sparse areas using gaussian noise?
delaunay triangulation
triangle filling
color restriction?

USER MODIFIABLE HYPERPARAMETERS:
blur
node sampling rate
gaussian noise
tolerances for canny?

average or center of mass color picking?

OOP Design:



"""
