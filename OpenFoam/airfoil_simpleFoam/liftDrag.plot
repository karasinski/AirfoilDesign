#!/usr/bin/gnuplot

set xlabel 'Analysis step'
set ylabel 'Lift coefficient'
set y2label 'Drag coefficient'

set y2tics

set grid

set term png size 1000,600
set output 'liftDrag.png'

plot 'postProcessing/forceCoeffs/0/forceCoeffs.dat' using 1:4 with lines title 'Lift coefficient' axis x1y1, \
     'postProcessing/forceCoeffs/0/forceCoeffs.dat' using 1:3 with lines title 'Drag coefficient' axis x1y2

