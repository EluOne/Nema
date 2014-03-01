#!/usr/bin/python
'Nova Echo Mining Assistant'
# Copyright (C) 2013  Tim Cumming
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Author: Tim Cumming aka Elusive One
# Created: 05/03/13

import os.path
import pickle

settings = {}

# System db id numbers
systemNames = {30002659: 'Dodixie', 30000142: 'Jita', 30002053: 'Hek', 30002187: 'Amarr'}
systemList = [[30002659, 'Dodixie'], [30000142, 'Jita'], [30002053, 'Hek'], [30002187, 'Amarr']]

# Mineral db id numbers
mineralIDs = {34: 'Tritanium', 35: 'Pyerite', 36: 'Mexallon', 37: 'Isogen', 38: 'Nocxium', 39: 'Zydrine', 40: 'Megacyte', 11399: 'Morphite'}

# EVE ore and ice volumes per unit as a dictionary
OreTypes = {'Arkonor': 16, 'Bistot': 16, 'Crokite': 16, 'Dark Ochre': 8,
    'Gneiss': 5, 'Hedbergite': 3, 'Hemorphite': 3, 'Jaspet': 2,
    'Kernite': 1.2, 'Mercoxit': 40, 'Omber': 0.6, 'Plagioclase': 0.35,
    'Pyroxeres': 0.3, 'Scordite': 0.15, 'Spodumain': 16, 'Veldspar': 0.1}
IceTypes = {'Blue Ice': 1000, 'White Glaze': 1000, 'Glacial Mass': 1000, 'Clear Icicle': 1000}

# Refined outputs: [0]Mineral Name, [1]Batch, [2]Tri, [3]Pye, [4]Mex, [5]Iso, [6]Noc, [7]Zyd, [8]Meg, [9]Mor
# TODO: Expand to include all ore types (2 more per group)
OreOutput = [['Arkonor', 200, 300, 0, 0, 0, 0, 166, 333, 0],
             ['Bistot', 200, 0, 170, 0, 0, 0, 341, 170, 0],
             ['Crokite', 250, 331, 0, 0, 0, 331, 663, 0, 0],
             ['Dark Ochre', 400, 250, 0, 0, 0, 500, 250, 0, 0],
             ['Gneiss', 400, 171, 0, 171, 343, 0, 171, 0, 0],
             ['Hedbergite', 500, 0, 0, 0, 708, 354, 32, 0, 0],
             ['Hemorphite', 500, 212, 0, 0, 212, 424, 28, 0, 0],
             ['Jaspet', 500, 259, 259, 518, 0, 259, 8, 0, 0],
             ['Kernite', 400, 386, 0, 773, 386, 0, 0, 0, 0],
             ['Mercoxit', 250, 0, 0, 0, 0, 0, 0, 0, 530],
             ['Omber', 500, 307, 123, 0, 307, 0, 0, 0, 0],
             ['Plagioclase', 333, 256, 512, 256, 0, 0, 0, 0, 0],
             ['Pyroxeres', 333, 844, 59, 120, 0, 11, 0, 0, 0],
             ['Scordite', 333, 833, 416, 0, 0, 0, 0, 0, 0, 0],
             ['Spodumain', 250, 700, 140, 0, 0, 0, 0, 140, 0],
             ['Veldspar', 300, 1000, 0, 0, 0, 0, 0, 0, 0]]

# Lets try to load up our settings from the ini file.
if (os.path.isfile('nema.ini')):
    iniFile = open('nema.ini', 'r')
    settings = pickle.load(iniFile)
    iniFile.close()
else:
    # Default compact mode to false
    settings['compact'] = False
    # Default market system to Jita
    settings['system'] = 30000142
