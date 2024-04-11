from cmu_graphics import *
import random
from board import getCellLeftTop, getCellSize
from soundAndGraphics import openImage

class Flower:
    size = 24
    #cx, cy: center coordinates of flower, cr: length of flower (rectangle image)
    def __init__(self, cx, cy):
        self.cx, self.cy, self.cr = cx, cy, Flower.size
        # colors: red, purple, yellow, blue
        self.flowerColor = random.choice([rgb(222, 131, 131), rgb(222, 122, 195), rgb(246, 177, 86), rgb(131, 196, 222)])
    
    def overlap(self, other):
        return abs(self.cx - other.cx) < self.cr and abs(self.cy - other.cy) < self.cr

def addNewFlower(app):
    # Pick possible grid position of flower such that they are not on roads, houses and trees
    row, col = (random.randrange(app.rows), random.randrange(app.cols)) 
    if (row, col) in app.roads or (row, col) in app.houses or (row, col) in app.trees:
        return addNewFlower(app) 
    else:
        # within chosen grid, pick random position
        ltx, lty = getCellLeftTop(app, row, col)
        cellWidth, cellHeight = getCellSize(app)
        cx, cy = (ltx + random.randrange(int(Flower.size), int(cellWidth-Flower.size)), lty + random.randrange(int(Flower.size), int(cellHeight-Flower.size))) 
        newFlower = Flower(cx, cy)
        if not overlapsWithExistingFlowers(app, newFlower):
            app.flowers.append(newFlower)
        else:
            return addNewFlower(app) 

def overlapsWithExistingFlowers(app, flowerObject):
    for existingFlower in app.flowers:
        if flowerObject.overlap(existingFlower):
            return True
    return False

''' Function to draw flower in redrawAll (main.py)'''
def drawFlower(app, flowerObject):
    alignList = ['bottom', 'bottom-left', 'left', 'top-left', 'top', 'top-right', 'right', 'bottom-right']
    for i in range(8):
        drawOval(flowerObject.cx, flowerObject.cy, flowerObject.cr*0.2, flowerObject.cr*0.5, align = alignList[i], rotateAngle = i*45, fill = flowerObject.flowerColor)
    drawCircle(flowerObject.cx, flowerObject.cy, flowerObject.cr*0.1, fill = 'lightyellow')
