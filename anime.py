# This demos getSnapshot and saveSnapshot

from cmu_112_graphics import *
from tkinter import *

class MyApp(App):
    def appStarted(self):
        self.image = None

    def keyPressed(self, event):
        if (event.key == 'g'):
            snapshotImage = self.getSnapshot()
            self.image = self.scaleImage(snapshotImage, 0.4)
        elif (event.key == 's'):
            a = getscreen().getcanvas()
            print(a)

    def redrawAll(self, canvas):
        canvas.create_text(350, 20, text='Press g to getSnapshot')
        canvas.create_text(350, 40, text='Press s to saveSnapshot')
        canvas.create_rectangle(50, 100, 250, 500, fill='cyan')
        if (self.image != None):
            canvas.create_image(525, 300, image=ImageTk.PhotoImage(self.image))

MyApp(width=700, height=600)
