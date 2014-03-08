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
import pickle

import config


class PreferencesDialog(wx.Dialog):
    def __init__(self, *args, **kwds):
        # begin wxGlade: MyDialog.__init__
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE
        wx.Dialog.__init__(self, *args, **kwds)
        self.label_2 = wx.StaticText(self, wx.ID_ANY, ("Market System"))

        self.systemChoices = []
        numItems = range(len(config.systemList))
        for i in numItems:
            self.systemChoices.append(str(config.systemList[i][1]))

        self.systemChoice = wx.Choice(self, wx.ID_ANY, choices=self.systemChoices)
        self.compact_cb = wx.CheckBox(self, wx.ID_ANY, ("Ore Compact Mode"))
        self.label_1 = wx.StaticText(self, wx.ID_ANY, ("Ore entries will be condensed down,\nonly showing their type not variant."))
        self.cancelBtn = wx.Button(self, wx.ID_CANCEL)
        self.okBtn = wx.Button(self, wx.ID_OK)

        self.__set_properties()
        self.__do_layout()
        # end wxGlade

        self.okBtn.Bind(wx.EVT_BUTTON, self.onSave)

    def __set_properties(self):
        # begin wxGlade: PreferencesDialog.__set_properties
        self.SetTitle(("Preferences"))
        self.SetSize((500, 200))

        selectedSystem = 0

        numItems = range(len(config.systemList))
        for x in numItems:
            if config.systemList[x][0] == config.settings['system']:
                selectedSystem = x
        self.systemChoice.SetSelection(selectedSystem)

        self.compact_cb.SetValue(config.settings['compact'])
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: PreferencesDialog.__do_layout
        grid_sizer_1 = wx.GridSizer(3, 2, 0, 0)
        grid_sizer_1.Add(self.label_2, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL | wx.ADJUST_MINSIZE, 0)
        grid_sizer_1.Add(self.systemChoice, 0, wx.ALIGN_CENTER_VERTICAL | wx.ADJUST_MINSIZE, 0)
        grid_sizer_1.Add(self.compact_cb, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL | wx.ADJUST_MINSIZE, 0)
        grid_sizer_1.Add(self.label_1, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL | wx.ADJUST_MINSIZE, 0)
        grid_sizer_1.Add(self.cancelBtn, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.ADJUST_MINSIZE, 0)
        grid_sizer_1.Add(self.okBtn, 0, wx.ALIGN_CENTER_VERTICAL | wx.ADJUST_MINSIZE, 0)
        self.SetSizer(grid_sizer_1)
        self.Layout()
        # end wxGlade

    def onSave(self, event):
        # Market Selection
        marketSelection = self.systemChoice.GetCurrentSelection()
        marketID = config.systemList[marketSelection][0]
        marketName = config.systemList[marketSelection][1]

        config.settings['system'] = marketID
        config.settings['systemName'] = marketName

        # Checkbox Setting
        config.settings['compact'] = self.compact_cb.GetValue()

        if config.settings != {}:
            iniFile = open('nema.ini', 'w')
            pickle.dump(config.settings, iniFile)
            iniFile.close()
        self.EndModal(0)

# end of class preferencesDialog
