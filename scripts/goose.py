from cmu_graphics import *
from soundAndGraphics import openImage

def distance(x1, y1, x2, y2):
    return ((x1-x2)**2+(y1-y2)**2)**0.5

''' Change set of goose sprite images based on direction'''
def getGooseSprite(app, direction):
    if direction == 'left':  
        spritestrip = openImage('../graphics/gooseLeft_spritesheet.png')
    elif direction == 'right':
        spritestrip = openImage('../graphics/gooseRight_spritesheet.png')
    elif direction == "down":
        spritestrip = openImage('../graphics/gooseDown_spritesheet.png')
    elif direction == "up":
        spritestrip = openImage('../graphics/gooseUp_spritesheet.png')

    # [Citation] This code was written with reference to the Piazza post
    app.gooseSprites = [ ]
    for i in range(5):
        # Seperate goose sprites in sprite sheet and crop them to the right size
        sprite = spritestrip.crop((0+500*i, 0, 500+500*i, 500))
        sprite = sprite.resize((app.gooseSize, app.gooseSize))
        sprite = CMUImage(sprite)
        app.gooseSprites.append(sprite)

''' Check if goose within circular radius of the object'''
def isNear(app, obj):
    return distance(obj.cx, obj.cy, app.height/2, app.width/2) <= (obj.cr + app.gooseSize/2)
     
''' Check if goose overlaps with rectangular object (e.g. illegal move by moving onto house) '''
# Essentially, we can check if two rectangles overlap
def onObstacle(app, obj):
    # the first rectangle: goose
    left0 = app.gooseX - app.gooseSize/2
    right0 = app.gooseX + app.gooseSize/2
    top0 = app.gooseY - app.gooseSize/2
    bottom0 = app.gooseY + app.gooseSize/2

    # the second rectangle:
    left1 = obj.cx - obj.cr/2
    right1 = obj.cx + obj.cr/2
    top1 = obj.cy - obj.cr/2
    bottom1 = obj.cy + obj.cr/2

    return ((right1 >= left0) and (right0 >= left1) and
        (bottom1 >= top0) and (bottom0 >= top1))

''' Draw cage when goose is trapped'''
def drawCage(app):
    cage = openImage('../graphics/cage.png') 
    cage = cage.resize((int(app.gooseSize*1.2), int(app.gooseSize*1.742)))
    cage = cage.convert('RGBA')
    cage = CMUImage(cage)
    drawImage(cage,app.width/2, app.height/2, align = 'center')