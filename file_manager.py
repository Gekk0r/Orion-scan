import actionsCamera as actC
import os
import subprocess
import ConfigParser
import locale

def get_file_name(main_window, file_number, index_camera):
    out = actC.download_file(main_window.usb_camera[index_camera], file_number)
    #Debug
    if locale.getdefaultlocale()[0] == "it_IT":
        out = out[0].split("\"")
        rtn = out[1].split(".")
    elif locale.getdefaultlocale()[0] == "en_US":
        out = out[0].split(" ")
        rtn = out[-1].split(".")
        rtn[1] = rtn[1][:-1]
    #Debug
    print("rtn:" + str(rtn))
    return rtn


def save_image(main_window, num , deg = 0, cam = 0 , pat = 0 , file_name_template="" , path_template = ""):
    print("Pat")
    print(pat)
    if file_name_template == "":
        file_name_template = main_window.file_name_template
    if path_template == "":
        path_template = main_window.path_template
    print ("Parameters bad ?!?")
    print(num)
    print(cam)
    file_name = get_file_name(main_window, num, cam)
    print("File name")
    print(file_name)
    print(main_window.folder)
    print(main_window.usb_camera)
    tmp_cam = str(cam + 1)
    if len(main_window.usb_camera) <= 2:
        if cam == 0:
            tmp_cam = "left"
        elif cam == 1:
            tmp_cam = "right"
    if pat != 0:
        pat = pat.split('.')[0].split('/')[1]
    else:
        pat = "None"
    placeholder_value = [main_window.folder, file_name[0], deg, tmp_cam, pat]
    for i in range(len(main_window.file_placeholder)):
        file_name_template = file_name_template.replace(str(main_window.file_placeholder[i]), str(placeholder_value[i]))
        path_template = path_template.replace(str(main_window.file_placeholder[i]), str(placeholder_value[i]))
    print (path_template)
    if not os.path.exists(path_template):
        create_path(path_template)
        print("Creating path")

    print(file_name)
    p = subprocess.Popen(["mv", file_name[0] + "." + file_name[1], path_template + "/" + file_name_template + '.' + file_name[-1]], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd="photos")
    print(p.communicate())

    # Debug
    print "path_template: " + str(path_template)
    print "file_name: " + str(file_name)

    return


def create_path (path):
    list_path = path.split("/")
    tmp = "photos"
    for i in range(len(list_path)):
        tmp += "/" + list_path[i]
        subprocess.Popen(["mkdir", tmp], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        #time.sleep(1)
        #print(tmp)
    return


def write_to_file(file = "log.config", text = ""):
    file = open(file, 'w')
    file.write(text)
    return


def read_file_line(line, file = "log.config", text = ""):
    file = open(file, "r")
    return file.readline(line)


def read_all_file(file = "log.config", text = ""):
    file = open(file, "r")
    return file.read()


# Save User Preferences

def load_user_preferences(config_file="bin/user_preferences.config"):

    conf_parser = ConfigParser.SafeConfigParser()
    conf_parser.read(config_file)
    print conf_parser.get("test_section", "test_option")
    conf_parser.set("test_section", "test_option", "25")
    conf_parser.write(open(config_file, "w"))

# DEBUG
#load_user_preferences()
