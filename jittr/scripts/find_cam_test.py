#! /usr/bin/env python

import argparse, yaml, numpy

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
    for line in objLines:
        words = line.rstrip().split()
        if len(words) != 2:
            pass
        elif words[0] == 'usemtl':
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
    # read yaml file.
    material = materials[args.materialID]
    matVectorList = vectorLists[args.materialID]
    drwords = args.input.rstrip().split('/')
    directory = args.input.rstrip().rstrip(drwords[-1])
    yamlFilePath = "%s%s.yaml" % (directory, material)
    print yamlFilePath
    def read_yaml_file(filePath):
        doc = yaml.load(open(filePath));
        K1 = doc['K1']
        print "K1 = %d" % K1
        #print "K2 = %d" % K2
        K2 = doc['K2']
        rot_matrix = numpy.array(doc['rotationMatrix'])
        translation = numpy.array(doc['translation'])
        cam_loc = numpy.dot(rot_matrix.transpose(), translation)
        project_matrix = numpy.insert(rot_matrix, 3, values=translation,
                                      axis=1)
        u0, v0 = doc['offsetU'], doc['offsetV']
        uScale, vScale = doc['scaleU'], doc['scaleV']
        calib_matrix = numpy.array([[uScale, 0.0   , u0 ],
                                    [0.0   , vScale, v0 ],
                                    [0.0   , 0.0   , 1.0]])
        project_matrix = numpy.dot(calib_matrix, project_matrix)
        return [project_matrix, K1, K2]
    projectMat, K1, K2 = read_yaml_file(yamlFilePath)
    def printComparison(uvxyz, projectMat, K1, K2):
        print "Old uv = %s,%s" % (uvxyz[0], uvxyz[1])
        xyz = list(uvxyz[2:])
        print uvxyz
        xyz.append(1.0)
        uvz = numpy.dot(projectMat, xyz)
        uv = uvz[:2]/uvz[2]
        rsqrd = uv[0]**2 + uv[1]**2
        uv[0] = uv[0]*(1.0 + K1*rsqrd + K2*rsqrd*rsqrd)
        uv[1] = uv[1]*(1.0 + K1*rsqrd + K2*rsqrd*rsqrd)
        print "New uv = %s,%s" % (uv[0], uv[1])
    uvxyz = matVectorList[100]
    printComparison(uvxyz, projectMat, K1, K2)

    
    



if __name__ == "__main__":
    main()






