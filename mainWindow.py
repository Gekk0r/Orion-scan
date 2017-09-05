import os
import wx
from wx.lib.agw.genericmessagedialog import GenericMessageDialog
import ConfigParser
import manage_projector as mngP

import manage_arduino as mng
import cameraPanel as camP
import runPanel as runP
import tablePanel as tabP
import popup
import extraPanel as extraP


class MainWindow(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, "Orion : arduinO Raspberry pI rOtating table image based recostructioN", style = wx.DEFAULT_FRAME_STYLE & ~wx.MAXIMIZE_BOX ^ wx.RESIZE_BORDER, size=(850,600))

        # ConfigParser config file
        self.config_file = "bin/user_preferences.config"

        # ConfigParser object
        self.conf_parser = ConfigParser.SafeConfigParser()
        self.conf_parser.read(self.config_file)

        # Attributes
        self.BrCamera = 9600
        self.BrTable = 115200
        self.parent = self
        self.run_status = "Stop"
        self.degree = 5     # Rotation degree of the table
        self.monitor = 1    # Monitors where will be projected the patterns
        self.arduinoBoards = mng.aruino_management()  # Arduino boards connected
        self.projector = mngP.projector_management()

        # Get background and panel colors from the config file

        if not self.conf_parser.has_section("gui_preferences"):
            self.conf_parser.add_section("gui_preferences")

        self.theme_names = self.conf_parser.get("gui_preferences", "theme_names").split(",") if self.conf_parser.has_option("gui_preferences", "theme_names") else ["No theme names found"]
        self.panel_bg_colors = self.conf_parser.get("gui_preferences", "panel_colors").split(",") if self.conf_parser.has_option("gui_preferences", "panel_colors") else ["#d2d2d2"]
        self.window_bg_colors = self.conf_parser.get("gui_preferences", "background_colors").split(",") if self.conf_parser.has_option("gui_preferences", "background_colors") else ["#eae9e9"]  # Main window background color
        self.current_theme = self.conf_parser.getint("gui_preferences", "current_theme") if self.conf_parser.has_option("gui_preferences", "current_theme") else 0
        self.current_theme = self.current_theme if self.current_theme < min(len(self.window_bg_colors), len(self.panel_bg_colors)) else 0
        self.SetBackgroundColour(self.window_bg_colors[self.current_theme])
        # self.SetBackgroundColour('#eae9e9')  # Main window background color (old = #d3d3d3)
        self.pattern = []  # Patterns that will be projected on the item
        self.backup_folder = "backup"  # Folder where will be done a backup before erasing camera files
        self.folder = "download"  # Folder where the photos will be saved
        self.usb_camera = []
        self.backup_existing_img = self.conf_parser.getboolean("img_save_preferences", "backup_images") if self.conf_parser.has_option("img_save_preferences", "backup_images") else False
        self.erase_camera_files = self.conf_parser.getboolean("img_save_preferences", "delete_images") if self.conf_parser.has_option("img_save_preferences", "delete_images") else False
        self.live_download_photo = False
        self.time_between_shots = 2
        self.number_of_shots = 2
        #self.file_name_template = "[DSC]_dg[DEG]_cam[CAM]_bg[PAT]"
        #self.path_template = "[DIR]/[CAM]"
        self.file_name_template = self.conf_parser.get("img_save_preferences", "img_filename") if self.conf_parser.has_option("img_save_preferences", "img_filename") else ""
        self.path_template = self.conf_parser.get("img_save_preferences", "img_path") if self.conf_parser.has_option("img_save_preferences", "img_path") else ""
        self.file_placeholder = ["[DIR]", "[DSC]", "[DEG]", "[CAM]", "[PAT]"]

        self.windowSizer = wx.BoxSizer(wx.VERTICAL)
        self.topSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.botSizer = wx.BoxSizer(wx.HORIZONTAL)

        self.cameraPan = camP.CameraPanel(self, size=(350, 200), style=wx.SIMPLE_BORDER)  # Will contain camera information/settings
        self.tablePan = tabP.TablePanel(self, size=(350, 200), style=wx.SIMPLE_BORDER)   # Will contain turning table information/settings
        self.additionalPan = extraP.extraPanel(self, size=(350, 210), style=wx.SIMPLE_BORDER)
        self.runPan = runP.runPanel(self, size=(350, 210), style=wx.SIMPLE_BORDER)       # Will contain running setting

        # Setting panels backgrounds
        self.cameraPan.SetBackgroundColour(self.panel_bg_colors[self.current_theme]) #Old #e2ae02
        self.tablePan.SetBackgroundColour(self.panel_bg_colors[self.current_theme])
        self.additionalPan.SetBackgroundColour(self.panel_bg_colors[self.current_theme])
        self.runPan.SetBackgroundColour(self.panel_bg_colors[self.current_theme])

        self.topSizer.Add(self.cameraPan, 1, wx.EXPAND | wx.ALL, 20)
        self.topSizer.Add(self.tablePan, 1, wx.EXPAND | wx.ALL, 20)
        self.botSizer.Add(self.additionalPan, 1, wx.EXPAND | wx.ALL, 20)
        self.botSizer.Add(self.runPan, 1, wx.EXPAND | wx.ALL, 20)

        self.windowSizer.Add(self.topSizer, 1, wx.EXPAND | wx.ALL, 20)
        self.windowSizer.Add(self.botSizer, 1, wx.EXPAND | wx.ALL, 20)
        self.SetSizer(self.windowSizer)
        #wx.Frame(parent, style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER)
        #self.Fit()
        self.Centre()
        self.Show()

        self.init_dropdown_menu()
        self.arduinoBoards.set_parent(main_window=self)
        self.projector.set_parent(self)
        self.readPattern()
        self.initModules()

    def init_dropdown_menu(self):


        # Menubar
        self.menubar = wx.MenuBar()

        # Menus and submenus

        self.file_menu = wx.Menu()
        self.advanced_settings_menu = wx.Menu()
        self.help_menu = wx.Menu()

        # File submenus
        self.theme_menu = wx.Menu()

        # Advanced Settings submenus
        self.camera_menu = wx.Menu()
        self.table_menu = wx.Menu()
        self.projector_menu = wx.Menu()
        self.save_menu = wx.Menu()

        # File submenus and events binding

        self.radio_theme = []
        for i in range(len(self.theme_names)):
            self.radio_theme.append(self.theme_menu.Append(i, self.theme_names[i], "", wx.ITEM_RADIO))
            self.Bind(wx.EVT_MENU, self.radio_theme_onClick, self.radio_theme[i])

        self.theme_menu.Check(self.current_theme, True)  # Checks the current theme radio item, otherwise the first one would be selected by default

        # File menu

        self.file_menu.AppendMenu(wx.ID_ANY, "Theme", self.theme_menu, "")
        #self.file_menu.Append(0, "Save", "", wx.ITEM_NORMAL)
        #self.file_menu.Append(1, "Save as", "", wx.ITEM_NORMAL)
        self.quit = wx.MenuItem(self.file_menu, wx.ID_EXIT, '&Quit\tCtrl+Q')

        # Advanced Settings submenus and events binding

        self.lbl_camera_serial = self.camera_menu.Append(wx.ID_ANY, "Serial: ", "", wx.ITEM_NORMAL)
        self.camera_menu.AppendSeparator()
        self.btn_camera_reset_serial = self.camera_menu.Append(wx.ID_ANY, "Reset Serial", "", wx.ITEM_NORMAL)
        self.btn_camera_set_delay = self.camera_menu.Append(wx.ID_ANY, "Delay", "", wx.ITEM_NORMAL)

        self.Bind(wx.EVT_MENU, self.btn_camera_reset_serial_onClick, self.btn_camera_reset_serial)
        self.Bind(wx.EVT_MENU, self.btn_camera_set_delay_onClick, self.btn_camera_set_delay)

        self.lbl_table_serial = self.table_menu.Append(wx.ID_ANY, "Serial: ", "", wx.ITEM_NORMAL)
        self.table_menu.AppendSeparator()
        self.btn_table_reset_serial = self.table_menu.Append(wx.ID_ANY, "Reset Serial", "", wx.ITEM_NORMAL)
        self.btn_table_set_acceleration = self.table_menu.Append(wx.ID_ANY, "Acceleration", "", wx.ITEM_NORMAL)

        self.Bind(wx.EVT_MENU, self.btn_table_reset_serial_onClick, self.btn_table_reset_serial)
        self.Bind(wx.EVT_MENU, self.btn_table_set_acceleration_onClick, self.btn_table_set_acceleration)

        self.lbl_projector_monitor = self.projector_menu.Append(wx.ID_ANY, "Monitor: ", "", wx.ITEM_NORMAL)
        self.lbl_projector_patterns = self.projector_menu.Append(wx.ID_ANY, "No. of patterns: ", "", wx.ITEM_NORMAL)

        self.btn_save_filename_preferences = self.save_menu.Append(wx.ID_ANY, "Filename preferences", "", wx.ITEM_NORMAL)
        self.save_menu.AppendSeparator()
        self.check_save_backup = self.save_menu.Append(wx.ID_ANY, "Backup photos on camera(s)", "", wx.ITEM_CHECK)
        self.check_save_backup.Check(self.backup_existing_img)
        self.check_save_delete = self.save_menu.Append(wx.ID_ANY, "Delete photos on camera(s)", "", wx.ITEM_CHECK)
        self.check_save_delete.Check(self.erase_camera_files)

        self.Bind(wx.EVT_MENU, self.btn_save_filename_preferences_onClick, self.btn_save_filename_preferences)
        self.Bind(wx.EVT_MENU, self.check_save_backup_onClick, self.check_save_backup)
        self.Bind(wx.EVT_MENU, self.check_save_delete_onClick, self.check_save_delete)

        # Advanced Settings menu

        self.advanced_settings_menu.AppendMenu(wx.ID_ANY, "Camera", self.camera_menu, "")
        self.advanced_settings_menu.AppendMenu(wx.ID_ANY, "Turning Table", self.table_menu, "")
        self.advanced_settings_menu.AppendMenu(wx.ID_ANY, "Projector", self.projector_menu, "")
        self.advanced_settings_menu.AppendMenu(wx.ID_ANY, "Save", self.save_menu, "")
        self.advanced_settings_menu.AppendSeparator()
        self.btn_advanced_redo_serial_config = self.advanced_settings_menu.Append(wx.ID_ANY, "Redo serial configuration", "", wx.ITEM_NORMAL)

        self.Bind(wx.EVT_MENU, self.btn_advanced_redo_serial_config_onClick, self.btn_advanced_redo_serial_config)

        # Append menus to menubar

        self.menubar.Append(self.file_menu, '&File')
        self.menubar.Append(self.advanced_settings_menu, "&Advanced Settings")

        # Debug stuff
        self.Bind(wx.EVT_MENU_OPEN, self.menu_open)

        # Setup
        self.SetMenuBar(self.menubar)
        self.Show(True)

    # Menu events

    def radio_theme_onClick(self, event):
        self.current_theme = event.GetId()

        # This code should be put into a function (along with the code in __init__)
        self.SetBackgroundColour(self.window_bg_colors[self.current_theme])
        self.cameraPan.SetBackgroundColour(self.panel_bg_colors[self.current_theme])
        self.tablePan.SetBackgroundColour(self.panel_bg_colors[self.current_theme])
        self.additionalPan.SetBackgroundColour(self.panel_bg_colors[self.current_theme])
        self.runPan.SetBackgroundColour(self.panel_bg_colors[self.current_theme])

        if not self.conf_parser.has_section("gui_preferences"):
            self.conf_parser.add_section("gui_preferences")

        self.conf_parser.set("gui_preferences", "current_theme", str(self.current_theme))

        self.conf_parser.write(open(self.config_file, 'w'))

    def btn_advanced_redo_serial_config_onClick(self, event):
        self.initModules()

    def btn_camera_reset_serial_onClick(self, event):
        self.arduinoBoards.reset_serial(self.arduinoBoards.serial_camera)

    def btn_camera_set_delay_onClick(self, event):
        camera_delay_input = popup.camera_delay_window(self)
        camera_delay_input.Show()

    def btn_table_reset_serial_onClick(self, event):
        self.arduinoBoards.reset_serial(self.arduinoBoards.serial_table)

    def btn_table_set_acceleration_onClick(self, event):
        table_acceleration_input = popup.table_acceleration_window(self)
        table_acceleration_input.Show()

    def btn_save_filename_preferences_onClick(self, event):
        file_name_input = popup.file_name_preferences(self)
        file_name_input.Show()

    def check_save_backup_onClick(self, event):
        self.backup_existing_img = self.check_save_backup.IsChecked()

        if not self.conf_parser.has_section("img_save_preferences"):
            self.conf_parser.add_section("img_save_preferences")

        self.conf_parser.set("img_save_preferences", "backup_images", str(self.backup_existing_img))
        self.conf_parser.write(open(self.config_file, "w"))

    def check_save_delete_onClick(self, event):
        self.erase_camera_files = self.check_save_delete.IsChecked()

        if not self.conf_parser.has_section("img_save_preferences"):
            self.conf_parser.add_section("img_save_preferences")

        self.conf_parser.set("img_save_preferences", "delete_images", str(self.erase_camera_files))
        self.conf_parser.write(open(self.config_file, "w"))

    def menu_open(self, event):
        if event.GetMenu() == self.advanced_settings_menu:
            #print("Advanced Settings menu opened!")
            self.lbl_camera_serial.SetText("Serial: " + str(self.arduinoBoards.port_camera))
            self.lbl_table_serial.SetText("Serial: " + str(self.arduinoBoards.port_table))

            self.lbl_projector_monitor.SetText("Monitor: " + str(self.monitor))
            self.lbl_projector_patterns.SetText("No. of patterns: " + str(len(self.pattern)))
        else:
            pass

    def initModules(self):
        dialog = GenericMessageDialog(
            self,
            'Choose the modules that you want use in the next windows',
            'Modules initialization',
            wx.OK | wx.ICON_INFORMATION)

        dialog.ShowModal()
        dialog.Destroy()

        self.initTable()
        self.initCameras()

    def initCameras(self):

        dialog = GenericMessageDialog(
            self,
            'Plug in ONLY the camera module and press OK, or CANCEL to skip',
            'Table camera module',
            wx.OK | wx.CANCEL | wx.ICON_QUESTION)

        answer = dialog.ShowModal()
        dialog.Destroy()

        if answer == wx.ID_OK:
            self.arduinoBoards.connect_camera()
            self.cameraPan.nameLabel.SetLabel("Name : " + str(self.arduinoBoards.port_camera))
        else:
            self.cameraPan.nameLabel.SetLabel("Name : No module camera attached")

    def initTable(self):

        dialog = GenericMessageDialog(
            self,
            'Plug in ONLY the table rotation module and press OK, or CANCEL to skip',
            'Table rotation module',
            wx.OK | wx.CANCEL | wx.ICON_QUESTION)

        answer = dialog.ShowModal()
        dialog.Destroy()

        if answer == wx.ID_OK:
            self.arduinoBoards.connect_table()
            self.tablePan.nameLabel.SetLabel("Name : " + str(self.arduinoBoards.port_table))
        else:
            self.tablePan.nameLabel.SetLabel("Name : No module rotation table attached")

    def readPattern(self):
        for image_name in os.listdir("projector_images/"):
            if image_name.endswith(".tif"):
                self.pattern.append((os.path.join("projector_images/", image_name)))

if __name__ == '__main__':
    app = wx.App()
    MainWindow(None)
    app.MainLoop()
