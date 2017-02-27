import pyPreProcPipe
from PIL import Image
import numpy as np


im = Image.open("test.TIF")
im = np.array(im, dtype='uint16')
out = np.zeros(shape=(im.shape[0]/2, im.shape[1]/2), dtype='uint16')
pyPreProcPipe.pyDownsize(im, out)
outout = np.zeros(shape=(im.shape[0], im.shape[1]), dtype='uint8')
pyPreProcPipe.py16to8(im, outout)

im = Image.fromarray(outout)
im.show()



