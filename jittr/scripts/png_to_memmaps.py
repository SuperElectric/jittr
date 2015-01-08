#! /usr/bin/env python

import argparse
from matplotlib.image import imread
import numpy
import os.path
import pdb
from numpy.lib.format import open_memmap


def main():
    def parse_args():
        parser = argparse.ArgumentParser(
            description=("Merges .pngs into a memmappable .npy file, and "
                         " generates corrsponding NORB labels as another "
                         ".npy file."))

        parser.add_argument("-i",
                            "--input_directory",
                            required=True,
                            help="Directory containing the .png files.")

        parser.add_argument("-p",
                            "--image_prefix",
                            default="a",
                            metavar="P",
                            help=("Images are assumed to have filenames "
                                  "of the form <P><N>.png, where P is this "
                                  "prefix, and N is the image number."))
        parser.add_argument("-o",
                            "--output_prefix",
                            required=True,
                            metavar="O",
                            help=("Output files will be O_images.npy and "
                                  "O_labels.npy."))

        result = parser.parse_args()

        assert os.path.splitext(result.output_prefix)[1] == ""

        return result

    args = parse_args()

    num_files = 3888
    image_shape = (96, 96, 4)

    images = open_memmap('%s_images.npy' % args.output_prefix,
                         dtype='uint8',
                         mode='w+',
                         shape=(num_files, ) + image_shape)

    labels = numpy.memmap('%s_labels.npy' % args.output_prefix,
                          dtype='int32',
                          mode='w+',
                          shape=(num_files, 5))

    image_prefix = os.path.join(args.input_directory, args.image_prefix)

    def get_filename(image_prefix, file_number):
        assert 1000 <= num_files
        assert file_number <= num_files

        if (file_number < 10):
            return "./%s000%d.png" % (image_prefix, file_number)
        elif (file_number < 100):
            return "./%s00%d.png" % (image_prefix, file_number)
        elif (file_number < 1000):
            return "./%s0%d.png" % (image_prefix, file_number)
        else:
            return "./%s%d.png" % (image_prefix, file_number)

    def get_norb_label(file_number):
        light = (file_number / 972)
        model = (file_number / 162) % 6
        elev = (file_number / 18) % 9
        azim = file_number % 18

        return numpy.asarray([0, model, elev, azim, light], dtype='int32')

    for file_number in range(num_files):
        name = get_filename(image_prefix, file_number + 1)
        if not os.path.exists(name):
            print "File '%s' not found." % name

        image = imread(name)  # row, column, RGBA
        images[file_number, ...] = numpy.round(image * 255)
        if file_number % 1000 == 0:
            print "read %d of %d" % (file_number + 1, num_files)

        labels[file_number, :] = get_norb_label(file_number)


if __name__ == '__main__':
    main()
