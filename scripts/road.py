from cmu_graphics import *
import random
from board import inBoard

''' Index of road represents type : For a square on the grid picked to be part of road,
how many sides of that square is connected to other roads?'''
def getIdx(app, row, col):
    indexDict = getIndexDict()
    adjacentRoads = getAdjacent(app, row, col)
    return indexDict[adjacentRoads]

'''
The following maps type of connnected roads to the index we will reference.
(up, down, left, right) --> e.g. If current road is connected to another road above it on the grid, 
the first component will be 1. 
{(0, 0, 0, 0): 0, 
(0, 0, 0, 1): 1, 
(0, 0, 1, 0): 2, 
(0, 0, 1, 1): 3, 
(0, 1, 0, 0): 4, 
(0, 1, 0, 1): 5, 
(0, 1, 1, 0): 6, 
(0, 1, 1, 1): 7, 
(1, 0, 0, 0): 8, 
(1, 0, 0, 1): 9, 
(1, 0, 1, 0): 10, 
(1, 0, 1, 1): 11, 
(1, 1, 0, 0): 12, 
(1, 1, 0, 1): 13, 
(1, 1, 1, 0): 14, 
(1, 1, 1, 1): 15}
'''
def getIndexDict():
    binary_values = [0, 1]
    res = dict()

    idx = 0
    for i in binary_values:
        for j in binary_values:
            for k in binary_values:
                for l in binary_values:
                    res[(i, j, k, l)] = idx
                    idx += 1
    return res

''' Check which sides of current road also contain road '''
def getAdjacent(app, row, col):
    dirs = [(0, -1), (0, 1), (-1, 0), (1, 0)]
    res = [0, 0, 0, 0]
    for i, (dx, dy) in enumerate(dirs):
        if (row+dy,col+dx) in app.roads: res[i] = 1
    return tuple(res)

''' Build connected roads by recursing with a modified Wilson's algorithm '''
def chooseRoads(app):
    for i in range(3):
        currentPath = set()

        while True:
            # Pick a random position to start from 
            currRow, currCol = (random.randrange(1, app.rows-1), random.randrange(1, app.cols-1)) #avoid edges so can put house
            if not isConnected(app.roads, currRow, currCol): 
                currentPath.add((currRow, currCol))
                currentPath = wilsonWalk(app, currentPath, currRow, currCol)
                if currentPath != None: 
                    app.roads = sorted(set(app.roads)|currentPath)
                    break

''' Modified Wilson's algorithm'''
def wilsonWalk(app, currentPath, currRow, currCol):
    
    # Base case: If reached part of existing roads that have been picked
    if isConnected(app.roads, currRow, currCol):
        return currentPath
    else:
        # Move in random directions from current position till we reach existing road
        dirs = [(-1, 0), (0, -1), (1, 0), (0, 1)]
        while dirs!=[]:
            dir_i = random.randrange(len(dirs))
            dx, dy = dirs[dir_i]
            nextRow, nextCol = (currRow + dx, currCol + dy) 
            # Do not connect to current path we are building from random position to existing road
            if not isConnected(currentPath, nextRow, nextCol, currRow, currCol) and inBoard(app, nextRow, nextCol): 
                currentPath.add((nextRow, nextCol))
                sol = wilsonWalk(app, currentPath, nextRow, nextCol)
                if sol!= set(): return sol
            dirs.pop(dir_i)
        return set()

''' Check if a certain cell is connected to an existing road '''
def isConnected(existingPath, testRow, testCol, prevRow = None, prevCol = None):
    dirs = [(-1, 0), (0, -1), (1, 0), (0, 1), (0, 0)]
    for dx, dy in dirs:
        if (testRow+dx,testCol+dy)!=(prevRow, prevCol) and (testRow+dx,testCol+dy) in existingPath: 
            return True
    return False

''' Use CMU graphics to draw the roads '''
def drawRoad(app, cx, cy, idx, size):
    roadWidth = 0.6
    innerWidth = 1 - roadWidth
    
    if idx == 1 or idx == 2 or idx == 3: # [0, 0, 0, 1], [0, 0, 1, 0], [0, 0, 1, 1]  -- right, left
        drawRect(cx, cy, size, size*roadWidth, align = "center", fill=app.roadFill)
        drawHorizontalDottedLine(cx, cy, size)
    elif idx == 4 or idx == 8 or idx == 12: # [0, 1, 0, 0], [1, 0, 0, 0], [1, 1, 1, 0]  -- down, up
        drawRect(cx, cy, size*roadWidth, size, align = "center", fill=app.roadFill)
        drawVerticalDottedLine(cx, cy, size)
    elif idx == 11: #[1, 0, 1, 1] -- T up
        ulx, uly = getCorner(cx, cy, size, 'ul')
        drawRect(ulx, uly, size, size*(roadWidth+innerWidth/2), align = "left-top", fill=app.roadFill)
        drawCurvedRoad(app, cx, cy, size, 'ul', roadWidth)
        drawCurvedRoad(app, cx, cy, size, 'ur', roadWidth)
        drawHorizontalDottedLine(cx, cy, size)
    elif idx == 7: #[0, 1, 1, 1] -- T down
        llx, lly = getCorner(cx, cy, size, 'll')
        drawRect(llx, lly, size, size*(roadWidth+innerWidth/2), align = "left-bottom", fill=app.roadFill)
        drawCurvedRoad(app, cx, cy, size, 'll', roadWidth)
        drawCurvedRoad(app, cx, cy, size, 'lr', roadWidth)
        drawHorizontalDottedLine(cx, cy, size)
    elif idx == 13: #[1, 1, 0, 1] -- T right
        urx, ury = getCorner(cx, cy, size, 'ur')
        drawRect(urx, ury, size*(roadWidth+innerWidth/2), size, align = "right-top", fill=app.roadFill)
        drawCurvedRoad(app, cx, cy, size, 'ur', roadWidth)
        drawCurvedRoad(app, cx, cy, size, 'lr', roadWidth)
        drawVerticalDottedLine(cx, cy, size)
    elif idx == 14: #[1, 1, 1, 0] -- T left
        ulx, uly = getCorner(cx, cy, size, 'ul')
        drawRect(ulx, uly, size*(roadWidth+innerWidth/2), size, align = "left-top", fill=app.roadFill)
        drawCurvedRoad(app, cx, cy, size, 'ul', roadWidth)
        drawCurvedRoad(app, cx, cy, size, 'll', roadWidth)
        drawVerticalDottedLine(cx, cy, size)
    elif idx == 15: 
        drawRect(cx, cy, size, size, align = "center", fill=app.roadFill)
        drawCurvedRoad(app, cx, cy, size, 'ul', roadWidth)
        drawCurvedRoad(app, cx, cy, size, 'ur', roadWidth)
        drawCurvedRoad(app, cx, cy, size, 'll', roadWidth)
        drawCurvedRoad(app, cx, cy, size, 'lr', roadWidth)
        drawRect(cx, cy, size*roadWidth, size*roadWidth, align = "center", fill = None, border = 'white', borderWidth = 10, dashes = True)
    elif idx == 10: #up, left
        drawCurvedRoad(app, cx, cy, size, 'ul', roadWidth, section='outerRoad')
        drawCurvedRoad(app, cx, cy, size, 'ul', roadWidth, section='dottedLine')
        drawCurvedRoad(app, cx, cy, size, 'ul', roadWidth, section='innerRoad')
        drawCurvedRoad(app, cx, cy, size, 'ul', roadWidth, section='innerGrass')
    elif idx == 9: #up, right
        drawCurvedRoad(app, cx, cy, size, 'ur', roadWidth, section='outerRoad')
        drawCurvedRoad(app, cx, cy, size, 'ur', roadWidth, section='dottedLine')
        drawCurvedRoad(app, cx, cy, size, 'ur', roadWidth, section='innerRoad')
        drawCurvedRoad(app, cx, cy, size, 'ur', roadWidth, section='innerGrass')
    elif idx == 6: #down, left
        drawCurvedRoad(app, cx, cy, size, 'll', roadWidth, section='outerRoad')
        drawCurvedRoad(app, cx, cy, size, 'll', roadWidth, section='dottedLine')
        drawCurvedRoad(app, cx, cy, size, 'll', roadWidth, section='innerRoad')
        drawCurvedRoad(app, cx, cy, size, 'll', roadWidth, section='innerGrass')
    elif idx == 5: #down, right
        drawCurvedRoad(app, cx, cy, size, 'lr', roadWidth, section='outerRoad')
        drawCurvedRoad(app, cx, cy, size, 'lr', roadWidth, section='dottedLine')
        drawCurvedRoad(app, cx, cy, size, 'lr', roadWidth, section='innerRoad')
        drawCurvedRoad(app, cx, cy, size, 'lr', roadWidth, section='innerGrass')


def drawHorizontalDottedLine(cx, cy, size):
    drawLine(cx-size*0.5, cy, cx+size*0.5, cy, fill='white', lineWidth=2, dashes=True)

def drawVerticalDottedLine(cx, cy, size):
    drawLine(cx, cy-size*0.5, cx, cy+size*0.5, fill='white', lineWidth=2, dashes=True)

def drawCurvedRoad(app, cx, cy, size, pos, roadWidth, section = 'innerGrass'):
    angleDict = {'ul':270, 'ur': 180, 'll':0, 'lr':90}
    startAngle = angleDict[pos]
    sweepAngle = 90 

    px, py = getCorner(cx, cy, size, pos)
    innerWidth = 1 - roadWidth
    arcWidthDict = {'innerGrass': size*innerWidth, 'outerRoad': size*(2 - innerWidth), 'dottedLine':size, 'innerRoad': (size-4)}
    arcWidth = arcWidthDict[section]
    fillDict = {'innerGrass': app.background, 'outerRoad': app.roadFill, 'dottedLine':None, 'innerRoad': app.roadFill}
    fillColor = fillDict[section]
    border, borderWidth, dashes = ('white', 4, True) if section == 'dottedLine' else (None, 1, False)
    
    drawArc(px, py, arcWidth, arcWidth, startAngle, sweepAngle, fill=fillColor, border=border, borderWidth=borderWidth, dashes=dashes) 

''' Given center of cell, get coordinates of its corners'''
def getCorner(cx, cy, size, pos):
    ulx, uly = cx-size*0.5, cy-size*0.5 #upperLeftX, upperLefY
    urx, ury = cx+size*0.5, cy-size*0.5 #upperRightX, upperRightY
    llx, lly = cx-size*0.5, cy+size*0.5 #lowerLeftX, lowerLeftY
    lrx, lry = cx+size*0.5, cy+size*0.5 #upperRightX, upperRightY
    coods = {'ul':(ulx, uly), 'ur': (urx, ury), 'll':(llx, lly), 'lr':(lrx, lry)}
    return coods[pos]


    


