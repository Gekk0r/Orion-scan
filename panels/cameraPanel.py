import wx
import detectionCameras as detC
import os
import actionsCamera as actC
from threading import Thread

class CameraPanel(wx.Panel):
    def __init__(self, parent, *a, **k):
        wx.Panel.__init__(self, parent, *a, **k)
        self.parent = parent
        self.cameras = []
        self.combos = []
        self.rowBoxs = []
        self.buttons = []
        self.ports = []
        self.panelSizer = wx.BoxSizer(wx.VERTICAL)  # Main panel
        self.topSizer = wx.BoxSizer(wx.HORIZONTAL)  # Number of cameras
        self.subPanel = wx.BoxSizer(wx.VERTICAL)  # Dynamic camera
        self.botSizer = wx.BoxSizer(wx.VERTICAL)  # Test buttons

        # Cameras proprieties
        self.numberCameras = ['1', '2', '3']  # Camera number
        #self.folders = ['apple', 'banana', 'coconut', 'download']
        self.folders = self.parent.conf_parser.get("img_save_preferences", "default_folders").split(",") if self.parent.conf_parser.has_option("img_save_preferences", "default_folders") else ["download"]
        self.cameraLabels = []

        # labels
        self.title = wx.StaticText(self, style=wx.ALIGN_CENTER, label="Camera Settings")
        self.numbersCamera = wx.StaticText(self, wx.ID_ANY, label="Number of cameras")
        self.nameLabel = wx.StaticText(self, wx.ID_ANY, label="Module name : ")

        # Buttons
        self.button = wx.Button(self, wx.ID_ANY, 'Test', pos=(10, 50))
        #self.btn_folder = wx.Button(self, -1, 'Set folder name', pos=(0, 150))

        # ComboBoxes
        self.combo = wx.Choice(self, choices=self.numberCameras)
        self.cmb_set_folder = wx.ComboBox(self, choices=self.folders, pos=(150, 152), size=(180, -1))
        self.combos = []

        #TextBoxes
        #self.textBox = wx.TextCtrl(self, value="insert a name", pos=(150, 152), size=(180, -1))

        # Events
        self.combo.Bind(wx.EVT_CHOICE, self.onChoice)
        self.button.Bind(wx.EVT_BUTTON, self.photo_test)
        self.cmb_set_folder.Bind(wx.EVT_COMBOBOX, self.set_folder)
        self.cmb_set_folder.Bind(wx.EVT_TEXT, self.set_folder)
        #self.btn_folder.Bind(wx.wx.EVT_BUTTON, self.set_folder)

        self.panelSizer.Add(self.title, 0, wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 0)
        self.topSizer.Add(self.numbersCamera, 1, 20)
        self.topSizer.Add(self.combo, 1, 20)
        self.botSizer.Add(self.button, 1, 20)
        self.botSizer.Add(self.nameLabel, 1, 20)
        # self.panelSizer.AddStretchSpacer()
        # self.panelSizer.AddStretchSpacer()
        # self.botSizer.Add(self.btn_folder, 1, 20)
        # self.botSizer.Add(self.textBox, 1, 20)

        self.panelSizer.Add(self.topSizer, 1, 20)
        self.panelSizer.Add(self.subPanel, 1, 20)
        self.panelSizer.Add(self.botSizer, 1, 20)

        self.panelSizer.AddStretchSpacer()
        self.SetSizer(self.panelSizer)
        self.Fit()

        self.cmb_set_folder.SetSelection(len(self.folders)-1)
    def onChoice(self, event):
        self.cameraLabels = []
        self.ports = []
        detC.portCamera(self.ports)
        #print("poorts", self.ports)
        if len(self.ports) == 0:
            self.cameraLabels.append("No camera found")

        for portNumber in self.ports:
            detC.infoCamera(self.cameraLabels, portNumber)

        for elem in self.rowBoxs:
            for widget in range(len(elem.GetChildren())):
                elem.Hide(widget)
                elem.Remove(widget)
            for widget in range(len(elem.GetChildren())):
                elem.Hide(widget)
                elem.Remove(widget)
        self.panelSizer.Layout()

        self.cameras = []
        self.combos = []
        self.rowBoxs = []
        self.buttons = []

        for x in range(self.combo.GetSelection() + 1):
            self.rowBoxs.append(wx.BoxSizer(wx.HORIZONTAL))
            self.cameras.append(wx.StaticText(self, style=wx.ALIGN_LEFT, label="Camera " + str(x + 1)))
            self.combos.append(wx.Choice(self, choices=self.cameraLabels))
            self.buttons.append(wx.Button(self, -1, "Test camera"))
            self.rowBoxs[x].Add(self.cameras[x], 1, 20)
            self.rowBoxs[x].Add(self.combos[x], 1, 20)
            self.rowBoxs[x].Add(self.buttons[x], 1, 20)
            self.subPanel.Add(self.rowBoxs[x], 1, 20)
            self.Bind(wx.EVT_CHOICE, lambda event: self.on_camera_choice(event, x), self.combos[x])
            self.Bind(wx.EVT_BUTTON, lambda event: self.on_button_camera_test(event, x), self.buttons[x])
        self.numbersCamera.Show()
        self.panelSizer.Layout()

    def photo_test(self, event):  # Shoot a test photo
        camera = self.parent.arduinoBoards.port_camera
        #print("Camera", camera)
        self.parent.arduinoBoards.trigger_camera(0)
        return

    def set_folder(self, event):     # Set the mainWindow folder attribute to one the chosen by user
        tmpfolder = self.cmb_set_folder.Value
        if tmpfolder != "" and not(os.path.isdir("photos/" + tmpfolder)):
            self.parent.folder = tmpfolder
            print("Set folder destination")
        else:
            print("Folder aldready exist!")
        return

    def on_camera_choice(self, event, index):
        self.parent.usb_camera.append(self.ports[self.combos[index].GetSelection()].replace(" ", ""))
        print (self.parent.usb_camera[index])
        return

    def on_button_camera_test(self, event, index):
        Thread(target=actC.shoot, args=(str(self.parent.usb_camera[index]),)).start()
        return
