import argparse, sys


def parseArgs():
    parser = argparse.ArgumentParser(
        description='Converts obj file to have only one texture')
    parser.add_argument('--input',
                        '-i',
                        default = '/home/daniel/urop/jittr/jittr/assets/models/tree/tree.obj',
                        help='.obj file to convert.')
    result = parser.parse_args()
    return result

# load file into lines and generate v and vt lists

args = parseArgs()
obj = open(args.input)
fileName = args.input.split('/')[-1]
modelName = fileName.rstrip('.obj')

lines = obj.readlines()

verts = []
uvs = []
for line in lines:
    if line.split()[0] == 'v':
        verts.append(line.rstrip())
    elif line.split()[0] == 'vt':
        uvs.append(line.rstrip())


