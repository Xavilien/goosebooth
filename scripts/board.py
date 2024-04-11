import math

''' Check if row, col on grid is within board'''
def inBoard(app, row, col):
    return 0<=row<app.rows and 0<=col<app.cols
    
''' Check if exact coordinates cx, cy is within screen'''
# To make the app more efficient, only elements within svreen are drawn
def inScreen(app, cx, cy):
    buffer = 60
    return -buffer <= cx <= (app.width+buffer) and -buffer <= cy <= (app.height+buffer)

'''Convert row, col on grid to exact coordintae, cx, cy'''
def cellToCoods(app, cellCollection, align = "left-top"):
    resCoods = []
    for (row, col) in cellCollection:
        if align == 'left-top':
            cellLeft, cellTop = getCellLeftTop(app, row, col)
            resCoods.append((cellLeft, cellTop))
        elif align == 'center':
            cellCenterX, cellCenterY = getCellCenter(app, row, col)
            resCoods.append((cellCenterX, cellCenterY))
    return resCoods

# Based on row, col of cell on grid, get top-left coordinates 
def getCellLeftTop(app, row, col):
    cellWidth, cellHeight = getCellSize(app)
    cellLeft = app.boardLeft + col * cellWidth
    cellTop = app.boardTop + row * cellHeight
    return (cellLeft, cellTop)

# Based on row, col of cell on grid, get center coordinates 
def getCellCenter(app, row, col):
    cellWidth, cellHeight = getCellSize(app)
    cellCenterX = app.boardLeft + (col+0.5) * cellWidth
    cellCenterY = app.boardTop + (row+0.5) * cellHeight
    return cellCenterX, cellCenterY

# Extract size of cells depending on boardWidth and number of friends
def getCellSize(app):
    cellWidth = app.boardWidth / app.cols
    cellHeight = app.boardHeight / app.rows
    return (cellWidth, cellHeight) 

# Get cell row, col in grid from exact coordinates cx, cy
def getCell(app, x, y):
    dx = x - app.boardLeft
    dy = y - app.boardTop
    cellWidth, cellHeight = getCellSize(app)
    rowExact = dy / cellHeight 
    colExact = dx / cellWidth 
    row = math.floor(rowExact)
    col = math.floor(colExact)
    return (row, col, rowExact, colExact)