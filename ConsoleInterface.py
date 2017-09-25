import serial.tools.list_ports
import time

def run_from_serial(deviceName, br, i=None,deg=1):  # bd = BAUDRATE
    s = serial.Serial(deviceName, br, timeout=0)
    #s.close()
    #s.open()
    s.flushInput()
    s.write('\r\n\r\n'.encode('ascii'))
    s.flushInput()
    if i == 0:
        #print("i = 0")
        print('Now serial ' + deviceName + '@' + str(br) + ' will be used to turn the table')
        try:
            s.write("\r\n\r\n".encode('ascii'))
            s.write("G17 G20 G90 G94 G54 G21\r\n".encode('ascii'))
            s.write("$102=222.22\r\n".encode('ascii'))
            s.write("$1=255\r\n".encode('ascii'))
            s.write("G92 Z0\r\n".encode('ascii'))
            time.sleep(2)
            txt = "Z" + str(deg/10)
            s.write(str("G0" + txt + "\r\n").encode("ascii"))
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
        s.write(str('camera trigger 2\n').encode('ascii'))
        return True

baudRateCamera = 9600
baudRateTable = 115200
'''
a = ""
a = input("Connect the camera, press enter when done")
print("asd")
#time.sleep(5)
tmp = input("Connect the table, press enter when done")
'''
table = (serial.tools.list_ports.comports()[-1]).device
camera = (serial.tools.list_ports.comports()[-2]).device
while True:
    scelta = input("Choose: \n1 to shoot a single photo,\n2 to rotate the table of x degrees,\n3 to shoot a photo every x degrees\n4 to exit\n")
    print(scelta)
    if (scelta == 1):
        print("Taking a photo")
        run_from_serial(camera, baudRateCamera, 2)
    elif (scelta == 2):
        n = input("How many degrees?\n")

        direction = input("Chose 1 to rotate clockwise, 2 to counterclockwise\n")
        if (direction == 1):
            n = -n
        print ("Rotating")
        run_from_serial(table, baudRateTable, 0, deg=n)
    elif (scelta == 3):
        n = input("How many degrees between photos\n")
        for i in range(0, 360, n):
            run_from_serial(camera, baudRateCamera, 2)
            run_from_serial(table, baudRateTable, 0, deg=n)
            time.sleep(1.5)
        print("done")
    elif(scelta == 4):
        exit()