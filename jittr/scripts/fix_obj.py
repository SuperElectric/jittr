#! /usr/bin/env python

import argparse


def parseArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument('input',
                        help='.obj file to convert')
    parser.add_argument('output', help='new .obj file')

    result = parser.parse_args()
    result.name = result.input.rstrip('.obj')
    result.newName = result.output.rstrip('.obj')
    return result


def main():

    args = parseArgs()
    obj = open('%s.obj' % args.name)
    mtl = open('%s.mtl' % args.name)
    objLines = obj.readlines()
    mtlLines = mtl.readlines()

    # generate list of materials
    materials = []
    for line in mtlLines:
        words = line.rstrip().split()
        if len(words) != 2:
            pass
        elif words[0] == 'newmtl':
            materials.append(words[1])
    print 'materials:'
    print materials

    # generate list of texture coordinates
    uvList = []
    for line in objLines:
        words = line.rstrip().split()
        if words == []:
            pass
        elif words[0] == 'vt':
            uvList.append((float(words[1]), float(words[2])))
    print ('vt count = %d' % len(uvList))

    # shift position of uv coordinate vertex 'vt' with material 'mat'
    def shiftUV(vt, mat):
        shiftedU = (uvList[vt][0] + materials.index(mat))/len(materials)
        shiftedV = uvList[vt][1]
        return (shiftedU, shiftedV)

    # shift uv coordinates for each face and write to newUvList
    newUvList = uvList[:]
    currentMaterial = ''
    for line in objLines:
        words = line.rstrip().split()
        if words == []:
            pass
        elif words[0] == 'usemtl':
            currentMaterial = words[1]
            print ('currentMaterial changed to: %s' % currentMaterial)
        elif words[0] == 'f':
            for word in words:
                if word != 'f':
                    numbers = word.split('/')
                    if len(numbers) == 1:
                        uvID = int(numbers[0]) - 1
                    elif numbers[1] == '':
                        uvID = int(numbers[0]) - 1
                    else:
                        uvID = int(numbers[1]) - 1
                    newUvList[uvID] = shiftUV(uvID, currentMaterial)

    # write new .mtl file:
    newMtl = open('%s.mtl' % args.newName, 'w')
    newMtlLines = ['newmtl material\n', 'map_Kd %s.jpg\n' % args.newName]
    newMtl.writelines(newMtlLines)

    # write new .obj file:
    newObj = open('%s.obj' % args.newName, 'w')
    newObjLines = []
    uvID = 0
    for line in objLines:
        words = line.rstrip().split()
        if words == []:
            newObjLines.append(line)
        elif words[0] == 'vt':
            newObjLines.append('vt %f %f\n' % newUvList[uvID])
            uvID = uvID + 1
        elif words[0] == 'usemtl':
            newObjLines.append('usemtl material\n')
        elif words[0] == 'mtllib':
            newObjLines.append('mtllib %s.mtl\n' % args.newName)
        else:
            newObjLines.append(line)
    newObj.writelines(newObjLines)

if __name__ == "__main__":
    main()