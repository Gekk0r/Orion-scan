import wx, time
import threading

class extraPanel(wx.Panel):
    def __init__(self, parent, *a, **k):
        wx.Panel.__init__(self, parent, *a, **k)

        self.parent = parent
        self.panelSizer = wx.BoxSizer(wx.VERTICAL)
        self.topSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.title = wx.StaticText(self, style=wx.ALIGN_CENTER, label="Extra Settings")
        self.monitorLabel = wx.StaticText(self, label="Monitor : ")
        self.monitor = 1
        self.time_between_shots_list = ('1','2','3','4','5','10','20')
        self.number_of_shots_list = ('1','2','3','4','5','10','20')
        self.monitorList = []
        self.show_patterns = False
        if wx.Display.GetCount() > 1:
            for monitor in range(wx.Display.GetCount()):
                self.monitorList.append(str(monitor + 1))
        else:
            self.monitorList.append("1")

        self.btn_test = wx.Button(self, label="Test projector")
        self.combo = wx.Choice(self, choices=self.monitorList)
        #self.cmb_delay_camera = wx.Choice(self, choices=["No camera found"])
        self.txt_shots_delay = wx.StaticText(self, label="Shots delay:", pos=(116, 138))
        self.txt_number_of_shots = wx.StaticText(self, label="Shots:", pos=(31, 138))
        self.cmb_shots_delay = wx.Choice(self, choices=self.time_between_shots_list, pos=(115, 158))
        self.cmb_number_of_shots = wx.Choice(self, choices=self.number_of_shots_list, pos=(30, 158))
        self.cmb_patterns = wx.Choice(self, choices=self.parent.pattern, pos=(170, 50), size=(150,30))
        self.btn_set_camera_option = wx.Button(self, label="Save Options", pos=(210, 160))
        self.btn_static_pattern = wx.Button(self, label="Project pattern", pos=(170, 18), size=(120, 30))

        # Events
        self.combo.Bind(wx.EVT_CHOICE, self.onChoice)
        self.cmb_patterns.Bind(wx.EVT_CHOICE, self.change_static_pattern)
	self.combo.Bind(wx.EVT_MOTION, self.refresh_monitor_list)
        self.btn_test.Bind(wx.EVT_BUTTON, self.tryPopup)
        self.btn_set_camera_option.Bind(wx.EVT_BUTTON, self.set_camera_setting)
        self.btn_static_pattern.Bind(wx.EVT_BUTTON, self.project_static_pattern)

        self.panelSizer.Add(self.title, 0, wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 0)
        self.topSizer.Add(self.monitorLabel, 1, 20)
        self.topSizer.Add(self.combo, 1, 20)
        self.panelSizer.Add(self.topSizer, 1, 20)
        self.panelSizer.Add(self.btn_test, 1, 20)
        self.panelSizer.AddStretchSpacer()
        #self.panelSizer.Add(self.cmb_delay_camera,1,20)
        self.panelSizer.AddStretchSpacer()
        self.SetSizer(self.panelSizer)
        self.Fit()
        self.cmb_number_of_shots.SetSelection(1)
        self.cmb_shots_delay.SetSelection(1)
        self.combo.SetSelection(0)

        self.btn_set_camera_option.Hide()
        self.cmb_shots_delay.Hide()
        self.cmb_number_of_shots.Hide()
        self.txt_number_of_shots.Hide()
        self.txt_shots_delay.Hide()
        self.cmb_patterns.Hide()

    def tryPopup(self, event): #Prints a popup test for few seconds
        projector = self.parent.projector
        projector.project_pattern()
        print("Projected")
        threading.Timer(1.5, projector.project_pattern, [False]).start()

    def onChoice(self, event):
        self.monitor = int(self.combo.GetString(self.combo.GetSelection()))
        self.parent.monitor = self.monitor
        self.parent.projector.screen = wx.Display(int(self.monitor) - 1).GetGeometry()[0]
        return

    def set_camera_setting(self, event):
        print("Set camera settings")
        self.parent.time_between_shots = self.time_between_shots_list[self.cmb_shots_delay.GetSelection()]
        self.parent.number_of_shots = self.number_of_shots_list[self.cmb_number_of_shots.GetSelection()]
        return

    def project_static_pattern(self, event):
        if not self.show_patterns:
            self.cmb_patterns.Clear()
            self.cmb_patterns.AppendItems(self.parent.pattern)
            self.cmb_patterns.SetSelection(0)
            self.cmb_patterns.Show()
            self.parent.projector.project_pattern()
            self.show_patterns = True
            self.btn_static_pattern.SetLabelText("Close pattern")
        else:
            self.cmb_patterns.Hide()
            self.parent.projector.project_pattern(False)
            self.show_patterns = False
            self.btn_static_pattern.SetLabelText("Project pattern")
        return
    def change_static_pattern (self, event):
        self.parent.projector.change_pattern(self.cmb_patterns.GetSelection())
        return
	
    def set_monitor_list(self):
        self.monitorList = []
        if wx.Display.GetCount() > 1:
            for monitor in range(wx.Display.GetCount()):
                self.monitorList.append(str(monitor + 1))
        else:
            self.monitorList.append("1")
        return

    def refresh_monitor_list(self, event=""):
        print("refresh")
        tmp = self.combo.GetSelection()
        self.combo.Clear()
        self.set_monitor_list()
        self.combo.SetItems(self.monitorList)
        self.combo.SetSelection(tmp)

