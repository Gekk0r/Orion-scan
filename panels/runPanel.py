import time
import wx
import task_manager as tsk
# import manage_arduino as mng
# import detectionCameras as detectCam
# import actionsCamera
from threading import Thread
import popup
class runPanel(wx.Panel):
    def __init__(self, parent , *a, **k):
        wx.Panel.__init__(self, parent, *a, **k)

        self.parent = parent

        # layout init
        self.panelSizer = wx.BoxSizer(wx.VERTICAL)
        self.topSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.botSizer = wx.BoxSizer(wx.HORIZONTAL)

        # label
        self.title = wx.StaticText(self, style=wx.ALIGN_CENTER, label="Execute Settings")
        #self.rotationLabel = wx.StaticText(self, label="Rotation Table ", pos=(20, 22))
        #self.projectorLabel = wx.StaticText(self, label="Projector ", pos=(20,62))
        #self.txt_live_download = wx.StaticText(self, label="Live download", pos=(20, 42))
        self.txt_status = wx.StaticText(self, label="Program Stopped", pos=(4, 155))

        # widget
        self.btn_run = wx.Button(self, label="Run acquisition", pos=(4, 105), size=(120, 45))
        self.btn_stop = wx.Button(self, label="Stop", pos=(127, 105), size=(100, 45))
        self.btn_single_shot = wx.Button(self, label="Single Shot", pos=(230, 105), size=(100,45))
        self.rotationCb = wx.CheckBox(self, -1, 'Rotation Table', pos=(4, 25))
        self.rotationCb.SetValue(True)
        self.projectorCb = wx.CheckBox(self, -1, 'Projector', pos=(4, 75))
        self.projectorCb.SetValue(False)
        self.live_download_cb = wx.CheckBox(self, -1, 'Live download', pos=(4, 50))
        self.live_download_cb.SetValue(False)
        self.progress_bar = wx.Gauge(self, -1, 100, pos=(4, 175), size=(320, 10), style=wx.GA_SMOOTH & wx.GA_HORIZONTAL)

        # Events
        self.btn_run.Bind(wx.EVT_BUTTON, self.acquisition)
        self.btn_stop.Bind(wx.EVT_BUTTON, self.stop_program)
        self.btn_single_shot.Bind(wx.EVT_BUTTON, self.single_shot)
        self.live_download_cb.Bind(wx.EVT_CHECKBOX, self.change_download_state)
        self.rotationCb.Bind(wx.EVT_CHECKBOX, self.change_download_state)
        self.rotationCb.Bind(wx.EVT_CHECKBOX, self.show_camera_config)
        # self.btn2.Bind(wx.EVT_BUTTON, self.acquisition2)

        # layout organization
        #self.panelSizer.Add(self.title, 0, wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 0)
        #self.topSizer.Add(self.rotationLabel, 1, 20)
        #self.topSizer.Add(self.rotationCb, 1, 20)
        #self.botSizer.Add(self.projectorLabel, 1, 20)
        #self.botSizer.Add(self.projectorCb, 1, 20)
        #self.panelSizer.Add(self.topSizer, 1, 20)
        #self.panelSizer.Add(self.botSizer, 1, 20)
        #self.panelSizer.Add(self.btn_run, 1, 20)

        #self.panelSizer.AddStretchSpacer()
        self.SetSizer(self.panelSizer)
        self.Fit()

    def increase_progress_bar(self):
        if (self.progress_bar.GetValue() != self.progress_bar.GetRange()):
            self.progress_bar.SetValue(self.progress_bar.GetValue()+1)
        return

    def decrease_progress_bar(self):
        if (self.progress_bar.GetValue() > 0):
            self.progress_bar.SetValue(self.progress_bar.GetValue() - 1)
        return

    def set_range_progress_bar(self, max):
        self.progress_bar.SetRange(max)
        self.progress_bar.SetValue(0)
        return

    def reset_progress_bar(self):
        self.progress_bar.SetValue(0)
        return

    def acquisition(self, event):
        if self.parent.run_status == "Stop":
            self.btn_run.SetLabelText("Pause")
            self.parent.run_status = "Start"
            tsk.thread_run_manager(self.parent)
        elif self.parent.run_status == "Start":
            self.parent.run_status = "Pause"
            self.btn_run.SetLabelText("Continue")
        elif self.parent.run_status == "Pause":
            self.parent.run_status = "Start"
            self.btn_run.SetLabelText("Pause")
        return

    def stop_program(self, event):
        print("Stopping program")
        self.parent.run_status = "Stop"
        return

    def change_download_state(self, event):
        self.parent.live_download_photo = self.live_download_cb.Value
        return

    def show_camera_config(self, event):
        extraPan = self.parent.additionalPan
        if not self.rotationCb.Value:
            extraPan.cmb_shots_delay.Show()
            extraPan.cmb_number_of_shots.Show()
            extraPan.btn_set_camera_option.Show()
            extraPan.txt_number_of_shots.Show()
            extraPan.txt_shots_delay.Show()
        else:
            extraPan.cmb_shots_delay.Hide()
            extraPan.cmb_number_of_shots.Hide()
            extraPan.btn_set_camera_option.Hide()
            extraPan.txt_number_of_shots.Hide()
            extraPan.txt_shots_delay.Hide()

    def single_shot (self, event):
        popup.shoot_at_window(self.parent)
        #popup.file_name_preferences(self.parent)