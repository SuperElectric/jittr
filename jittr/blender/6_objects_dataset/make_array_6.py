import matplotlib.image as mpimg
import numpy
import os.path


colour_output = numpy.memmap('colour_array', dtype='uint8', mode='w+', shape=(3888, 9216, 2))
alpha_output = numpy.memmap('alpha_array', dtype='uint8', mode='w+', shape=(3888, 9216, 2))
x = numpy.zeros((4,96,96), dtype='uint8')
colour = numpy.zeros((96,96), dtype='uint8')
alpha = numpy.zeros((96,96), dtype='uint8')
for i in range(3888):
    j = i+1
    if (j<10):   
        name = "./a000%s.png" % j
    elif (j<100):
        name = "./a00%s.png" % j
    elif (j<1000):
        name = "./a0%s.png" % j
    else:
        name = "./a%s.png" % j
    if not os.path.exists(name):
        print "File not found"
    x[:] = mpimg.imread(name).swapaxes(1,2).swapaxes(0,1)
    colour = 85*numpy.sum(x[:3], axis=0)
    alpha = x[4]
    colour_output[i][:] = colour.reshape((9216))
    alpha_output[i][:] = alpha.reshape((9216))
    if i%1000 == 0:
        print i

     
labels = numpy.memmap('labels', dtype='int32', mode='w+', shape=(3888,5))
for i in range(3888):
    light = (i/972)
    model = (i/162) % 6
    elev = (i/18) % 9
    azim = i % 18
    labels[i][:] = [0,model,elev,azim,light]

