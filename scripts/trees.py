from cmu_graphics import *
import random
from soundAndGraphics import openImage

''' Class for trees: 3 types of trees '''
class OrchardTree:
    size = 100
    def __init__(self, cx, cy):
        # cx, cy: coordinates of center of trees; cr: radius of tree
        self.cx, self.cy = cx, cy
        cr = self.cr = OrchardTree.size 
        self.shaking = False
        self.leafType = random.choice(['oval', 'ternate', 'star'])
        # coordinates of leaves and apples relative to center of tree are stored in an array
        self.leaves = []
        self.apples = []
        # vary the shades of leaves
        leafColors = ['forestgreen', 'darkgreen', 'green']
        # ternate leaves consist of 3 ovals, take longer time to draw. So draw less
        numLeaves = 100 if self.leafType != 'ternate' else 50

        # pick random positions within circle to place leaves and apple
        for i in range(numLeaves):
            while True:
                lx, ly = random.randrange(-cr, cr), random.randrange(-cr, cr)
                if distance(lx+cx, ly+cy, cx, cy) <= cr: # ensure that coords are within circle
                    self.leaves.append([lx, ly, random.randrange(len(leafColors)), random.randrange(180)])
                    break

        # place random number of apples
        for i in range(random.randrange(1, 4)):
            while True:
                lx, ly = random.randrange(-cr, cr), random.randrange(-cr, cr)
                if distance(lx+cx, ly+cy, cx, cy) <= cr:
                    self.apples.append([lx, ly])
                    break

''' Apples fallen to the ground '''
class Apple: 
    size = 25
    def __init__(self, cx, cy):
        self.cx, self.cy = cx, cy
        self.cr = Apple.size

def distance(x1, y1, x2, y2):
    return ((x1-x2)**2+(y1-y2)**2)**0.5

''' Pick position of trees such that they do not cover roads and houses '''
def pickTreePos(app):
    row, col = (random.randrange(app.rows), random.randrange(app.cols)) 
    return pickTreePos(app) if (row, col) in app.roads or (row, col) in app.houses else (row, col)

''' Define function to draw trees '''
def drawTree(app, treeObject):
    # draw leaves and then apples on top
    if isinstance(treeObject, OrchardTree):
        leafColors = ['forestgreen', 'darkgreen', 'green'] 
        for (lx, ly, color_index, angle) in treeObject.leaves:
            cr = treeObject.cr
            if treeObject.leafType == 'oval':
                drawOval(lx+treeObject.cx, ly+treeObject.cy, cr/3, cr/6, fill=leafColors[color_index], rotateAngle=angle)
            elif treeObject.leafType == 'ternate':
                drawTernateShape(app, lx+treeObject.cx, ly+treeObject.cy, h=cr/6, fill=leafColors[color_index], dir="up")
            elif treeObject.leafType == 'star':
                drawStar(lx+treeObject.cx, ly+treeObject.cy, cr/3, 5, fill=leafColors[color_index], roundness=20, rotateAngle=angle)

        for (lx, ly) in treeObject.apples:
            drawApple(lx+treeObject.cx, ly+treeObject.cy, int(cr/4))

''' Define function to draw apples '''
def drawApple(cx, cy, size=Apple.size, split=False):
    if split:
        apple = openImage('../graphics/duriansplit.png')
    else:
        apple = openImage('../graphics/durian.png')
    size *= 2
    apple = apple.resize((size, size))
    apple = CMUImage(apple)
    drawImage(apple, cx, cy, align = 'center')

''' Draw shape of ternate leaves for trees. This shape is also used for goose footprints'''
def drawTernateShape(app, cx, cy, h=10, fill='black', opacity=100, dir="up"):
    if dir == "up":
        drawOval(cx-h*0.5, cy, h, h*2, rotateAngle = -45, fill = fill, opacity = opacity, align = 'bottom')
        drawOval(cx, cy, h, h*2, fill = fill, opacity = opacity, rotateAngle = 0, align = 'bottom')
        drawOval(cx+h*0.5, cy, h, h*2, rotateAngle = +45, fill = fill, opacity = opacity, align = 'bottom')
    elif dir == "down":
        drawOval(cx-h*0.5, cy, h, h*2, rotateAngle = 90-45, fill = fill, opacity = opacity, align = 'bottom')
        drawOval(cx, cy+h*0.5, h, h*2, fill = fill, opacity = opacity, rotateAngle = 0, align = 'bottom')
        drawOval(cx+h*0.5, cy, h, h*2, rotateAngle = 90+45, fill = fill, opacity = opacity, align = 'bottom')
    elif dir == "left":
        drawOval(cx, cy+h*0.5, h, h*2, rotateAngle = 90-45, fill = fill, opacity = opacity, align = 'right')
        drawOval(cx, cy, h, h*2, fill = fill, opacity = opacity, rotateAngle = 90, align = 'right')
        drawOval(cx, cy-h*0.5, h, h*2, rotateAngle = 90+45, fill = fill, opacity = opacity, align = 'right')
    if dir == "right":
        drawOval(cx, cy+h*0.5, h, h*2, rotateAngle = 90+45, fill = fill, opacity = opacity, align = 'left')
        drawOval(cx, cy, h, h*2, fill = fill, opacity = opacity, rotateAngle = 90, align = 'left')
        drawOval(cx, cy-h*0.5, h, h*2, rotateAngle = 90-45, fill = fill, opacity = opacity, align = 'left')


''' What to do when tree shakes and apple drops '''
def dropApple(app, treeObject):
    if treeObject.apples !=[]:
        # remove apple from treeObject 
        ax, ay = treeObject.apples.pop()
        # find absolute coordinates (ax, ay) in list is relative to coordinates of center of tree
        ax, ay = ax+treeObject.cx, ay+treeObject.cy
        # find new coordinates of fallen apple below tree
        newApple = Apple(ax, treeObject.cy + treeObject.cr + 20)
        # add to global list of fallen apples
        app.groundApples.append(newApple)

''' Animate leaves when shaking trees:
For Oval/Star trees: Rotate leaves
For Ternate trees: Move leaves up and down '''
def shakeTree(app, treeObject):
    for leaf in treeObject.leaves:
        if app.steps % 2 == 0:
            if treeObject.leafType == 'oval' or treeObject.leafType == 'star': 
                leaf[3] += 20
            else:
                leaf[1] += 5
        elif app.steps % 1 == 0: 
            if treeObject.leafType == 'oval' or treeObject.leafType == 'star': 
                leaf[3] -= 20
            else:
                leaf[1] -= 5
