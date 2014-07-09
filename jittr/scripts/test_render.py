from panda3d.core import loadPrcFileData
from panda3d.core import WindowProperties
from panda3d.core import AntialiasAttrib
from panda3d.core import PNMImage
from direct.showbase.ShowBase import ShowBase
import argparse
import numpy  # arrays and linear algebra
from matplotlib import pyplot  # plotting

def parse_args():
    parser = argparse.ArgumentParser(
        description="Renders a .egg file to an image file in current folder")

    parser.add_argument('--width',
                        type=int,
                        default=300,
                        help="The width of the output image")

    parser.add_argument('--height',
                        type=int,
                        default=200,
                        help="The height of the output image")

    parser.add_argument('-i',
                        '--input',
                        default="../assets/panda-model.egg.pz",
                        help="The .egg file to render")

    result = parser.parse_args()

    return result

"""def render(obj_file_path, width, height):
    loadPrcFileData('', 'win-size ' + str(width) + ' ' + str(height) )
    #loadPrcFileData('', 'framebuffer-multisample 1 \n multisamples 2')
    base = ShowBase()
    #base.render.setAntialias(AntialiasAttrib.MMultisample) #
    base.model = base.loader.loadModel(obj_file_path)
    base.model.setPos(0,4000,0);
    base.model.reparentTo(base.render)
    base.graphicsEngine.renderFrame()
    base.screenshot(namePrefix = 'render')
    base.run()"""

def renderToArray(obj_file_path, width, height):    
    loadPrcFileData('', 'win-size ' + str(width) + ' ' + str(height) )
    base = ShowBase()
    base.model = base.loader.loadModel(obj_file_path)
    base.model.setPos(0,4000,0);
    base.model.reparentTo(base.render)    
    base.graphicsEngine.renderFrame()
    image = PNMImage()
    dr = base.camNode.getDisplayRegion(0)
    dr.getScreenshot(image)
    arrayImage = numpy.zeros((height, width, 3))
    i = 0
    j = 0
    while (i<width):
        while (j<height):
            arrayImage[j,i,0] = image.getRed(i,j)
            arrayImage[j,i,1] = image.getGreen(i,j)
            arrayImage[j,i,2] = image.getBlue(i,j)
            j = j+1
        j=0
        i = i+1
    return arrayImage

def main():

    args = parse_args()
    image = renderToArray(args.input, args.width, args.height)  # get array of pixels

    # Get current axes, hide the tick marks
    axes = pyplot.gca()
    axes.get_xaxis().set_visible(False)
    axes.get_yaxis().set_visible(False)

    axes.imshow(image)  # "plot"s the pixel array in the axes.
    pyplot.show()  # display plotting window 


# Runs this code if this file is executed as a script.
if __name__ == "__main__":
    main()
