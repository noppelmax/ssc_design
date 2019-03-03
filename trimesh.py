#!/usr/bin/python
import logging
from PIL import Image, ImageDraw
import random
import sys
import numpy as np
import math
from scipy.spatial import Delaunay


FGTHEMES = ["fire","ice","darkgreen","lightgreen","dblue"]
BGTHEMES = ["black_bg", "white_bg", "blue_bg"]


def printUsage():
	exit("Usage: <outputimage> <inputimage> <ndots>")

try:
	if sys.argv[1] is None:
		printUsage()
	if sys.argv[2] is None:
		printUsage()
	if sys.argv[3] is None:
		printUsage()

except IndexError:
	printUsage()

FORMAT = "%(asctime)-15s %(levelname)s %(message)s"
logging.basicConfig(format=FORMAT, level=logging.INFO)
logger = logging.getLogger("main")
logger.info("Starting!")

OUTPUTIMAGE = sys.argv[1]
IN = Image.open(sys.argv[2])
INPUTIMAGE = IN.load()
(SIZEX, SIZEY) = IN.size
if(SIZEX != SIZEY):
	logger.error("Quadratisches Bild bitte!")
	exit(1)
SIZE = SIZEY
DOTS = int(sys.argv[3])
OVERLAY = None
OVERLAYIMAGE = None
COLORINDEX = 3
FG = 1
BG = 2

OVERLAY_W = Image.open("hose_w.png")
OVERLAYIMAGE_W = OVERLAY_W.load()
(w,h) = OVERLAY_W.size
if w != SIZE or h != SIZE:
	logger.error("Die Masse des Overlays muessen dem des Inputbildes entsprechen. %d x %d pixel" % (SIZE,SIZE))
	exit(1)

OVERLAY_B = Image.open("hose_b.png")
OVERLAYIMAGE_B = OVERLAY_B.load()
(w,h) = OVERLAY_B.size
if w != SIZE or h != SIZE:
	logger.error("Die Masse des Overlays muessen dem des Inputbildes entsprechen. %d x %d pixel" % (SIZE,SIZE))
	exit(1)

LINEWIDTH = 0

def generateDots(ndots,size):
	dots = []

	for i in range(0,ndots):
		d = [int(random.random() * SIZE), int(random.random() * SIZE)]
		skip = False
		for dot in dots:
			if (abs(dot[0] - d[0]) < 10) and (abs(dot[1] - d[1]) < 10):
				skip = True
		if not skip:
			dots.append(d)

	return dots

def getFGColor(fgcolor):
	thPic = Image.open("themes/" + FGTHEMES[fgcolor] + ".png")
	themePic = thPic.load()

	(sx, sy) = thPic.size
	(c1,c2,c3) = themePic[int(random.random()*sx),0]
	return (c1,c2,c3)

def getBGColor(bgcolor):
	thPic = Image.open("themes/" + BGTHEMES[bgcolor] + ".png")
	themePic = thPic.load()

	(sx, sy) = thPic.size
	(c1,c2,c3) = themePic[int(random.random()*sx),0]
	return (c1,c2,c3)

def buildMesh( inImage, dots):
	newTris = []
	tris = Delaunay(dots)

	for simplex in tris.simplices:
		x = np.average([int(dots[int(simplex[0])][0]),int(dots[int(simplex[1])][0]),int(dots[int(simplex[2])][0])])
		y = np.average([int(dots[int(simplex[0])][1]),int(dots[int(simplex[1])][1]),int(dots[int(simplex[2])][1])])

		(color1, color2, color3, alpha) = inImage[x,y]
		if int(random.random() * 255 ) >= color1:
			simplex = np.append(simplex,FG)
		else:
			simplex = np.append(simplex,BG)
		newTris.append([int(simplex[0]), int(simplex[1]), int(simplex[2]), int(simplex[3])])
	return (dots,newTris)

def getGradientLine(simplex,dots):
	xMin = np.min([int(dots[int(simplex[0])][0]),int(dots[int(simplex[1])][0]),int(dots[int(simplex[2])][0])])
	yMin = np.min([int(dots[int(simplex[0])][1]),int(dots[int(simplex[1])][1]),int(dots[int(simplex[2])][1])])

	xMax = np.max([int(dots[int(simplex[0])][0]),int(dots[int(simplex[1])][0]),int(dots[int(simplex[2])][0])])
	yMax = np.max([int(dots[int(simplex[0])][1]),int(dots[int(simplex[1])][1]),int(dots[int(simplex[2])][1])])

	if (dots[int(int(simplex[0]))][0]-xMin) == 0:
		x1 = 0
	else:
		x1 = int(100 / float(((xMax-xMin)/(dots[int(simplex[0])][0]-xMin))))

	if (dots[int(simplex[0])][1]-yMin) == 0:
		y1 = 0
	else:
		y1 = int(100 / float(((yMax-yMin)/(dots[int(simplex[0])][1]-yMin))))


	if (dots[int(simplex[1])][0]-xMin) == 0:
		x2 = 0
	else:
		x2 = int(100 / float(((xMax-xMin)/(dots[int(simplex[1])][0]-xMin))))

	if (dots[int(simplex[1])][1]-yMin) == 0:
		y2 = 0
	else:
		y2 = int(100 / float(((yMax-yMin)/(dots[int(simplex[1])][1]-yMin))))


	#find the center
	cx = (x1+x2)/2;
	cy = (y1+y2)/2;

	#move the line to center on the origin
	x1=x1-cx;
	y1=y1-cy;
	x2=x2-cx;
	y2=y2-cy;

	#rotate both points
	xtemp = x1
	ytemp = y1
	x1=-ytemp
	y1=xtemp

	xtemp = x2
	ytemp = y2
	x2=-ytemp
	y2=xtemp

	#move the center point back to where it was
	x1=x1+cx
	y1=y1+cy
	x2=x2+cx
	y2=y2+cy
	return (x1,y1,x2,y2)

def getGradient(gradient, simplex, dots, c1, c2, c3, p):

	(x1,y1,x2,y2) = getGradientLine(simplex, dots)
	r = "\n<linearGradient id=\"grad" + str(gradient) + "\" x1=\"%d%%\" y1=\"%d%%\" x2=\"%d%%\" y2=\"%d%%\">\n<stop offset=\"0%%\" style=\"stop-color:rgb(%d,%d,%d);stop-opacity:1\" />\n<stop offset=\"80%%\" style=\"stop-color:rgb(%d,%d,%d);stop-opacity:1\" />\n</linearGradient>" % (x1,y1,x2,y2,min(int(c1*p),255),min(int(c2*p),255),min(int(c3*p),255),c1,c2,c3)

	return r

def getSVGTriangle(simplex, dots, gradient):
	return "<polygon points=\"%d,%d %d,%d %d,%d\" style=\"fill:url(#grad%d),stroke-width:0\" />\n" % (dots[int(simplex[0])][0],dots[int(simplex[0])][1],dots[int(simplex[1])][0],dots[int(simplex[1])][1],dots[int(simplex[2])][0],dots[int(simplex[2])][1],gradient)

def exportPic(outImage, tris, dots, fgcolor, bgcolor, size, monobg = False, overlayImage = None, lineWidth=0):
	canvas = (SIZE,SIZE)
	svgGrad = ""
	svgPoly = ""

	gradient = 0

	if bgcolor is 1:
		im = Image.new('RGB', canvas, (255,255,255,255))
	else:
		im = Image.new('RGB', canvas, (0,0,0,255))
	draw = ImageDraw.Draw(im, 'RGBA')

	for simplex in tris:
		#idx = np.argmin([int(dots[simplex[0]][0]),int(dots[simplex[1]][0]),int(dots[simplex[2]][0])])
		x = np.average([int(dots[int(simplex[0])][0]),int(dots[int(simplex[1])][0]),int(dots[int(simplex[2])][0])])
		y = np.average([int(dots[int(simplex[0])][1]),int(dots[int(simplex[1])][1]),int(dots[int(simplex[2])][1])])

		if simplex[COLORINDEX] == FG:
			(c1,c2,c3) = getFGColor(fgcolor)
			draw.polygon([dots[int(simplex[0])][0],dots[int(simplex[0])][1],dots[int(simplex[1])][0],dots[int(simplex[1])][1],dots[int(simplex[2])][0],dots[int(simplex[2])][1]], fill=(c1,c2,c3,255))

			p = 1.8
			grad = getGradient(gradient, simplex, dots, c1, c2, c3, p)
			svgGrad = svgGrad + grad
			svgPoly = svgPoly + getSVGTriangle(simplex, dots, gradient)
			gradient = gradient + 1
		else:
			(c1,c2,c3) = getBGColor(bgcolor)
			# Drawing the bg parts only when not in monobg mode
			if not monobg:
				draw.polygon([dots[int(simplex[0])][0],dots[int(simplex[0])][1],dots[int(simplex[1])][0],dots[int(simplex[1])][1],dots[int(simplex[2])][0],dots[int(simplex[2])][1]], fill=(c1,c2,c3,255))

				p = 1.05
				grad = getGradient(gradient, simplex, dots, c1, c2, c3, p)
				svgGrad = svgGrad + grad
				svgPoly = svgPoly + getSVGTriangle(simplex, dots, gradient)
				gradient = gradient + 1


		# DRAWING the gaps
		if bgcolor is 0:
			c = (0,0,0,255)
			svgBG = "<polygon points=\"0,0 %d,0 %d,%d 0,%d\" fill=\"rgb(0,0,0)\" />\n" % (SIZE,SIZE,SIZE,SIZE)
		else:
			c = (255,255,255,255)
			svgBG = "<polygon points=\"0,0 %d,0 %d,%d 0,%d\" fill=\"rgb(255,255,255)\" />\n" % (SIZE,SIZE,SIZE,SIZE)

		w = lineWidth
		if w != 0:
			draw.line([dots[int(simplex[0])][0],dots[int(simplex[0])][1],dots[int(simplex[1])][0],dots[int(simplex[1])][1]], width=w, fill=c)
			draw.line([dots[int(simplex[0])][0],dots[int(simplex[0])][1],dots[int(simplex[2])][0],dots[int(simplex[2])][1]], width=w, fill=c)
			draw.line([dots[int(simplex[2])][0],dots[int(simplex[2])][1],dots[int(simplex[1])][0],dots[int(simplex[1])][1]], width=w, fill=c)

	if overlayImage is not None:
		im.paste(overlayImage, (0,0), overlayImage)
	im.save(outImage+".png")

	svg = "<svg height=\""+str(SIZE)+"\" width=\""+str(SIZE)+"\">\n" + "<defs>\n" + svgGrad + "</defs>\n" + svgBG + svgPoly + "</svg>"
	f = open(outImage + ".svg", "w")
	f.write(svg)

# MAIN
if __name__ == "__main__":
	try:

		if True:
			dots = generateDots(DOTS, SIZE)
			(dots,tris) = buildMesh(INPUTIMAGE,dots)
			np.savetxt("meshDot.dat", dots)
			np.savetxt("meshTris.dat", tris)
		else:
			dots = np.loadtxt("meshDot.dat")
			tris = np.loadtxt("meshTris.dat")
		print(tris[0])

		for fg in range(0,len(FGTHEMES)):
			for bg in range(0,len(BGTHEMES)):
				if bg == 1:
					exportPic(OUTPUTIMAGE + "_"+ str(fg) + "-" + str(bg), tris, dots, fg, bg, SIZE, overlayImage = OVERLAY_W, lineWidth=LINEWIDTH)
				else:
					exportPic(OUTPUTIMAGE + "_"+ str(fg) + "-" + str(bg), tris, dots, fg, bg, SIZE, overlayImage = OVERLAY_B, lineWidth=LINEWIDTH)



	except KeyboardInterrupt as e:
		logger.warning("Received KeyboardInterrupt! Terminating")
		exit(0)
