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

import wx
from operator import itemgetter


class MainWindow(wx.Frame):
    def __init__(self, parent, title):
        self.dirname = ''

        wx.Frame.__init__(self, parent, title=title, size=(1024, 600))

        panel = wx.Panel(self, -1)
        panel.SetBackgroundColour(wx.NullColour)  # Use system default colour

        # Set up some content holders and labels in the frame.
        self.lblOre = wx.StaticText(panel, label="Ore:")
        self.oreBox = wx.TextCtrl(panel, style=wx.TE_MULTILINE, size=(-1, -1))
        self.oreBox.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT,
                                                   wx.FONTSTYLE_NORMAL,
                                                   wx.FONTWEIGHT_NORMAL,
                                                   False))

        self.lblIce = wx.StaticText(panel, label="Ice:")
        self.iceBox = wx.TextCtrl(panel, style=wx.TE_MULTILINE, size=(-1, -1))
        self.iceBox.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT,
                                                   wx.FONTSTYLE_NORMAL,
                                                   wx.FONTWEIGHT_NORMAL,
                                                   False))

        self.lblSalvage = wx.StaticText(panel, label="Salvaged Materials:")
        self.salvageBox = wx.TextCtrl(panel, style=wx.TE_MULTILINE, size=(-1, -1))
        self.salvageBox.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT,
                                                   wx.FONTSTYLE_NORMAL,
                                                   wx.FONTWEIGHT_NORMAL,
                                                   False))

        self.lblOther = wx.StaticText(panel, label="Other:")
        self.otherBox = wx.TextCtrl(panel, style=wx.TE_MULTILINE, size=(-1, -1))
        self.otherBox.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT,
                                                   wx.FONTSTYLE_NORMAL,
                                                   wx.FONTWEIGHT_NORMAL,
                                                   False))

        self.statusbar = self.CreateStatusBar()  # A Statusbar in the bottom of the window
        self.statusbar.SetStatusText('Welcome to Nema')

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

        # Use some sizers to see layout options
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        oreSizer = wx.BoxSizer(wx.VERTICAL)
        iceSizer = wx.BoxSizer(wx.VERTICAL)
        salvageSizer = wx.BoxSizer(wx.VERTICAL)
        otherSizer = wx.BoxSizer(wx.VERTICAL)
        panel.SetSizer(sizer)

        oreSizer.Add(self.lblOre, 0, wx.EXPAND | wx.ALL, 1)
        oreSizer.Add(self.oreBox, 1, wx.EXPAND | wx.ALL, 1)

        iceSizer.Add(self.lblIce, 0, wx.EXPAND | wx.ALL, 1)
        iceSizer.Add(self.iceBox, 1, wx.EXPAND | wx.ALL, 1)

        salvageSizer.Add(self.lblSalvage, 0, wx.EXPAND | wx.ALL, 1)
        salvageSizer.Add(self.salvageBox, 1, wx.EXPAND | wx.ALL, 1)

        otherSizer.Add(self.lblOther, 0, wx.EXPAND | wx.ALL, 1)
        otherSizer.Add(self.otherBox, 1, wx.EXPAND | wx.ALL, 1)

        sizer.Add(oreSizer, 1, wx.EXPAND | wx.ALL, 1)
        sizer.Add(iceSizer, 1, wx.EXPAND | wx.ALL, 1)
        sizer.Add(salvageSizer, 1, wx.EXPAND | wx.ALL, 1)
        sizer.Add(otherSizer, 1, wx.EXPAND | wx.ALL, 1)

        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(panel, 1, wx.EXPAND)
        self.SetSizer(mainSizer)
        mainSizer.Layout()

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

    def OnOpen(self, e):
        # Open a file
        self.dirname = ''

        compact = bool(False)

        #Initialise lists
        oreGroups = []
        ice = []
        salvage = []
        other = []

        pilots = []
        icePilots = []
        orePilots = []

        oreTotals = []
        iceTotals = []

        # These are the expected column headers from the first row of the data file
        columns = {'Time', 'Character', 'Item Type', 'Quantity', 'Item Group'}

        # EVE ore and ice volumes per unit as a dictionary
        OreTypes = {'Arkonor': 16, 'Bistot': 16, 'Crokite': 16, 'Dark Ochre': 8,
            'Gneiss': 5, 'Hedbergite': 3, 'Hemorphite': 3, 'Jaspet': 2,
            'Kernite': 1.2, 'Mercoxit': 40, 'Omber': 0.6, 'Plagioclase': 0.35,
            'Pyroxeres': 0.3, 'Scordite': 0.15, 'Spodumain': 16, 'Veldspar': 0.1}
        IceTypes = {'Blue Ice': 1000, 'White Glaze': 1000, 'Glacial Mass': 1000, 'Clear Icicle': 1000}

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
                numLines = range(len(content))

                for lineNum in numLines:
                    # Process each line that was in the log file.
                    line = content[lineNum].rstrip('\r\n')

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
                                oreGroups.append([data[1], data[2], data[3], data[4], volume])
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

                if compact is True:
                    # Compact Mode:
                    # Process the list of ore mined for duplicate type entries, and add them together. This produces a list that only details the ore group.
                    oreGroups = sorted(oreGroups, key=itemgetter(0, 3))
                    numItems = range(len(oreGroups))

                    for item in numItems:
                        if item > 0:
                            previous = item - 1
                            if (oreGroups[item][0] == oreGroups[previous][0]) and (oreGroups[item][3] == oreGroups[previous][3]):
                                newQuantity = (int(oreGroups[item][2]) + int(oreGroups[previous][2]))
                                newVolume = (OreTypes[oreGroups[item][3]] * int(newQuantity))
                                oreGroups[item] = [oreGroups[item][0], oreGroups[item][3], newQuantity, oreGroups[item][3], newVolume]
                                oreGroups[previous] = 'deleted'

                    for o in oreGroups[:]:
                        if o == 'deleted':
                            oreGroups.remove(o)
                else:
                    # Process the list of ore mined for duplicate entries, and add them together.
                    oreGroups = sorted(oreGroups, key=itemgetter(0, 1))
                    numItems = range(len(oreGroups))

                    for item in numItems:
                        if item > 0:
                            previous = item - 1
                            if (oreGroups[item][0] == oreGroups[previous][0]) and (oreGroups[item][1] == oreGroups[previous][1]):
                                newQuantity = (int(oreGroups[item][2]) + int(oreGroups[previous][2]))
                                newVolume = (OreTypes[oreGroups[item][3]] * int(newQuantity))
                                oreGroups[item] = [oreGroups[item][0], oreGroups[item][1], newQuantity, oreGroups[item][3], newVolume]
                                oreGroups[previous] = 'deleted'

                    for o in oreGroups[:]:
                        if o == 'deleted':
                            oreGroups.remove(o)

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

                if ice or oreGroups or salvage or other:
                    if ice:  # Build a string to output to the text box named ice.
                        totalIce = 0
                        for entry in ice:
                            totalIce = entry[4] + totalIce

                        iceOutput = ''  # Init String
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

                        iceTotals = sorted(iceTotals, key=itemgetter(2), reverse=True)
                        iceOutput = ('%s\nPercentage of Ore: (%s) m3\n\n' % (iceOutput, totalIce))

                        iceRange = range(len(iceTotals))  # Remove calc from loop below.
                        for entry in iceRange:
                            if iceTotals[(entry)][1] > 0:
                                iceOutput = ('%s%.2f%% %s: %s m3\n' % (iceOutput, (iceTotals[(entry)][2]), iceTotals[(entry)][0], iceTotals[(entry)][1]))

                        self.iceBox.SetValue(iceOutput)  # Changes text box content to string iceOutput.

                    if oreGroups:  # Build a string to output to the text box named ore.
                        totalOre = 0
                        for entry in oreGroups:
                            totalOre = entry[4] + totalOre

                        oreOutput = ''  # Init String
                        for name in sorted(orePilots):
                            pilotOre = 0
                            oreOutput = ('%s%s\n' % (oreOutput, name))
                            for entry in sorted(oreGroups, key=itemgetter(0, 3)):
                                if name == entry[0]:
                                    if compact is True:
                                        oreOutput = ('%s%s x %s = %.2f m3\n' % (oreOutput, entry[2], entry[3], entry[4]))
                                    else:
                                        oreOutput = ('%s%s x %s = %.2f m3\n' % (oreOutput, entry[2], entry[1], entry[4]))
                                    pilotOre = entry[4] + pilotOre
                            oreTotals.append([name, pilotOre, ((float(pilotOre) / float(totalOre)) * 100)])
                            oreOutput = oreOutput + '\n'

                        oreTotals = sorted(oreTotals, key=itemgetter(2), reverse=True)
                        oreOutput = ('%s\nPercentage of Ore: (%.2f) m3\n\n' % (oreOutput, totalOre))

                        oreRange = range(len(oreTotals))  # Remove calc from loop below.
                        for entry in oreRange:
                            if oreTotals[(entry)][1] > 0:
                                oreOutput = ('%s%.2f%% %s: %.2f m3\n' % (oreOutput, (oreTotals[(entry)][2]), oreTotals[(entry)][0], oreTotals[(entry)][1]))

                        self.oreBox.SetValue(oreOutput)  # Changes text box content to string oreOutput.

                    if salvage:  # Build a string to output to the text box named salvage.
                        salvageOutput = ''  # Init String
                        pilot = ''
                        for entry in sorted(salvage, key=itemgetter(0)):
                            if pilot == '':  # This will be the first entry
                                pilot = entry[0]
                                salvageOutput = ('%s%s\n' % (salvageOutput, pilot))
                            elif pilot != entry[0]:  # All others will need a /n adding to space them out
                                pilot = entry[0]
                                salvageOutput = ('%s\n%s\n' % (salvageOutput, pilot))
                            salvageOutput = ('%s%s x %s\n' % (salvageOutput, entry[2], entry[1]))

                        self.salvageBox.SetValue(salvageOutput)  # Changes text box content to string salvageOutput.

                    if other:  # Build a string to output to the text box named other.
                        otherOutput = ''  # Init String
                        pilot = ''
                        for entry in sorted(other, key=itemgetter(0)):
                            if pilot == '':  # This will be the first entry
                                pilot = entry[0]
                                otherOutput = ('%s%s\n' % (otherOutput, pilot))
                            elif pilot != entry[0]:  # All others will need a /n adding to space them out
                                pilot = entry[0]
                                otherOutput = ('%s\n%s\n' % (otherOutput, pilot))
                            otherOutput = ('%s%s x %s\n' % (otherOutput, entry[2], entry[1]))

                        self.otherBox.SetValue(otherOutput)  # Changes text box content to string otherOutput.

                self.statusbar.SetBackgroundColour(wx.NullColour)  # Resets to system default if changed by file check.
                self.statusbar.SetStatusText(self.filename)

        dlg.Destroy()

    def OnExit(self, e):
        dlg = wx.MessageDialog(self, 'Are you sure to quit Nema?', 'Please Confirm', wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
        if dlg.ShowModal() == wx.ID_YES:
            self.Close(True)


if __name__ == '__main__':
    app = wx.App(0)
    frame = MainWindow(None, "Nema")
    app.SetTopWindow(frame)
    frame.Show()
    app.MainLoop()
