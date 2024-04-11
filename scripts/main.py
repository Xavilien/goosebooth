#import CMU graphics and built-in python libraries
from cmu_graphics import *
import copy
import math
import random

#import python files from scripts folder
import goose
import trees
import road
import building 
import boy
import instructions
import flowers
import soundAndGraphics 
from board import inBoard, inScreen, cellToCoods, getCellCenter, getCellSize, getCell

'''[Citation]
- Goose sprite was redrawn by me with reference to the original Untitled Goose Game https://goose.game/ 
- Boy sprite obtained from https://stock.adobe.com/images/boy-character-sprite-sheet-with-walk-cycle-and-run-cycle-animation-sequence-boy-character-with-different-poses/453156997
- Lady sprite obtained from https://sketchfab.com/3d-models/female-running-free-animation-20-frames-loop-a2d122fc447248559dc842a0f2865153
- Cage sprite obtained from https://creazilla.com/nodes/1995599-bird-cage-clipart
- Rest of sprites are self-drawn
- All sounds obtained from pixabay https://pixabay.com/'''

def onAppStart(app):
    ''' Define parameters of board. '''
    app.height = 600
    app.width = 600
    app.rows = 23
    app.cols = 23

    ''' Initially, board is zoomed in. '''
    app.isScaledDown = False
    setZoomedInView(app)

    ''' Define colors of key terrain '''
    app.background = rgb(111, 158, 122) # Background is green (grass)
    app.roadFill = rgb(171, 168, 164) # Road is gray

    ''' Set timesteps per second (number of times onStep is called per second) '''
    app.stepsPerSecond = 30
    app.steps = 0 # Counter for number of steps taken thus far

    ''' Define arrays of objects: houses, roads, trees '''
    app.houses = []
    # Ensure there is road wherever goose is standing initially. Note that number of roads is odd, 
    # so math.floor(app.rows/2) would exactly be in the middle
    app.roads = [(math.floor(app.rows/2), math.floor(app.cols/2))]
    # Run the algorithm to pick reasonable grids for roads
    road.chooseRoads(app)
    # Index of road represents whether it is a curve, an intersection, or a straight road 
    # (Depending on whether it is connected to other road chunks on its left/right/up/down) 
    app.roadIdx = []
    app.roadIdx = [road.getIdx(app, row, col) for (row, col) in app.roads]
    # Check for dead ends of roads (ie. only one side connected to another road chunk) 
    # --> place a house there to make it look like a more natural "end of road"
    building.placeHouseAtRoadEnd(app)

    # Pick grid positions such that tree is not on road and not on house
    app.trees = []
    for i in range(10):
        app.trees.append(trees.pickTreePos(app))

    # Create list of flowers
    app.flowers = []
    for i in range(100):
        flowers.addNewFlower(app)

    ''' Define parameters of goose '''
    # Goose will always remain in the middle of the screen
    app.gooseX = app.width/2
    app.gooseY = app.height/2
    # Goose can grow while eating apples. It is allowed to grow up to twice its size.
    # Note that goose is a square sprite, so gooseSize refers to both height, width
    app.gooseSize = 80
    app.gooseSizeLimit = (80, 160)
    # gooseSpriteCounter changes as goose walks to animate the goose
    app.gooseSpriteCounter = 0
    app.gooseDirection = 'left'
    app.gooseIsWalk = False
    # app.gooseSteps stores the 5 previous steps taken by the goose, and are used to determine
    # the position to draw footprints of goose
    app.gooseSteps = []
    app.gooseStepsDirs = [] # directions that footsteps should face
    app.gooseStepSize = 5
    # Populate app.gooseSprites with appropriate set of frames of goose for animation
    # (current frame given by "gooseSpriteCounter")
    goose.getGooseSprite(app, app.gooseDirection)
    # Goose trapped (ie. game over)
    app.gooseTrapped = False

    ''' Convert cell to coordinates. For trees and houses, convert coordinates to objects. '''
    app.roads = cellToCoods(app, app.roads, align = 'center')
    app.houses = cellToCoods(app, app.houses, align = 'center')
    app.trees = cellToCoods(app, app.trees, align = 'center')
    
    for i in range(len(app.trees)):
        cx, cy = app.trees.pop(0)
        app.trees.append(trees.OrchardTree(cx, cy))

    for i in range(len(app.houses)):
        cx, cy = app.houses.pop(0)
        cr, _ = getCellSize(app)
        new_house = building.House(cx, cy, cr)

        if i == 0:
            new_house.houseType = "hawker1"
        elif i == 1:
            new_house.houseType = "hawker2"
        elif i == 2:
            new_house.houseType = "hawker3"

        app.houses.append(new_house)

    ''' Apples can only be eaten when dropped on the ground. 
    Store array of coordinates of dropped apples (that can be eaten)'''
    app.groundApples = []
    app.appleDropped = False

    ''' Load all sound effect files, such as honking and apple eating'''
    soundAndGraphics.defineSounds(app)

    ''' Define attributes of boy sprite'''
    boyWidth = 90
    boyHeight = 150
    # Pick a position for boy such that he is not on the road, on a house, or a tree
    app.boyRow, app.boyCol = boy.pickBoyPos(app)
    print("[For grading purposes] Coordinates of boy:", app.boyRow, app.boyCol)
    boyX, boyY = getCellCenter(app, app.boyRow, app.boyCol)
    app.boyObject = boy.Human(boyX, boyY, boyWidth, boyHeight)

    ''' Define attributes of lady sprite and interaction'''
    ladyWidth = 180
    ladyHeight = 180
    ladyRow, ladyCol = boy.pickLadyPos(app)
    print("[For grading purposes] Coordinates of lady:", ladyRow, ladyCol)
    ladyX, ladyY = getCellCenter(app, ladyRow, ladyCol)
    app.ladyObject = boy.Human(ladyX, ladyY, ladyWidth, ladyHeight)
    app.ladyDirection = 'idle'
    app.ladySpriteCounter = 0
    app.ladyObject.isChasing = False
    app.gracePeriod = False
    app.gracePeriodTimer = 0
    app.chaseTimer = 0
    boy.getLadySprite(app, app.ladyDirection, app.ladyObject)

    ''' Initially, instruction screen is hidden/'''
    app.showGuidebook = False

    app.showWinScreen = False

''' Draw objects in following order to make perspective/overlap correct:
Roads --> Flowers --> Goose footsteps --> Houses, Fallen Apples, Goose, Tree, Boy --> Guidebook --> Instructions'''
def redrawAll(app):
    '''Draw roads'''
    for i, (cx, cy) in enumerate(app.roads):
        size, _ = getCellSize(app)
        if inScreen(app, cx, cy): road.drawRoad(app, cx, cy, app.roadIdx[i], size)
        
    ''' Draw flowers'''
    for flower in app.flowers:
        if inScreen(app, flower.cx, flower.cy): flowers.drawFlower(app, flower)

    '''Draw goose footsteps'''   
    for i, (cx, cy) in enumerate(app.gooseSteps):
        trees.drawTernateShape(app, cx-10, cy+10, h=app.gooseStepSize, fill='saddleBrown', opacity=20+i*20, dir=app.gooseStepsDirs[i])
        trees.drawTernateShape(app, cx+10, cy-10, h=app.gooseStepSize, fill='saddleBrown', opacity=20+i*20, dir=app.gooseStepsDirs[i])

    '''Draw houses'''   
    for house in app.houses:
        if inScreen(app, house.cx, house.cy): building.drawHouse(app, house)

    '''Draw fallen apples'''   
    for apple in app.groundApples:
        cx, cy, cr = apple.cx, apple.cy, apple.cr
        if inScreen(app, cx, cy): trees.drawApple(cx, cy, cr)

    '''Draw goose'''   
    gooseSprite = app.gooseSprites[app.gooseSpriteCounter]
    drawImage(gooseSprite, app.width/2, app.height/2, align = 'center')
    if app.gooseTrapped:
        goose.drawCage(app)

    '''Draw boy'''   
    if inScreen(app, app.boyObject.cx, app.boyObject.cy): 
        boy.drawBoy(app.boyObject)
        if not app.boyObject.happy: boy.drawIceCream(app.boyObject)

    '''Draw lady'''   
    idx = app.ladySpriteCounter if app.ladyObject.isChasing else 0
    ladySprite = app.ladySprites[idx]
    if inScreen(app, app.ladyObject.cx, app.ladyObject.cy): 
        drawImage(ladySprite, app.ladyObject.cx, app.ladyObject.cy, align = 'bottom')

    '''Draw trees'''   
    for tree in app.trees:
        if inScreen(app, tree.cx, tree.cy): trees.drawTree(app, tree)

    ''' Draw timer label if goose is being chased '''
    if app.ladyObject.isChasing:
        drawLabel(f"RUN!! but don't worry, she's getting tired.", app.width, 10, align = 'right')
        drawLabel(f"Just {6 - app.chaseTimer} more seconds.", app.width, 25, align = 'right')


    '''Draw guidebook icon (top left corner of screen)'''   
    instructions.drawGuidebook()

    '''Draw instructions (when guidebook clicked)'''   
    if app.showGuidebook:
        drawRect(0, 0, app.width, app.height, opacity = 50)
        instructions.drawInstructions()

    if app.showWinScreen:
        drawRect(0, 0, app.width, app.height, fill = 'black', opacity = 50)
        offset = 20
        drawLabel("Congratulations!", app.width/2, app.height/2-offset, fill = 'white', size = 30)
        drawLabel("You've found the hawker centre!", app.width/2, app.height/2+offset, fill = 'white', size = 30)


def onKeyHold(app, keys):
    for k in keys:
        if k in {"up", "down", "left", "right"} and not app.gooseTrapped:

            '''1.1 Side-scrolling: When up/down/left/right pressed, shift all objects'''
            # coordinates of roads and goose footsteps are stored in lists
            app.roads = changeListCood(app.roads, k)
            app.gooseSteps = changeListCood(app.gooseSteps, k)
            # house, tree, apple, flower objects are stored in global lists
            for house in app.houses: changeObjectCood(house, k)
            for tree in app.trees: changeObjectCood(tree, k)
            for apple in app.groundApples: changeObjectCood(apple, k)
            for flower in app.flowers: changeObjectCood(flower, k)
            # boy object is a global var
            changeObjectCood(app.boyObject, k)
            if not app.ladyObject.isChasing: changeObjectCood(app.ladyObject, k)

            '''1.2: If goose moves onto house, reverse movement because that is an illegal move'''
            for house in app.houses: 
                if goose.onObstacle(app, house): 
                    r = reverseK(k)
                    app.roads = changeListCood(app.roads, r)
                    app.gooseSteps = changeListCood(app.gooseSteps, r)
                    for house in app.houses: changeObjectCood(house, r)
                    for tree in app.trees: changeObjectCood(tree, r)
                    for apple in app.groundApples: changeObjectCood(apple, r)
                    for flower in app.flowers: changeObjectCood(flower, r)
                    changeObjectCood(app.boyObject, r)
                    if not app.ladyObject.isChasing: changeObjectCood(app.ladyObject, r)
            
            '''1.3 Update goose sprite based on direction'''
            app.gooseDirection = k
            app.gooseIsWalk = True
            goose.getGooseSprite(app, app.gooseDirection)

            '''1.4 If goose moves near crying boy, play crying sound effect. 
            Else, pause it (if goose too far from boy)'''
            if goose.isNear(app, app.boyObject) and not app.boyObject.happy:
                app.cryingSound.play(loop=True)
            else:
                app.cryingSound.pause()


            '''1.5 Reset grace period timer when goose starts moving and lady is chasing him'''
            if app.ladyObject.isChasing: app.gracePeriodTimer = 0

    ''' 2. If goose is near tree, allow goose to shake it by pressing 's' key'''
    if 's' in keys:
        for tree in app.trees:
            if goose.isNear(app, tree): 
                tree.shaking = True
                app.rustleSound.play(loop=True)
    
def onKeyPress(app, key):

    '''1. Press 'a' key to eat apple on ground (after shaking tree)'''
    if key == 'd':
        for apple in app.groundApples:
            if goose.isNear(app, apple): # Check if goose is sufficiently near to an apple
                app.groundApples.remove(apple) # Make the apple disappear
                app.crunchSound.play(restart=True) 
                # If goose is smaller than maximum allowed size, allow goose to grow bigger
                if app.gooseSize < app.gooseSizeLimit[1]: app.gooseSize += 20 
                # Update goose sprite
                goose.getGooseSprite(app, app.gooseDirection)
    
    '''2. Press 'h' key to honk'''
    if key == 'h':
        app.honkSound.play(restart=True)
        # If goose honks near boy, make boy drop ice cream and cry
        if goose.isNear(app, app.boyObject): 
            app.boyObject.happy = False
            app.cryingSound.play(loop=True)
        if goose.isNear(app, app.ladyObject):
            app.gracePeriod = True
            app.ladyObject.isChasing = True
            boy.getLadySprite(app, app.ladyDirection, app.ladyObject)

    ''' 3. Press 'z' to zoom in/out '''
    if key == 'z':
        changeScale(app)
        app.isScaledDown = not app.isScaledDown

    ''' 4. Press 'x' to close guidebook '''
    if key == 'x':
        app.showGuidebook = False
        app.showWinScreen = False

    if key == 'e':
        if goose.isNear(app, app.houses[0]) or goose.isNear(app, app.houses[1]) or goose.isNear(app, app.houses[2]):
            app.showWinScreen = True

def onKeyRelease(app, key):
    # Stop goose walking animation if up/down/left/right released
    if key in {"up", "down", "left", "right"}:
        app.gooseIsWalk = False

    # Stop tree shaking
    for tree in app.trees: tree.shaking = False
    
    if key == 's':
        # Reset appleDropped variable (allow another apple to drop next time shaking starts)
        app.appleDropped = False
        app.rustleSound.pause()

def onStep(app):
    # Update steps counter
    app.steps += 1

    # Regenerate objects
    regenAllObj(app)
    regenRoad(app)
    
    if app.gooseIsWalk: 
        # Animate goose sprite 
        if app.steps%1==0: app.gooseSpriteCounter = (1 + app.gooseSpriteCounter) % len(app.gooseSprites)
        # Save footprints in array every interval
        if app.steps%5 == 0: 
            app.gooseSteps.append((app.width/2+random.randrange(-8,8), app.height/2+30+random.randrange(-8,8)))
            app.gooseStepsDirs.append(app.gooseDirection)
            # Update position of lady
            boy.ladyChase(app, app.ladyObject)
            boy.getLadySprite(app, app.ladyDirection, app.ladyObject)

    # Remove footsteps every interval or when more than 5 have been saved
    if app.steps%app.stepsPerSecond == 0 or len(app.gooseSteps)>= 5:
        if app.gooseSteps!=[]: 
            app.gooseSteps.pop(0)
            app.gooseStepsDirs.pop(0)
            # Update position of lady
            boy.ladyChase(app, app.ladyObject)
            boy.getLadySprite(app, app.ladyDirection, app.ladyObject)

    # Shrink goose every interval until he reaches original size
    if app.steps%75 == 0:
        if app.gooseSize > app.gooseSizeLimit[0]: 
            app.gooseSize -= 20  
            goose.getGooseSprite(app, app.gooseDirection)
    
    # Check if an apple should be dropped
    for tree in app.trees:
        if tree.shaking:
            trees.shakeTree(app, tree)
            if not app.appleDropped: 
                trees.dropApple(app, tree)
                app.thudSound.play(restart=True)
                app.appleDropped = True

    # gracePeriod: Lady not allowed to chase goose
    if app.gracePeriod:
        #print(app.gracePeriodTimer)
        if app.steps%app.stepsPerSecond==0: 
            app.gracePeriodTimer += 1
        if app.gracePeriodTimer >= 5: 
            app.gracePeriod = False
            if not app.gooseIsWalk: 
                app.gooseTrapped = True
                app.ladyObject.isChasing = False
                
    if app.ladyObject.isChasing and app.steps%app.stepsPerSecond==0:
        app.chaseTimer += 1
        if app.chaseTimer >= 6: 
            app.ladyObject.isChasing = False
            app.gracePeriod = False
            app.gooseTrapped = False
            app.chaseTimer = 0

    if app.ladyObject.isChasing:
        app.ladySpriteCounter = (1 + app.ladySpriteCounter) % len(app.ladySprites)
        boy.getLadySprite(app, app.ladyDirection, app.ladyObject)


def onMousePress(app, mouseX, mouseY):
    ''' If guidebook icon clicked, show help instructions for the game '''
    if 20 <= mouseX <= 100  and 20 <= mouseY <= 100:
        app.showGuidebook = True

''' Function that takes LIST OF COORDINATES as input and shifts according to goose movement'''
def changeListCood(L, k):
    speed = 10 
    if k == "up":
        return [(cx, cy+speed) for (cx, cy) in L]
    if k == "down":
        return [(cx, cy-speed) for (cx, cy) in L]
    if k == "right":
        return [(cx-speed, cy) for (cx, cy) in L]
    if k == "left":
        return [(cx+speed, cy) for (cx, cy) in L]
        
''' Function that takes OBJECT (with attributes cx, cy) as input and shifts according to goose movement'''
def changeObjectCood(obj, k):
    speed = 10
    if k == "up":
        obj.cy += speed
    if k == "down":
        obj.cy -= speed
    if k == "right":
        obj.cx -= speed
    if k == "left":
        obj.cx += speed

''' Return the opposite of '''
def reverseK(k):
    if k == "up":
        return "down"
    if k == "down":
        return "up"
    if k == "right":
        return "left"
    if k == "left":
        return "right"


''' Define functions for autogeneration: if coordinate lies outside of current board, add/subtract
boardWidth/boardTop such that it falls within board again. E.g. If object is sent too far left
of the board, it should be regenerated on the right of the board '''

def regenObjects(app, objectList):
    for obj in objectList:
        if obj.cx <= app.boardLeft: 
            obj.cx += app.boardWidth
        elif obj.cx >= app.boardRight:
            obj.cx -= app.boardWidth
        if obj.cy <= app.boardTop:
            obj.cy += app.boardHeight
        elif obj.cy >= app.boardBottom:
            obj.cy -= app.boardHeight
        
def regenAllObj(app):
    allObjects = [app.trees, app.houses,[app.boyObject, app.ladyObject], app.flowers]
    for objectList in allObjects:
        regenObjects(app, objectList)

def regenRoad(app):
    oldCoods = copy.deepcopy(app.roads)
    for i, (cx, cy) in enumerate(oldCoods):
        if cx <= app.boardLeft: 
            app.roads[i] = (cx+app.boardWidth, cy)
        elif cx >= app.boardRight:
            app.roads[i] = (cx-app.boardWidth, cy)
        if cy <= app.boardTop:
            app.roads[i] = (cx, cy+app.boardHeight)
        elif cy >= app.boardBottom:
            app.roads[i] = (cx, cy-app.boardHeight)

''' Zoom in/Zoom out function '''
def changeScale(app):
    # Define whether to scale up or down depending on current view
    scale = (1/0.6) if app.isScaledDown else 0.6 
    # Update size of goose sprite
    app.gooseSize = int(app.gooseSize * scale)
    # Update size of goose footprints
    app.gooseStepSize = int(app.gooseStepSize* scale)
    # Update min and max limits of goose sprite size
    app.gooseSizeLimit = (app.gooseSizeLimit[0]*scale, app.gooseSizeLimit[1]*scale*2)
    # Update goose sprite 
    goose.getGooseSprite(app, app.gooseDirection)
    boy.getLadySprite(app, app.ladyDirection, app.ladyObject)

    # Update size of apples (still attached to trees)
    trees.Apple.size = int(trees.Apple.size * scale)
    
    # Check current row/col in grid for each piece of road
    for i, (cx, cy) in enumerate(app.roads):
        _, _, rowExact, colExact = getCell(app, cx, cy)
        app.roads.pop(i)
        app.roads.insert(i, (rowExact-0.5, colExact-0.5)) #-0.5 because we got the middle of the cell

    # Do the same for all objects 
    objectList = [app.trees, app.groundApples, app.houses, [app.boyObject, app.ladyObject], app.flowers]  
    for objtype in objectList:
        for i, obj in enumerate(objtype):
            _, _, rowExact, colExact = getCell(app, obj.cx, obj.cy)
            obj.rowExact = rowExact-0.5
            obj.colExact = colExact-0.5

    # Resize the board
    if app.isScaledDown:
        setZoomedInView(app)
    else:
        setZoomedOutView(app)
    
    # Notice that current row/col in grid stays the same even after we zoom in/out
    # For roads and each object, convert row, col to coordinates
    app.roads = cellToCoods(app, app.roads, align = 'center')
    
    for objtype in objectList:
        for i, obj in enumerate(objtype):
            obj.cx, obj.cy = getCellCenter(app, obj.rowExact, obj.colExact)
            obj.cr = int(obj.cr*scale)

    for tree in app.trees:
        for i in range(len(tree.leaves)): 
            # Note that tree.leaves[i] = [lx, ly] 
            # lx = leaf displacement from center of tree
            tree.leaves[i][0], tree.leaves[i][1] = tree.leaves[i][0]*scale, tree.leaves[i][1]*scale
        for i in range(len(tree.apples)): 
            tree.apples[i][0], tree.apples[i][1] = tree.apples[i][0]*scale, tree.apples[i][1]*scale
    
    # Objects that aren't square. apart from shifting cr, (which is height).
    # we must shift width cw.
    app.boyObject.cw *= scale
    app.ladyObject.cw *= scale


''' Define functions to zoom in or zoom out by adjusting size of board '''
def setZoomedInView(app):
    app.boardLeft = -app.width * 2
    app.boardTop = -app.height * 2
    app.boardRight = app.width * 3
    app.boardBottom = app.height * 3
    app.boardWidth = app.width*5
    app.boardHeight = app.height*5

def setZoomedOutView(app):
    app.boardLeft = -app.width
    app.boardTop = -app.height 
    app.boardRight = app.width*2 
    app.boardBottom = app.height*2 
    app.boardWidth = app.width*3
    app.boardHeight = app.height*3
    
def main():
    runApp()

main()
