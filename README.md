# ReefScape-vision
Vision coding for FRC 2025 ReefScape

This repository is intended to build a computer vision system based on Raspberry Pi 5 using WPILibPi libraries.

Initial thinkings:
	1. Use multiprocessing, create 
		a. Use fixed number of Pools, 1 or 2 less than the CPU number. Only copy the resources as fork does for once.
		b. Try not to call Pool function (make a copy all resources) all the time.
		c. Pre-allocate memory, avoid do it for each acquired image.
	2. Use camera server for at least 2 cameras - one Pool
		a. When initiating camera, make sure to reset camera hardware with pre-set parameters. 
		b. Endless loop for acquiring the image in shared memory at given h*w@fps
		c. Stream images to drive station (0, 1, or 2 camera).
	3. Two pools for two cameras
		a. Pool 1. Apriltag detection - send location to Roborio
		b. Pool 2. Vision Servoing - send detection to roborio
		c. Or a Pool can do both apriltag detection and object detection.
		d. When no image update. The pools give out the control of CPU
