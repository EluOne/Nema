NEMA - Nova Echo Mining Assistant
=====

The goal of this project it to produce an application to interpret the output of fleet logs produced by the game "Eve Online" by CCP Games, into something more usable by mining directors and production managers.
This orginally started out as a command line python script for my personal use. But as I have had some requests to make it a bit more user friendly, a GUI seemed a good place to start.

At present it is a single window application which will output the data from a single log file selected by the user.

Currently this output groups by pilot and ore type, then outputs the fleet percentages of volume mined.
Salvaged materials and everything else not ice or ore currently dumps into their own columns only grouped by pilot.

The unreleased version of NEMA is currently under going a large UI overhaul and expansion of features to be more of a general fleet tool, with work being done on a Loot analysis tool to give suggestions on what should be sold and what should be refined according to your prefered local in game market.
The Loot analysis tool requires an internet connection to fetch data from the out of game market data soure eve-central.com

This project uses wxPython and ObjectListView modules.