import time
import sys
import os
# import multiprocessing as mp
from multiprocessing.shared_memory import SharedMemory
from multiprocessing import Array, freeze_support, Process, Lock
# import logging
import random
import json

from numpy import array, sqrt, copy, matmul, dot, empty, uint8, zeros, \
    ndarray, copyto, prod, rot90
from cv2 import imread, cvtColor, COLOR_BGR2GRAY, line, imshow, waitKey, \
    circle, resize, VideoCapture, CAP_V4L2, CAP_PROP_FRAME_WIDTH, \
    CAP_PROP_FRAME_HEIGHT, CAP_PROP_FPS

from cscore import UsbCamera, CvSource, _cscore, MjpegServer
from ntcore import NetworkTableInstance, EventFlags, PubSubOptions, _now

#############################################################################
# Using the estimator of robotpy_apriltag 2024.3.1.0 runs on PC will have an
# error TypeError: Unable to convert function return value to a Python field_type!
# 2024.3.2.1 fixed the issue.
import robotpy_apriltag
#############################################################################
import ntcore
import subprocess
from apriltag2xyz import read_apriltag_abs_coord, get_xy_shift, \
    get_abs_field_coord
# from tools import print2log, backup_file, print2log1, create_sequencial_dir

from camera_hardware import get_USB_cameras  # Ensure this is properly defined
from tools import print2log, print2log1, create_random_dir, backup_file,\
    is_directory_writable, create_sequential_dir

DEBUG = False
DISPLAY_IMAGE = True
DISPLAY_BORDER = True

# TODO:
#  1. read /sys/firmware/devicetree/base/model for hardware. Enable write for
#  5B. - done
#  2. Climber camera rotate image by 90 degrees - done
#  3. Climber camera no circle. - done
#  4. Clean the USB drive
#  5. Check the hardware (RPi5 or RPi3). Save the videos
#  6. Add coral source detection
#  7. Add reef tip detection
#  8. test USB recording file size.


DEBUG = False
DEBUG_IMAGE_COUNT = 5
# SAVE_VIDEO = False

if sys.platform.startswith('linux'):
    SAVE_VIDEO = True
    with open(r"/sys/firmware/devicetree/base/model", "r") as f_sys:
        hardware_info = f_sys.read()
    if hardware_info.find("Raspberry Pi 5") >= 0:
        RPI_5 = True
    else:
        SAVE_VIDEO = False
        RPI_5 = False

    TARGET_DEST_FOLDER = r"/mnt/usb/"
    DEFAULT_DEST_FOLDER = r"/home/pi/Downloads/"
    if is_directory_writable(TARGET_DEST_FOLDER):
        DEST_DIR = TARGET_DEST_FOLDER
    else:
        if is_directory_writable(DEFAULT_DEST_FOLDER):
            DEST_DIR = DEFAULT_DEST_FOLDER
        else:
            print2log(f"Neither {TARGET_DEST_FOLDER} nor "
                      f"{DEFAULT_DEST_FOLDER} is writable. exit(6487)")
            SAVE_VIDEO = False

    if SAVE_VIDEO:
        IMAGE_PATH = create_sequencial_dir(os.path.join(DEST_DIR, "FRC_field"))
        LOG_PATH = create_random_dir(os.path.join(DEST_DIR, "logs"))


def camera_process(camera_index, camera_path, camera_name, shm_name,
                   stream_shape, lock):
    stream_w = stream_shape[1]
    stream_h = stream_shape[0]
    stream_channels = stream_shape[2]

    while True:
        attempts = 0
        try:
            cam = VideoCapture(camera_path, CAP_V4L2)
        except Exception:
            if attempts < 100:
                attempts += 1
            else:
                exit(8453)
        break

    cam.set(CAP_PROP_FRAME_WIDTH, 640)
    cam.set(CAP_PROP_FRAME_HEIGHT, 480)
    cam.set(CAP_PROP_FPS, 30)

    """Captures frames from a specific camera and writes to shared memory."""

    shm = SharedMemory(name=shm_name)
    shm_array = ndarray(stream_shape, dtype=uint8, buffer=shm.buf)

    # cam = UsbCamera(name=f"Camera {camera_index}", path=camera_path)
    # cam.setResolution(stream_shape[1], stream_shape[0])
    if camera_name[:12].lower() == 'global shutt':
        raw_shape = (1080, 1920, 3)
        # with lock:
        #     print2log1("global shutter camera")
    else:
        raw_shape = (480, 640, 3)
        # with lock:
        #     print2log1("Non global shutter camera")

    capture_mat = zeros(raw_shape, dtype=uint8)  # Placeholder frame
    rotate_mat = zeros((raw_shape[1], raw_shape[0], raw_shape[2]),
                       dtype=uint8) # Placeholder frame

    while True:
        ret, capture_mat = cam.read()
        if ret:
            if camera_name[:12].lower() == 'global shutt':
                rotate_mat = rot90(capture_mat)
                # rotate_mat = rot90(capture_mat, k=-1) # rotate image
                # clockwise.
                stream_mat = resize(rotate_mat[:, 0:810, :], (stream_w,
                                                             stream_h))
            else:
                stream_mat = resize(capture_mat, (stream_w, stream_h))
                # Draw a red circle on the frame (for visualization)
                circle(stream_mat, (stream_w // 2, stream_h // 2), 30,
                       (0, 0, 255), 3)

            copyto(shm_array, stream_mat)


def output_stream(shm_names, shape, arr_from_main_arr):
    """Continuously send processed frames from shared memory to the MJPEG stream, switching every 5 seconds."""


    # Creates the CvSource and MjpegServer and connects them
    output_stream = CvSource("Blur", _cscore.VideoMode.PixelFormat.kMJPEG, 640,
                             480, 30)

    mjpeg_server2 = MjpegServer("serve_Blur", 1182)
    mjpeg_server2.setSource(output_stream)

    shms = [SharedMemory(name=name) for name in shm_names]
    shm_arrays = [ndarray(shape, dtype=uint8, buffer=shm.buf) for shm in
                  shms]

    cam_index = 0
    last_switch_time = time.time()
    while True:
        # print(f"arr_from_main_arr={arr_from_main_arr}")
        cam_index = arr_from_main_arr[1]
        print(f"cam_index is {cam_index}.")

        output_stream.putFrame(shm_arrays[cam_index])
        time.sleep(0.03)  # Maintain stream FPS


if __name__ == "__main__":
    freeze_support()

    try:
        SharedMemory.close()
        SharedMemory.unlink()
    except Exception:
        print2log("Shared memory exists and was deleted.")
        pass

    # Retrieve available USB cameras
    dict_cameras = get_USB_cameras()
    print2log1("Detected Cameras:", dict_cameras)

    """
    Detected Cameras: {'/dev/video4': 'HD Pro Webcam C920 (usb-xhci-hcd.0-2):',
     '/dev/video0': 'Global Shutter Camera: Global S (usb-xhci-hcd.1-1):',
      '/dev/video2': 'Teslong Camera: Teslong Camera (usb-xhci-hcd.1-2.4):'}
    """

    if len(dict_cameras) == 0:
        print2log1("No camera was detected.")
        exit()

    frame_shape = (240, 320, 3)
    shm_names = [f"shm_cam_{i}" for i in range(len(dict_cameras))]
    print2log(f"shm_names is {shm_names}")
    shms = []
    for name in shm_names:
        # shms.append(SharedMemory(create=False, size=prod(streaming_frame_shape),
        #                          name=name))

        try:
            shm = SharedMemory(create=True, size=prod(frame_shape),
                               name=name)
        except FileExistsError:
            shm = SharedMemory(create=False, size=prod(frame_shape),
                               name=name)
        except Exception as shm_e:
            print2log1('Error:' + str(shm_e))
            print2log1('Error:' + str(shm_e))
            exit(73766)

        shms.append(shm)


    # shms = [SharedMemory(create=True, size=prod(streaming_frame_shape), name=name) for
    #         name in shm_names]

    # Create a separate process for each camera
    lock = Lock()
    camera_processes = []
    for cam_i, (camera_path, camera_name) in enumerate(dict_cameras.items()):
        process = Process(target=camera_process,
                             args=(
                                 cam_i, camera_path, camera_name,
                                 shm_names[cam_i],
                                 frame_shape, lock))
        camera_processes.append(process)
        process.start()
        # if cam_i == 2:
        #     break

    arr_from_main_arr = Array('i', [0, 0])

    # Start the output streaming process
    output_process = Process(target=output_stream,
                                args=(shm_names, frame_shape, arr_from_main_arr))
    output_process.start()


    # logging.basicConfig(filename='myapp.log', level=logging.DEBUG)
    inst = NetworkTableInstance.getDefault()
    table = inst.getTable("datatable")
    time_offset = inst.getServerTimeOffset()
    # xSub = table.getDoubleTopic("x").subscribe(0)
    # ySub = table.getDoubleTopic("Y").subscribe(0)
    # zPub = table.getDoubleTopic("z").publish()
    streaming_cam_ID_Sub = table.getIntegerTopic("Camera_ID").subscribe(0)
    server_counter_sub = table.getIntegerTopic("counter").subscribe(0)

    # timeStamp = table.getIntegerTopic("-1").publish(ntcore.PubSubOptions(periodic=0.01))
    # aaStr = table.getStringTopic("apriltag_json").publish(
    #     PubSubOptions(periodic=0.01))
    tsStrPub = table.getStringTopic("apriltag_json2").publish(
        PubSubOptions(periodic=0.001))

    # inst.configPythonLogging(
    #     min=NetworkTableInstance.LogLevel.kLogInfo,
    #     max=NetworkTableInstance.LogLevel.kLogCritical,
    #     name='networktable')
    inst.startClient4("example client")
    ######################################################
    #   When set the server, use inst.setServer(ip address or hostname in str), or
    #   inst.setServer(TEAM_NUMBER_IN_INTEGER)
    ######################################################
    inst.setServer("192.168.0.92")
    # where TEAM=190, 294, etc, or use "
    # "inst.setServer("hostname") or similar
    inst.startDSClient()  # recommended if running on DS computer; this gets the robot IP from the DS

    # cam = cv2.VideoCapture("/dev/video0", cv2.CAP_V4L2)
    random.seed(12345)
    json_dict = {
        "serverTime": 0,
        "time": 0,
        "counter": 0,
        "streaming_cam_ID": 0
    }

    counter = 0
    while True:
        time.sleep(0.001)
        # ret, img = cam.read()

        #################################################################
        # The topics can only read once.
        #################################################################
        # x = xSub.get()

        server_counter = server_counter_sub.getAtomic()
        server_time = server_counter.serverTime
        client_time = server_counter.time
        value = server_counter.value

        streaming_cam_ID = streaming_cam_ID_Sub.getAtomic()
        # print2log(f'streaming_cam_ID is: {streaming_cam_ID}')
        streaming_cam = streaming_cam_ID.value

        with arr_from_main_arr.get_lock():
            arr_from_main_arr[0] = server_time
            arr_from_main_arr[1] = streaming_cam

        json_dict = {
            "serverTime": server_time,
            "client_time": client_time,
            "counter": value,
            "streaming_cam_ID": streaming_cam
        }

        rd_txt = json.dumps(json_dict)
        if counter % 10 == 0:
            # print2log(time.time(), rd_txt, streaming_cam_ID)
            pass

        tsStrPub.set(rd_txt)
        # inst.flush()

        counter += 1


    # # Keep main process alive
    # try:
    #     while True:
    #         time.sleep(0.001)
    # except KeyboardInterrupt:
    #     print2log("Stopping processes...")

    # Terminate all processes
    for process in camera_processes:
        process.terminate()
        process.join()

    output_process.terminate()
    output_process.join()

    # Clean up shared memory
    for shm in shms:
        shm.close()
        shm.unlink()