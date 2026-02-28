import time
import os
import sys
from multiprocessing import Array, freeze_support, Process, Lock, Queue
import random
import json

# import numpy as np
from numpy import rot90, zeros, uint8
from cv2 import resize, circle

from cscore import CameraServer, UsbCamera, CvSink, CvSource
from ntcore import NetworkTableInstance, EventFlags, PubSubOptions, _now

from camera_hardware import get_USB_cameras  # Ensure this is properly defined
from tools import print2log, print2log1, create_random_dir, backup_file,\
    is_directory_writable, create_sequential_dir

# TODO:
#  1. read /sys/firmware/devicetree/base/model for hardware. Enable write for
#  5B. - done
#  2. Climber camera rotate image by 90 degrees - done
#  3. Climber camera no circle. - done
#  4. Clean the USB drive, add a new USB instead. - done
#  5. Check the hardware (RPi5 or RPi3). Save the videos
#  6. Add coral source detection
#  7. Add reef tip detection
#  8. test USB recording file size. Reduced frame rate
#  9. CameraID. use model number for cameraID
#  10. Network Tables server need to use team number.

TEAM_NUMBER_IN_INTEGER = 5422
RAW_IMG_WIDTH = 640
RAW_IMG_HEIGHT = 480
STREAM_WIDTH = 320
STREAM_HEIGHT = 240
SIMULATION = True
SAVE_VIDEO = True

if sys.platform.startswith('linux'):
    with open(r"/sys/firmware/devicetree/base/model", "r") as f_sys:
        hardware_info = f_sys.read()

    if hardware_info.find("Raspberry Pi 5") >= 0:
        HARDWARE_VER = "RPI_5"
    elif hardware_info.find("Raspberry Pi 3") >= 0:
        HARDWARE_VER = "RPI_3"
        SAVE_VIDEO = False

    TARGET_DEST_FOLDERS = [r"/mnt/usb/", r"/mnt/usb1/", r"/home/pi/Downloads/"]

    dest_folder = ""
    for folder in TARGET_DEST_FOLDERS:
        if is_directory_writable(folder):
            dest_folder = folder
            SAVE_VIDEO = True
            break

    if SAVE_VIDEO and os.path.isdir(dest_folder):
        print(f"dest_folder is {dest_folder}")
        IMAGE_PATH = create_sequential_dir(os.path.join(dest_folder, "FRC_field"))
        LOG_PATH = create_sequential_dir(os.path.join(dest_folder, "logs"))

def video_processor(camera_queue, output_queue):
    """Process video frames and add effects before sending to the output queue."""
    CameraServer.enableLogging()

    dict_cameras = get_USB_cameras()

    # Create two USB dict_cameras
    for camera_path, camera_name in dict_cameras.items():
        cam1 = UsbCamera(name=camera_name[:12], path=camera_path)

    # Set resolution
    cam1.setResolution(RAW_IMG_WIDTH, RAW_IMG_HEIGHT)
    

    # Create CvSink objects to grab frames
    sink1 = CameraServer.getVideo(camera=cam1)
    

    # Create CvSource to send processed frames
    # output = CameraServer.putVideo("ProcessedVideo", RAW_IMG_WIDTH, RAW_IMG_HEIGHT)

    frame = zeros((RAW_IMG_HEIGHT, RAW_IMG_WIDTH, 3), dtype=uint8)  # Placeholder frame
    rotate_mat = zeros((RAW_IMG_WIDTH, RAW_IMG_HEIGHT, 3), dtype=uint8)  #
    # Placeholder frame
    resized_mat = zeros((STREAM_WIDTH, STREAM_HEIGHT, 3), dtype=uint8)  # Placeholder
    # frame

    cs_start = time.time()
    frame_num = 0
    last_streaming_camera = 0
    while True:
        #TODO: cameras other than current_cam are not read. The cause of the
        # faster speed than video_stream_n_process8.py?
        current_cam = camera_queue.get()  # Get the latest camera selection
        # print(current_cam)
        # camera_queue.put(current_cam)  # Put it back to maintain state

        # Select the appropriate camera sink
        current_sink = sink1 
        time.sleep(0.01)  # ~100 FPS

        # Capture frame
        timestamp, frame = current_sink.grabFrame(frame)

        if frame is None or frame.size == 0:
            continue  # Skip invalid frames

        # Send processed frame to output queue
        if current_cam == 0:
            # Draw a red circle on the frame
            circle(frame, (320, 240), 50, (0, 0, 255), 3)
            resized_mat = resize(frame, (320, 240))
            output_queue.put(resized_mat)
        elif current_cam == 1:
            rotate_mat = rot90(frame, k=2)
            resized_mat = resize(rotate_mat, (320, 240))
            output_queue.put(resized_mat)
            # print("camera 1")
        else:
            print(f"wrong current_cam value {current_cam}")

        frame_num += 1
        # elapse = time.time() - cs_start
        # print(f"frame_num={frame_num}, elapse={elapse}s.")

        if current_cam != last_streaming_camera:
            print(f"Switched camera from {last_streaming_camera} to"
                  f" {current_cam}.")
            last_streaming_camera = current_cam
        last_streaming_camera = current_cam


def output_stream(output_queue):
    """Continuously send processed frames to the MJPEG stream."""
    output = CameraServer.putVideo("ProcessedVideo", STREAM_WIDTH, STREAM_HEIGHT)

    while True:
        frame = output_queue.get()  # Get the latest processed frame
        output.putFrame(frame)  # Send it to the output stream


freeze_support()
# Shared queue for camera switching
camera_queue = Queue()
camera_queue.put(0)  # Start with camera 0

# Shared queue for processed frames
output_queue = Queue()

arr_from_main_arr = Array('i', [0, 0])

# Create processes
switcher_process = Process(target=camera_switcher, args=(camera_queue,
                                                         arr_from_main_arr))
processor_process = Process(target=video_processor,
                               args=(camera_queue, output_queue))
output_process = Process(target=output_stream, args=(output_queue,))

# Start processes
switcher_process.start()
processor_process.start()
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
# inst.setServer(TEAM_NUMBER_IN_INTEGER)
# where TEAM=190, 294, etc, or use "
# "inst.setServer("hostname") or similar
######################################################
if SIMULATION:
    # IP address of desktop computer
    if HARDWARE_VER == "RPI_3":
        inst.setServer("192.168.0.92")
    elif HARDWARE_VER == "RPI_5":
        inst.setServer("192.168.0.92")
    else:
        print2log1("IP address of co-processor was not found. Exit(78436)")
        exit(78436)
else:
    inst.setServer(TEAM_NUMBER_IN_INTEGER)

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
    time.sleep(0.01)
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
    streaming_cam = streaming_cam_ID.value

    # print(f"streaming camera id {streaming_cam_ID}")
    # TODO: comment following line will allow the camera changes.
    # streaming_cam = 0

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
    if counter % 500 == 0:
        local_time = time.time()
        print(f"time.time()={local_time}, rd_txt=\n{rd_txt}")
        pass

    tsStrPub.set(rd_txt)
    # inst.flush()

    counter += 1

# Keep main process alive
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Stopping processes...")
    switcher_process.terminate()
    processor_process.terminate()
    output_process.terminate()
    switcher_process.join()
    processor_process.join()
    output_process.join()


#TODO: fix error: bind() to port 1181 failed: Address already in use