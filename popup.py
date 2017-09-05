import wx
import wx.lib.intctrl
import time
import task_manager as tsk
#import subprocess
from threading import Thread
from wx.lib.agw.genericmessagedialog import GenericMessageDialog


class camera_delay_window(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, "Camera Delay", style=wx.DEFAULT_FRAME_STYLE & ~wx.MAXIMIZE_BOX ^ wx.RESIZE_BORDER, size=(200, 65 + (len(parent.usb_camera)+1)*35))
        self.parent = parent
        self.window_sizer = wx.BoxSizer(wx.HORIZONTAL)
        #panel = wx.Panel(self, -1)

        self.lbl_camera_delay = wx.StaticText(self, wx.ID_ANY, label="Camera delay (milliseconds)", pos=(10, 5))

        self.txt_camera_delay = []
        self.btn_camera_delay_dec = []
        self.btn_camera_delay_inc = []

        for i in range(len(self.parent.usb_camera)):
            #self.txt_camera_delay[i] = wx.TextCtrl(self, pos=(15, i*35), id=i)
            #self.btn_camera_delay_dec[i] = wx.Button(self, i, "-", pos=(120, i*35), size=(20, 20))
            #self.btn_camera_delay_inc[i] = wx.Button(self, i, "+", pos=(145, i*35), size=(20, 20))

            #self.txt_camera_delay.append(wx.TextCtrl(self, 2*i, pos=(15, 45 + i*35)))
            wx.StaticText(self, wx.ID_ANY, label="camera {0}".format(i+1), pos=(10, 38 + i*35))
            self.txt_camera_delay.append(wx.lib.intctrl.IntCtrl(self, id=wx.ID_ANY, pos=(90, 35 + i*35), limited=True, min=0, max=8192))
            self.btn_camera_delay_dec.append(wx.Button(self, 2*i, "-", pos=(120, 35 + i*35), size=(20, 20)))
            self.btn_camera_delay_inc.append(wx.Button(self, 2*i + 1, "+", pos=(145, 35 + i*35), size=(20, 20)))

            self.window_sizer.Add(self.txt_camera_delay[i], 1, wx.EXPAND | wx.ALL, 25)

            self.Bind(wx.EVT_BUTTON, self.btn_camera_delay_inc_dec_onClick, self.btn_camera_delay_dec[i])
            self.Bind(wx.EVT_BUTTON, self.btn_camera_delay_inc_dec_onClick, self.btn_camera_delay_inc[i])

        self.btn_camera_delay_apply = wx.Button(self, wx.ID_ANY, "Apply delay", pos=(15, 35 + len(self.txt_camera_delay)*35), size=(85, 30))
        self.Bind(wx.EVT_BUTTON, self.btn_camera_delay_apply_onClick, self.btn_camera_delay_apply)
        self.Bind(wx.EVT_CLOSE, self.on_closing)
        #self.btn_camera_delay_dec.SetLabel("-")
        #self.btn_camera_delay_inc.SetLabel("+")

        #self.window_sizer.Add(self.txt_camera_delay, 1, wx.EXPAND | wx.ALL, 25)

        wx.Frame(parent, style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER)

        #self.Fit()
        self.MakeModal()
        self.Centre()
        self.Show()

    # Menu events

    def btn_camera_delay_inc_dec_onClick(self, event):

        btn_id = event.GetId() // 2
        delay = self.txt_camera_delay[btn_id].GetValue()
        print delay

        if event.GetId() % 2 == 0:
            # Dec delay
            delay -= 1
        else:
            # Inc delay
            delay += 1

        self.txt_camera_delay[btn_id].SetValue(delay)

    def btn_camera_delay_apply_onClick(self, event):

        self.parent.arduinoBoards.serial_camera.flushOutput()

        print("setting delay for {0} camera(s)".format(len(self.parent.usb_camera)))

        for i in range(len(self.parent.usb_camera)):
            print "set camera " + str(i+1) + " delay " + str(self.txt_camera_delay[i].GetValue())  # DEBUG!
            self.parent.arduinoBoards.send_command(self.parent.arduinoBoards.port_camera, "set camera " + str(i+1) + " delay " + str(self.txt_camera_delay[i].GetValue()))  # +1 FOR DEBUG!
            time.sleep(0.1)

    def on_closing(self, event):
        self.MakeModal(False)
        self.Destroy()


class table_acceleration_window(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, "Camera Delay", style=wx.DEFAULT_FRAME_STYLE & ~wx.MAXIMIZE_BOX ^ wx.RESIZE_BORDER, size=(240, 115))
        self.parent = parent
        self.window_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.lbl_table_acceleration = wx.StaticText(self, id=wx.ID_ANY, label="Turntable acceleration (mm/s^2)", pos=(10, 5))

        self.txt_table_acceleration = wx.lib.intctrl.IntCtrl(self, id=wx.ID_ANY, pos=(10, 35), limited=True, value=1, min=0, max=128)
        self.txt_table_acceleration.Value = self.parent.conf_parser.get("turntable_preferences", "acceleration") if self.parent.conf_parser.has_option("turntable_preferences", "acceleration") else "0"
        self.btn_table_acceleration_dec = wx.Button(self, id=0, label="-", pos=(120, 35), size=(20, 20))
        self.btn_table_acceleration_inc = wx.Button(self, id=1, label="+", pos=(145, 35), size=(20, 20))

        self.Bind(wx.EVT_BUTTON, self.btn_table_acceleration_inc_dec_onClick, self.btn_table_acceleration_dec)
        self.Bind(wx.EVT_BUTTON, self.btn_table_acceleration_inc_dec_onClick, self.btn_table_acceleration_inc)

        self.btn_table_acceleration_apply = wx.Button(self, id=wx.ID_ANY, label="Apply acceleration", pos=(10, 70), size=(140, 30))
        self.Bind(wx.EVT_BUTTON, self.btn_table_acceleration_apply_onClick, self.btn_table_acceleration_apply)
        self.Bind(wx.EVT_CLOSE, self.on_closing)

        wx.Frame(parent, style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER)

        self.MakeModal()
        self.Centre()
        self.Show()

    # Menu Events

    def btn_table_acceleration_inc_dec_onClick(self, event):

        acceleration = self.txt_table_acceleration.GetValue()

        if event.GetId() % 2 == 0:
            # Dec acceleration
            acceleration -= 1
        else:
            # Inc acceleration
            acceleration += 1

        self.txt_table_acceleration.SetValue(acceleration)

    def btn_table_acceleration_apply_onClick(self, event):

        self.parent.arduinoBoards.serial_table.flushOutput()

        print("$122={0}".format(self.txt_table_acceleration.GetValue()))

        self.parent.arduinoBoards.send_command(self.parent.arduinoBoards.port_table, "$122={0}\r\n".format(self.txt_table_acceleration.GetValue()))

        if not self.parent.conf_parser.has_section("turntable_preferences"):
            self.parent.add_section("turntable_preferences")

        self.parent.conf_parser.set("turntable_preferences", "acceleration", str(self.txt_table_acceleration.GetValue()))
        self.parent.conf_parser.write(open(self.parent.config_file, "w"))

    def on_closing(self, event):
        self.MakeModal(False)
        self.Destroy()


class shoot_at_window(wx.Frame):
    degree_list = ["5", "10", "15", "20", "25", "30", "45", "60", "90", "120", "180"]
    camera_list = []
    pattern_list = []

    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, "Shoot  at", style=wx.DEFAULT_FRAME_STYLE & ~wx.MAXIMIZE_BOX ^ wx.RESIZE_BORDER, size=(530, 80))
        self.parent = parent
        self.window_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.pattern_list = self.parent.pattern
        self.camera_list = []
        self.camera_list.append("All")
        for i in range(len(self.parent.usb_camera)):
            self.camera_list.append(str(i+1))
        self.lbl_degree = wx.StaticText(self, style=wx.ALIGN_CENTER, label="Degree", pos=(10, 10))
        self.lbl_camera = wx.StaticText(self, style=wx.ALIGN_CENTER, label="Camera", pos=(100, 10))
        self.lbl_pattern = wx.StaticText(self, style=wx.ALIGN_CENTER, label="Pattern", pos=(200, 10))
        self.cmb_camera = wx.Choice(self, choices=self.camera_list, pos=(100, 30))
        self.cmb_degree = wx.Choice(self, choices=self.degree_list, pos=(10, 30))
        self.cmb_pattern = wx.Choice(self, choices=self.pattern_list, pos=(200, 30))
        self.btn_shoot = wx.Button(self, label="Shoot",  size=(100, 32), pos=(420, 30))

        self.btn_shoot.Bind(wx.EVT_BUTTON, self.shoot)
        self.Bind(wx.EVT_CLOSE, self.on_closing)

        self.cmb_camera.SetSelection(0)
        self.cmb_degree.SetSelection(0)
        self.cmb_pattern.SetSelection(0)
        self.MakeModal()
        self.Centre()
        self.Show()

    def shoot(self, event):
        degree = self.degree_list[self.cmb_degree.GetSelection()]
        pattern = self.cmb_pattern.GetSelection()
        camera = self.camera_list[self.cmb_camera.GetSelection()]
        if camera == "All":
            camera = 0
        print("Camera")
        print(camera)
        Thread(target=tsk.shoot_at, args=(self.parent, degree, pattern, camera,)).start()

    def on_closing(self, event):
        self.MakeModal(False)
        self.Destroy()
# if __name__ == '__main__':
#     app = wx.App()
#     frame = camera_delay_window(parent=None)
#     frame.Show()
#     camera_delay_window(None)
#     app.MainLoop()


def start_shoot_at_dialog(main_window):

    dialog = GenericMessageDialog(
        main_window,
        'Do you want shoot extra photos?',
        'Extra',
        wx.YES | wx.NO | wx.ICON_QUESTION)

    answer = dialog.ShowModal()
    dialog.Destroy()

    if answer == wx.ID_YES:
        shoot_at_window(main_window)


class file_name_preferences(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, "File name preferences", style=wx.DEFAULT_FRAME_STYLE & ~wx.MAXIMIZE_BOX ^ wx.RESIZE_BORDER, size=(530, 300))
        self.parent = parent
        self.window_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.txt_filename = wx.TextCtrl(self, 0, size=(210, 20), pos=(20, 200))
        self.txt_path = wx.TextCtrl(self, 0, size=(210, 20), pos=(300, 200))
        self.btn_save = wx.Button(self, label="Save", pos=(20, 250), size=(490, 30))
        self.lbl_filname = wx.StaticText(self, label="Filename", pos=(22, 175))
        self.lbl_path = wx.StaticText(self, label="Path", pos=(302, 175))
        self.lbl_dir = wx.StaticText(self, label="[DIR] ---> Root directory", pos=(20, 25))
        self.lbl_dsc = wx.StaticText(self, label="[DSC] ---> Camera's filename", pos=(300, 25))
        self.lbl_deg = wx.StaticText(self, label="[DEG] ---> Degree position", pos=(20, 75))
        self.lbl_cam = wx.StaticText(self, label="[CAM] ---> Current camera", pos=(300, 75))
        self.lbl_pat = wx.StaticText(self, label="[PAT] ---> Current pattern", pos=(20, 125))

        self.txt_filename.Value = parent.file_name_template
        self.txt_path.Value = parent.path_template

        self.btn_save.Bind(wx.EVT_BUTTON, self.save_preferences)
        self.Bind(wx.EVT_CLOSE, self.on_closing)

        self.MakeModal()
        self.Centre()
        self.Show()

    def save_preferences(self, event):
        self.parent.file_name_template = self.txt_filename.Value
        self.parent.path_template = self.txt_path.Value

        # Save preferences on config file
        if not self.parent.conf_parser.has_section("img_save_preferences"):
            self.parent.conf_parser.add_section("img_save_preferences")

        self.parent.conf_parser.set("img_save_preferences", "img_filename", str(self.txt_filename.Value))
        self.parent.conf_parser.set("img_save_preferences", "img_path", str(self.txt_path.Value))
        self.parent.conf_parser.write(open(self.parent.config_file, "w"))

        print(self.parent.file_name_template)
        print(self.parent.path_template)

    def on_closing(self, event):
        self.MakeModal(False)
        self.Destroy()
# if __name__ == '__main__':
#     app = wx.App()
#     frame = file_name_preferences(parent=None)
#     frame.Show()
#     app.MainLoop()
#
# def send_notify(title,text,image=None):
#     if image is None:
#         #image = os.path.dirname(os.path.abspath(__file__)) + "/bin/logo.png"
#         image = "~/logo.png"
#     print image
#     subprocess.call(["notify-send","-i" , image, title, text ],cwd="bin")


def check_devices_dialog(main_window):

    dialog = GenericMessageDialog(
        main_window,
        'Do you want test the devices?',
        'Test',
        wx.YES | wx.NO | wx.ICON_QUESTION)

    answer = dialog.ShowModal()
    dialog.Destroy()

    return answer == wx.ID_YES


def check_devices_response_dialog(main_window):

    dialog = GenericMessageDialog(
        main_window,
        'Does all device worked?',
        'Test',
        wx.YES | wx.NO | wx.ICON_QUESTION)

    answer = dialog.ShowModal()
    dialog.Destroy()

    return answer == wx.ID_YES
