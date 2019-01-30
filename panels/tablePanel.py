import wx
import manage_arduino
import threading
import time


class TablePanel(wx.Panel):
    def __init__(self, parent,*a, **k):
        wx.Panel.__init__(self, parent, *a, **k)

        self.parent = parent
        self.panelSizer = wx.BoxSizer(wx.VERTICAL)  # Main panel
        self.topSizer = wx.BoxSizer(wx.HORIZONTAL)  # Number of cameras

        self.title = wx.StaticText(self, style=wx.ALIGN_CENTER, label="Turntable Settings")
        self.degreeLabel = wx.StaticText(self, label="Degree")
        self.nameLabel = wx.StaticText(self, label="Module name : ")
        self.shootLabel = wx.StaticText(self, label="Number of shoots : 72")

        self.degreeList = ["5", "10", "15", "20", "25", "30", "45", "60", "90", "120", "180"]
        #ComboBox
        self.combo = wx.Choice(self, choices=self.degreeList)

        #Buttons
        self.btnTest = wx.Button(self, -1, 'Test Table', pos=(0, 150))
        # Events
        self.combo.Bind(wx.EVT_CHOICE, self.onChoice)
        self.btnTest.Bind(wx.EVT_BUTTON, self.test_table)
        self.panelSizer.Add(self.title, 0, wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 0)
        self.topSizer.Add(self.degreeLabel, 1, 20)
        self.topSizer.Add(self.combo, 1, 20)
        self.panelSizer.Add(self.topSizer, 1, 20)
        self.panelSizer.Add(self.nameLabel, 1, 20)
        self.panelSizer.Add(self.shootLabel, 1, 20)

        self.panelSizer.AddStretchSpacer()
        self.SetSizer(self.panelSizer)
        self.Fit()
        self.combo.SetSelection(0)

    def onChoice(self, event):
        self.shootLabel.SetLabel("Number of shoots : " + str(360 / int(self.combo.GetString(self.combo.GetSelection()))))
        self.parent.degree = int(self.combo.GetString(self.combo.GetSelection()))
        self.panelSizer.Layout()

    def test_table(self, event):
        degree_rotation = self.parent.degree
        print ("device " + self.parent.arduinoBoards.port_table)
        threading.Thread(target=self.parent.arduinoBoards.rotate_table).start()
        threading.Timer(degree_rotation * 5.5 / 360 + 2, self.parent.arduinoBoards.rotate_table, [0]).start()
        #manageArduino.arduinoManagment.run_from_serial(self.parent.arduinoBoards, self.parent.arduinoBoards.table, self.parent.BrTable, 3)