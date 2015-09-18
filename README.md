# AirfoilDesign

A group of Python scripts to interact with third party programs to design and calculate the properties of airfoils. Both scripts can generate/load NACA four-digit airfoils and sweep over an array of angles of attack at a specific Reynolds number.

The NACA four-digit wing sections define the profile by:
  - First digit describing maximum camber as percentage of the chord.
  - Second digit describing the distance of maximum camber from the airfoil leading edge in tens of percents of the chord.
  - Last two digits describing maximum thickness of the airfoil as percent of the chord.

Currently working (other versions may or may not work):
  * OpenFOAM 2.3.0
  * XFOIL 6.97
