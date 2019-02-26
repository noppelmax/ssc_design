#!/usr/bin/python
import logging
from PIL import Image, ImageDraw
import random
import sys
import numpy as np
import math
from scipy.spatial import Delaunay

FGCOLOR_RED = 0
FGCOLOR_FIRE = 1

BGCOLOR_BLACK = 0
BGCOLOR_WHITE = 1


def printUsage():
	exit("Usage: <outputimage> <inputimage> <ndots> [overlay]")

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
try:
	if sys.argv[4]:
		logger.info("Use overlay")
		OVERLAY = Image.open(sys.argv[4])
		OVERLAYIMAGE = OVERLAY.load()
		(w,h) = OVERLAY.size
		if w != SIZE or h != size:
			logger.error("Die Masse des Overlays muessen dem des Inputbildes entsprechen. %d x %d pixel" % (SIZE,SIZE))
			exit(1)
except:
	pass

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

def setColor(fgcolor):
	if fgcolor is FGCOLOR_RED:
		c1 = 0 + int(random.random() * 255)
		c2 = 0 + int(random.random() * 30)
		c3 = 0 + int(random.random() * 30)

	if fgcolor is FGCOLOR_FIRE:
		c1 = 255
		c2 = 30 + int(random.random() * 225)
		c3 = 0 + int(random.random() * 50)
	return (c1,c2,c3)

def setBW(bgcolor):
	if bgcolor is BGCOLOR_WHITE:
		c1 =  255 - int(random.random() * 50)
	else:
		c1 = int(random.random() * 50)
	c2 = c1
	c3 = c1
	return (c1,c2,c3)

def draw( outImage, inImage, ndots, fgcolor, bgcolor, size, monobg = False, overlayImage = None, lineWidth=0):
	(dots,tris) = generateDots(ndots, size)
	canvas = (SIZE,SIZE)

	svgGrad = ""
	svgPoly = ""

	gradient = 0

	if bgcolor is BGCOLOR_WHITE:
		im = Image.new('RGB', canvas, (255,255,255,255))
	else:
		im = Image.new('RGB', canvas, (0,0,0,255))
	draw = ImageDraw.Draw(im, 'RGBA')

	for simplex in tris.simplices:
		#idx = np.argmin([int(dots[simplex[0]][0]),int(dots[simplex[1]][0]),int(dots[simplex[2]][0])])
		x = np.average([int(dots[simplex[0]][0]),int(dots[simplex[1]][0]),int(dots[simplex[2]][0])])
		y = np.average([int(dots[simplex[0]][1]),int(dots[simplex[1]][1]),int(dots[simplex[2]][1])])

		#(color1, color2, color3, alpha) = inImage[int(dots[simplex[idx]][0]),int(dots[simplex[idx]][1])]
		(color1, color2, color3, alpha) = inImage[x,y]
		if int(random.random() * 255 ) >= color1:

			(c1,c2,c3) = setColor(fgcolor)
			draw.polygon([dots[simplex[0]][0],dots[simplex[0]][1],dots[simplex[1]][0],dots[simplex[1]][1],dots[simplex[2]][0],dots[simplex[2]][1]], fill=(c1,c2,c3,255))

			p = 1.01
			grad = "<linearGradient id=\"grad" + str(gradient) + "\" x1=\"0%%\" y1=\"0%%\" x2=\"0%%\" y2=\"300%%\">\n<stop offset=\"0%%\" style=\"stop-color:rgb(%d,%d,%d);stop-opacity:1\" />\n<stop offset=\"200%%\" style=\"stop-color:rgb(%d,%d,%d);stop-opacity:1\" /></linearGradient>" % (c1,c2,c3, int(c1*p),int(c1*p),int(c1*p))
			svgGrad = svgGrad + grad

			#svgPoly = svgPoly + "<polygon points=\"%d,%d %d,%d %d,%d\" fill=\"rgb(%d,%d,%d)\" />\n" % (dots[simplex[0]][0],dots[simplex[0]][1],dots[simplex[1]][0],dots[simplex[1]][1],dots[simplex[2]][0],dots[simplex[2]][1],c1,c2,c3)
			svgPoly = svgPoly + "<polygon points=\"%d,%d %d,%d %d,%d\" fill=\"url(#grad%d)\" />\n" % (dots[simplex[0]][0],dots[simplex[0]][1],dots[simplex[1]][0],dots[simplex[1]][1],dots[simplex[2]][0],dots[simplex[2]][1],gradient)
			gradient = gradient + 1
		else:

			(c1,c2,c3) = setBW(bgcolor)
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
		if bgcolor is BGCOLOR_BLACK:
			c = (0,0,0,255)
		else:
			c = (255,255,255,255)

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
		draw(OUTPUTIMAGE + "_red_black.png", INPUTIMAGE, DOTS, FGCOLOR_RED, BGCOLOR_BLACK, SIZE, overlayImage = OVERLAY, lineWidth=LINEWIDTH)
		#draw(OUTPUTIMAGE + "_fire_black.png", INPUTIMAGE, DOTS, FGCOLOR_FIRE, BGCOLOR_BLACK, SIZE, overlayImage = OVERLAY, lineWidth=LINEWIDTH)
		draw(OUTPUTIMAGE + "_red_white.png", INPUTIMAGE, DOTS, FGCOLOR_RED, BGCOLOR_WHITE, SIZE, overlayImage = OVERLAY, lineWidth=LINEWIDTH)
		#draw(OUTPUTIMAGE + "_fire_white.png", INPUTIMAGE, DOTS, FGCOLOR_FIRE, BGCOLOR_WHITE, SIZE, overlayImage = OVERLAY, lineWidth=LINEWIDTH)

		#draw(OUTPUTIMAGE + "_red_black_monobg.png", INPUTIMAGE, DOTS, FGCOLOR_RED, BGCOLOR_BLACK, SIZE, monobg = True, overlayImage = OVERLAY, lineWidth=LINEWIDTH)
		#draw(OUTPUTIMAGE + "_fire_black_monobg.png", INPUTIMAGE, DOTS, FGCOLOR_FIRE, BGCOLOR_BLACK, SIZE, monobg = True, overlayImage = OVERLAY, lineWidth=LINEWIDTH)
		#draw(OUTPUTIMAGE + "_red_white_monobg.png", INPUTIMAGE, DOTS, FGCOLOR_RED, BGCOLOR_WHITE, SIZE, monobg = True, overlayImage = OVERLAY, lineWidth=LINEWIDTH)
		#draw(OUTPUTIMAGE + "_fire_white_monobg.png", INPUTIMAGE, DOTS, FGCOLOR_FIRE, BGCOLOR_WHITE, SIZE, monobg = True, overlayImage = OVERLAY, lineWidth=LINEWIDTH)

	except KeyboardInterrupt as e:
		logger.warning("Received KeyboardInterrupt! Terminating")
		exit(0)
