#!/usr/bin/python
import logging
from PIL import Image, ImageDraw
import random
import sys
import numpy as np
import math
from scipy.spatial import Delaunay


FGTHEMES = ["fire","ice","darkgreen","lightgreen"]
BGTHEMES = ["black_bg", "white_bg"]


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

OVERLAY_W = Image.open("anzug_w.png")
OVERLAYIMAGE_W = OVERLAY_W.load()
(w,h) = OVERLAY_W.size
if w != SIZE or h != SIZE:
	logger.error("Die Masse des Overlays muessen dem des Inputbildes entsprechen. %d x %d pixel" % (SIZE,SIZE))
	exit(1)

OVERLAY_B = Image.open("anzug_b.png")
OVERLAYIMAGE_B = OVERLAY_B.load()
(w,h) = OVERLAY_B.size
if w != SIZE or h != SIZE:
	logger.error("Die Masse des Overlays muessen dem des Inputbildes entsprechen. %d x %d pixel" % (SIZE,SIZE))
	exit(1)

LINEWIDTH = 0

def generateDots(ndots,size):

	#for i in range(0,DOTS):
	#	dots.append((int(random.random() * WIDTH), int(random.random() * HEIGHT)))
	dots = np.random.randint(1, size-1, (ndots+4, 2))
	dots[0] = [0,0]
	dots[1] = [size-1,0]
	dots[2] = [0,size-1]
	dots[3] = [size-1,size-1]

	tris = Delaunay(dots)

	return (dots,tris)

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

def buildMesh( inImage, tris, dots):
	newTris = []

	for simplex in tris.simplices:
		x = np.average([int(dots[simplex[0]][0]),int(dots[simplex[1]][0]),int(dots[simplex[2]][0])])
		y = np.average([int(dots[simplex[0]][1]),int(dots[simplex[1]][1]),int(dots[simplex[2]][1])])

		(color1, color2, color3, alpha) = inImage[x,y]
		if int(random.random() * 255 ) >= color1:
			simplex = np.append(simplex,FG)
		else:
			simplex = np.append(simplex,BG)
		newTris.append([simplex[0], simplex[1], simplex[2], simplex[3]])
	return (dots,newTris)


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
		x = np.average([int(dots[simplex[0]][0]),int(dots[simplex[1]][0]),int(dots[simplex[2]][0])])
		y = np.average([int(dots[simplex[0]][1]),int(dots[simplex[1]][1]),int(dots[simplex[2]][1])])

		if simplex[COLORINDEX] == FG:
			(c1,c2,c3) = getFGColor(fgcolor)
			draw.polygon([dots[simplex[0]][0],dots[simplex[0]][1],dots[simplex[1]][0],dots[simplex[1]][1],dots[simplex[2]][0],dots[simplex[2]][1]], fill=(c1,c2,c3,255))

			p = 1.01
			grad = "<linearGradient id=\"grad" + str(gradient) + "\" x1=\"0%%\" y1=\"0%%\" x2=\"0%%\" y2=\"300%%\">\n<stop offset=\"0%%\" style=\"stop-color:rgb(%d,%d,%d);stop-opacity:1\" />\n<stop offset=\"200%%\" style=\"stop-color:rgb(%d,%d,%d);stop-opacity:1\" /></linearGradient>" % (c1,c2,c3, int(c1*p),int(c1*p),int(c1*p))
			svgGrad = svgGrad + grad

			#svgPoly = svgPoly + "<polygon points=\"%d,%d %d,%d %d,%d\" fill=\"rgb(%d,%d,%d)\" />\n" % (dots[simplex[0]][0],dots[simplex[0]][1],dots[simplex[1]][0],dots[simplex[1]][1],dots[simplex[2]][0],dots[simplex[2]][1],c1,c2,c3)
			svgPoly = svgPoly + "<polygon points=\"%d,%d %d,%d %d,%d\" fill=\"url(#grad%d)\" />\n" % (dots[simplex[0]][0],dots[simplex[0]][1],dots[simplex[1]][0],dots[simplex[1]][1],dots[simplex[2]][0],dots[simplex[2]][1],gradient)
			gradient = gradient + 1
		else:
			(c1,c2,c3) = getBGColor(bgcolor)
			# Drawing the bg parts only when not in monobg mode
			if not monobg:
				draw.polygon([dots[simplex[0]][0],dots[simplex[0]][1],dots[simplex[1]][0],dots[simplex[1]][1],dots[simplex[2]][0],dots[simplex[2]][1]], fill=(c1,c2,c3,255))

				p = 1.01
				grad = "<linearGradient id=\"grad" + str(gradient) + "\" x1=\"0%%\" y1=\"0%%\" x2=\"0%%\" y2=\"100%%\">\n<stop offset=\"0%%\" style=\"stop-color:rgb(%d,%d,%d);stop-opacity:1\" />\n<stop offset=\"100%%\" style=\"stop-color:rgb(%d,%d,%d);stop-opacity:1\" /></linearGradient>" % (c1,c2,c3, int(c1*p),int(c1*p),int(c1*p))
				svgGrad = svgGrad + grad
				#svgPoly = svgPoly + "<polygon points=\"%d,%d %d,%d %d,%d\" fill=\"rgb(%d,%d,%d)\" />\n" % (dots[simplex[0]][0],dots[simplex[0]][1],dots[simplex[1]][0],dots[simplex[1]][1],dots[simplex[2]][0],dots[simplex[2]][1],c1,c2,c3)
				svgPoly = svgPoly + "<polygon points=\"%d,%d %d,%d %d,%d\" fill=\"url(#grad%d)\" />\n" % (dots[simplex[0]][0],dots[simplex[0]][1],dots[simplex[1]][0],dots[simplex[1]][1],dots[simplex[2]][0],dots[simplex[2]][1],gradient)
				gradient = gradient + 1


		# DRAWING the gaps
		if bgcolor is 0:
			c = (0,0,0,255)
		else:
			c = (230,230,230,255)

		w = lineWidth
		if w != 0:
			draw.line([dots[simplex[0]][0],dots[simplex[0]][1],dots[simplex[1]][0],dots[simplex[1]][1]], width=w, fill=c)
			draw.line([dots[simplex[0]][0],dots[simplex[0]][1],dots[simplex[2]][0],dots[simplex[2]][1]], width=w, fill=c)
			draw.line([dots[simplex[2]][0],dots[simplex[2]][1],dots[simplex[1]][0],dots[simplex[1]][1]], width=w, fill=c)

	if overlayImage is not None:
		im.paste(overlayImage, (0,0), overlayImage)
	im.save(outImage)
	svg = "<svg height=\""+str(SIZE)+"\" width=\""+str(SIZE)+"\">\n" + "<defs>\n" + svgGrad + "</defs>\n" + svgPoly + "</svg>"
	f = open("test.svg", "w")
	f.write(svg)

# MAIN
if __name__ == "__main__":
	try:
		(dots,tris) = generateDots(DOTS, SIZE)
		(dots,tris) = buildMesh(INPUTIMAGE,tris, dots)

		for fg in range(0,len(FGTHEMES)):
			for bg in range(0,len(BGTHEMES)):
				if bg == 1:
					exportPic(OUTPUTIMAGE + "_"+ str(fg) + "-" + str(bg) + ".png", tris, dots, fg, bg, SIZE, overlayImage = OVERLAY_W, lineWidth=LINEWIDTH)
				else:
					exportPic(OUTPUTIMAGE + "_"+ str(fg) + "-" + str(bg) + ".png", tris, dots, fg, bg, SIZE, overlayImage = OVERLAY_B, lineWidth=LINEWIDTH)


	except KeyboardInterrupt as e:
		logger.warning("Received KeyboardInterrupt! Terminating")
		exit(0)
