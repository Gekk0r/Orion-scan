from threading import Thread
import time
import wx
import actionsCamera as actC
import subprocess
import file_manager as fm
import detectionCameras as detC
import popup

def run_manager(main_window):
    print ("Run manager")
    check_rotation = main_window.runPan.rotationCb.Value
    time_delay = main_window.time_between_shots
    check_projector = main_window.runPan.projectorCb.Value
    degree_rotation = main_window.degree
    num_patterns = len(main_window.pattern)
    live_download = main_window.live_download_photo
    number_of_shots = main_window.number_of_shots if not check_rotation else 360 / degree_rotation
    last_file = []
    if main_window.erase_camera_files:
        last_file.append(0)
    if not check_rotation:
        degree_rotation = 360 / int(number_of_shots)
    remaining_shots = 360 // degree_rotation
    wx.CallAfter(change_shoot_panel, main_window, num_patterns, check_projector, remaining_shots)
    main_window.runPan.set_range_progress_bar(remaining_shots+2)
    subprocess.Popen(["rm", main_window.backup_folder+"/", "-r"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd="photos")
    for i in range(len(main_window.usb_camera)):
        wx.CallAfter(write_shoot_panel, main_window, "Erasing files from the camera(s)...")
        if main_window.backup_existing_img:
            actC.save_camera_files(main_window.usb_camera[i], main_window.backup_folder, "/cam" + str(i+1) + "/")
        if main_window.erase_camera_files:
            actC.erase_camera_files(main_window.usb_camera[i])
        else:
            last_file.append(detC.last_photo(main_window.usb_camera[i]))
        if main_window.run_status == "Stop":
            wx.CallAfter(write_shoot_panel, main_window, "Stopping program...")
            time.sleep(2)
            main_window.runPan.btn_run.SetLabelText("Run acquisition")
            wx.CallAfter(write_shoot_panel, main_window, "Program Stopped")
            return
    if live_download:
        subprocess.Popen(["rm", main_window.folder + "/", "-r"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd="photos")
    main_window.runPan.increase_progress_bar()
    wx.CallAfter(change_shoot_panel, main_window, num_patterns, check_projector, remaining_shots)
    print("Erased")
    if check_projector:
        wx.CallAfter(main_window.projector.project_pattern)
    pos = 0
    for i in range(0, 360, degree_rotation):
        while main_window.run_status == "Pause":
            wx.CallAfter(write_shoot_panel, main_window, "Program Paused")
            time.sleep(1)
            print(main_window.run_status)
            if main_window.run_status == "Stop":
                break
        if main_window.run_status == "Stop":
            wx.CallAfter(write_shoot_panel, main_window, "Stopping program...")
            break
        wx.CallAfter(change_shoot_panel, main_window, num_patterns, check_projector, remaining_shots)
        if check_rotation:
            main_window.arduinoBoards.rotate_table(i)
            time.sleep(degree_rotation * 5.5 / 360 + 2)
            pos = i
        if check_projector:
            for j in range(num_patterns):
                wx.CallAfter(main_window.projector.change_pattern, j)
                time.sleep(1 + (0.008 * i))
                main_window.arduinoBoards.trigger_camera(0)
                print ("Scattato")
                time.sleep(2 if check_rotation else int(time_delay))
                if live_download:
                    for k in range(len(main_window.usb_camera)):
                        last_file[k] += 1
                        #tmp += main_window.folder+"_" + (str(i) if check_rotation else str(i/degree_rotation))
                        #tmp += "_bg" + str(j)
                        #print(tmp)
                        #actC.download_file(main_window.usb_camera[k], last_file, name=tmp)

                        # Debug
                        print "last_file: " + str(last_file)
                        print "pos: " + str(pos)
                        print "k: " + str(k)

                        try:
                            fm.save_image(main_window, last_file[k], pos, k, main_window.pattern[j])
                        except:
                            main_window.run_status = "Stop"
                            wx.CallAfter(write_shoot_panel, main_window, "An error has occurred!!!")
                            time.sleep(2)
        else:
            main_window.arduinoBoards.trigger_camera(0)
            time.sleep(2 if check_rotation else int(time_delay))
            if live_download:
                for j in range(len(main_window.usb_camera)):
                    last_file[j] += 1
                    fm.save_image(main_window, last_file[j], pos, j)
                #     tmp = main_window.folder + "/cam" + str(j+1) + "/"
                #     if j == 0:
                #         tmp = main_window.folder + "/left/"
                #     elif j == 1:
                #         tmp = main_window.folder + "/right/"
                #     tmp += main_window.folder+"_" + str(i) + "_bg1"
                    #actC.download_file(main_window.usb_camera[j], tmp, last_file)
        main_window.runPan.increase_progress_bar()
        remaining_shots -= 1
    if check_projector:
        wx.CallAfter(main_window.projector.project_pattern, False)
    if check_rotation:
        main_window.arduinoBoards.rotate_table(0)
        #main_window.arduinoBoards.reset_serial(# )
    if not live_download:
        wx.CallAfter(write_shoot_panel, main_window, "Downloading photos...")
        pos = 0
        subprocess.Popen(["rm", main_window.folder + "/", "-r"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd="photos")
        for i in range(1, int((number_of_shots +1)  if not check_projector else number_of_shots * num_patterns), (1 if not check_projector else num_patterns)):
            print(i)
            print("ma what?")
            print(int(number_of_shots - remaining_shots if not check_projector else (number_of_shots  - remaining_shots)* num_patterns))
            if check_rotation:
                pos = i // num_patterns * degree_rotation
            for j in range(len(main_window.usb_camera)):
                if check_projector:
                    for k in range(num_patterns):
                        try:
                            fm.save_image(main_window, i+k + last_file[j], pos, j, pat=main_window.pattern[k])
                        except:
                            pass
                else:
                    try:
                        fm.save_image(main_window, i + last_file[j], pos, j)
                    except:
                        pass
    main_window.runPan.increase_progress_bar()
    wx.CallAfter(write_shoot_panel, main_window, "Done")
    time.sleep(1.5)
    wx.CallAfter(write_shoot_panel, main_window, "Program Stopped")
    main_window.runPan.btn_run.SetLabelText("Run acquisition")
    main_window.run_status = "Stop"
    for i in range(360/degree_rotation+2, -1, -1):
        main_window.runPan.decrease_progress_bar()
        time.sleep(0.2)
    wx.CallAfter(popup.start_shoot_at_dialog, main_window)
    return


def thread_run_manager(main_window):
    print("Start thread run manager")
    if check_devices(main_window):
        Thread(target=run_manager, args=(main_window,)).start()
    else:
        main_window.runPan.btn_run.SetLabelText("Run acquisition")
        main_window.runPan.parent.run_status = "Stop"
    print("Done")
    return


def change_shoot_panel(main_window, num_patterns, check_projector, index):
    main_window.runPan.txt_status.SetLabel("Remaining shots:  " + str(index) + (("   ( x " + str(num_patterns) + "  panels)") if check_projector else ""))
    return


def write_shoot_panel(main_window, text):
    main_window.runPan.txt_status.SetLabel(text)
    return


def shoot_at(main_window, degree, pattern=-1, camera=0):
    degree = int(degree)
    main_window.arduinoBoards.rotate_table(degree)
    time.sleep(degree * 5.5 / 360 + 2)
    if pattern != -1:
        print "Projected " + str(pattern)
        #Thread(target = wx.CallAfter, args=(main_window.projector.project_pattern,)).start()
        wx.CallAfter(main_window.projector.project_pattern)
        wx.CallAfter(main_window.projector.change_pattern, pattern)
        time.sleep(1.5)
    main_window.arduinoBoards.trigger_camera(camera)
    time.sleep(1)
    main_window.arduinoBoards.rotate_table(0)
    if pattern != -1:
        wx.CallAfter(main_window.projector.project_pattern, False)

    print(len(main_window.usb_camera))
    for i in range(len(main_window.usb_camera)):
        last_photo = detC.last_photo(main_window.usb_camera[i])
        fm.save_image(main_window, last_photo, degree, i, (main_window.pattern[pattern] if pattern != -1 else 0))
    return


def check_devices(main_window):
    if popup.check_devices_dialog(main_window):
        for i in range(len(main_window.usb_camera)):
            main_window.arduinoBoards.trigger_camera(i+1)
            time.sleep(1.5)
        main_window.arduinoBoards.rotate_table(20)
        time.sleep(1)
        main_window.arduinoBoards.rotate_table(0)
        if not popup.check_devices_response_dialog(main_window):
            main_window.arduinoBoards.reset_serial(main_window.arduinoBoards.serial_table)
            main_window.arduinoBoards.reset_serial(main_window.arduinoBoards.serial_camera)
            return False
    return True
