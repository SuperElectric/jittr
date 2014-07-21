#! /usr/bin/env python

import argparse, numpy, pylab, imp
from panda3d.core import loadPrcFileData, WindowProperties, Material, VBase4, PointLight
from direct.showbase.ShowBase import ShowBase
from math import sin, cos, pi
import render_settings as settings

class Settings:
    width = 0
    height = 0
    models = []
    output = []
    dontSave = False
    verticalOffset = 0
    cameraFocalLength = 1
    scale = 1
    elevations = []
    azimuths = []
    lightingPositions = []
    def __init__ (self,filePath):
        textFile = open(filePath)
        lines = textFile.readlines()
        for line in lines:
            line = line.replace(' ','')
            line = line.rstrip()
            words = line.split(':')
            if len(words) == 2 :
                if words[0] == 'width' : self.width = int(words[1])
                elif words[0] == 'height' : self.height = int(words[1])
                elif words[0] == 'models' : self.models = words[1].split(',')
                elif words[0] == 'output' : self.output = words[1].split(',')
                elif words[0] == 'dontSave' :
                    if words[1] == 'True' :
                        self.dontSave = True
                    elif words[1] == 'False' :
                        self.dontSave = False
                elif words[0] == 'verticalOffset' : self.verticalOffset = float(words[1])
                elif words[0] == 'cameraFocalLength' : self.cameraFocalLength = float(words[1])
                elif words[0] == 'scale' : self.scale = float(words[1])
                elif words[0] == 'elevations' :
                    self.elevations = []
                    values = words[1].split(',')
                    for value in values:
                        self.elevations.append(float(value))
                elif words[0] == 'azimuths' :
                    self.azimuths = []
                    values = words[1].split(',')
                    for value in values:
                        self.azimuths.append(float(value))
                elif words[0] == 'lightingPositions' : self.lightingPositions = words[1].split(',')

def parse_args():
    parser = argparse.ArgumentParser(
        description="Generates norb data set of N .egg models and saves renders as .npy arrays")

    parser.add_argument('--width',
                        type=int,
                        default=0,
                        help="The width of the output images")

    parser.add_argument('--height',
                        type=int,
                        default=0,
                        help="The height of the output images")

    parser.add_argument('-i',
                        '--input',
                        nargs='+',
                        default = [],
                        help="The .egg files to render")

    parser.add_argument('-o',
                        '--output',
                        nargs=2,
                        default=["fromFile", "fromFile"],
                        help="The output arrays, e.g \"images.npy labels.npy\"")
    result = parser.parse_args()
    
    parser.add_argument('--settings',
                        default="../render_settings.txt",
                        help="The render settings file")
    result = parser.parse_args()
    return result

def main():

    args = parse_args()
    settings = Settings(args.settings)
    if args.width < 1 : width = settings.width
    else : width = args.width
    if args.height < 1 : height = settings.height
    else : height = args.height
    if args.input == [] : models = settings.models
    else :  models = args.input
    if args.output == ["fromFile", "fromFile"] : output = settings.output
    else: output = args.output
        
    dontSave = settings.dontSave
    verticalOffset = settings.verticalOffset
    cameraFocalLength = settings.cameraFocalLength
    scale = settings.scale
    elevations = settings.elevations
    azimuths = settings.azimuths
    lightingPositions = settings.lightingPositions
    numberOfAzimuths = len(azimuths)
    numberOfElevations = len(elevations)
    numberOfLightingPositions = len (lightingPositions)
    cameraPositions = numpy.zeros((numberOfAzimuths,numberOfElevations,3))

    # generate an array of camera positions ordered by azimuth and elevation IDs
    for i in range(len(azimuths)):
        azR = azimuths[i]*pi/180
        for j in range(len(elevations)):
            elevR = elevations[j]*pi/180
            cameraPositions[i,j,:] = numpy.array([scale*cos(elevR)*cos(azR),scale*cos(elevR)*sin(azR),scale*sin(elevR)])
    
    numberOfModels = len(models)
    numberOfImages = numberOfModels*len(elevations)*len(azimuths)
    imagesArray = numpy.zeros([numberOfImages, height, width, 3], dtype='uint8')
    labelsArray = numpy.zeros([numberOfImages, 4], dtype='uint8') # Each image has [modelID, azimuth, elevation, lightingID]

    loadPrcFileData('', 'win-size ' + str(width) + ' ' + str(height) )
    base = ShowBase()
    base.mouseInterface.detachNode() # otherwise, base.taskMgr.step() overrides the camera properties
    base.models = []
    base.plight = PointLight('plight')
    base.plnp = base.render.attachNewNode(base.plight)
    base.camLens.setFocalLength(cameraFocalLength)


    # this function will set lighting position to the one denoted by "lightingID"
    def setLighting(lightingID):
        if lightingPositions[lightingID] == "noLights":            
            base.plight.setColor(VBase4(1, 1, 1, 1))
            base.plnp.setPos(0, 0, 10)
            base.render.setLight(base.plnp)

    def setCameraState(azID, elevID):
        base.camera.setPos(cameraPositions[azID,elevID,0],
                           cameraPositions[azID,elevID,1],
                           cameraPositions[azID,elevID,2])
        base.camera.setHpr(90+azimuths[azID],-elevations[elevID],0)
    
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

    # iterate through images by model, azimuth, elevation, lighting
    n=0
    for i in range(numberOfModels):
        model = base.loader.loadModel(models[i])
        base.models.append(model)
        if (i>0):
            base.models[i-1].removeNode()        
        base.models[i].reparentTo(base.render)
        base.models[i].setPos(0,0,-verticalOffset)
        for j in range(numberOfAzimuths):
            for k in range(numberOfElevations):
                setCameraState(j,k)
                for l in range(numberOfLightingPositions):
                    setLighting(l)
                    labelsArray[n,0] = i # integer model ID
                    labelsArray[n,1] = j # integer azimuth ID
                    labelsArray[n,2] = k # integer elevation ID
                    labelsArray[n,3] = l # integer lighting ID
                    imagesArray[n,:,:,:] = renderToArray()
                    n = n+1

    if  dontSave == False :    
        numpy.save(output[0], imagesArray)
        numpy.save(output[1], labelsArray)

if __name__ == "__main__":
    main()



