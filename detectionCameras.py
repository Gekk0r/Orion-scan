import subprocess
from types import NoneType


def infoCamera(cameras, port):
    p = subprocess.Popen(["gphoto2", "--summary", "--port", port], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out = p.communicate()

    label = ""
    for element in out:
        if type(element) != NoneType:
            features = element.split("\n")
            label = features[2] + features[4]
    cameras.append(label[:15])
    return


def portCamera(port):
    p = subprocess.Popen(["gphoto2", "--auto-detect"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    out = p.communicate()
    if "Error" in out[0]:
        port.append("No camera found")

    else:
        for element in out:
            if type(element) != NoneType:
                features = element.split("\n")
                ndev = len(features) - 3
                for x in range(ndev):
                    port.append("usb" + (features[(x + 2) * -1]).split("usb")[1])
    return

def last_photo(port):
    p = subprocess.Popen(["gphoto2", "--list-files", "--port", port], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out = p.communicate()
    #print(out)
    tmp = out[0].split("#")[-1]
    i = 0
    last = ""
    while (tmp[i]!=" "):
        last+= tmp[i]
        i +=1

    # Debug
    print "last: " + last

    return int(last)

def get_string_port_camera(port):
    portCamera(port)
    device = str(str(port).split(" ")[0])[2:]
    return device

