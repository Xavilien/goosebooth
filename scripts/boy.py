from cmu_graphics import *
import random
from soundAndGraphics import openImage

''' Boy will belong to human class, ice cream belong to randomItem class'''
class Human:
    #cx, cy: center coordinates of boy, cw: width, cr: height
     def __init__(self, cx, cy, cw, cr): 
          self.cx, self.cy, self.cw, self.cr = cx, cy, cw, cr
          self.happy = True

class randomItem:
    # cr is radius of item
     def __init__(self, cx, cy, cr):
          self.cx, self.cy, self.cr = cx, cy, cr

''' Pick possible grid position of boy such that he does not stand on roads, houses and trees'''
def pickBoyPos(app):
    row, col = (random.randrange(app.rows), random.randrange(app.cols)) 
    if (row, col) in app.roads or (row, col) in app.houses or (row, col) in app.trees:
        return pickBoyPos(app) 
    else:
        return (row, col)

''' Function to draw boy in redrawAll (main.py)'''
def drawBoy(boyObject):
    if boyObject.happy:
        boy = openImage('../graphics/happyboy.png') 
    else:
        boy = openImage('../graphics/cryingboy.png') 

    boy = boy.resize((int(boyObject.cw), int(boyObject.cr)))
    boy = CMUImage(boy)
    drawImage(boy, boyObject.cx, boyObject.cy, align = 'center')

''' Function to draw ice cream in redrawAll (main.py)'''
def drawIceCream(boyObject):
    icecream = openImage('../graphics/icecream.png') 
    icecream = icecream.resize((int(boyObject.cr*0.2), int(boyObject.cr*0.2)))
    icecream = CMUImage(icecream)
    drawImage(icecream, boyObject.cx-boyObject.cw*0.55, boyObject.cy+boyObject.cr*0.45, align = 'center')

''' Pick possible grid position of lady'''
def pickLadyPos(app):
    row, col = (random.randrange(app.rows), random.randrange(app.cols)) 
    if (row, col) in app.roads or (row, col) in app.houses or (row, col) in app.trees or (row, col) == (app.boyRow, app.boyCol):
        return pickLadyPos(app)
    else:
        return (row, col)


def ladyChase(app, ladyObject):
    if ladyObject.isChasing:
        if app.gooseSteps!=[]: 
            ladyObject.cx, ladyObject.cy = app.gooseSteps[0]
            app.ladyDirection = app.gooseStepsDirs[0]
            getLadySprite(app, app.ladyDirection, app.ladyObject)
        else:
            ladyObject.cx, ladyObject.cy = (app.width/2 - ladyObject.cw, app.height/2 + ladyObject.cr/2)
            app.gooseTrapped = True
            ladyObject.isChasing = False

def getLadySprite(app, direction, ladyObject):
    app.ladySprites = []
    if not ladyObject.isChasing or direction == 'idle':
        sprite = openImage('../graphics/lady_idle.png')
        sprite = sprite.resize((int(ladyObject.cw), int(ladyObject.cr)))
        sprite = CMUImage(sprite)
        app.ladySprites.append(sprite)
    else:
        spritestrip = openImage(f'../graphics/lady_{direction}_spritesheet.png')
        num = 6 if direction == 'left' or direction == 'right' else 5
        for i in range(num):
            # Seperate lady sprites in sprite sheet and crop them to the right size
            sprite = spritestrip.crop((0+500*i, 0, 500+500*i, 500))
            sprite = sprite.resize((int(ladyObject.cw), int(ladyObject.cr)))
            sprite = CMUImage(sprite)
            app.ladySprites.append(sprite)