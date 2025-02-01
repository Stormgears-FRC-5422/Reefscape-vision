import os
import numpy as np
import cv2
import time
from matplotlib import pyplot as plt

FASTER_CAPTURE = True
SINGLE_CAMERA = True
PICTURE_ONLY = True

def start_cam(cam_id=0):
    cam = cv2.VideoCapture(cam_id, cv2.CAP_DSHOW)
    for i in range(1, 10):
        assert cam.isOpened(), "Camera has not opened."
        time.sleep(0.1)
        if i > 10:
            print(f"Failed to start camera: {cam_id} ")
            exit(3256)

    goal_width = 1920
    goal_height = 1080
    fps = 30

    cam.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc('M', 'J', 'P', 'G'))
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, goal_width)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, goal_height)
    cam.set(cv2.CAP_PROP_FPS, fps)
    actual_width = int(cam.get(cv2.CAP_PROP_FRAME_WIDTH))
    actual_height = int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT))
    actual_fps = int(cam.get(cv2.CAP_PROP_FPS))

    print(f"actual_width: {actual_width}, goal_width: {goal_width}")
    print(f"actual_height: {actual_height}, goal_height {goal_height}")
    print(f"actual_fps: {actual_fps}, goal_fps: {fps}")

    assert actual_width == goal_width, "Frame width does not match setting"
    assert actual_height == goal_height, "Frame height does not match setting"
    assert actual_fps == fps, "Video fps does not match setting"
    print("Camera was set at", actual_width, actual_height, fps)

    return cam

if SINGLE_CAMERA:
    cam_l = start_cam(0)
else:
    cam_l = start_cam(0)
    time.sleep(20)
    cam_r = start_cam(1)

if PICTURE_ONLY:
    i = 0
    while True:
        if SINGLE_CAMERA:
            result, imgL = cam_l.read()
            print("Move camera to take RIGHT eye image.")
            input("Press any key when ready...")
            result, imgR = cam_l.read()
        else:
            result, imgL = cam_l.read()
            result, imgR = cam_r.read()
        cv2.imwrite(f"tsukuba{i}_l.png", imgL)
        cv2.imwrite(f"tsukuba{i}_r.png", imgR)
        print("Move camera to take NEXT SET of raw.")
        input("Press any key when ready...")

        i += 1
else:
    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'X264')
    out = cv2.VideoWriter('output.mp4', fourcc, 30, (3840, 1080))

    all_frames = []
    for i in range(500):
        if FASTER_CAPTURE:
            if not (cam_l.grab() and cam_r.grab()):
                print("No more frames")
                break
            _, imgL = cam_l.retrieve()
            _, imgR = cam_r.retrieve()

        else:
            resultL, imgL = cam_l.read()
            resultR, imgR = cam_r.read()

            if resultL and resultR:
                if imgL is not None and imgR is not None:
                    pass
                else:
                    if imgL is None:
                        print("imgL is None")
                    elif imgR is None:
                        print("imgR is None")
                    else:
                        print("Unexpected situation of img L and R.")
            else:
                if not resultL:
                    print("resultL is false")
                elif not resultR:
                    print("resultR is false")
                else:
                    print("Unexpected situation of result L and R.")

        combined_image = cv2.hconcat([imgL, imgR])
        all_frames.append(combined_image)

        i += 1

    # Release everything if job is finished
    cam_l.release()
    cam_r.release()

    for combined_image in all_frames:
        # write the frame
        out.write(combined_image)

    out.release()

