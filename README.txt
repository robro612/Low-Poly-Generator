
LOWPOLYGEN: Adobe-Bridge-esque Low Poly Image Renderer
By Rohan Jha

LowPolyGen uses cmu112's animation framework to mimic the user experience and
aesthetics of Adobe Bridge, but renders an image in a low-poly style reminiscent
of early 90's video game polygon meshes. In addition to simply generating these
renders, the user can actively change the render parameters and experience the
differences.

HOW TO RUN:
Simply run the animation_class.py file as main from the term-project working directory to begin.

Necessary Libraries:
numpy
matplotlib
scipy
tkinter
cmu_112_graphics*
PIL
cv2
random
time
io

*Note that the cmu_112_graphics package in this folder has been modified to 
allow a crucial MVC violation that allows rendering to happen. Vanilla cmu_112_graphics packages will not work.

SHORTCUTS:
"s" to save a render to the Saved folder in term-project folder
"p" to change parameters
"h" to go to help screen"
Left/Right arrow keys to zoom file grid
Up/Down to scroll file grid
