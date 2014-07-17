import bpy, numpy
from math import sin, cos, pi

##################### arguments ##########################
# could instead import all of these from a text file, so that Blender and Panda render identical
# views without having to carefully edit variables in their scripts
width = 300
height = 200
scale = 10 # camera distance
verticalOffset = 0
cameraFocalLength = 1 # relative to sensor width.
models = ['model0', 'model1'] # list of names of meshes in blender to render in order.
elevations = [30,35,40,45,50,55,60,65,70] # list of elevation angles in degrees
azimuths = [] # list of azimuth angles in degrees
for i in range(18):
    azimuths.append(20*i)

numberOfAzimuths = len(azimuths)
numberOfElevations = len(elevations) + 0
numberOfLightingPositions = 1
cameraPositions = numpy.zeros((numberOfAzimuths,numberOfElevations,3))
##########################################################

# set camera settings
camData = bpy.data.cameras['Camera']
camObj = bpy.data.objects['Camera']
bpy.data.scenes["Scene"].render.resolution_x = width
bpy.data.scenes["Scene"].render.resolution_y = height
if (height > width):
    camData.sensor_width = height/width
else:
    camData.sensor_width = 1
    
camData.lens = cameraFocalLength + 0
numberOfModels = len(models) + 0
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
    pass

def setCameraState(azID, elevID):
    camObj.location = [cameraPositions[azID, elevID, 0],
                       cameraPositions[azID, elevID, 1], 
                       cameraPositions[azID, elevID, 2]]
    camObj.rotation_euler = [pi*(90-elevations[elevID])/180, 0, pi*(90+azimuths[azID])/180]
                       

def renderToArray():
    pass

# make all models invisible initially
for i in range(numberOfModels):
    bpy.data.objects[models[i]].hide = True
    bpy.data.objects[models[i]].keyframe_insert(data_path = "hide", frame = 0)

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
                setLighting(l)
                labelsArray[n,0] = i # integer model ID
                labelsArray[n,1] = j # integer azimuth ID
                labelsArray[n,2] = k # integer elevation ID
                labelsArray[n,3] = l # integer lighting ID
               #imagesArray[n,:,:,:] = renderToArray()
                for i in range(3):
                    camObj.keyframe_insert(data_path = "location", frame = n, index = i)
                    camObj.keyframe_insert(data_path = "rotation_euler", frame = n, index = i)
                n = n+1

#numpy.save(args.output[0], imagesArray)
#numpy.save(args.output[1], labelsArray)

