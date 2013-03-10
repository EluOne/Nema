#!/usr/bin/python
'Nova Echo Mining Assistant'
# Tim Cumming aka Elusive One
# Created: 05/03/13
# Modified: 10/03/13

import os
import wx
from operator import itemgetter


class MainWindow(wx.Frame):
    def __init__(self, parent, title):
        self.dirname=''
        
        # A "-1" in the size parameter instructs wxWidgets to use the default size.
        # In this case, we select 200px width and the default height.
        wx.Frame.__init__(self, parent, title=title, size=(200,-1))
        
        self.lblOre = wx.StaticText(self, label="Ore:")
        self.oreBox = wx.TextCtrl(self, style=wx.TE_MULTILINE, size=(300,400))
        
        self.lblIce = wx.StaticText(self, label="Ice:")
        self.iceBox = wx.TextCtrl(self, style=wx.TE_MULTILINE, size=(300,400))
        
        self.lblSalvage = wx.StaticText(self, label="Salvage:")
        self.salvageBox = wx.TextCtrl(self, style=wx.TE_MULTILINE, size=(300,400))
        
        self.lblOther = wx.StaticText(self, label="Other:")
        self.otherBox = wx.TextCtrl(self, style=wx.TE_MULTILINE, size=(300,400))
        
        self.CreateStatusBar() # A Statusbar in the bottom of the window

        # Setting up the menu.
        filemenu= wx.Menu()
        menuAbout= filemenu.Append(wx.ID_ABOUT, "&About"," Information about this program")
        menuOpen = filemenu.Append(wx.ID_OPEN, "&Open"," Open a log file")
        menuExit = filemenu.Append(wx.ID_EXIT,"E&xit"," Terminate the program")

        # Creating the menubar.
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu,"&File") # Adding the "filemenu" to the MenuBar
        self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.

        # Menu events.
        self.Bind(wx.EVT_MENU, self.OnOpen, menuOpen)
        self.Bind(wx.EVT_MENU, self.OnExit, menuExit)
        self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)

        # Use some sizers to see layout options
        grid = wx.GridBagSizer(hgap=5, vgap=5)
        
        self.oreSizer = wx.BoxSizer(wx.VERTICAL)
        grid.Add(self.lblOre, pos=(0, 0))
        grid.Add(self.oreBox, pos=(1, 0))
        
        grid.Add(self.lblIce, pos=(0, 1))
        grid.Add(self.iceBox, pos=(1, 1))
        
        grid.Add(self.lblSalvage, pos=(0, 2))
        grid.Add(self.salvageBox, pos=(1, 2))
        
        grid.Add(self.lblOther, pos=(0, 3))
        grid.Add(self.otherBox, pos=(1, 3))
        
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer.Add(grid, 1, wx.EXPAND)
        
        #Layout sizers
        self.SetSizer(self.sizer)
        self.SetAutoLayout(1)
        self.sizer.Fit(self)
        self.Show()

    def OnAbout(self, e):
        # A message dialog box with an OK button. wx.OK is a standard ID in wxWidgets.
        dlg = wx.MessageDialog( self, "Nova Echo Mining Assistant", "About Nema")
        dlg.ShowModal() # Show it
        dlg.Destroy() # finally destroy it when finished.
        
    def OnOpen(self,e):
        # Open a file
        self.dirname = ''
        
        compact = bool(True)
        
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
    
        # EVE ore and ice volumes per unit as a dictionary
        OreTypes = {'Arkonor': 16, 'Bistot': 16, 'Crokite': 16, 'Dark Ochre': 8,
            'Gneiss': 5, 'Hedbergite': 3, 'Hemorphite': 3, 'Jaspet': 2,
            'Kernite': 1.2, 'Mercoxit': 40, 'Omber': 0.6, 'Plagioclase': 0.35,
            'Pyroxeres': 0.3, 'Scordite': 0.15, 'Spodumain': 16, 'Veldspar': 0.1}
        IceTypes = {'Blue Ice': 1000}        

        dlg = wx.FileDialog(self, "Choose a log file", self.dirname, "", "*.txt", wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.filename = dlg.GetFilename()
            self.dirname = dlg.GetDirectory()
#            print self.dirname, self.filename
            f = open(os.path.join(self.dirname, self.filename), 'r')
            
#            logFile = open(log, 'r')
            content = f.readlines() + ['\r\n']
            f.close()
    
            for lineNum in range(len(content)):
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
                oreGroups = sorted(oreGroups, key=itemgetter(0,3))
                for item in range(len(oreGroups)):
                    if item > 0:
                        previous = item -1
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
                oreGroups = sorted(oreGroups, key=itemgetter(0,1))
                for item in range(len(oreGroups)):
                    if item > 0:
                        previous = item -1
                        if (oreGroups[item][0] == oreGroups[previous][0]) and (oreGroups[item][1] == oreGroups[previous][1]):
                            newQuantity = (int(oreGroups[item][2]) + int(oreGroups[previous][2]))
                            newVolume = (OreWeights[oreGroups[item][3]] * int(newQuantity))
                            oreGroups[item] = [oreGroups[item][0], oreGroups[item][1], newQuantity, oreGroups[item][3], newVolume]
                            oreGroups[previous] = 'deleted'
                
                for o in oreGroups[:]:
                    if o == 'deleted':
                        oreGroups.remove(o)
                        
                        
            # Process the list of salvaged items for duplicate entries, and add them together.        
            salvage = sorted(salvage, key=itemgetter(0,1))
            for item in range(len(salvage)):
                if item > 0:
                    previous = item -1
                    if (salvage[item][0] == salvage[previous][0]) and (salvage[item][1] == salvage[previous][1]):
                        newQuantity = (int(salvage[item][2]) + int(salvage[previous][2]))
                        salvage[item] = [salvage[item][0], salvage[item][1], newQuantity, 0]
                        salvage[previous] = 'deleted'
                        
            for s in salvage[:]:
                if s == 'deleted':
                    salvage.remove(s)
        

            # Process the list of other items for duplicate entries, and add them together.
            other = sorted(other, key=itemgetter(0,1))
            for item in range(len(other)):
                if item > 0:
                    previous = item -1
                    if (other[item][0] == other[previous][0]) and (other[item][1] == other[previous][1]):
                        newQuantity = (int(other[item][2]) + int(other[previous][2]))
                        other[item] = [other[item][0], other[item][1], newQuantity, 0]
                        other[previous] = 'deleted'
        
            for e in other[:]:
                if e == 'deleted':
                    other.remove(e)
                    
                        
            if ice or oreGroups or salvage or other:
                if ice: # Build a string to output to the text box named ice.
                    totalIce = 0
                    for entry in iceGroups:
                        totalIce = entry[4] + totalIce
        
                    iceOutput = '' # Init String
                    for name in sorted(icePilots):
                        pilotIce = 0
                        iceOutput = ('%s%s\n' % (iceOutput, name))           
                        for entry in sorted(iceGroups, key=itemgetter(0,3)):
                            if name == entry[0]:
                                if compact is True:
                                    iceOutput = ('%s%s x %s = %s m3\n' % (iceOutput, entry[2], entry[3], entry[4]))
                                else:
                                    iceOutput = ('%s%s x %s = %s m3\n' % (iceOutput, entry[2], entry[1], entry[4]))
                                pilotIce = entry[4] + pilotIce
                        iceTotals.append([name,pilotIce,((pilotIce / totalIce) * 100)])
            
                    iceTotals = sorted(iceTotals, key=itemgetter(2), reverse=True)
                    iceOutput = ('%s\nPercentage of Ore: (%s) m3\n\n' % (iceOutput, totalIce))
                    for entry in range(len(iceTotals)):
                        if iceTotals[(entry)][1] > 0:
                            iceOutput = ('%s%s%% %s: %s m3\n' % (iceOutput, round((iceTotals[(entry)][2]), 2), iceTotals[(entry)][0], iceTotals[(entry)][1]))

                    self.iceBox.SetValue(iceOutput) # Changes text box content to string iceOutput.
        
        
                if oreGroups: # Build a string to output to the text box named ore.
                    totalOre = 0
                    for entry in oreGroups:
                        totalOre = entry[4] + totalOre
        
                    oreOutput = '' # Init String
                    for name in sorted(orePilots):
                        pilotOre = 0
                        oreOutput = ('%s%s\n' % (oreOutput, name))           
                        for entry in sorted(oreGroups, key=itemgetter(0,3)):
                            if name == entry[0]:
                                if compact is True:
                                    oreOutput = ('%s%s x %s = %s m3\n' % (oreOutput, entry[2], entry[3], entry[4]))
                                else:
                                    oreOutput = ('%s%s x %s = %s m3\n' % (oreOutput, entry[2], entry[1], entry[4]))
                                pilotOre = entry[4] + pilotOre
                        oreTotals.append([name,pilotOre,((pilotOre / totalOre) * 100)])
                        oreOutput = oreOutput + '\n'
            
                    oreTotals = sorted(oreTotals, key=itemgetter(2), reverse=True)
                    oreOutput = ('%s\nPercentage of Ore: (%s) m3\n\n' % (oreOutput, totalOre))
                    for entry in range(len(oreTotals)):
                        if oreTotals[(entry)][1] > 0:
                            oreOutput = ('%s%s%% %s: %s m3\n' % (oreOutput, round((oreTotals[(entry)][2]), 2), oreTotals[(entry)][0], oreTotals[(entry)][1]))

                    self.oreBox.SetValue(oreOutput) # Changes text box content to string oreOutput.
        
        
                if salvage: # Build a string to output to the text box named salvage.
                    salvageOutput = '' # Init String
                    pilot = ''
                    for entry in sorted(salvage, key=itemgetter(0)):
                        if pilot == '': # This will be the first entry
                            pilot = entry[0]
                            salvageOutput = ('%s%s\n' % (salvageOutput, pilot))           
                        elif pilot != entry[0]: # All others will need a /n adding to space them out
                            pilot = entry[0]
                            salvageOutput = ('%s\n%s\n' % (salvageOutput, pilot))           
                        salvageOutput = ('%s%s x %s\n' % (salvageOutput, entry[2], entry[1]))
        
                    self.salvageBox.SetValue(salvageOutput) # Changes text box content to string salvageOutput.

        
                if other: # Build a string to output to the text box named other.
                    otherOutput = '' # Init String
                    pilot = ''
                    for entry in sorted(other, key=itemgetter(0)):
                        if pilot == '': # This will be the first entry
                            pilot = entry[0]
                            otherOutput = ('%s%s\n' % (otherOutput, pilot))           
                        elif pilot != entry[0]: # All others will need a /n adding to space them out
                            pilot = entry[0]
                            otherOutput = ('%s\n%s\n' % (otherOutput, pilot))           
                        otherOutput = ('%s%s x %s\n' % (otherOutput, entry[2], entry[1]))

                    self.otherBox.SetValue(otherOutput) # Changes text box content to string otherOutput.   

        dlg.Destroy()

    def OnExit(self, e):
        self.Close(True)  # Close the frame.

app = wx.App(False)
frame = MainWindow(None, "NEMA")
app.MainLoop()
