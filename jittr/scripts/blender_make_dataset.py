import bpy, numpy
from math import sin, cos, pi

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


def main():
        
    settings = Settings("../render_settings.txt")
    
    width  = settings.width
    height = settings.height
#    models = settings.models
    output = settings.output    
    dontSave = settings.dontSave
    verticalOffset = settings.verticalOffset
    cameraFocalLength = settings.cameraFocalLength
    scale = settings.scale
    elevations = settings.elevations
    azimuths = settings.azimuths
    lightingPositions = settings.lightingPositions
    
    numberOfAzimuths = len(azimuths)
    numberOfElevations = len(elevations)
    numberOfLightingPositions = len(lightingPositions)
    cameraPositions = numpy.zeros((numberOfAzimuths,numberOfElevations,3))
    
    # set camera settings
    camData = bpy.data.cameras['Camera']
    camObj = bpy.data.objects['Camera']
    bpy.data.scenes["Scene"].render.resolution_x = width
    bpy.data.scenes["Scene"].render.resolution_y = height
    if (height > width):
        camData.sensor_width = height/width
    else:
        camData.sensor_width = 1
        
    camData.lens = cameraFocalLength
    numberOfModels = len(models)
    numberOfImages = numberOfModels*len(elevations)*len(azimuths)
    imagesArray = numpy.zeros([numberOfImages, height, width, 3], dtype='uint8')
    labelsArray = numpy.zeros([numberOfImages, 4], dtype='uint8') # Each image has [modelID, azimuth, elevation, lightingID]
    
    # generate an array of camera positions ordered by azimuth and elevation IDs
    for i in range(len(azimuths)):
        azR = azimuths[i]*pi/180
        for j in range(len(elevations)):
            elevR = elevations[j]*pi/180
            cameraPositions[i,j,:] = numpy.array([scale*cos(elevR)*cos(azR),scale*cos(elevR)*sin(azR),scale*sin(elevR)])
    
    # this function will set lighting position to the one denoted by "lightingID"
    def setLighting(lightingID):
        for i in bpy.data.objects
    
    def setCameraState(azID, elevID):
        camObj.location = [cameraPositions[azID, elevID, 0],
                           cameraPositions[azID, elevID, 1], 
                           cameraPositions[azID, elevID, 2]]
        camObj.rotation_euler = [pi*(90-elevations[elevID])/180, 0, pi*(90+azimuths[azID])/180]
                           
    
    def renderToArray():
        pass
    
    # make all models and lighting conditions invisible initially
    for i in range(numberOfModels):
        bpy.data.objects[models[i]].hide = True
        bpy.data.objects[models[i]].keyframe_insert(data_path = "hide", frame = 0)
    for i in range(numberOfLightingPositions):
        bpy.data.objects[lights[i]].hide = True
        bpy.data.objects[lights[i]].keyframe_insert(data_path = "hide", frame = 0)
    
    # iterate through images by model, azimuth, elevation, lighting
    n=0
    for i in range(numberOfModels):
        if (i>0):
            bpy.data.objects[models[i-1]].hide = True
            bpy.data.objects[models[i-1]].keyframe_insert(data_path = "hide", frame = n)
        bpy.data.objects[models[i]].hide = False
        bpy.data.objects[models[i]].keyframe_insert(data_path = "hide", frame = n)
        for j in range(numberOfAzimuths):
            for k in range(numberOfElevations):
                setCameraState(j,k)
                for l in range(numberOfLightingPositions):
                    currentLightingID = setLighting(l)
                    labelsArray[n,0] = i # integer model ID
                    labelsArray[n,1] = j # integer azimuth ID
                    labelsArray[n,2] = k # integer elevation ID
                    labelsArray[n,3] = l # integer lighting ID
                    imagesArray[n,:,:,:] = renderToArray()
                    for i in range(3):
                        camObj.keyframe_insert(data_path = "location", frame = n, index = i)
                        camObj.keyframe_insert(data_path = "rotation_euler", frame = n, index = i)
                    n = n+1

    if dontSave == False :
        numpy.save(args.output[0], imagesArray)
        numpy.save(args.output[1], labelsArray)

if __name__ == "__main__":
    main()
