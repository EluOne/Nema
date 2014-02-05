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

import math
import urllib2
import httplib
import traceback

import sqlite3 as lite
import xml.etree.ElementTree as etree

import wx
from wx.lib.ticker import Ticker
from operator import itemgetter

from ObjectListView import ObjectListView, ColumnDefn, GroupListView

# This needs connecting to the ui soon.
compact = bool(False)

#Initialise lists
ore = []
ice = []
salvage = []
other = []

pilots = []
icePilots = []
orePilots = []

# System db id numbers
systemNames = {30002659: 'Dodixie', 30000142: 'Jita'}
# Mineral db id numbers
mineralIDs = {34: 'Tritanium', 35: 'Pyerite', 36: 'Mexallon', 37: 'Isogen', 38: 'Nocxium', 39: 'Zydrine', 40: 'Megacyte', 11399: 'Morphite'}
# Set the market prices from Eve Central will look like:
# mineralBuy = {34: 4.65, 35: 11.14, 36: 43.82, 37: 120.03, 38: 706.93, 39: 727.19, 40: 1592.10}
mineralBuy = {}
mineralSell = {}

itemBuy = {}
itemSell = {}

# These are the expected column headers from the first row of the data file
columns = {'Time', 'Character', 'Item Type', 'Quantity', 'Item Group'}

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


class Salvage(object):
    def __init__(self, itemID, itemName, itemBuyValue, itemSellValue, reprocessBuyValue, reprocessSellValue, action):
        self.itemID = itemID
        self.itemName = itemName
        # '{:,.2f}'.format(value) Uses the Format Specification Mini-Language to produce more human friendly output.
        self.itemBuyValue = '{:,.2f}'.format(itemBuyValue)
        self.itemSellValue = '{:,.2f}'.format(itemSellValue)
        self.reprocessBuyValue = '{:,.2f}'.format(reprocessBuyValue)
        self.reprocessSellValue = '{:,.2f}'.format(reprocessSellValue)
        self.action = action


def onError(error):
    dlg = wx.MessageDialog(None, 'An error has occurred:\n' + error, '', wx.OK | wx.ICON_ERROR)
    dlg.ShowModal()  # Show it
    dlg.Destroy()  # finally destroy it when finished.
#    print('An error has occurred:\n' + error, '\n')


def id2name(idType, ids):  # Takes a list of IDs to query the local db or api server.
    typeNames = {}
    typePortions = {}
    if idType == 'name':
        # We'll use the local static DB for items as they don't change.
        if ids != []:  # We have some ids we don't know.
            try:
                idList = ('", "'.join(map(str, ids[:])))
                con = lite.connect('static.db')

                with con:
                    cur = con.cursor()
                    statement = "SELECT typeID, typeName, portionSize FROM invtypes WHERE typeName IN (\"" + idList + "\")"
                    cur.execute(statement)

                    rows = cur.fetchall()

                    # Use the item strings returned to populate the typeNames dictionary.
                    for row in rows:
                        typeNames.update({int(row[0]): str(row[1])})
                        typePortions.update({int(row[0]): str(row[2])})
                        ids.remove(row[1])

                if ids != []:  # We have some ids we don't know.
                    #numItems = range(len(ids))
                    #for y in numItems:
                    #    typeNames.update({str(ids[y]): str(ids[y])})
                    error = ('Item not found in database: ' + str(ids))  # Error String
                    onError(error)

            except lite.Error as err:
                error = ('SQL Lite Error: ' + str(err.args[0]) + str(err.args[1:]))  # Error String
                #ids = idList.split("', '")
                #numItems = range(len(ids))
                #for y in numItems:
                #    typeNames.update({str(ids[y]): str(ids[y])})
                onError(error)
            finally:
                if con:
                    con.close()
    return typeNames, typePortions


def fetchMinerals():
    global mineralBuy
    global mineralSell

    # All base minerals from Dodi url:
    # http://api.eve-central.com/api/marketstat?typeid=34&typeid=35&typeid=36&typeid=37&typeid=38&typeid=39&typeid=40&usesystem=30002659
    apiURL = 'http://api.eve-central.com/api/marketstat?typeid=34&typeid=35&typeid=36&typeid=37&typeid=38&typeid=39&typeid=40&typeid=11399&usesystem=30002659'

    try:  # Try to connect to the API server
        target = urllib2.urlopen(apiURL)  # download the file
        downloadedData = target.read()  # convert to string
        target.close()  # close file because we don't need it anymore

        tree = etree.fromstring(downloadedData)
        types = tree.findall('.//type')

        for child in types:
            ids = child.attrib
            buy = child.find('buy')
            sell = child.find('sell')
            if int(ids['id']) in mineralIDs:
                mineralBuy[int(ids['id'])] = float(buy.find('max').text)
                mineralSell[int(ids['id'])] = float(sell.find('min').text)
    except urllib2.HTTPError as err:
        error = ('HTTP Error: %s %s\n' % (str(err.code), str(err.reason)))  # Error String
        onError(error)
    except urllib2.URLError as err:
        error = ('Error Connecting to Tranquility: ' + str(err.reason))  # Error String
        onError(error)
    except httplib.HTTPException as err:
        error = ('HTTP Exception')  # Error String
        onError(error)
    except Exception:
        error = ('Generic Exception: ' + traceback.format_exc())  # Error String
        onError(error)


def fetchItems(typeIDs):
    global itemBuy
    global itemSell

    if typeIDs != []:
        # Calculate the number of ids we have. We'll use a maximum of 100 IDs per query.
        # So we'll need to split this into multiple queries.

        numIDs = len(typeIDs)
        idList = []

        if numIDs > 100:
            startID = 0
            endID = 100
            while startID < numIDs:
                idList.append("&typeid=".join(map(str, typeIDs[startID:endID])))
                startID = startID + 100
                if ((numIDs - endID)) > 100:
                    endID = endID + 100
                else:
                    endID = numIDs

        else:
            idList.append("&typeid=".join(map(str, typeIDs[0:numIDs])))

        numIdLists = list(range(len(idList)))
        for x in numIdLists:  # Iterate over all of the id lists generated above.
            # Item prices from Dodi url:
            # http://api.eve-central.com/api/marketstat?typeid=16437&typeid=4473&usesystem=30002659
            apiURL = 'http://api.eve-central.com/api/marketstat?typeid=16437&typeid=%s&usesystem=30002659' % (idList[x])
            print(apiURL)

            try:  # Try to connect to the API server
                target = urllib2.urlopen(apiURL)  # download the file
                downloadedData = target.read()  # convert to string
                target.close()  # close file because we don't need it anymore

                tree = etree.fromstring(downloadedData)
                types = tree.findall('.//type')

                for child in types:
                    ids = child.attrib
                    buy = child.find('buy')
                    sell = child.find('sell')
                    if int(ids['id']) in typeIDs:
                        itemBuy[int(ids['id'])] = float(buy.find('max').text)
                        itemSell[int(ids['id'])] = float(sell.find('min').text)
            except urllib2.HTTPError as err:
                error = ('HTTP Error: %s %s' % (str(err.code), str(err.reason)))  # Error String
                onError(error)
            except urllib2.URLError as err:
                error = ('Error Connecting to Tranquility: ' + str(err.reason))  # Error String
                onError(error)
            except httplib.HTTPException as err:
                error = ('HTTP Exception')  # Error String
                onError(error)
            except Exception:
                error = ('Generic Exception: ' + traceback.format_exc())  # Error String
                onError(error)


def reprocess(itemID):  # Takes a list of IDs to query the local db or api server.
    minerals = {}
    # We'll use the local static DB for items as they don't change.
    if itemID != '':  # We have some ids we don't know.
        try:
            con = lite.connect('static.db')

            with con:
                cur = con.cursor()
                statement = "SELECT materialTypeID, quantity FROM invTypeMaterials WHERE typeID = " + str(itemID)
                cur.execute(statement)

                rows = cur.fetchall()

                # Use the item strings returned to populate the typeNames dictionary.
                for row in rows:
                    minerals.update({int(row[0]): int(row[1])})

        except lite.Error as err:
            error = ('SQL Lite Error: ' + str(err.args[0]) + str(err.args[1:]))  # Error String
            onError(error)
        finally:
            if con:
                con.close()
    return minerals


def fetchData(logContent):
    #Initialise globals lists
    global ore
    global ice
    global salvage
    global other

    global pilots
    global icePilots
    global orePilots

    #Initialise lists
    ore = []
    ice = []
    salvage = []
    other = []

    pilots = []
    icePilots = []
    orePilots = []

    numLines = range(len(logContent))

    for lineNum in numLines:
        # Process each line that was in the log file.
        line = logContent[lineNum].rstrip('\r\n')

        clean = line.strip()   # Removes newline characters
        if len(clean) > 0:
            data = clean.split('\t')   # Drops empty lines and outputs tuple
            # Output: [0] Time, [1] Character, [2] ItemType, [3] Quantity, [4] ItemGroup

            if data[0] != 'Time':   # Skip first line of log
                if data[1] not in pilots:
                    pilots.append(data[1])
                # Split ore from other items
                if data[4] in OreTypes:
                    if data[1] not in orePilots:
                        orePilots.append(data[1])
                    volume = (OreTypes[(data[4])] * int(data[3]))
                    ore.append([data[1], data[2], data[3], data[4], volume])
                # Split ice from other items
                elif data[4] == 'Ice':
                    if data[1] not in icePilots:
                        icePilots.append(data[1])
                    volume = (IceTypes[(data[2])] * int(data[3]))
                    ice.append([data[1], data[2], data[3], data[4], volume])
                elif data[4] == 'Salvaged Materials':
                    salvage.append([data[1], data[2], data[3], data[4], 0])
                # Everything else
                else:
                    other.append([data[1], data[2], data[3], data[4], 0])


def refineOre(oreMined):
    # TODO: Use the ore to mineral values to calculate mineral output
    #for key in oreMined:
    numItems = range(len(OreOutput))
    numMinerals = range(2, 9)  # We only need these values from OreOutput
    # To match the keys used above:
    mineralNames = {2: 'Tritanium', 3: 'Pyrite', 4: 'Mexallon', 5: 'Isogen', 6: 'Nocxium', 7: 'Zydrine', 8: 'Megacyte', 9: 'Morphite'}

    # Iterate over the ore types
    for item in numItems:
        # Refined outputs: [0]Mineral Name, [1]Batch, [2]Tri, [3]Pye, [4]Mex, [5]Iso, [6]Noc, [7]Zyd, [8]Meg, [9]Mor
        if (OreOutput[item][0]) in oreMined:
            batches = math.floor(float(oreMined[OreOutput[item][0]]) / float(OreOutput[item][1]))
            print('%s x %s' % (OreOutput[item][0], batches))
            for x in numMinerals:
                if OreOutput[item][x] > 0:
                    mineral = OreOutput[item][x] * batches
                    print('    %s x %s' % (mineralNames[x], mineral))


def processLog():
    # This uses the data taken from the global variables.
    global ore
    global ice
    global salvage
    global other

    global pilots
    global icePilots
    global orePilots

    oreTotals = []
    iceTotals = []

    oreMined = {}

    # Output: [0] Character, [1] ItemType, [2] Quantity, [3] ItemGroup, [4] Volume
    if compact is True:
        # Compact Mode:
        # Process the list of ore mined for duplicate type entries, and add them together. This produces a list that only details the ore group.
        ore = sorted(ore, key=itemgetter(0, 3))
        numItems = range(len(ore))

        for item in numItems:
            if (ore[item][3]) in oreMined:
                oreMined[ore[item][3]] = int(oreMined[ore[item][3]]) + int(ore[item][2])
            else:
                oreMined[ore[item][3]] = ore[item][2]

            if item > 0:
                previous = item - 1
                if (ore[item][0] == ore[previous][0]) and (ore[item][3] == ore[previous][3]):
                    newQuantity = (int(ore[item][2]) + int(ore[previous][2]))
                    newVolume = (OreTypes[ore[item][3]] * int(newQuantity))
                    ore[item] = [ore[item][0], ore[item][3], newQuantity, ore[item][3], newVolume]
                    ore[previous] = 'deleted'

        for o in ore[:]:
            if o == 'deleted':
                ore.remove(o)
    else:
        # Process the list of ore mined for duplicate entries, and add them together.
        ore = sorted(ore, key=itemgetter(0, 1))
        numItems = range(len(ore))

        for item in numItems:
            if (ore[item][1]) in oreMined:
                oreMined[ore[item][1]] = int(oreMined[ore[item][1]]) + int(ore[item][2])
            else:
                oreMined[ore[item][1]] = ore[item][2]

            if item > 0:
                previous = item - 1
                if (ore[item][0] == ore[previous][0]) and (ore[item][1] == ore[previous][1]):
                    newQuantity = (int(ore[item][2]) + int(ore[previous][2]))
                    newVolume = (OreTypes[ore[item][3]] * int(newQuantity))
                    ore[item] = [ore[item][0], ore[item][1], newQuantity, ore[item][3], newVolume]
                    ore[previous] = 'deleted'

        for o in ore[:]:
            if o == 'deleted':
                ore.remove(o)

    # Process the list of salvaged items for duplicate entries, and add them together.
    salvage = sorted(salvage, key=itemgetter(0, 1))
    numItems = range(len(salvage))

    for item in numItems:
        if item > 0:
            previous = item - 1
            if (salvage[item][0] == salvage[previous][0]) and (salvage[item][1] == salvage[previous][1]):
                newQuantity = (int(salvage[item][2]) + int(salvage[previous][2]))
                salvage[item] = [salvage[item][0], salvage[item][1], newQuantity, 0]
                salvage[previous] = 'deleted'

    for s in salvage[:]:
        if s == 'deleted':
            salvage.remove(s)

    # Process the list of other items for duplicate entries, and add them together.
    other = sorted(other, key=itemgetter(0, 1))
    numItems = range(len(other))

    for item in numItems:
        if item > 0:
            previous = item - 1
            if (other[item][0] == other[previous][0]) and (other[item][1] == other[previous][1]):
                newQuantity = (int(other[item][2]) + int(other[previous][2]))
                other[item] = [other[item][0], other[item][1], newQuantity, 0]
                other[previous] = 'deleted'

    for e in other[:]:
        if e == 'deleted':
            other.remove(e)

    if ice or ore or salvage or other:
        totalsOutput = ''  # Init String
        iceOutput = ''  # Init String
        oreOutput = ''  # Init String
        salvageOutput = ''  # Init String
        otherOutput = ''  # Init String

        if ice:  # Build a string to output to the text box named ice.
            totalIce = 0
            for entry in ice:
                totalIce = entry[4] + totalIce

            for name in sorted(icePilots):
                pilotIce = 0
                iceOutput = ('%s%s\n' % (iceOutput, name))
                for entry in sorted(ice, key=itemgetter(0, 3)):
                    if name == entry[0]:
                        if compact is True:
                            iceOutput = ('%s%s x %s = %s m3\n' % (iceOutput, entry[2], entry[3], entry[4]))
                        else:
                            iceOutput = ('%s%s x %s = %s m3\n' % (iceOutput, entry[2], entry[1], entry[4]))
                        pilotIce = entry[4] + pilotIce
                iceTotals.append([name, pilotIce, ((float(pilotIce) / float(totalIce)) * 100)])
                iceOutput = iceOutput + '\n'

            iceTotals = sorted(iceTotals, key=itemgetter(2), reverse=True)
            totalsOutput = ('%sPercentage of Ice: (%s) m3\n\n' % (totalsOutput, totalIce))

            iceRange = range(len(iceTotals))  # Remove calc from loop below.
            for entry in iceRange:
                if iceTotals[(entry)][1] > 0:
                    totalsOutput = ('%s%.2f%% %s: %s m3\n' % (totalsOutput, (iceTotals[(entry)][2]), iceTotals[(entry)][0], iceTotals[(entry)][1]))

            totalsOutput = ('%s\n' % (totalsOutput))

        if ore:  # Build a string to output to the text box named ore.
            totalOre = 0
            for entry in ore:
                totalOre = entry[4] + totalOre

            for name in sorted(orePilots):
                pilotOre = 0
                oreOutput = ('%s%s\n' % (oreOutput, name))
                for entry in sorted(ore, key=itemgetter(0, 3)):
                    if name == entry[0]:
                        if compact is True:
                            oreOutput = ('%s%s x %s = %.2f m3\n' % (oreOutput, entry[2], entry[3], entry[4]))
                        else:
                            oreOutput = ('%s%s x %s = %.2f m3\n' % (oreOutput, entry[2], entry[1], entry[4]))
                        pilotOre = entry[4] + pilotOre
                oreTotals.append([name, pilotOre, ((float(pilotOre) / float(totalOre)) * 100)])
                oreOutput = oreOutput + '\n'

            totalsOutput = ('%sUnits of Ore:\n\n' % (totalsOutput))

            for key in oreMined:
                totalsOutput = ('%s%s x %s\n' % (totalsOutput, key, oreMined[key]))
            totalsOutput = ('%s\n' % (totalsOutput))

            refineOre(oreMined)

            oreTotals = sorted(oreTotals, key=itemgetter(2), reverse=True)
            totalsOutput = ('%sPercentage of Ore: (%.2f) m3\n\n' % (totalsOutput, totalOre))

            oreRange = range(len(oreTotals))  # Remove calc from loop below.
            for entry in oreRange:
                if oreTotals[(entry)][1] > 0:
                    totalsOutput = ('%s%.2f%% %s: %.2f m3\n' % (totalsOutput, (oreTotals[(entry)][2]), oreTotals[(entry)][0], oreTotals[(entry)][1]))

            totalsOutput = ('%s\n' % (totalsOutput))

        if salvage:  # Build a string to output to the text box named salvage.
            pilot = ''
            for entry in sorted(salvage, key=itemgetter(0)):
                if pilot == '':  # This will be the first entry
                    pilot = entry[0]
                    salvageOutput = ('%s%s\n' % (salvageOutput, pilot))
                elif pilot != entry[0]:  # All others will need a /n adding to space them out
                    pilot = entry[0]
                    salvageOutput = ('%s\n%s\n' % (salvageOutput, pilot))
                salvageOutput = ('%s%s x %s\n' % (salvageOutput, entry[2], entry[1]))

        if other:  # Build a string to output to the text box named other.
            pilot = ''
            for entry in sorted(other, key=itemgetter(0)):
                if pilot == '':  # This will be the first entry
                    pilot = entry[0]
                    otherOutput = ('%s%s\n' % (otherOutput, pilot))
                elif pilot != entry[0]:  # All others will need a /n adding to space them out
                    pilot = entry[0]
                    otherOutput = ('%s\n%s\n' % (otherOutput, pilot))
                otherOutput = ('%s%s x %s\n' % (otherOutput, entry[2], entry[1]))

    return iceOutput, oreOutput, salvageOutput, otherOutput, totalsOutput


class MainWindow(wx.Frame):
    def __init__(self, *args, **kwds):
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)

        self.dirname = ''

        self.mainNotebook = wx.Notebook(self, -1, style=0)

        # Job tab widgets
        self.notebookLogPane = wx.Panel(self.mainNotebook, -1)

        # Set up some content holders and labels in the frame.
        self.lblOre = wx.StaticText(self.notebookLogPane, label="Ore:")
        self.oreBox = wx.TextCtrl(self.notebookLogPane, style=wx.TE_MULTILINE, size=(-1, -1))
        self.oreBox.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT,
                                                   wx.FONTSTYLE_NORMAL,
                                                   wx.FONTWEIGHT_NORMAL,
                                                   False))

        self.lblIce = wx.StaticText(self.notebookLogPane, label="Ice:")
        self.iceBox = wx.TextCtrl(self.notebookLogPane, style=wx.TE_MULTILINE, size=(-1, -1))
        self.iceBox.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT,
                                                   wx.FONTSTYLE_NORMAL,
                                                   wx.FONTWEIGHT_NORMAL,
                                                   False))

        self.lblTotals = wx.StaticText(self.notebookLogPane, label="Totals:")
        self.totalsBox = wx.TextCtrl(self.notebookLogPane, style=wx.TE_MULTILINE, size=(-1, -1))
        self.totalsBox.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT,
                                                   wx.FONTSTYLE_NORMAL,
                                                   wx.FONTWEIGHT_NORMAL,
                                                   False))

        self.lblSalvage = wx.StaticText(self.notebookLogPane, label="Salvaged Materials:")
        self.salvageBox = wx.TextCtrl(self.notebookLogPane, style=wx.TE_MULTILINE, size=(-1, -1))
        self.salvageBox.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT,
                                                   wx.FONTSTYLE_NORMAL,
                                                   wx.FONTWEIGHT_NORMAL,
                                                   False))

        self.lblOther = wx.StaticText(self.notebookLogPane, label="Loot:")
        self.otherBox = wx.TextCtrl(self.notebookLogPane, style=wx.TE_MULTILINE, size=(-1, -1))
        self.otherBox.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT,
                                                   wx.FONTSTYLE_NORMAL,
                                                   wx.FONTWEIGHT_NORMAL,
                                                   False))

        # salvageList tab widgets
        self.notebookSalvagePane = wx.Panel(self.mainNotebook, -1)
        self.salvageList = GroupListView(self.notebookSalvagePane, -1, style=wx.LC_REPORT | wx.SUNKEN_BORDER)

        self.ticker = Ticker(self)

        self.statusbar = self.CreateStatusBar()  # A Statusbar in the bottom of the window

        # Setting up the menu.
        filemenu = wx.Menu()
        menuAbout = filemenu.Append(wx.ID_ABOUT, "&About", " Information about this program")
        menuOpen = filemenu.Append(wx.ID_OPEN, "&Open", " Open a log file")
        menuExit = filemenu.Append(wx.ID_EXIT, "E&xit", " Terminate the program")

        # Creating the menubar.
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu, "&File")  # Adding the "filemenu" to the MenuBar
        self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.

        # Menu events.
        self.Bind(wx.EVT_MENU, self.OnOpen, menuOpen)
        self.Bind(wx.EVT_MENU, self.OnExit, menuExit)
        self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)

        self.__set_properties()
        self.__do_layout()

    def __set_properties(self):
        self.SetTitle('Nema')
        self.SetSize((1024, 600))
        self.SetBackgroundColour(wx.NullColour)  # Use system default colour

        self.statusbar.SetStatusText('Welcome to Nema')

        self.ticker.SetDirection('rtl')
        self.ticker.SetFPS(20)
        self.ticker.SetPPF(2)
        self.ticker.SetText('')

        # itemID, itemName, itemBuyValue, itemSellValue, reprocessBuyValue, reprocessSellValue, action
        self.salvageList.SetColumns([
            ColumnDefn('Item', 'left', 300, 'itemName'),
            ColumnDefn('Market Buy Orders', 'right', 165, 'itemBuyValue'),
            ColumnDefn('Market Sell Orders', 'right', 165, 'itemSellValue'),
            ColumnDefn('Materials Buy Orders', 'right', 165, 'reprocessBuyValue'),
            ColumnDefn('Materials Sell Orders', 'right', 165, 'reprocessSellValue'),
            ColumnDefn('Recommendation', 'centre', 100, 'action')
        ])
        self.salvageList.SetSortColumn(self.salvageList.columns[6])

    def __do_layout(self):
        # Use some sizers to see layout options
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        oreSizer = wx.BoxSizer(wx.VERTICAL)
#        iceSizer = wx.BoxSizer(wx.VERTICAL)
        totalSizer = wx.BoxSizer(wx.VERTICAL)
        salvageSizer = wx.BoxSizer(wx.VERTICAL)

        oreSizer.Add(self.lblOre, 0, wx.EXPAND | wx.ALL, 1)
        oreSizer.Add(self.oreBox, 1, wx.EXPAND | wx.ALL, 1)
        oreSizer.Add(self.lblIce, 0, wx.EXPAND | wx.ALL, 1)
        oreSizer.Add(self.iceBox, 1, wx.EXPAND | wx.ALL, 1)

#        iceSizer.Add(self.lblIce, 0, wx.EXPAND | wx.ALL, 1)
#        iceSizer.Add(self.iceBox, 1, wx.EXPAND | wx.ALL, 1)
        totalSizer.Add(self.lblTotals, 0, wx.EXPAND | wx.ALL, 1)
        totalSizer.Add(self.totalsBox, 1, wx.EXPAND | wx.ALL, 1)

        salvageSizer.Add(self.lblSalvage, 0, wx.EXPAND | wx.ALL, 1)
        salvageSizer.Add(self.salvageBox, 1, wx.EXPAND | wx.ALL, 1)
        salvageSizer.Add(self.lblOther, 0, wx.EXPAND | wx.ALL, 1)
        salvageSizer.Add(self.otherBox, 1, wx.EXPAND | wx.ALL, 1)

        sizer.Add(oreSizer, 1, wx.EXPAND | wx.ALL, 1)
#        sizer.Add(iceSizer, 1, wx.EXPAND | wx.ALL, 1)
        sizer.Add(totalSizer, 1, wx.EXPAND | wx.ALL, 1)
        sizer.Add(salvageSizer, 1, wx.EXPAND | wx.ALL, 1)

        mainSizer = wx.BoxSizer(wx.VERTICAL)
        reprocessSizer = wx.BoxSizer(wx.VERTICAL)

        #logSizer.Add(self.jobBtn, 0, wx.ALIGN_RIGHT | wx.ADJUST_MINSIZE, 0)
        reprocessSizer.Add(self.salvageList, 1, wx.EXPAND | wx.ALL, 1)
        #logSizer.Add(self.jobDetailBox, 1, wx.EXPAND, 0)
        self.notebookLogPane.SetSizer(sizer)
        self.notebookSalvagePane.SetSizer(reprocessSizer)

        self.mainNotebook.AddPage(self.notebookLogPane, ("Log"))
        self.mainNotebook.AddPage(self.notebookSalvagePane, ("Loot"))
        mainSizer.Add(self.mainNotebook, 1, wx.EXPAND, 0)
        mainSizer.Add(self.ticker, flag=wx.EXPAND | wx.ALL, border=5)

        self.SetSizer(mainSizer)
        self.Layout()

    def OnOpen(self, e):
        # Open a file
        self.dirname = ''

        dlg = wx.FileDialog(self, "Choose a log file", self.dirname, "", "*.txt", wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.filename = dlg.GetFilename()
            self.logFile = dlg.GetPath()
            f = open(self.logFile, 'r')

            content = f.readlines() + ['\r\n']
            f.close()

            # File sanity check. Test that the first line is what is expected of a Fleet log.
            fileCheck = 'OK'
            testLine = (content[0].rstrip('\r\n')).split('\t')
            for c in testLine[:]:
                if c not in columns:
                    self.statusbar.SetBackgroundColour('RED')
                    self.statusbar.SetStatusText(self.filename + ' is not a valid Fleet Log. Please check the file and try again.')
                    fileCheck = 'FAILED'

            if fileCheck == 'OK':
                fetchData(content)

                iceOutput, oreOutput, salvageOutput, otherOutput, totalsOutput = processLog()

                self.iceBox.SetValue(iceOutput)  # Changes text box content to string iceOutput.
                self.oreBox.SetValue(oreOutput)  # Changes text box content to string oreOutput.
                self.salvageBox.SetValue(salvageOutput)  # Changes text box content to string salvageOutput.
                self.otherBox.SetValue(otherOutput)  # Changes text box content to string otherOutput.
                self.totalsBox.SetValue(totalsOutput)

                if other:
                    systemID = 30002659
                    names = []
                    fetchMinerals()

                    ticker = ("%s:    " % systemNames[systemID])
                    #print("Mineral Prices from %s\n" % systemNames[systemID])

                    for mineral in mineralIDs:
                        ticker = ('%s%s: Buy: %s / Sell: %s    ' % (ticker, mineralIDs[mineral], mineralBuy[mineral], mineralSell[mineral]))
                        #print('%s (%s): Buy: %s / Sell: %s' % (mineralIDs[mineral], int(mineral), mineralBuy[mineral], mineralSell[mineral]))

                    #print(other)
                    for item in other:
                        if item[1] not in names:
                            names.append(item[1])

                    #print(names)

                    typeNames, typePortions = id2name('name', names)

                    #systemID = 30002659
                    idList = []
                    for item in typeNames:
                        idList.append(item)

                    #print(idList)
                    #idList = [4473, 16437]
                    fetchItems(idList)

                    #print("\nPrices Limited to %s:    " % systemNames[systemID])

                    tempSalvageRows = []
                    #print(typeNames)
                    #print(itemBuy)
                    #print(itemSell)

                    for item in typeNames:
                        #output = reprocess(16437)
                        output = reprocess(int(item))
                        #print(typeNames[item])
                        #print('%s (%s): Buy: %s / Sell: %s' % (typeNames[item], int(item), itemBuy[item], itemSell[item]))
                        #print(output)

                        buyTotal = 0  # Fullfilling Buy orders
                        sellTotal = 0  # Placing Sell orders
                        for key in output:
                            if key in mineralIDs:
                                #print('%s x %s = %s' % (mineralIDs[key], output[key], (int(output[key]) * mineralBuy[key])))
                                buyTotal = buyTotal + (int(output[key]) * mineralBuy[key])
                                sellTotal = sellTotal + (int(output[key]) * mineralSell[key])
                        #print('Reprocess total fullfilling Buy orders= %s ISK' % (buyTotal))
                        #print('Reprocess total placing Sell orders= %s ISK\n' % (sellTotal))
                        if (sellTotal > itemSell[item]):
                            action = 'Reprocess'
                        else:
                            action = 'Sell'

                        if typePortions[item] != '1':
                            itemName = '%s (x%s)' % (typeNames[item], typePortions[item])
                            tempSalvageRows.append(Salvage(int(item), itemName, (float(itemBuy[item]) * float(typePortions[item])),
                                                           (float(itemSell[item]) * float(typePortions[item])), buyTotal, sellTotal, action))
                        else:
                            tempSalvageRows.append(Salvage(int(item), typeNames[item], itemBuy[item], itemSell[item], buyTotal, sellTotal, action))

                    if tempSalvageRows != []:
                        salvageRows = tempSalvageRows[:]
                    self.salvageList.SetObjects(salvageRows)

                self.statusbar.SetBackgroundColour(wx.NullColour)  # Resets to system default if changed by file check.
                self.statusbar.SetStatusText(self.filename)
                self.ticker.SetText(ticker)

        dlg.Destroy()

    def OnAbout(self, e):
        description = """A tool designed initially for our corporate industrialists to
enable them analyse their fleet logs out of game.

If you like my work please consider an ISK donation to Elusive One.

All EVE-Online related materials are property of CCP hf."""

        licence = """NEMA is released under GNU GPLv3:

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>."""

        info = wx.AboutDialogInfo()

        #info.SetIcon(wx.Icon('', wx.BITMAP_TYPE_PNG))
        info.SetName('Nova Echo Mining Assistant')
        info.SetVersion('1.0.1')
        info.SetDescription(description)
        #info.SetCopyright('(C) 2013 Tim Cumming')
        info.SetWebSite('https://github.com/EluOne/Nema')
        info.SetLicence(licence)
        info.AddDeveloper('Tim Cumming aka Elusive One')
        #info.AddDocWriter('')
        #info.AddArtist('')
        #info.AddTranslator('')

        wx.AboutBox(info)

    def OnExit(self, e):
        dlg = wx.MessageDialog(self, 'Are you sure to quit Nema?', 'Please Confirm', wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
        if dlg.ShowModal() == wx.ID_YES:
            self.Close(True)


class MyApp(wx.App):
    def OnInit(self):
        frame = MainWindow(None, -1, '')
        self.SetTopWindow(frame)
        frame.Center()
        frame.Show()
        return 1

# end of class MyApp

if __name__ == '__main__':
    app = MyApp(0)
    app.MainLoop()
