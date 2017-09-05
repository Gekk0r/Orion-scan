import serial
import time
import serial.tools.list_ports

def run_from_serial(deviceName, br, i=None):  # bd = BAUDRATE
    s = serial.Serial(deviceName, br, timeout=0)
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
            s.write(str("G0 Z10\r\n").encode("ascii"))
            return True
        except:
            print "nessuna turning table"
            return False
    elif i == 1:
        print('Now serial ' + deviceName + '@' + str(br) + ' will be used to manage cameras')
        self.camerasSerial = s
        return True
    elif i == 2:
        time.sleep(2)
        s.write(str('xxx 1\n').encode('ascii'))
        return True
table = (serial.tools.list_ports.comports()[-1]).device
run_from_serial(table, 9600, 2)