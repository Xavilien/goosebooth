from cmu_graphics import *
import random
from soundAndGraphics import openImage
from board import inBoard

class House:
    #cx, cy: center coordinates of house, cr: length of house
    def __init__(self, cx, cy, cr):
        self.cx, self.cy, self.cr = cx, cy, cr
        # self.houseType = random.choice(['house', 'house1', 'house2'])
        self.houseType = random.choice(['nasilemak', 'adobo', 'dimsum'])

''' Houses should be placed at the dead ends of roads'''
def placeHouseAtRoadEnd(app): #roads should be passed in as board rows and cols
    for i, idx in enumerate(app.roadIdx):
        roadRow, roadCol = app.roads[i]
        # Identify dead end roads
        if idx == 1: #house on left
            houseRow, houseCol = (roadRow, roadCol-1)
        elif idx == 2: #house on right
            houseRow, houseCol = (roadRow, roadCol+1)
        elif idx == 8: #house below
            houseRow, houseCol = (roadRow+1, roadCol)
        elif idx == 4: #house above
            houseRow, houseCol = (roadRow-1, roadCol)
        else:
            continue
        
        # Ensure that potential position of house is within board
        if inBoard(app, houseRow, houseCol):
            app.houses.append((houseRow, houseCol))

''' Function to draw house in redrawAll (main.py)'''
def drawHouse(app, houseObject):
    house = openImage(f'../graphics/{houseObject.houseType}.png')
    house = house.resize((int(houseObject.cr), int(houseObject.cr)))
    house = CMUImage(house)
    drawRect(houseObject.cx-10, houseObject.cy-10, houseObject.cr, houseObject.cr, align = 'center', opacity = 50)
    drawImage(house, houseObject.cx, houseObject.cy, align = 'center')