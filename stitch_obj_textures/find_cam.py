#! /usr/bin/env python

import argparse
import numpy
from scipy.optimize import minimize
import random
import math


def parseArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument('input',
                        help='.obj file to use to deduce camera angles')

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

    def sampleVerticies(sizeOfSample, material):
        verticies = []
        for i in range(sizeOfSample):
            verticies.append(random.choice(vectorLists[materialIDs[material]]))
        return verticies

    def linearEqnConsts(verticies):
        n = len(verticies)
        matrix = numpy.zeros((2*n, 12))
        for i in range(n):
            vert = verticies[i]
            xyz1 = numpy.array([vert[2], vert[3], vert[4], 1.0])
            u = vert[0]
            zeros = numpy.zeros((4))
            matrix[i][:] = numpy.concatenate((xyz1, zeros, -u*xyz1))
        for i in range(n):
            vert = verticies[i]
            xyz1 = numpy.array([vert[2], vert[3], vert[4], 1.0])
            v = vert[1]
            zeros = numpy.zeros((4))
            matrix[n + i][:] = numpy.concatenate((zeros, xyz1, -v*xyz1))
        return matrix

    def sumOfSquares(projectMatrix):
        projectMatrix = numpy.reshape(projectMatrix, (3, 4))
        total = 0
        for i in range(1000):
            vert = random.choice(vectorLists[0])
            olduv = vert[:2]
            xyz1 = numpy.array([vert[2], vert[3], vert[4], 1])
            newuvz = numpy.dot(projectMatrix, xyz1)
            newuv = newuvz[:2]/newuvz[2]
            total = total + (newuv[0]-olduv[0])**2 + (newuv[1]-olduv[1])**2
        return total

    def estimateProjectMatrix(n, epsilon, material):
        total = numpy.zeros((12))
        i = 0
        while (i < n):
            vertices = sampleVerticies(6, material)
            matrix = linearEqnConsts(vertices)
            collum = numpy.zeros((12))
            for j in range(12):
                collum[j] = epsilon*(numpy.random.rand() - 0.5)
            try:
                projectMatrix = numpy.linalg.solve(matrix,collum)
                total = total + projectMatrix
                i = i + 1
            except numpy.linalg.linalg.LinAlgError:
                pass
        total = total/n
        print "estimateProjectMatrix completed."
        return total

    def xyzToUv(projectMatrix, K1, K2, ScaleU, ScaleV, xyz):
        # for now, this assumes distortion is radial from the centre of the UV map
        # with corrected aspect ratio
        projectMatrix = numpy.reshape(projectMatrix, (3, 4))
        xyz1 = numpy.append(xyz,(1.0))
        uvz = numpy.dot(projectMatrix, xyz1)
        uv = uvz[:2]/uvz[2]
        tempUv = numpy.array([ScaleU*(uv[0]-0.5), ScaleV*(uv[1]-0.5)])
        radiusSqrd = tempUv[0]**2 + tempUv[1]**2
        tempUv = (1 + K1*radiusSqrd + K2*radiusSqrd**2)*tempUv
        uv = numpy.array([0.5 + tempUv[0]/ScaleU, 0.5 + tempUv[1]/ScaleV])
        return uv

    def sumOferrors(matrix, vertexSet, omittedIndex):
        total = 0
        projectMatrix = numpy.concatenate((matrix[:omittedIndex],
                                           [1],
                                           matrix[omittedIndex:]))
        projectMatrix = numpy.reshape(projectMatrix[:12], (3, 4))
        if len(matrix) == 13:
            K1 = matrix[11]
            K2 = matrix[12]
        else:
            K1 = 0
            K2 = 0
        for vertex in vertexSet:
            xyz = numpy.array(vertex[2:])
            uv = numpy.array(vertex[:2])
            newUv = xyzToUv(projectMatrix, K1, K2, 1, 1.333333, xyz)
            error = (uv[0] - newUv[0])**2 + (uv[1] - newUv[1])**2
            total = total + error
        return total/len(vertexSet)

    def solve(matrix, useDistortion, material):
        if not useDistortion:
            matrix = matrix[:11]
        vertexSet = sampleVerticies(100, material)
        result = minimize(sumOferrors,
                          matrix,
                          args=(vertexSet, omittedIndex),
                          method='Nelder-Mead',
                          options={'maxiter': 1000, 'disp': False})
        return result

    material = materials[1]
    useDistort = True

    estimateMatrix = estimateProjectMatrix(100, 0.0000001, material)
    omittedIndex = numpy.argmax(estimateMatrix)
    estimateMatrix = estimateMatrix/estimateMatrix[omittedIndex]
    estimate11Matrix = numpy.delete(estimateMatrix, omittedIndex)
    estimate13Matrix = numpy.append(estimate11Matrix, [0, 0])

    result = solve(estimate13Matrix, useDistort, material)
    function = result.fun
    matrix = estimate13Matrix
    iterations = 10
    while (function > 0.01):
        estimateMatrix = estimateProjectMatrix(100, 0.0000001, material)
        omittedIndex = numpy.argmax(estimateMatrix)
        estimateMatrix = estimateMatrix/estimateMatrix[omittedIndex]
        estimate11Matrix = numpy.delete(estimateMatrix, omittedIndex)
        estimate13Matrix = numpy.append(estimate11Matrix, [0, 0])
        result = solve(estimate13Matrix, useDistort, material)
        matrix = result.x
        function = result.fun
    for i in range(iterations):
        if result.fun < function:
            function = result.fun
            matrix = result.x
        result = solve(matrix, useDistort, material)
        print function
    print matrix
    print sumOferrors(matrix, vectorLists[materialIDs[material]], omittedIndex)



    #===========================================================================
    # projectMatrix = numpy.reshape(projectMatrix, (3, 4))
    # mag = numpy.linalg.norm(projectMatrix[:][0])
    # projectMatrix = projectMatrix/mag
    # print projectMatrix
    # for i in range(10):
    #     vert = random.choice(vectorLists[0])
    #     olduv = vert[:2]
    #     xyz1 = numpy.array([vert[2], vert[3], vert[4], 1])
    #     newuvz = numpy.dot(projectMatrix, xyz1)
    #     newuv = newuvz[:2]/newuvz[2]
    #     print ("Old UV = " + str(olduv))
    #     print ("New UV = " + str(newuv))
    #     print ''
    #===========================================================================

if __name__ == '__main__':
    main()
