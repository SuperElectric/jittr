#! /usr/bin/env python

"""
Some skeleton code that just displays a random array of RGB pixels.

Eventually, this will load a 3D model file (probably an Alias|Wavefront .OBJ
file) and render it from some simply-chosen viewpoint and lighting.
"""


from __future__ import print_function  # python 3.0's version of print()
import numpy  # arrays and linear algebra
import argparse  # command-line argument parsing
from matplotlib import pyplot  # plotting


def parse_args():
    """
    Parses command-line args.

    Returns: namespace
    Contains command-line arguments as named variables.
    """

    parser = argparse.ArgumentParser(
        description="Renders a .obj file to an image.")

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
                        default=None,
                        help="The .obj file to render (currently ignored).")

    result = parser.parse_args()

    return result


def render(obj_file_path, width, height):
    """
    Renders a 3D model to an RGB image with the given dimensions.

    Parameters
    ----------
    obj_file_path: str
    Full path to the model file.

    width: Width of output image, in pixels

    height: height of output image, in pixels
    """

    if obj_file_path is not None:
        print("A file '%s' was provided, but we're ignoring it for now." %
              obj_file_path)

    # Returns random numbers between 0.0 and 1.0
    return numpy.random.rand(height, width, 3)


def main():

    args = parse_args()
    image = render(args.input, args.width, args.height)  # get array of pixels

    # Get current axes, hide the tick marks
    axes = pyplot.gca()
    axes.get_xaxis().set_visible(False)
    axes.get_yaxis().set_visible(False)

    axes.imshow(image)  # "plot"s the pixel array in the axes.
    pyplot.show()  # display plotting window


# Runs this code if this file is executed as a script.
if __name__ == "__main__":
    main()
