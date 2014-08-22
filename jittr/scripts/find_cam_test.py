#! /usr/bin/env python

import argparse

def parseArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument('input',
                        help='.obj file to use to deduce camera angles')
    parser.add_argument('materialID', type=int)

    result = parser.parse_args()
    result.name = result.input.rstrip('.obj')
    return result

def main():
    args = parseArgs()
    obj = open('%s.obj' % args.name)
    mtl = open('%s.mtl' % args.name)
    objLines = obj.readlines()
    mtlLines = mtl.readlines()
    
    # generate list of materials
    materials = []
    materialIDs = {}
    for line in mtlLines:
        words = line.rstrip().split()
        if len(words) != 2:
            pass
        elif words[0] == 'newmtl':
            material = words[1]
            if material not in materials:
                materials.append(material)
                materialIDs[material] = len(materials) - 1
    print('materials = %s' % materials)

    # generate lists of xyz and uv points
    uvList = []
    xyzList = []
    for line in objLines:
        words = line.rstrip().split()
        if words == []:
            pass
        elif words[0] == 'vt':
            uvList.append((float(words[1]), float(words[2])))
        elif words[0] == 'v':
            xyzList.append((float(words[1]), float(words[2]), float(words[3])))

    print ('vt count = %d' % len(uvList))
    print ('v count = %d' % len(xyzList))

    # for each 'usemtl' statement, create a list of vectors,
    # each of the form uvxyz
    vectorLists = []
    for material in materials:
        vectorLists.append([])
    currentMaterial = ''
    for line in objLines:
        words = line.rstrip().split()
        if words == []:
            pass
        elif words[0] == 'usemtl':
            currentMaterial = words[1]
            #print ('currentMaterial changed to: %s' % currentMaterial)
        elif words[0] == 'f':
            for word in words:
                if word != 'f':
                    numbers = word.split('/')
                    if len(numbers) == 1:
                        xyzID = int(numbers[0]) - 1
                        uvID = int(numbers[0]) - 1
                    elif numbers[1] == '':
                        xyzID = int(numbers[0]) - 1
                        uvID = int(numbers[0]) - 1
                    else:
                        xyzID = int(numbers[0]) - 1
                        uvID = int(numbers[1]) - 1
                    materialID = materials.index(currentMaterial)
                    vectorLists[materialID].append((uvList[uvID][0],
                                                    uvList[uvID][1],
                                                    xyzList[xyzID][0],
                                                    xyzList[xyzID][1],
                                                    xyzList[xyzID][2]))


if __name__ == "__main__":
    main()
