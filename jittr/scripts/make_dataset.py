#! /usr/bin/env python

import argparse
import numpy
import yaml
import sys
import os
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

JITTR_DIR = os.environ['JITTR_DIR'].rstrip(' ').rstrip('/')


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
    
    n = 0

    def __init__(self, settings):
        self.settings = settings
        self.models = []
        if 'Camera' not in bpy.data.objects:
            bpy.ops.object.camera_add()
        self.camera = bpy.data.objects['Camera']
        self.camera.data.lens = 1.0
        width, height = self.settings.width, self.settings.height
        bpy.data.scenes['Scene'].render.resolution_x = self.settings.width
        bpy.data.scenes['Scene'].render.resolution_y = self.settings.height
        if (width < height):
            self.camera.data.sensor_width = float(height) / float(width)
        else:
            self.camera.data.sensor_width = 1.0

    def loadModels(self):
        for modelData in self.settings.modelDatas:
            if modelData.name not in bpy.data.objects:
                if modelData.useBlendFile:
                    bpy.ops.wm.link_append(
                        directory="%s/jittr/assets/models/%s/%s/Object/"
                        % (JITTR_DIR, modelData.name, modelData.blendFile),
                        filename=modelData.name,
                        link=False)
            model = bpy.data.objects[modelData.name]
            self.models.append(model)
            model.hide = True
            model.keyframe_insert(data_path = "hide", frame=0)
            m = modelData
            model.location = [m.offset[0], m.offset[1], m.offset[2]]
            model.scale = [m.scale, m.scale, m.scale]
            model.rotation_euler = [m.rotation[0], m.rotation[1], m.rotation[2]]

    def loadLighting(self):
        pass

    def setLighting(self, lightingID):
        pass

    def setCameraState(self, azID, elevID, cameraPositions):
        self.camera.location = [cameraPositions[azID, elevID, 0],
                                cameraPositions[azID, elevID, 1],
                                cameraPositions[azID, elevID, 2]]
        self.camera.rotation_euler = [pi*(90-self.settings.elevations[elevID])/180,
                                      0,
                                      pi*(90+self.settings.azimuths[azID])/180]
        self.camera.keyframe_insert(data_path = "location", frame = self.n)
        self.camera.keyframe_insert(data_path = "rotation_euler", frame = self.n)

    def setBackgroundImage(self, backID):
        pass

    def showModel(self, modelID):
        self.models[modelID].hide = False
        self.models[modelID].keyframe_insert(data_path = "hide", frame = self.n)

    def hideModel(self, modelID):
        self.models[modelID].hide = True
        self.models[modelID].keyframe_insert(data_path = "hide", frame = self.n)

    def renderToArray(self):
        return numpy.zeros((self.settings.height, self.settings.width, 3))


class pandaScene(scene):

    def __init__(self, settings):
        self.settings = settings
        loadPrcFileData('', 'win-size %d %d' % (self.settings.width,
                                                self.settings.height))
        self.base = ShowBase()
        self.base.mouseInterface.detachNode()
        self.models = []
        self.base.plight = PointLight('plight')
        self.base.plnp = self.base.render.attachNewNode(self.base.plight)
        self.base.camLens.setFocalLength(self.settings.cameraFocalLength)
        self.base.camLens.setNear(settings.cameraNear)
        self.base.camLens.setFar(settings.cameraFar)

    def loadModels(self):
        for modelData in self.settings.modelDatas:
            model = self.base.loader.loadModel("%s/jittr/assets/models/%s/%s" % (
                JITTR_DIR, modelData.name, modelData.modelFile))
            texture = self.base.loader.loadTexture("%s/jittr/assets/models/%s/%s" % (
                JITTR_DIR, modelData.name, modelData.texture))
            self.models.append(model)
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
            self.base.plnp.setPos(10, 10, 10)
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
            self.models[modelID].reparentTo(self.base.render)

    def hideModel(self, modelID):
        if modelID >= 0:
            self.models[modelID].removeNode()

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
        modelSettingsFile = open('%s/jittr/assets/models/%s/%s.yaml' %
                                 (JITTR_DIR, model, model), 'r')
        modelSettingsDictionary = yaml.load(modelSettingsFile)
        modelData = namespace()
        modelData.__dict__.update(modelSettingsDictionary)
        modelData.name = model
        result.modelDatas.append(modelData)
    return result


def parseArgs():
    if usingBlender:
        class namespace(object):
            pass
        result = namespace()
        result.width = 0
        result.height = 0
        result.models = []
        result.output = []
        result.settings = "%s/jittr/render_settings.yaml" % JITTR_DIR
        return result
    parser = argparse.ArgumentParser(
        description='Generates norb data set of N models and saves '
        'renders as .npy arrays (or just images if using blender)')

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
                        'cube" will use files in JITTR_DIR/jittr/assets/models/cube/'
                        ' if they exist')

    parser.add_argument('-o',
                        '--output',
                        nargs=2,
                        default=[],
                        help="The output arrays, e.g \"images.npy labels.npy\""
                        )

    parser.add_argument('--settings',
                        default="%s/jittr/render_settings.yaml" % JITTR_DIR,
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
                    n = n+1
                    # sc.n is used for setting blender keyframes
                    sc.n = n

    if not settings.dontSave:
        numpy.save(settings.output[0], imagesArray)
        numpy.save(settings.output[1], labelsArray)

if __name__ == "__main__":
    main()

