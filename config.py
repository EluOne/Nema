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
