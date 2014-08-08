#! /usr/bin/env python

import subprocess
import argparse


def parseArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument('input',
                        help='.mtl file that lists image textures')
    parser.add_argument('output', help='output image file')
    result = parser.parse_args()
    return result


def main():

    args = parseArgs()
    mtl = open(args.input)
    lines = mtl.readlines()
    currentMaterial = ''
    currentTexture = ''
    command = ['convert']
    for line in lines:
        words = line.rstrip().split()
        if words[0] == 'newmtl':
            currentMaterial = words[1]
        if words[0] == 'map_Kd':
            currentTexture = words[1]
            command.append(currentTexture)

    command.append('+append')
    command.append(args.output)
    subprocess.call(command)

if __name__ == "__main__":
    main()