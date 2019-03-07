#!/bin/bash

for file in svg_*.svg
do
	echo "Processing $file"
	fileTrimmed=${file%%.svg}
	inkscape -D -z --file=$fileTrimmed.svg --export-pdf=$fileTrimmed.pdf --export-latex
done

pdflatex document.tex

rm document.out
rm document.log
rm document.aux

