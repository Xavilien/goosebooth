from cmu_graphics import *
from soundAndGraphics import openImage

''' Function to draw guidebook icon (top left corner) in redrawAll (main.py) '''
def drawGuidebook():
    book = openImage(f'../graphics/guidebook.png')
    book = book.resize((100, 100))
    book = CMUImage(book)
    drawImage(book, 20, 20)

''' Function to draw instructions in redrawAll (main.py)'''
def drawInstructions():
    book = openImage(f'../graphics/instructions2.png')
    book = book.resize((400, 282))
    book = CMUImage(book)
    drawImage(book, app.width/2, app.height/2, align = 'center')