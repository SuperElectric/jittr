import matplotlib.image as mpimg
import numpy
import os.path

n=0

colour_output = numpy.memmap('colour_array', dtype='uint8', mode='w+', shape=(3888, 9216, 2))
alpha_output = numpy.memmap('alpha_array', dtype='uint8', mode='w+', shape=(3888, 9216, 2))
x = numpy.zeros((4,96,96), dtype='uint8')
colour = numpy.zeros((96,96), dtype='uint8')
alpha = numpy.zeros((96,96), dtype='uint8')
for i in range(3888):
    if (i<10):   
        name = "./renders/a000%s.png" % i
    elif (i<100):
        name = "./renders/a00%s.png" % i
    elif (i<1000):
        name = "./renders/a0%s.png" % i
    else:
        name = "./renders/a%s.png" % i
    if not os.path.exists(name):
        print "File not found"
    x[:] = mpimg.imread(name).swapaxes(1,2).swapaxes(0,1)
    colour = 85*numpy.sum(x[:3], axis=0)
    alpha = x[4]
    colour_output[i][:] = colour.reshape((9216))
    alpha_output[i][:] = alpha.reshape((9216))
    if i%1000 == 0:
        print i
