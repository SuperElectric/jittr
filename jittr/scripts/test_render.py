#! /usr/bin/env python

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

def renderToArray(obj_file_path, width, height):    
    loadPrcFileData('', 'win-size ' + str(width) + ' ' + str(height) )
    base = ShowBase()
    base.model = base.loader.loadModel(obj_file_path)
    base.model.setPos(0,4000,0);
    base.model.reparentTo(base.render)    
    base.graphicsEngine.renderFrame()
    base.taskMgr.step() # first thing I found except for run() which updates the display
    my_display_region = base.win.getActiveDisplayRegion(0)
    my_screenshot = my_display_region.getScreenshot()
    my_ram_image = my_screenshot.get_uncompressed_ram_image()
    data = my_ram_image.getData()
    my_pixels = numpy.fromstring(data, dtype='uint8')
    my_pixels = my_pixels.reshape((height,width,4))
    my_pixels =  my_pixels[:, :, :3]
    my_pixels = my_pixels[::-1,::-1,::-1] # for some reason, when this line is deleted, pyplot scales colours differently.
    return my_pixels

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
