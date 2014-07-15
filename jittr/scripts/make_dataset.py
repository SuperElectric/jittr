#! /usr/bin/env python

import argparse
import numpy, pylab
from panda3d.core import loadPrcFileData, WindowProperties
from direct.showbase.ShowBase import ShowBase
from math import sin, cos, pi
width = 300
height = 200 # initialize width and height
verticalOffset = 300
scale = 2000 # distance from the camera to the origin
elevations = [30,35,40,45,50,55,60,65,70] # list of elevation angles in degrees
azimuths = [] # list of azimuth angles in degrees
for i in range(18):
    azimuths.append(20*i)
numberOfAzimuths = len(azimuths)
numberOfElevations = len(elevations)
numberOfLightingPositions = 1
cameraStates = []

# generate a list of camera states
for azimuth in azimuths:
    azR = azimuth*pi/180
    for elevation in elevations:
        elevR = elevation*pi/180
        # each camera state is of the form [x,y,z,azimuth,elevation]
        cameraStates.append([scale*cos(elevR)*cos(azR),scale*cos(elevR)*sin(azR),scale*sin(elevR),azimuth,elevation])

# window width and height can be set only once using loadPrcFileData
def setup():
    loadPrcFileData('', 'win-size ' + str(width) + ' ' + str(height) )
    base = ShowBase()
    base.mouseInterface.detachNode() # otherwise, base.taskMgr.step() overrides the camera properties
    base.models = []

def parse_args():
    parser = argparse.ArgumentParser(
        description="Generates norb data set of N .egg models and saves renders as .npy arrays")

    parser.add_argument('--width',
                        type=int,
                        default=300,
                        help="The width of the output images")

    parser.add_argument('--height',
                        type=int,
                        default=200,
                        help="The height of the output images")

    parser.add_argument('-i',
                        '--input',
                        nargs='+',
                        help="The .egg files to render")

    parser.add_argument('-o',
                        '--output',
                        nargs=2,
                        default="../assets/images.npy ../assets/labels.npy",
                        help="The output arrays, e.g \"images.npy labels.npy\"")

    result = parser.parse_args()
    return result

# this function will set lighting position to the one denoted by "lightingID"
def setLighting(lightingID):
    pass

def renderToArray():
    base.graphicsEngine.renderFrame()
    base.taskMgr.step()
    display_region = base.win.getActiveDisplayRegion(0)
    screenshot = display_region.getScreenshot()
    ram_image = screenshot.get_uncompressed_ram_image()
    data = ram_image.getData()
    pixels = numpy.fromstring(data, dtype='uint8')
    pixels = pixels.reshape((height,width,4))
    pixels =  pixels[:, :, :3]
    pixels = pixels[::-1,:,::-1]
    return pixels

def main():
    args = parse_args()
    global width    
    width = args.width
    global height
    height = args.height
    setup()
    numberOfModels = len(args.input)
    numberOfImages = numberOfModels*len(elevations)*len(azimuths)
    imagesArray = numpy.zeros([numberOfImages, height, width, 3], dtype='uint8')
    labelsArray = numpy.zeros([numberOfImages, 4], dtype='uint8') # Each image has [modelID, azimuth, elevation, lightingID]

    # iterate through images by model, azimuth, elevation, lighting
    n=0
    for i in range(numberOfModels):
        model = base.loader.loadModel(args.input[i])
        base.models.append(model)
        if (i>0):
            base.models[i-1].removeNode()        
        base.models[i].reparentTo(base.render)
        base.models[i].setPos(0,0,-verticalOffset)
        for j in range(numberOfAzimuths):
            for k in range(numberOfElevations):
                c = cameraStates[n]
                base.camera.setPos(c[0],c[1],c[2])
                base.camera.setHpr(90+c[3],-c[4],0)
                for l in range(numberOfLightingPositions):
                    setLighting(l)
                    labelsArray[n,0] = i # integer model ID
                    labelsArray[n,1] = j # integer azimuth ID
                    labelsArray[n,2] = k # integer elevation ID
                    labelsArray[n,3] = l # integer lighting ID
                    imagesArray[n,:,:,:] = renderToArray()
                    #pylab.imshow(imagesArray[n,:,:,:])
                    #pylab.show()
                    n = n+1

if __name__ == "__main__":
    main()



