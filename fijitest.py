from ij import IJ, ImageStack, ImagePlus
from ij import *
import jarray
from ij import IJ, ImageStack, ImagePlus
from ij import *
import jarray
import os, glob
from ij.process import ImageConverter
import re
import os

#@String mypath


def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    return [ atoi(c) for c in re.split('(\d+)', text) ]

os.chdir(mypath)
alist = os.listdir(mypath)
alist.sort(key=natural_keys)

imp = IJ.openImage(mypath + alist[0])
signedpix = imp.getProcessor().toFloat(1, None)
width=signedpix.getWidth()
height=signedpix.getHeight()
stack = ImageStack(width, height)
i=0


for file in alist[:10]:
	print("Current File Being Processed is: " + file)
	imp = IJ.openImage(mypath + file)
	signedpix = imp.getProcessor().toFloat(1, None)
	stack.addSlice(str(i), signedpix)
	i = i + 1

imp = ImagePlus("", stack)
ImageConverter(imp).convertToGray8()
imp.show()  

IJ.runPlugIn("ij3d.ImageJ3DViewer", "")


