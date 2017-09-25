import subprocess
from types import NoneType
import os.path
#import detectionCameras


def shoot(port):
    p = subprocess.Popen(["gphoto2", "--capture-image", "--port", port], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    out = p.communicate()
    if "Error" in out[0]:
        print("No camera found")
        #print(out)


def downloadLastImage(port):
    p = subprocess.Popen(["gphoto2", "--list-files", "--port", port], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out = p.communicate()

    if "Error" in out[0]:
        print("No camera found")
        return

    else:
        photoNumber = ""
        for element in out:
            if type(element) != NoneType:
                features = element.split("\n")
                photoName = features[-2].split("    ")[1]
                photoNumber = features[-2].split("    ")[0].split("#")[1]
    print photoNumber, photoName
    if os.path.isfile(photoName):
        print "already downloaded"
    else:
        p = subprocess.Popen(["gphoto2", "--get-file", photoNumber, "--port", port], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        out = p.communicate()
        print out


def shootAndDownload(port):
    p = subprocess.Popen(["gphoto2", "--capture-image-and-download", "--port", port], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,cwd="photos")
    out = p.communicate()
    print out


def erase_camera_files(port):
    p = subprocess.Popen(["gphoto2", "--delete-all-files", "--recurse", "--port", port], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out = p.communicate()
    #print out


def save_camera_files(port, name, folder, degree_rotation=1, patterns=1, file_number=1, project_pattern=False):
    out = ""
    index = 0
    step = 0
    while not ("Error".upper() in str(out).upper()) and not ("Failed".upper() in str(out).upper()):
        path = name + "/" + folder
        file = name+"_"+str(step*degree_rotation)+"_bg"+str(index+1) + ".jpg"
        p = subprocess.Popen(["gphoto2", "--get-file", str(file_number), "--filename", path + file, "--port", port], stdout=subprocess.PIPE,stderr=subprocess.STDOUT, cwd="photos")
        out = p.communicate()
        file_number += 1
        index += 1
        if index % patterns == 0 or not project_pattern:
            step += 1
            index = 0

def download_file(port, file_number, name = ""):
    print "gphoto port: " + port
    if name != "":
        file = name + ".jpg"
        p = subprocess.Popen(["gphoto2", "--get-file", str(file_number), "--filename", file, "--port", port], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd="photos")
    else:
        p = subprocess.Popen(["gphoto2", "--get-file", str(file_number), "--port", port, "--force-overwrite"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd="photos")
    out = p.communicate()
    return out

# DEBUG
'''
port = []
device = detectionCameras.get_string_port_camera(port)
print("Banana")
a = download_file(device, 1)
print(a)
'''