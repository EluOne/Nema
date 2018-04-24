NEMA - Nova Echo Mining Assistant
=====

This project is no longer in development as similar functionality is now provided in game.
-----

The goal of this project it to produce an application to interpret the output of fleet logs produced by the game "Eve Online" by CCP Games, into something more usable by mining directors and production managers.
This originally started out as a command line python script for my personal use. But as I have had some requests to make it a bit more user friendly, a GUI seemed a good place to start.

At present it is a single window application written in Python which will output the data from a single log file selected by the user.

Currently this output groups by pilot and ore type, then outputs the fleet percentages of volume mined.
Salvaged materials and everything else not ice or ore currently dumps into their own columns only grouped by pilot.

The unreleased version of NEMA is currently under going a large UI overhaul and expansion of features to be more of a general fleet tool.

The main window now uses a tabbed layout to make way for the new 'Loot' tab showing the output from a new analysis tool to give the user an overview of what should be done with the items collected.
The Loot analysis tool makes use the CCP static data dump in sqlite3 format and requires an internet connection to fetch current market data in XML format from the out of game source eve-central.com to give suggestions on what should be sold and what should be reprocessed according to your preferred local in game market.

This project uses wxPython, sqlite3, requests, ElementTree and ObjectListView modules.
