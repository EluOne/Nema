NEMA - Nova Echo Mining Assistant
=====

The goal of this project it to produce an application to interpret the output of fleet logs produced by the game "Eve Online" by CCP Games, into something more usable by mining directors and production managers.
This orginally started out as a command line python script for my personal use. But as I have had some requests to make it a bit more user friendly, a GUI seemed a good place to start.

At present it is a single window application which will output the data from a single log file selected by the user.

Currently this output groups by pilot and ore type, then outputs the fleet percentages of volume mined.
Salvaged materials and everything else not ice or ore currently dumps into their own columns only grouped by pilot.

I am using this project to help me learn wxPython and further my understanding of python, so there are bound to be mistakes/bugs.
