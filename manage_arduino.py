import serial.tools.list_ports
from  threading import Thread


class arduino_management:
    time_sleep = 2
    port_table = None
    port_camera = None
    serial_camera = None
    serial_table = None
    parent = None
    baud_table = 115200
    baud_camera = 9600

    def set_parent(self, main_window):
        self.parent = main_window
        return

    def init_serial(self, port, baud, timeout=0):
        s = None
        print("Connecting to " + str(port))
        try:
            s = serial.Serial(port=port, baudrate=baud, timeout=timeout)
            s.close()
            s.open()
            s.flushInput()
        except:
            print("Connection lost")
            pass
            return s
        return s

    def connect_table(self):
        # last device attached
        if serial.tools.list_ports.comports() > 0:
            print serial.tools.list_ports.comports()
            for i in range(len(serial.tools.list_ports.comports())):
                if serial.tools.list_ports.comports()[i].description == "Arduino Uno":
                    print("Connected with Arduino Uno Table")
                    self.port_table = (serial.tools.list_ports.comports()[i]).device
                    break

        self.serial_table = self.init_serial(port=self.port_table, baud=self.baud_table)

        print("Table Serial connected" if self.serial_table is not None else "Table Serial not connected")

        return self.serial_table is None

    def connect_camera(self):
        # last device attached
        if serial.tools.list_ports.comports() > 0:
            for i in range(len(serial.tools.list_ports.comports())):
                if (serial.tools.list_ports.comports()[i].description == "Arduino Uno" and self.port_table != (
                        serial.tools.list_ports.comports()[i]).device):
                    print("Connected with Arduino Uno Camera")
                    self.port_camera = (serial.tools.list_ports.comports()[i]).device
                    break

        self.serial_camera = self.init_serial(port=self.port_camera, baud=self.baud_camera)

        print("Camera Serial connected" if self.serial_camera is not None else "Camera Serial not connected")

        return self.serial_camera is None

    def rotate_table(self, degree= None):
        if degree is None:
            degree = self.parent.degree
        Thread(target=self.serial_table.write, args=(str("G0 Z" + str(int(degree) / 10.0) + "\r\n"),)).start()
        return

    def trigger_camera(self, cam):
        if cam == 0:
            cam = "all"
        print str(cam)
        Thread(target=self.serial_camera.write, args=(str("camera trigger " + str(cam)) + "\r\n",)).start()
        return

    def reset_serial(self, serial=""):
        if serial == "":
            serial = self.serial_table
        try:
            serial.close()
            serial.open()
            serial.flushInput()
            serial.flushOutput()
        except:
            return False
        return True

    def send_command(self, port, command):

        try:
            if port == self.port_camera:
                print("sending cmd '{0}' to the camera module".format(command))
                self.serial_camera.write(command)
            elif port == self.port_table:
                print("sending cmd '{0}' to the turntable".format(command))
                self.serial_table.write(command)
        except:
            return False
        return True
