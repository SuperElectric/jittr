#! /usr/bin/env python

import argparse
import numpy
from scipy.optimize import minimize
import random
import math
import thread
import pylab

key = ''
def userInput():
    while (True):
        global key
        key = raw_input()


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
                    materialID = materials.index(rse.cmake'
rm 'cpp/cmake_modules/FindEigen.cmake'
rm 'cpp/cmake_modules/FindGflags.cmake'
rm 'cpp/cmake_modules/FindGlog.cmake'
rm 'cpp/cmake_modules/FindSharedPtr.cmake'
rm 'cpp/cmake_modules/FindSphinx.cmake'
rm 'cpp/cmake_modules/FindSuiteSparse.cmake'
rm 'cpp/cmake_modules/UpdateCacheVariable.cmake'
rm 'cpp/cmake_modules/config.h.in'
rm 'cpp/cmake_modules/iOS.cmake'
rm 'cpp/cmake_modules/uninstall.cmake.in'
rm 'cpp/include/jittr/hello_world.h'
rm 'cpp/src/CMakeLists.txt'
rm 'cpp/src/hello_world.cpp'
rm 'cpp/src/hello_world_main.cpp'
daniel@daniel-Precision-M4800 ~/urop/jittr/jittr $ git mv ../assets .
daniel@daniel-Precision-M4800 ~/urop/jittr/jittr $ 
currentMaterial)
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
        xyz1 = numpy.append(xyz, (1.0))
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
            newUv = xyzToUv(projectMatrix, K1, K2, 1.0, 1.333333, xyz)
            error = (uv[0] - newUv[0])**2 + (uv[1] - newUv[1])**2
            total = total + error
        return total/len(vertexSet)

    def errorArray(matrix, vertexSet, omittedIndex):
        list = []
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
            newUv = xyzToUv(projectMatrix, K1, K2, 1.0, 1.333333, xyz)
            error = (uv[0] - newUv[0])**2 + (uv[1] - newUv[1])**2
            list.append(error)
        return numpy.array(list)


    def solve(matrix, useDistortion, material, maxiter):
        if not useDistortion:
            matrix = matrix[:11]
        vertexSet = sampleVerticies(20, material)
        result = minimize(sumOferrors,
                          matrix,
                          args=(vertexSet, omittedIndex),
                          method='Nelder-Mead',
                          options={'maxiter': maxiter, 'disp': False})
        return result

    # saves matrix11 or matrix13 to .npy array that has 14 elements.
    # The last two elements are the distortion values
    def save(matrix, omittedIndex, material):
        projectMatrix = numpy.concatenate((matrix[:omittedIndex],
                                           [1],
                                           matrix[omittedIndex:]))
        K1 = 0
        K2 = 0
        if len(matrix) == 13:
            K1 = matrix[11]
            K2 = matrix[12]
        saveMatrix = numpy.append(projectMatrix, (K1, K2))
        numpy.save('%s.npy' % material, saveMatrix)

    material = materials[args.materialID]
    useDistort = True

    functionValue = 1.0
    iterations = 1000
    thread.start_new_thread(userInput, ())
    matrix = numpy.zeros((13))
    omittedIndex = 0
    while (functionValue > 0.00001):
        estimateMatrix = estimateProjectMatrix(100, 0.0000001, material)
        omittedIndex = numpy.argmax(estimateMatrix)
        estimateMatrix = estimateMatrix/estimateMatrix[omittedIndex]
        estimate11Matrix = numpy.delete(estimateMatrix, omittedIndex)
        estimate13Matrix = numpy.append(estimate11Matrix, [0, 0])
        result = solve(estimate13Matrix, useDistort, material, 10)
        matrix = result.x
        functionValue = result.fun
    i = 0

    save(matrix, omittedIndex, material)

    while (i < iterations and key != 'stop'):
        if result.fun < functionValue:
            functionValue = result.fun
            matrix = result.x
        result = solve(matrix, useDistort, material, 1000)
        print functionValue
    print matrix
    save(matrix, omittedIndex, material)
    #print sumOferrors(matrix, vectorLists[materialIDs[material]], omittedIndex)
    #pylab.hist(errorArray(matrix, vectorLists[materialIDs[material]], omittedIndex))
    #pylab.show()


if __name__ == '__main__':
    main()
