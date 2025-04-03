import os
import re
import json
import subprocess

from cv2 import imread, cvtColor, COLOR_BGR2GRAY, line, imshow, waitKey, \
    circle, resize, VideoCapture, CAP_V4L2, CAP_PROP_FRAME_WIDTH, \
    CAP_PROP_FRAME_HEIGHT, CAP_PROP_FPS, CAP_PROP_FOURCC, VideoWriter

from globals import linked_keys
from tools import print2log

DEBUG = False

def get_USB_cameras() -> dict:
    f_cameras = "dict_cameras.txt"
    try:
        list_device_result = subprocess.run(["v4l2-ctl", "--list-devices"],
                                            stdout=subprocess.PIPE)
    except:
        print2log("error from running: v4l2-ctl --list-devices")
        exit(56736)

    camera_info = list_device_result.stdout.decode()

    cameras = {}
    read_next_line = False
    name_and_port = ""
    for line in camera_info.split("\n"):
        print(line)
        if read_next_line:
            cameras[line.strip()] = name_and_port
            read_next_line = ""
            read_next_line = False

        if line.find("usb-") >= 0:
            read_next_line = True
            name_and_port = line.strip()

    print(cameras)
    return cameras


def get_cam_fmt_options(cam_addr: str, cam_model: str) -> dict:
    cam_port = cam_addr.strip().split("/")[-1]
    f_cam_fmt = cam_model[:12] + "_" + cam_port + "_fmt.txt"

    keep_old_file = False
    try:
        cmd = ["v4l2-ctl", "-d " + cam_addr, "--list-formats-ext"]
        # print(cmd)
        # list_cam_fmt = subprocess.run(cmd, stdout=subprocess.PIPE)
        # print(list_cam_fmt)

        list_cam_fmt = []
        cmd1 = " ".join(cmd)
        process = subprocess.Popen(cmd1,
                                   shell=True,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   # bufsize=0,
                                   # text=True,
                                   )
        for line in process.stdout:
            list_cam_fmt.append(line.decode())
        for line in process.stderr:
            list_cam_fmt.append(line.decode())
        errcode = process.returncode
        if DEBUG:
            print(list_cam_fmt)
            print(f"the error code is {errcode}")
    except:
        keep_old_file = True

    if not keep_old_file:
        if os.path.isfile(f_cam_fmt):
            os.remove(f_cam_fmt)
            assert not os.path.isfile(f_cam_fmt), f"{f_cam_fmt} was not " \
                                                      "removed."
    if DEBUG:
        print(list_cam_fmt)

    with open(f_cam_fmt, "w") as fout:
        for camera_info in list_cam_fmt:
            fout.write(camera_info)

    with open(f_cam_fmt, "r") as fin:
        list_cam_fmt = fin.read()

    camera_info = list_cam_fmt.split("\n")
    mode = ""
    size = []
    img_modes = {}
    for line in camera_info:
        # print(line)
        mode_line_obj = re.search(r"\[\d\]", line)
        if mode_line_obj:
            mode_obj = re.search(r"'(\S{4})'", line)
            if mode_obj:
                mode = mode_obj.group(1)
                img_modes[mode] = {}

        if len(mode) > 0:
            # print("mode")
            # print(line)
            size_regex = re.search(r"Size:\sDiscrete\s(\d+)x(\d+)", line, re.I)
            if size_regex:
                # print("size")
                # print(f"width: {size_regex.group(1)}")
                # print(f"height: {size_regex.group(2)}")
                size = f'{size_regex.group(1)} X {size_regex.group(2)}'
                if size in img_modes[mode]:
                    pass
                else:
                    img_modes[mode][size] = []
                    # print(img_modes)


            if len(size) > 0:
                fps_regex = re.search(r"\(([\d\.]+)\sfps\)", line, re.I)

                if fps_regex:
                    print(f"fps: {fps_regex.group(0)}")
                    fps = int(float(fps_regex.group(1)))
                    img_modes[mode][size].append(fps)

    print(img_modes)
    # print(field_type(img_modes))
    return img_modes


def set_cam_fmt(cam_addr: str, cam_model: str, cam_fmt: dict) -> bool:
    # TODO: Change to software because the camera format is defined in json
    #  file from camera_GUI6.py and get rid of this piece.
    fmt_ctrls = ['pixel_mode', 'frame_width', 'frame_height', 'fps']
    for ctl in fmt_ctrls:
        assert ctl in cam_fmt, f"Camera {cam_model}, at {cam_addr} did not" \
                               f"receive control parameter {ctl}."
    w = cam_fmt['frame_width']
    h = cam_fmt['frame_height']
    fps = cam_fmt['fps']
    pf =  cam_fmt['pixel_mode']
    cmd = ["v4l2-ctl", "-d", f"{cam_addr}", "--verbose", "-p", f"{fps}",
           "--try-fmt-video", f"width={w},height={h},pixelformat={pf}"]
    try:
        subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error setting control: {e.output.decode()}")
        return False


def get_cam_hw_ctl(cam_addr: str, cam_model: str) -> dict:
    cam_port = cam_addr.strip().split("/")[-1]
    f_cam_ctl = cam_model[:12] + "_" + cam_port + "_ctl.txt"
    try:
        # "v4l2-ctl --list-ctrls -d /dev/video0"
        # cmd = ["v4l2-ctl", "-d " + cam_addr, "--list-ctrls"]
        cmd = ["v4l2-ctl", "-d " + cam_addr, "--all"]
        # print(cmd)
        # list_cam_fmt = subprocess.run(cmd, stdout=subprocess.PIPE)
        # print(list_cam_fmt)

        list_cam_ctl = []
        cmd1 = " ".join(cmd)
        process = subprocess.Popen(cmd1,
                                   shell=True,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   # bufsize=0,
                                   # text=True,
                                   )
        for line in process.stdout:
            list_cam_ctl.append(line.decode())
        for line in process.stderr:
            list_cam_ctl.append(line.decode())
        errcode = process.returncode
        if DEBUG:
            print(list_cam_ctl)
            print(f"the error code is {errcode}")
    except:
        keep_old_file = True

    if not keep_old_file:
        if os.path.isfile(f_cam_ctl):
            os.remove(f_cam_ctl)
            assert not os.path.isfile(f_cam_ctl), f"{f_cam_ctl} was not " \
                                                      "removed."

    if DEBUG:
        print(list_cam_ctl)

    with open(f_cam_ctl, "w") as fout:
        for camera_info in list_cam_ctl:
            fout.write(camera_info)

    # of the file to output of "v4l2-ctl --all"
    with open(f_cam_ctl, "r") as fin:
        list_cam_ctl = fin.read()

    print(list_cam_ctl)
    lines = len(list_cam_ctl)
    print(f"line nuber is {lines}")

    all_ctrls = {}
    ctrl_types = ["Camera Controls", "User Controls"]
    section = ""
    previous_type_menu = False
    for i, ctrl in enumerate(list_cam_ctl.split("\n")):
        # print(list_cam_ctl)
        # "auto_exposure 0x009a0901 (menu)   : min=0 max=3 default=3 value=1 (Manual Mode)"
        print(f"line {i} of list_cam_ctl is: \n {ctrl}")

        for ctrl_type in ctrl_types:
            if ctrl.find(ctrl_type) >= 0: #Do not process parameters in
                section = ctrl_type

        if section in ctrl_types:
            meta_data_raw = ctrl.split(":")
            meta_data = []
            if len(meta_data_raw) == 2:
                meta_data.append(meta_data_raw[0].strip())
                meta_data.append(meta_data_raw[1].strip())
                # print("meta_data is: ")
                # print(meta_data)
                # in_parenthesis = re.findall(r"\(.*?\)", meta_data[0])
                if meta_data[0].find("(int)") > 0:
                    data_type = "int"
                    previous_type_menu = False
                elif meta_data[0].find("(bool)") > 0:
                    data_type = "bool"
                    previous_type_menu = False
                elif meta_data[0].find("(menu)") > 0:
                    data_type = "menu"
                    previous_type_menu = True
                elif previous_type_menu:
                    print(meta_data)
                # print(meta_data, data_type)
                field_name_obj = re.search(r"\s*?(\S+?)\s.+?\b", meta_data[0])
                if field_name_obj:
                    fields = {}
                    field_name = field_name_obj.group(1)
                    fields['name'] = field_name
                    fields['data_type'] = data_type
                    # print(f"field_name is {field_name}, data_type is {data_type}.")
                    if data_type == 'int':
                        # "min=1 max=10000 step=1 default=156 value=156"
                        # print(meta_data[1])
                        # print(re.findall(r"min=[-\d]+?",meta_data[1]))
                        min = re.findall(r"min=\s*([-\d]+)", meta_data[1])[0]
                        max = re.findall(r"max=\s*([-\d]+)", meta_data[1])[0]
                        step = re.findall(r"step=\s*([-\d]+)", meta_data[1])[0]
                        default = re.findall(r"default=\s*([-\d]+)", meta_data[1])[0]
                        value = re.findall(r"value=\s*([-\d]+)", meta_data[1])[0]
                        # print(f"{min}, {max}, {step}, {default}, {value}")
                        fields['min'] = int(min)
                        fields['max'] = int(max)
                        fields['step'] = int(step)
                        fields['default'] = int(default)
                        fields['value'] = int(value)
                    elif data_type == "bool":
                        default = re.findall(r"default=\s*([-\d])+", meta_data[1])[0]
                        value = re.findall(r"value=\s*([-\d])+", meta_data[1])[0]
                        # print(f"{default}, {value}")
                        assert default == "0" or default == "1", "wrong boolean " \
                                                                 "value"
                        assert value == "0" or value == "1", "wrong boolean " \
                                                             "value"
                        fields['default'] = int(default)
                        fields['value'] = int(value)
                        if default == 0:
                            fields['options'] = {0: "default value", 1: ""}
                        else:
                            fields['options'] = {1: "default value", 0: ""}
                    elif data_type == "menu":
                        min = re.findall(r"min=\s*([-\d]+)", meta_data[1])[0]
                        max = re.findall(r"max=\s*([-\d]+)", meta_data[1])[0]
                        default = re.findall(r"default=\s*([-\d]+)", meta_data[1])[0]
                        value = re.findall(r"value=\s*([-\d]+)", meta_data[1])[0]
                        value_note = re.findall(r"\s*\((.*)\)", meta_data[1])[0]
                        # print(f"{min}, {max}, {default}, {value}, {value_note}")
                        fields['min'] = int(min)
                        fields['max'] = int(max)
                        fields['default'] = int(default)
                        fields['value'] = int(value)
                        fields['value_note'] = value_note
                        fields['options'] = {}
                    all_ctrls[field_name] = fields
                else:
                    print("meta_data is: ")
                    print(meta_data)
                    print("field name not found.")
                    if previous_type_menu:
                        value = int(meta_data[0].strip())
                        note = meta_data[1].strip()
                        print(f"add to menu item {value}, and {note}")
                        fields['options'][value] = note
            else:
                previous_type_menu = False

    print(all_ctrls)
    return all_ctrls

def change_1_para(cam_addr, key='', value=0):
    cmd = ["v4l2-ctl", "-d" + cam_addr, "--set-ctrl", f"{key}={value}"]
    print("Command to change the cameral hardware control:")
    print(cmd)
    try:
        subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error setting control: {e.output.decode()}")
        return False

def set_cam_hw_ctl(cam_addr: str, cam_model: str, dict_hw_control: dict) -> tuple:
    # Space is disallowed in elements of cmd!!!

    not_changeable_keys = ['tilt_absolute', 'pan_absolute', 'zoom_absolute']

    # , ,
    # for key in not_changeable_keys:
    #     dict_hw_control.pop(key, None)
    print("dict_hw_control is: ")
    print(dict_hw_control)
    fmt_ctrls = ['pixel_mode', 'frame_width', 'frame_height', 'fps']
    failed = {}
    cam_fmt_ctls = {}
    for key, value in dict_hw_control.items():
        if key in fmt_ctrls:
            cam_fmt_ctls[key] = value
        elif key in not_changeable_keys:
            pass
        else:
            if key in linked_keys:
                prereq_key = linked_keys[key][0]
                prereq_value = linked_keys[key][1]
                ret = change_1_para(cam_addr, key=prereq_key,
                                                value=prereq_value)
                if not ret:
                    failed[prereq_key] = prereq_value

            ret = change_1_para(cam_addr, key=key, value=value)
            if not ret:
                failed[key] = value

    if len(cam_fmt_ctls) > 0:
        cam_fmt_changed = set_cam_fmt(cam_addr, cam_model, cam_fmt_ctls)
    # assert cam_fmt_changed, "failed to set fmt."

    if len(failed) > 0:
        print("set_cam_hw_ctl returns:")
        print(f"failed: {failed}")
        exit(62476)
    else:
        print("All parameters were changed correctly.")
    # print(f"sw changed: {cam_fmt_changed}")
    print(f"camera format is: {cam_fmt_ctls}")
    return cam_fmt_ctls

def create_opencv_cam(cam_name, cam_path):
    json_file = cam_name[:12] + "_ctl&fmt.json"
    with open(json_file, 'r') as file:
        data = file.read()
    cam_ctrl_fmt_para_dict = json.loads(data)
    print("Current json string: ")
    print(data)

    cam_fmt_ctls = set_cam_hw_ctl(cam_path, cam_name,
                                cam_ctrl_fmt_para_dict)

    ['pixel_mode', 'frame_width', 'frame_height', 'fps']
    key = cam_fmt_ctls['pixel_mode']

    while True:
        try:
            cam = VideoCapture(cam_path, CAP_V4L2)
            if cam.isOpened():
                break
        except Exception:
            print("retry to connect camera")

    cam.set(CAP_PROP_FOURCC,
            VideoWriter.fourcc(*key))

    goal_width, goal_height, goal_fps = [cam_fmt_ctls['frame_width'],
                                         cam_fmt_ctls['frame_height'],
                                         cam_fmt_ctls['fps']]

    cam.set(CAP_PROP_FRAME_WIDTH, goal_width)
    cam.set(CAP_PROP_FRAME_HEIGHT, goal_height)
    cam.set(CAP_PROP_FPS, goal_fps)
    actual_width = int(cam.get(CAP_PROP_FRAME_WIDTH))
    actual_height = int(cam.get(CAP_PROP_FRAME_HEIGHT))
    actual_fps = int(cam.get(CAP_PROP_FPS))

    print2log(f"actual_width: {actual_width}, goal_width: {goal_width}")
    if actual_width != goal_width:
        print2log("Frame width does not match setting")

    print2log(f"actual_height: {actual_height}, goal_height {goal_height}")
    if actual_height != goal_height:
        print2log("Frame height does not match setting")

    print2log(f"actual_fps: {actual_fps}, goal_fps: {goal_fps}")
    if actual_fps != goal_fps:
        print("Video fps does not match setting")
    print2log(f"Camera was set at width: {actual_width}, height:"
              f" {actual_height}, FPS: {actual_fps}")

    return cam

# def run_win_cmd(cmd):
#     result = []
#     process = subprocess.Popen(cmd,
#                                shell=True,
#                                stdout=subprocess.PIPE,
#                                stderr=subprocess.PIPE,
#                                # bufsize=0,
#                                # text=True,
#                                )
#     for line in process.stdout:
#         result.append(line)
#     for line in process.stderr:
#         result.append(line)
#     errcode = process.returncode
#
#     if errcode is not None:
#         raise Exception('cmd %s failed, see above for details', cmd)
#
#     return result
#
# def get_camera_names():
#     # run_win_cmd('ffmpeg -list_devices true -f dshow -i dummy -hide_banner')
#     camera_list = run_win_cmd('ffmpeg -list_devices true -f dshow -i dummy -hide_banner')
#
#     camera_names = []
#     for line in camera_list:
#         print(line)
#         if isinstance(line,str):
#             text = line
#         elif isinstance(line, bytes):
#             text = line.decode(encoding="utf-8", errors="ignore")
#         # print(text)
#         if text.find("Microphone") >=0 or text.find("Alternative name") >=0 or \
#                 text.find("DirectShow") >= 0:
#             pass
#         else:
#             # print(text)
#             camera_name_obj = re.search("\"(.+)\"", text)
#             if camera_name_obj:
#                 camera_name = camera_name_obj.group(1)
#                 # print(camera_name)
#                 camera_names.append(camera_name)
#
#     return camera_names
#
#
# def get_camera_formats(camera_name):
#     # This command can only not be run by Python.
#     formats_return = run_win_cmd("chcp 65001 > nul")
#     formats_return = run_win_cmd(f'set cam="{camera_name}"')
#     cmd = f'ffmpeg -loglevel trace -list_options true -f dshow -i video="{camera_name}"'
#     # print(cmd)
#     formats_return = run_win_cmd(cmd)
#
#     # print("command finished")
#     # print(formats_return)
#
#     formats = []
#     for line in formats_return:
#         # print(line)
#         text = line.decode(encoding="utf-8", errors="ignore")
#         num_equal_sign = len(re.findall("=", text))
#         if num_equal_sign >= 2:
#             print(text)
#
#     return formats


# def get_camera_names_win():
#     # run_win_cmd('ffmpeg -list_devices true -f dshow -i dummy -hide_banner')
#     camera_list = run_win_cmd('ffmpeg -list_devices true -f dshow -i dummy -hide_banner')
#
#     camera_names = []
#     for line in camera_list:
#         print(line)
#         if isinstance(line,str):
#             text = line
#         elif isinstance(line, bytes):
#             text = line.decode(encoding="utf-8", errors="ignore")
#         # print(text)
#         if text.find("Microphone") >=0 or text.find("Alternative name") >=0 or \
#                 text.find("DirectShow") >= 0:
#             pass
#         else:
#             # print(text)
#             camera_name_obj = re.search("\"(.+)\"", text)
#             if camera_name_obj:
#                 camera_name = camera_name_obj.group(1)
#                 # print(camera_name)
#                 camera_names.append(camera_name)
#
#     return camera_names
#
#
# def run_win_cmd(cmd):
#     result = []
#     process = subprocess.Popen(cmd,
#                                shell=True,
#                                stdout=subprocess.PIPE,
#                                stderr=subprocess.PIPE,
#                                # bufsize=0,
#                                # text=True,
#                                )
#     for line in process.stdout:
#         result.append(line)
#     for line in process.stderr:
#         result.append(line)
#     errcode = process.returncode
#
#     if errcode is not None:
#         raise Exception('cmd %s failed, see above for details', cmd)
#     return result


if __name__ == "__main__":
    cameras = get_USB_cameras()
    print(cameras)
    print(type(cameras))

    for addr, model in cameras.items():
        print(addr)
        print(model)
        # formats = get_camera_fmt(addr, model)
        # print(f"camera {model} at {addr} have following formats:")
        # print(formats)
        # print("\n\n\n\n\n")
        # controls = get_cam_ctrls(addr, model)
        # print(controls)
        # print("\n\n\n\n\n")

# camera_names = get_camera_names()
#
# print(camera_names)

# for camera in camera_names:
#     cmd = f'ffmpeg -f dshow -show_video_device_dialog true -i video="{camera}"'
#     print(cmd)
#     run_win_cmd(cmd)
#
#     print("To get camera format.")
#     try:
#         camera_imaging_format = get_camera_formats(camera)
#     except Exception:
#         print(Exception)
#
#     # cmd = f'ffmpeg -list_options true -f dshow -i video="{camera}"'
#     # print(cmd)
#     # run_win_cmd(cmd)
#
#
# # list_controls = subprocess.run(['v4l2-ctl', '--list-ctrls'],
# #                                stdout=subprocess.PIPE)
# # camera_ctrl = list_controls.stdout.decode().split("\n")