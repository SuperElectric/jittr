#! /usr/bin/env python

import argparse
import numpy
import yaml
import sys
from math import sin, cos, pi
try:
    import bpy
    usingBlender = True
except ImportError:
    from panda3d.core import (loadPrcFileData,
                              VBase4,
                              PointLight)
    from direct.showbase.ShowBase import ShowBase
    usingBlender = False

class scene(object):
    def loadModels(self):
        raise NotImplementedError
    def loadLighting(self):
        raise NotImplementedError
    def setLighting(self, lightingID):
        raise NotImplementedError
    def setCameraState(self, azID, elevID, cameraPositions):
        raise NotImplementedError
    def setBackgroundImage(self, backID):
        raise NotImplementedError
    def showModel(self, modelID):
        raise NotImplementedError
    def hideModel(self, modelID):
        raise NotImplementedError
    def renderToArray(self):
        raise NotImplementedError


class blenderScene(scene):
    pass


class pandaScene(scene):

    def __init__(self, settings):
        self.settings = settings
        loadPrcFileData('', 'win-size %d %d' % (self.settings.width,
                                                self.settings.height))
        self.base = ShowBase()
        self.base.mouseInterface.detachNode()
        self.base.models = []
        self.base.plight = PointLight('plight')
        self.base.plnp = self.base.render.attachNewNode(self.base.plight)
        self.base.camLens.setFocalLength(self.settings.cameraFocalLength)
        self.base.camLens.setNear(settings.cameraNear)
        self.base.camLens.setFar(settings.cameraFar)

    def loadModels(self):
        for modelData in self.settings.modelDatas:
            model = self.base.loader.loadModel("../assets/models/%s/%s" % (
                modelData.name, modelData.model3dFile))
            texture = self.base.loader.loadTexture("../assets/models/%s/%s" % (
                modelData.name, modelData.texture))
            self.base.models.append(model)
            model.setTexture(texture)
            m = modelData
            model.setPos(m.offset[0], m.offset[1], m.offset[2])
            model.setScale(m.scale)
            model.setHpr(m.rotation[0], m.rotation[1], m.rotation[2])

    def loadLighting(self):
        raise NotImplementedError

    def setLighting(self, lightingID):
        if self.settings.lightingPositions[lightingID] == "noLights":
            self.base.plight.setColor(VBase4(1, 1, 1, 1))
            self.base.plnp.setPos(0, 0, 10)
            self.base.render.setLight(self.base.plnp)

    def setCameraState(self, azID, elevID, cameraPositions):
        self.base.camera.setPos(cameraPositions[azID, elevID, 0],
                                cameraPositions[azID, elevID, 1],
                                cameraPositions[azID, elevID, 2])
        self.base.camera.setHpr(90 + self.settings.azimuths[azID],
                                -self.settings.elevations[elevID],
                                0)

    def setBackgroundImage(self, backID):
        raise NotImplementedError

    def showModel(self, modelID):
        if modelID >= 0:
            self.base.models[modelID].reparentTo(self.base.render)

    def hideModel(self, modelID):
        if modelID >= 0:
            self.base.models[modelID].removeNode()

    def renderToArray(self):
        self.base.graphicsEngine.renderFrame()
        self.base.taskMgr.step()
        display_region = self.base.win.getActiveDisplayRegion(0)
        screenshot = display_region.getScreenshot()
        ram_image = screenshot.get_uncompressed_ram_image()
        data = ram_image.getData()
        pixels = numpy.fromstring(data, dtype='uint8')
        pixels = pixels.reshape((self.settings.height, self.settings.width, 4))
        pixels = pixels[:, :, :3]
        pixels = pixels[::-1, :, ::-1]
        return pixels


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
    result.modelDatas = []

    for model in result.models:
        modelSettingsFile = open('../assets/models/%s/%s.yaml' %
                                 (model, model), 'r')
        modelSettingsDictionary = yaml.load(modelSettingsFile)
        modelData = namespace()
        modelData.__dict__.update(modelSettingsDictionary)
        modelData.name = model
        result.modelDatas.append(modelData)
    return result


def parseArgs():
    parser = argparse.ArgumentParser(
        description='Generates norb data set of N .egg models and saves '
        'renders as .npy arrays')

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
                        help='Names of models to render. Example: "--models '
                        'cube" will use files ../assets/models/cube/cube.* if '
                        'they exist')

    parser.add_argument('-o',
                        '--output',
                        nargs=2,
                        default=[],
                        help="The output arrays, e.g \"images.npy labels.npy\""
                        )

    parser.add_argument('--settings',
                        default="../render_settings.yaml",
                        help="The render settings file")
    result = parser.parse_args()
    return result


def main():
    args = parseArgs()
    settings = parseSettings(args)
    if usingBlender:
        sc = blenderScene(settings)
    else:
        sc = pandaScene(settings)

    def getCameraPositions():
        cameraPositions = numpy.zeros((len(settings.azimuths),
                                       len(settings.elevations), 3))
        for azimuthID in range(len(settings.azimuths)):
            azR = settings.azimuths[azimuthID] * pi / 180
            for elevationID in range(len(settings.elevations)):
                elevR = settings.elevations[elevationID] * pi / 180
                cameraDistance = settings.cameraDistance
                cameraPositions[azimuthID, elevationID, :] = \
                    numpy.array([cameraDistance * cos(elevR) * cos(azR),
                                 cameraDistance * cos(elevR) * sin(azR),
                                 cameraDistance * sin(elevR)])
                cameraPositions[azimuthID, elevationID, :] += \
                    -numpy.array(settings.cameraOffset)
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

    sc.loadModels()

    # iterate through images by model, azimuth, elevation, lighting
    n = 0
    for modelID in range(len(settings.models)):
        sc.hideModel(modelID-1)
        sc.showModel(modelID)
        for azimuthID in range(len(settings.azimuths)):
            for elevationID in range(len(settings.elevations)):
                sc.setCameraState(azimuthID, elevationID, cameraPositions)
                for lightingID in range(len(settings.lightingPositions)):
                    sc.setLighting(lightingID)
                    labelsArray[n, 0] = modelID
                    labelsArray[n, 1] = azimuthID
                    labelsArray[n, 2] = elevationID
                    labelsArray[n, 3] = lightingID
                    imagesArray[n, :, :, :] = sc.renderToArray()
                    n = n + 1

    if not settings.dontSave:
        numpy.save(settings.output[0], imagesArray)
        numpy.save(settings.output[1], labelsArray)

if __name__ == "__main__":
    main()