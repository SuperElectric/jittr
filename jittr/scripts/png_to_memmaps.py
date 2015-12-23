#! /usr/bin/env python

"""
Script for generating image and label memmaps from .png renderings by blender.
"""

from __future__ import print_function

import argparse
import os
import sys
import re
from matplotlib.image import imread
import numpy
from numpy.lib.format import open_memmap
from nose.tools import assert_true, assert_equal, assert_greater
from numpy.testing import assert_array_equal


def main():
    """ Entry point of script. """

    def parse_args():
        """ Parse command-line args, return as namespace. """

        parser = argparse.ArgumentParser(
            description=("Merges .pngs into a memmappable .npy file, and "
                         " generates corrsponding NORB labels as another "
                         ".npy file. Expects all .pngs to be in one directory,"
                         " and to be named as <prefix><number>.png"))


        def existing_dir(arg):
            assert_true(os.path.isdir(arg))
            return arg

        parser.add_argument("-i",
                            "--input-dir",
                            type=existing_dir,
                            required=True,
                            help="Directory containing the .png files.")

        parser.add_argument("-p",
                            "--image-prefix",
                            default="a",
                            metavar="P",
                            help=("Images are assumed to have filenames "
                                  "of the form <P><N>.png, where P is this "
                                  "prefix, and N is the image number."))
        parser.add_argument("-o",
                            "--output-dir",
                            required=True,
                            type=existing_dir,
                            metavar="O",
                            help=("Will save images.npy and labels.npy to "
                                  "this directory."))

        def positive_int(arg):
            """ Parse a positive int arg. """

            arg = int(arg)
            assert_greater(arg, 0)
            return arg

        parser.add_argument("--num_lightings",
                            type=positive_int,
                            default=4,
                            help="The number of lighting setups.")

        result = parser.parse_args()

        return result

    args = parse_args()

    def get_png_files():
        """
        Returns filenames of images under args.input_directory.

        Filenames will be of the form <args.image_prefix><integer>.png.

        Aborts if the integers aren't contiguous from 1 to num_images.
        """
        # regex for <prefix><number>.png
        #
        # r: raw string; don't interpret backslashes as escapes.
        # ^: start of string
        # \d+: 1 or more digits
        # \Z: end of string
        regex = re.compile(r"^{}\d+\.png\Z".format(args.image_prefix))

        for _, _, filenames in os.walk(args.input_dir):
            image_files = [f for f in filenames
                           if regex.match(f) is not None]
            assert_greater(len(image_files), 0)

            image_files.sort()
            digits = numpy.asarray([int(f[len(args.image_prefix):-4])
                                    for f in image_files])
            # digits.sort()
            assert_array_equal(digits, numpy.arange(1, len(image_files) + 1))

            return image_files

    png_files = get_png_files()
    num_files = len(png_files)
    num_azimuths = 18
    num_elevations = 9
    files_per_object = num_azimuths * num_elevations * args.num_lightings

    num_objects = num_files // files_per_object
    assert_equal(num_objects * files_per_object, num_files)

    # num_files = 3888

    # def get_filename(image_prefix, file_number):
    #     assert 1000 <= num_files
    #     assert file_number <= num_files

    #     if (file_number < 10):
    #         return "%s000%d.png" % (image_prefix, file_number)
    #     elif (file_number < 100):
    #         return "%s00%d.png" % (image_prefix, file_number)
    #     elif (file_number < 1000):
    #         return "%s0%d.png" % (image_prefix, file_number)
    #     else:
    #         return "%s%d.png" % (image_prefix, file_number)

    def make_labels():
        """ Create the labels memmap """

        labels = open_memmap(os.path.join(args.output_dir, 'labels.npy'),
                             dtype='int32',
                             mode='w+',
                             shape=(num_files, 5))

        row_index = 0
        for lighting in xrange(args.num_lightings):
            for object_id in xrange(num_objects):
                for elevation in xrange(num_elevations):
                    for azimuth in xrange(0, num_azimuths * 2, 2):
                        labels[row_index, :] = [0,
                                                object_id,
                                                elevation,
                                                azimuth,
                                                lighting]
                        row_index += 1

    make_labels()

    def make_images():
        """ Create the images memmap """

        image_shape = (96, 96, 4)

        images = open_memmap(os.path.join(args.output_dir, 'images.npy'),
                             dtype='uint8',
                             mode='w+',
                             shape=(num_files, ) + image_shape)

        for file_number, filename in enumerate(png_files):
            filepath = os.path.join(args.input_dir, filename)
            if not os.path.exists(filepath):
                print("Couldn't find '{}'.".format(filepath))
                sys.exit(1)

            image = imread(filepath)  # row, column, channel (RGBA, float)
            images[file_number, ...] = numpy.round(image * 255)
            if file_number % 100 == 0:
                print("read {} of {}".format(file_number + 1, num_files))

        print("read {} of {}".format(num_files, num_files))

    make_images()
    print("wrote images.npy and labels.npy to {}".format(args.output_dir))

    # def get_norb_label(file_number):
    #     light = (file_number / 972)
    #     model = (file_number / 162) % 6
    #     elev = (file_number / 18) % 9
    #     azim = (file_number % 18) * 2

    #     return numpy.asarray([0, model, elev, azim, light], dtype='int32')

    # for file_number in range(num_files):
    #     name = get_filename(image_prefix, file_number + 1)
    #     if not os.path.exists(name):
    #         print "File '%s' not found." % name

    #     image = imread(name)  # row, column, RGBA
    #     images[file_number, ...] = numpy.round(image * 255)
    #     if file_number % 1000 == 0:
    #         print "read %d of %d" % (file_number + 1, num_files)

    #     labels[file_number, :] = get_norb_label(file_number)


if __name__ == '__main__':
    main()
