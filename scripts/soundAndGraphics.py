from cmu_graphics import *
import os, pathlib
from PIL import Image

def loadSound(relativePath):
    # Convert to absolute path (because pathlib.Path only takes absolute paths)
    absolutePath = os.path.abspath(relativePath)
    # Get local file URL
    url = pathlib.Path(absolutePath).as_uri()
    # Load Sound file from local URL
    return Sound(url)

def defineSounds(app):
    app.rustleSound = loadSound("../sound/rustling-leaves.mp3")
    app.crunchSound = loadSound("../sound/apple-crunch.mp3")
    app.honkSound = loadSound("../sound/honk.wav")
    app.cryingSound = loadSound("../sound/anthony.mp3")
    app.thudSound = loadSound("../sound/thud.mp3")
    app.victorySound = loadSound("../sound/victory.mp3")

def openImage(fileName): 
        return Image.open(os.path.join(pathlib.Path(__file__).parent,fileName))