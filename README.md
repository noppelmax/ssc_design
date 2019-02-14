# TriMesh Builder

## Install
Install all dependencies via pip, conda or you packagemanager.

## Run
```
python3 <outputname> <inputimage> <ndots> [overlayimage]
```
Outname should be a short indicator which run it is. Existing files will be overwritten. For example choose "result". The files will be named "result\_fire\_black.png", "result\_red\_white.png" ...

Inputimage should be a grayscale quadratic image (width = height), where black is corresonding to the probability a triangle is draw in color. (red or fire)

ndots is the number of dots the delaunay triangulation is running on. Choose many to get a smaller mesh.

The overlayimage is optional but should have the same size as the inputimage.

An example:
```
python3 trimesh.py result input.png 1200 anzug.png
```

