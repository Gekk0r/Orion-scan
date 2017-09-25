
import time
import panels.extraPanel as extra
import serial.tools.list_ports
from threading import Thread
import detectionCameras as dectCam
import actionsCamera as actCam


class arduinoManagment():
    time_sleep = 0
    table = None
    cameras = None
    tableSerial = None
    camerasSerial = None
    parent = None

    def run_from_serial(self, deviceName, br, i=None):  # bd = BAUDRATE
        print("devicename", deviceName)
        s = serial.Serial(deviceName, br, timeout=0)
        print(s)
        s.close()
        s.open()
        s.flushInput()
        s.write('\r\n\r\n'.encode('ascii'))
        s.flushInput()

        if i == 0:
            print("i = 0")
            print('Now serial ' + deviceName + '@' + str(br) + ' will be used to turn the table')
            try:
                s.write("\r\n\r\n".encode('ascii'))
                s.write("G17 G20 G90 G94 G54 G21\r\n".encode('ascii'))
                s.write("$102=222.22\r\n".encode('ascii'))
                s.write("$1=255\r\n".encode('ascii'))
                s.write("G92 Z0\r\n".encode('ascii'))
                time.sleep(2)
                print("Primo write")
                self.move_turning_table(device=s, stepDegree=self.parent.degree)
                self.tableSerial = s
                return True
            except:
                print "turning table not detected"
                return False
        elif i == 1:
            print('Now serial ' + deviceName + '@' + str(br) + ' will be used to manage cameras')
            self.camerasSerial = s
            return True
        elif i == 2:
            print("take a photo")
            time.sleep(2)
            out = s.write("camera trigger all")
            print("done ", out)
            return True
        elif i == 3:
            self.move_turning_table(device=s, stepDegree=self.parent.degree, test=True, mainwindow=self.parent)
    def move_turning_table(self, device="default", stepDegree=0, delay=3, mainwindow=None, test = False):
        print (device)
        if device == "default":
            device = self.table
            return
        self.time_sleep = ((stepDegree * 6) / 360) + 2
        usb_camera = dectCam.get_string_port_camera()
        if (not test and usb_camera is not None and self.cameras is not None):
            try:
                actCam.save_camera_files(usb_camera, self.parent.backupFolder)  # Doing a backup
                actCam.erase_camera_files(usb_camera)  # Erasing all files
            except:
                pass
        if stepDegree != 0:
            for degree in range(0, 361, stepDegree):
                Thread(target=device.write, args=(str("G0 Z" + str(degree / 10.0) + "\r\n"), )).start()
                #device.write(str("G0 Z" + str(degree / 10.0) + "\r\n").encode("ascii"))
                time.sleep(self.time_sleep) #Let the serial write to exit
                if self.cameras is not None and degree <= 359 and mainwindow.runPan.projectorCb.Value is True and not test:
                    print "projector mode"
                    #threading.Timer(self.time_sleep, self.acq_project, mainwindow).start()
                    self.acq_project(mainwindow)
                elif self.cameras is not None and degree <= 359 and not test:
                    print("cameras")
                    self.run_from_serial(self.cameras, 9600, 2)
                    time.sleep(1.5)
                    '''
                    time.sleep(self.time_sleep)
                    self.camerasSerial.write(str('xxx 1\n').encode('ascii'))
                    time.sleep(delay)
                    '''
                #else:
                #    time.sleep(self.time_sleep)
        else:
            device.write(str("G0 Z0\r\n").encode("ascii"))
        if (not test and usb_camera is not None and self.cameras is not None):
            try:
                actCam.save_camera_files(usb_camera, self.parent.folder)  # Saving photos
            except:
                pass

    def connect_table(self):
        # last device attached
        print("Connetto il tavolo")
        if serial.tools.list_ports.comports() > 0:
            print serial.tools.list_ports.comports()
            for i in range (len(serial.tools.list_ports.comports())):
                if serial.tools.list_ports.comports()[i].description == "Arduino Uno":
                    print("Connected with Arduino Uno Table")
                    self.table = (serial.tools.list_ports.comports()[i]).device
                    break
            '''
            try:
                if self.run_from_serial(self.table, 115200, 0):
                    print("Connected to", self.table)
                    return [self.table, 115200, 0]
                else:
                    return ["turning table not detected", None, None]
            except:
                return ["turning table not detected", None, None]
            '''
    def connect_cameras(self):
        # last device attached
        if serial.tools.list_ports.comports() > 0:
            for i in range(len(serial.tools.list_ports.comports())):
                if (serial.tools.list_ports.comports()[i].description == "Arduino Uno" and self.table != (serial.tools.list_ports.comports()[i]).device):
                    print("Connected with Arduino Uno Camera")
                    self.cameras = (serial.tools.list_ports.comports()[i]).device
                    break
            '''
            try:
                if self.run_from_serial(self.cameras, 9600, 1):
                    return [self.cameras, 9600, 1]
                else:
                    return ["no camera module detected", None, None]
            except:
                return ["no camera module detected", None, None]
            '''
    def acq_project(self, mainWindow):
        #print self.camerasSerial
        print ("Using camera", self.cameras)
        extrapanel = None
        pattern = mainWindow.pattern
        for index in range(len(pattern)):
            if index is 0:
                extrapanel = extra.projector(mainWindow.additionalPan.xcord, pattern[index])
            else:
                #threading.Timer(3.0 + index * 2.5, extrapanel.changeBackground, [pattern[index]]).start()
                extrapanel.changeBackground(pattern[index])
            self.run_from_serial(self.cameras, 9600, 2)
            time.sleep(1)
            #threading.Timer(3.0 + index * 2.5, self.shootWithCamera, []).start()
            #threading.Timer(3.0 + index * 2.5, self.run_from_serial, [self.cameras, 9600, 2]).start()
        extrapanel.Show(False)
        #threading.Timer(3 * len(pattern) + len(pattern)*2, extrapanel.Show,[False]).start()
        # threading.Timer(3 * len(pattern) + len(pattern)*2, extrapanel.Destroy, []).start()

    def shootWithCamera(self):
        self.camerasSerial.write(str('xxx 1\n').encode('ascii'))
        time.sleep(2)

    def setParent(self, parent):
        self.parent = parent
# a = arduinoManagment()
# deviceName = serial.tools.list_ports.comports()[-1].device
# # 9600 2400 4800 19200
# a.run_from_serial(deviceName, 115200, 0, [180])
# print a.time_sleep

# a = arduinoManagment()
# a.connect_cameras()
