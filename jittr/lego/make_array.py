import matplotlib.image as mpimg
import numpy
import os.path

n=0

output = numpy.memmap('images', dtype='uint8', mode='w+', shape=(111456, 9216))
x = numpy.zeros((96,96), dtype='uint8')
for i in range(111456):
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
    x[:] = 85*numpy.sum(mpimg.imread(name), axis=2)  # 85 = 255 / 3, to make averaging channels work
    output[i][:] = x.reshape((9216))
    if i%1000 == 0:
        print i
