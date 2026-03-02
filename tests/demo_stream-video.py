from cscore import CameraServer
import cv2
import numpy as np

width = 640
height = 480

CameraServer.enableLogging()
camera = CameraServer.startAutomaticCapture()
camera.setResolution(width, height)
sink = CameraServer.getVideo()
input_img = np.zeros(shape=(height, width, 3), dtype=np.uint8)

#
# CameraServer initialization code here
#
output = CameraServer.putVideo("Name", width, height)

while True:
   time, input_img = sink.grabFrame(input_img)
   if time == 0: # There is an error
      output.notifyError(sink.getError())
      continue
   #
   # Insert processing code here
   #
   processed_img = input_img
   output.putFrame(processed_img)