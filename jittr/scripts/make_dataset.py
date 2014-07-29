#! /usr/bin/env python

import argparse
import numpy
import yaml
import sys
from panda3d.core import (loadPrcFileData,
                          VBase4,
                          PointLight)
from direct.showbase.ShowBase import ShowBase
from math import sin, cos, pi


def parseSettings(args):
    filePath = args.settings
    doc = yaml.load(open(filePath))

    class namespace(object):
        pass
    result = namespace()

    if 'width' in doc and args.width > 0:
        doc['width'] = args.width
        print('Width specified. Ignoring width value in "%s"' % filePath)
    elif 'width' in doc:
        print('Width not specified. Using width value in "%s"' % filePath)
    elif args.width > 0:
        doc['width'] = args.width
    else:
        sys.exit('Width not specified in arguments or in "%s"' % filePath)

    if 'height' in doc and args.height > 0:
        doc['height'] = args.height
        print('height specified. Ignoring height value in "%s"' % filePath)
    elif 'height' in doc:
        print('height not specified. Using height value in "%s"' % filePath)
    elif args.height > 0:
        doc['height'] = args.height
    else:
        sys.exit('height not specified in arguments or in "%s"' % filePath)

    if 'models' in doc and args.models != []:
        doc['models'] = args.models
        print('Models specified. Ignoring models in "%s"' % filePath)
    elif 'models' in doc:
        print('Models not specified. Using models in "%s"' % filePath)
    elif args.models != []:
        doc['models'] = args.models
    else:
        sys.exit('No models specified in arguments or in "%s"' % filePath)

    if 'output' in doc and args.output != []:
        doc['output'] = args.output
        print('Output files specified. Ignoring outputs in "%s"' % filePath)
    elif 'output' in doc:
        print('Output files not specified. Using outputs in "%s"' % filePath)
    elif args.output != []:
        doc['output'] = args.output
    else:
        sys.exit('No output files specified in arguments or in "%s"'
                 % filePath)

    result.__dict__.update(doc)

    # Could create a "Model" class and for each model, say "cube", in
    # result.models, create a new Model object called "cube" which contains all
    # data from the "cube.settings" file. But for now file "model.settings" is
    # simply read (assumed to be in ../assets/) and result.model3DFiles is
    # created.

    result.model3dFiles = []
    for model in result.models:
        modelSettingsFile = open('../assets/models/%s/%s.settings.yml' % (model,model), 'r')
        modelSettingsDictionary = yaml.load(modelSettingsFile)
        model3dFile = modelSettingsDictionary['model3dFile']
        result.model3dFiles.append(model3dFile)
    return result


def parseArgs():
    parser = argparse.ArgumentParser(
        description='Generates norb data set of N .egg models and saves renders'
        ' as .npy arrays')

    parser.add_argument('--width',
                        type=int,
                        default=0,
                        help="The width of the output images")

    parser.add_argument('--height',
                        type=int,
                        default=0,
                        help="The height of the output images")

    parser.add_argument('-m',
                        '--models',
                        nargs='+',
                        default=[],
                        help='Names of models to render. Example: "--models cube'
                        ' will use data specified in ./cube.settings if it exists')

    parser.add_argument('-o',
                        '--output',
                        nargs=2,
                        default=[],
                        help="The output arrays, e.g \"images.npy labels.npy\""
                        )

    parser.add_argument('--settings',
                        default="../render_settings.yml",
                        help="The render settings file")
    result = parser.parse_args()
    return result


def main():

    args = parseArgs()
    settings = parseSettings(args)

    def getCameraPositions():
        cameraPositions = numpy.zeros((len(settings.azimuths),
                                       len(settings.elevations), 3))

        for i in range(len(settings.azimuths)):
            azR = settings.azimuths[i] * pi / 180
            for azimuthID in range(len(settings.elevations)):
                elevR = settings.elevations[azimuthID] * pi / 180
                scale = settings.scale
                cameraPositions[i, azimuthID, :] = \
                    numpy.array([scale * cos(elevR) * cos(azR),
                                 scale * cos(elevR) * sin(azR),
                                 scale * sin(elevR)])

        return cameraPositions

    cameraPositions = getCameraPositions()

    # generate an array of camera positions ordered by azimuth and elevation
    # IDs

    numberOfImages = len(settings.models) * len(settings.elevations) * \
        len(settings.azimuths)
    imagesArray = numpy.zeros([numberOfImages,
                               settings.height,
                               settings.width, 3], dtype='uint8')
    labelsArray = numpy.zeros([numberOfImages, 4], dtype='uint8')
    # Each image has [modelID, azimuth, elevation, lightingID]

    loadPrcFileData('', 'win-size %d %d' % (settings.width, settings.height))
    base = ShowBase()
    base.mouseInterface.detachNode()  # Otherwise, base.taskMgr.step()
    # overrides the camera properties
    base.models = []
    base.plight = PointLight('plight')
    base.plnp = base.render.attachNewNode(base.plight)
    base.camLens.setFocalLength(settings.cameraFocalLength)

    # The lightingID is mapped to a name, say "noLights" by the
    # render_settings.yml file.
    # This function determines how "noLights" is rendered by panda
    def setLighting(lightingID):
        if settings.lightingPositions[lightingID] == "noLights":
            base.plight.setColor(VBase4(1, 1, 1, 1))
            base.plnp.setPos(0, 0, 10)
            base.render.setLight(base.plnp)

    def setCameraState(azID, elevID):
        base.camera.setPos(cameraPositions[azID, elevID, 0],
                           cameraPositions[azID, elevID, 1],
                           cameraPositions[azID, elevID, 2])
        base.camera.setHpr(90 + settings.azimuths[azID],
                           -settings.elevations[elevID],
                           0)

    def renderToArray():
        base.graphicsEngine.renderFrame()
        base.taskMgr.step()
        display_region = base.win.getActiveDisplayRegion(0)
        screenshot = display_region.getScreenshot()
        ram_image = screenshot.get_uncompressed_ram_image()
        data = ram_image.getData()
        pixels = numpy.fromstring(data, dtype='uint8')
        pixels = pixels.reshape((settings.height, settings.width, 4))
        pixels = pixels[:, :, :3]
        pixels = pixels[::-1, :, ::-1]
        return pixels

    # load all models before rendering
    for modelID in range(len(settings.models)):
        model = base.loader.loadModel(settings.model3dFiles[modelID])
        base.models.append(model)

    # iterate through images by model, azimuth, elevation, lighting
    n = 0
    for modelID in range(len(settings.models)):
        if (modelID > 0):
            base.models[modelID - 1].removeNode()
        base.models[modelID].reparentTo(base.render)
        base.models[modelID].setPos(0, 0, -settings.verticalOffset)
        for azimuthID in range(len(settings.azimuths)):
            for elevationID in range(len(settings.elevations)):
                setCameraState(azimuthID, elevationID)
                for lightingID in range(len(settings.lightingPositions)):
                    setLighting(lightingID)
                    labelsArray[n, 0] = modelID
                    labelsArray[n, 1] = azimuthID
                    labelsArray[n, 2] = elevationID
                    labelsArray[n, 3] = lightingID
                    imagesArray[n, :, :, :] = renderToArray()
                    n = n + 1

    if not settings.dontSave:
        numpy.save(settings.output[0], imagesArray)
        numpy.save(settings.output[1], labelsArray)

if __name__ == "__main__":
    main()
