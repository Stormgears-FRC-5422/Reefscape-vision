import os
import sys
from pathlib import Path

from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QSlider,
    QGroupBox,
    QComboBox,
    QMessageBox,
    QPushButton,
    QInputDialog,
    QLineEdit,
    QFileDialog
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QImage, QPixmap
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import cv2
from numpy import copy, array, uint8, ones, random

valid_color_spaces = \
    ['COLOR_BGR2BGR555',
     'COLOR_BGR2BGR565',
     'COLOR_BGR2BGRA',
     'COLOR_BGR2GRAY',
     'COLOR_BGR2HLS',
     'COLOR_BGR2HLS_FULL',
     'COLOR_BGR2HSV',
     'COLOR_BGR2HSV_FULL',
     'COLOR_BGR2LAB',
     'COLOR_BGR2LUV',
     'COLOR_BGR2Lab',
     'COLOR_BGR2Luv',
     'COLOR_BGR2RGB',
     'COLOR_BGR2RGBA',
     'COLOR_BGR2XYZ',
     'COLOR_BGR2YCR_CB',
     'COLOR_BGR2YCrCb',
     'COLOR_BGR2YUV',
     'COLOR_BGR2YUV_I420',
     'COLOR_BGR2YUV_IYUV',
     'COLOR_BGR2YUV_UYNV',
     'COLOR_BGR2YUV_UYVY',
     'COLOR_BGR2YUV_Y422',
     'COLOR_BGR2YUV_YUNV',
     'COLOR_BGR2YUV_YUY2',
     'COLOR_BGR2YUV_YUYV',
     'COLOR_BGR2YUV_YV12',
     'COLOR_BGR2YUV_YVYU',
     'COLOR_BGRA2BGR',
     'COLOR_BGRA2BGR555',
     'COLOR_BGRA2BGR565',
     'COLOR_BGRA2GRAY',
     'COLOR_BGRA2RGB',
     'COLOR_BGRA2RGBA',
     'COLOR_BGRA2YUV_I420',
     'COLOR_BGRA2YUV_IYUV',
     'COLOR_BGRA2YUV_UYNV',
     'COLOR_BGRA2YUV_UYVY',
     'COLOR_BGRA2YUV_Y422',
     'COLOR_BGRA2YUV_YUNV',
     'COLOR_BGRA2YUV_YUY2',
     'COLOR_BGRA2YUV_YUYV',
     'COLOR_BGRA2YUV_YV12',
     'COLOR_BGRA2YUV_YVYU',
     'COLOR_HLS2BGR',
     'COLOR_HLS2BGR_FULL',
     'COLOR_HLS2RGB',
     'COLOR_HLS2RGB_FULL',
     'COLOR_HSV2BGR',
     'COLOR_HSV2BGR_FULL',
     'COLOR_HSV2RGB',
     'COLOR_HSV2RGB_FULL',
     'COLOR_LAB2BGR',
     'COLOR_LAB2LBGR',
     'COLOR_LAB2LRGB',
     'COLOR_LAB2RGB',
     'COLOR_LBGR2LAB',
     'COLOR_LBGR2LUV',
     'COLOR_LBGR2Lab',
     'COLOR_LBGR2Luv',
     'COLOR_LRGB2LAB',
     'COLOR_LRGB2LUV',
     'COLOR_LRGB2Lab',
     'COLOR_LRGB2Luv',
     'COLOR_LUV2BGR',
     'COLOR_LUV2LBGR',
     'COLOR_LUV2LRGB',
     'COLOR_LUV2RGB',
     'COLOR_Lab2BGR',
     'COLOR_Lab2LBGR',
     'COLOR_Lab2LRGB',
     'COLOR_Lab2RGB',
     'COLOR_Luv2BGR',
     'COLOR_Luv2LBGR',
     'COLOR_Luv2LRGB',
     'COLOR_Luv2RGB',
     'COLOR_RGB2BGR',
     'COLOR_RGB2BGR555',
     'COLOR_RGB2BGR565',
     'COLOR_RGB2BGRA',
     'COLOR_RGB2GRAY',
     'COLOR_RGB2HLS',
     'COLOR_RGB2HLS_FULL',
     'COLOR_RGB2HSV',
     'COLOR_RGB2HSV_FULL',
     'COLOR_RGB2LAB',
     'COLOR_RGB2LUV',
     'COLOR_RGB2Lab',
     'COLOR_RGB2Luv',
     'COLOR_RGB2RGBA',
     'COLOR_RGB2XYZ',
     'COLOR_RGB2YCR_CB',
     'COLOR_RGB2YCrCb',
     'COLOR_RGB2YUV',
     'COLOR_RGB2YUV_I420',
     'COLOR_RGB2YUV_IYUV',
     'COLOR_RGB2YUV_UYNV',
     'COLOR_RGB2YUV_UYVY',
     'COLOR_RGB2YUV_Y422',
     'COLOR_RGB2YUV_YUNV',
     'COLOR_RGB2YUV_YUY2',
     'COLOR_RGB2YUV_YUYV',
     'COLOR_RGB2YUV_YV12',
     'COLOR_RGB2YUV_YVYU',
     'COLOR_RGBA2BGR',
     'COLOR_RGBA2BGR555',
     'COLOR_RGBA2BGR565',
     'COLOR_RGBA2BGRA',
     'COLOR_RGBA2GRAY',
     'COLOR_RGBA2RGB',
     'COLOR_RGBA2YUV_I420',
     'COLOR_RGBA2YUV_IYUV',
     'COLOR_RGBA2YUV_UYNV',
     'COLOR_RGBA2YUV_UYVY',
     'COLOR_RGBA2YUV_Y422',
     'COLOR_RGBA2YUV_YUNV',
     'COLOR_RGBA2YUV_YUY2',
     'COLOR_RGBA2YUV_YUYV',
     'COLOR_RGBA2YUV_YV12',
     'COLOR_RGBA2YUV_YVYU',
     'COLOR_XYZ2BGR',
     'COLOR_XYZ2RGB',
     'COLOR_YCR_CB2BGR',
     'COLOR_YCR_CB2RGB',
     'COLOR_YCrCb2BGR',
     'COLOR_YCrCb2RGB',
     'COLOR_YUV2BGR',
     'COLOR_YUV2RGB']


# class MplCanvas(FigureCanvas):
#     def __init__(self, parent=None, width=5, height=4, dpi=100):
#         fig = Figure(figsize=(width, height), dpi=dpi)
#         self.axes = fig.add_subplot(111)
#         super(MplCanvas, self).__init__(fig)


class MatplotlibCanvas(FigureCanvas):
    def __init__(self, image_path, parent=None):
        # Create a Matplotlib figure
        fig = Figure()
        self.ax = fig.add_subplot(111)
        super().__init__(fig)
        self.setParent(parent)

        # Load and display the image
        img = mpimg.imread(image_path)
        self.ax.imshow(img, aspect='equal')
        self.ax.axis("off")  # Hide the axes

    def plot_np_array(self, img_array):
        # self.ax.clear()
        self.ax.imshow(img_array, aspect='equal')
        self.ax.axis("off")  # Hide the axes
        self.draw()


class CustomSlider(QWidget):
    # Define a custom signal to emit the slider's value
    value_changed = pyqtSignal(int)

    def __init__(self, label, min_value=0, max_value=255, initial_value=127):
        super().__init__()
        self.label = label
        self.init_ui(min_value, max_value, initial_value)

    def init_ui(self, min_value, max_value, initial_value):
        # Create the main layout
        main_layout = QVBoxLayout()

        # Create a horizontal layout for the slider and its labels
        slider_layout = QHBoxLayout()

        # Create labels for minimum and maximum values
        self.min_label = QLabel(str(min_value), self)
        self.min_label.setAlignment(Qt.AlignLeft)
        self.max_label = QLabel(str(max_value), self)
        self.max_label.setAlignment(Qt.AlignRight)

        # Create a QSlider
        self.slider = QSlider(Qt.Horizontal, self)
        self.slider.setMinimum(min_value)
        self.slider.setMaximum(max_value)
        self.slider.setValue(initial_value)

        # Add the minimum label, slider, and maximum label to the horizontal layout
        slider_layout.addWidget(self.min_label)
        slider_layout.addWidget(self.slider)
        slider_layout.addWidget(self.max_label)

        # Create a QLabel to display the current value
        self.value_label = QLabel(f"{self.label}: {initial_value}", self)
        self.value_label.setAlignment(Qt.AlignCenter)

        # Add layouts and widgets to the main layout
        main_layout.addLayout(slider_layout)
        main_layout.addWidget(self.value_label)

        # Set the layout for this widget
        self.setLayout(main_layout)

        # Connect the slider value change signal to a method
        self.slider.valueChanged.connect(self.handle_value_change)

    def handle_value_change(self, value):
        # Update the value label
        self.value_label.setText(f"{self.label}: {value}")
        # Emit the custom signal with the new value
        self.value_changed.emit(value)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # Create a central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create the main layout
        main_layout = QHBoxLayout()
        image_layout = QVBoxLayout()
        control_layout = QVBoxLayout()

        self.img_path, _ = QFileDialog.getOpenFileName(self, 'Select Image', "",
                                               "Images (*.png *.jpg *.jpeg *.gif)")

        print(f"self.img_path is {self.img_path}")

        self.image_canvas = MatplotlibCanvas(self.img_path)  # Replace with your PNG

        self.image_canvas2 = MatplotlibCanvas(self.img_path)

        self.input_img = cv2.imread(self.img_path)
        self.masked_image_rgb = cv2.cvtColor(self.input_img, cv2.COLOR_BGR2RGB)

        group_box0 = QGroupBox("Convert")
        group_layout0= QVBoxLayout()
        # creating a combo box widget
        self.cb_color_space = QComboBox()
        # # setting geometry of combo box
        # cb_color_space.setGeometry(200, 150, 120, 40)
        # adding items to combo box
        for color_space in valid_color_spaces:
            # if color_space.startswith("COLOR_BGR"):
            self.cb_color_space.addItem(color_space[6:])
        group_layout0.addWidget(self.cb_color_space)
        group_box0.setLayout(group_layout0)

        group_box4 = QGroupBox("Inverse Convert")
        group_layout4 = QVBoxLayout()
        # creating a combo box widget
        self.cb_color_space_inv = QComboBox()
        # # setting geometry of combo box
        # cb_color_space.setGeometry(200, 150, 120, 40)
        # adding items to combo box
        for color_space in valid_color_spaces:
            # if color_space.find("BGR") >= 0:
            self.cb_color_space_inv.addItem(color_space[6:])
        group_layout4.addWidget(self.cb_color_space_inv)
        group_box4.setLayout(group_layout4)

        # Create a QGroupBox to group the sliders
        group_box1 = QGroupBox("Channel 1")
        group_layout1 = QVBoxLayout()
        # Add two SliderExample widgets to the group box
        self.slider1 = CustomSlider('min', 0, 255, 0)
        self.slider2 = CustomSlider('max', 0, 255, 255)
        group_layout1.addWidget(self.slider1)
        group_layout1.addWidget(self.slider2)
        group_box1.setLayout(group_layout1)

        # Create a QGroupBox to group the sliders
        group_box2 = QGroupBox("Channel 2")
        group_layout2 = QVBoxLayout()
        # Add two SliderExample widgets to the group box
        self.slider3 = CustomSlider('min', 0, 255, 0)
        self.slider4 = CustomSlider('max', 0, 255, 255)
        group_layout2.addWidget(self.slider3)
        group_layout2.addWidget(self.slider4)
        group_box2.setLayout(group_layout2)

        # Create a QGroupBox to group the sliders
        group_box3 = QGroupBox("Channel 3")
        group_layout3 = QVBoxLayout()
        # Add two SliderExample widgets to the group box
        self.slider5 = CustomSlider('min', 0, 255, 0)
        self.slider6 = CustomSlider('max', 0, 255, 255)
        group_layout3.addWidget(self.slider5)
        group_layout3.addWidget(self.slider6)
        group_box3.setLayout(group_layout3)

        self.save_btn = QPushButton("Save Masked Image")
        self.save_btn.clicked.connect(self.on_save_image)

        control_layout.addWidget(self.cb_color_space)
        control_layout.addWidget(self.cb_color_space_inv)
        control_layout.addWidget(group_box1)
        control_layout.addWidget(group_box2)
        control_layout.addWidget(group_box3)
        control_layout.addWidget(self.save_btn)

        # Add the image and group box to the main layout
        image_layout.addWidget(self.image_canvas)
        image_layout.addWidget(self.image_canvas2)
        # main_layout.addWidget(image_canvas)
        # main_layout.addWidget(image_canvas2)
        main_layout.addLayout(image_layout, 4)
        main_layout.addLayout(control_layout, 1)

        # Set the layout for the central widget
        central_widget.setLayout(main_layout)

        # Connect the custom signals to slots in QMainWindow
        self.slider1.value_changed.connect(self.on_slider1_value_changed)
        self.slider2.value_changed.connect(self.on_slider2_value_changed)
        self.slider3.value_changed.connect(self.on_slider3_value_changed)
        self.slider4.value_changed.connect(self.on_slider4_value_changed)
        self.slider5.value_changed.connect(self.on_slider5_value_changed)
        self.slider6.value_changed.connect(self.on_slider6_value_changed)
        self.cb_color_space.currentIndexChanged.connect(self.on_colorspace_changed)

        # Set the main window properties
        self.setWindowTitle("PyQt5 Sliders with Matplotlib Image")
        self.resize(600, 300)
        # self.timer = QTimer(self)
        # self.timer.timeout.connect(self.update_label)
        # self.timer.start(1000)  # 1000 milliseconds = 1 second

        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.setInterval(2000)
        self.timer.timeout.connect(self.filter_image)

    # def get_image_file(self):
    #     dialog = QFileDialog(self)
    #     # dialog.setDirectory() #Can be used to customize working directory
    #     dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
    #     dialog.setNameFilter("Images (*.png *.jpg *.jpeg *.gif)")
    #     # dialog.setViewMode(QFileDialog.ViewMode.List)
    #
    #     if dialog.exec():
    #         filenames = dialog.selectedFiles()
    #         return filenames
    #         # if filenames:
    #         #     self.file_list.addItems([str(Path(filename)) for filename in filenames])
    #

    def resetTimer(self):
        # if self.timer.isActive():
        #     self.label.setText('reset')
        # else:
        #     self.label.setText('restarted')
        # start() will always restart the timer, no matter if it was active
        # or not, and will use the previously set interval (set with
        # setInterval() or the last start() call
        self.timer.start()

    def on_colorspace_changed(self, idx):
        print(f"combobox index changed to {idx}.")
        print(f"combobox text should be {valid_color_spaces[idx][6:]}")
        new_color_space = valid_color_spaces[idx]
        components = new_color_space.split("_")
        origin, convert = components[1].split("2")
        print(origin, convert)
        invert_color_conv = f"{components[0]}_{convert}2RGB"
        if len(components) == 3:
            invert_color_conv += f"_{components[2]}"
        print(invert_color_conv)

        if invert_color_conv in valid_color_spaces:
            print(f"inverted color conversion is: {invert_color_conv}")
            idx = valid_color_spaces.index(invert_color_conv)
            print(idx)
            self.cb_color_space_inv.setCurrentIndex(idx)
            # input("stop here...")
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)

            # setting message for Message Box
            msg.setText("Manually select inverse color conversion for "
                        "correctly display the filtered image.")

            # setting Message box window title
            msg.setWindowTitle("Warning MessageBox")

            # declaring buttons on Message Box
            msg.setStandardButtons(QMessageBox.Ok)

            # start the app
            retval = msg.exec_()

        # self.timer.start()

    def on_slider1_value_changed(self, value):
        print(f"Slider 1 Value Changed: {value}")
        self.timer.start()

    def on_slider2_value_changed(self, value):
        print(f"Slider 2 Value Changed: {value}")
        self.timer.start()

    def on_slider3_value_changed(self, value):
        print(f"Slider 3 Value Changed: {value}")
        self.timer.start()

    def on_slider4_value_changed(self, value):
        print(f"Slider 4 Value Changed: {value}")
        self.timer.start()

    def on_slider5_value_changed(self, value):
        print(f"Slider 5 Value Changed: {value}")
        self.timer.start()

    def on_slider6_value_changed(self, value):
        print(f"Slider 6 Value Changed: {value}")
        self.timer.start()

    def filter_image(self):
        lower_b = array([self.slider1.slider.value(),
                         self.slider3.slider.value(),
                         self.slider5.slider.value()])
        upper_b = array([self.slider2.slider.value(),
                         self.slider4.slider.value(),
                         self.slider6.slider.value()])

        print(lower_b)
        print(upper_b)
        new_color_space = valid_color_spaces[self.cb_color_space.currentIndex()]
        print("color conversion", new_color_space)
        src2dest_color_conv = getattr(cv2, new_color_space)
        converted_img = cv2.cvtColor(self.input_img, cv2.COLOR_BGR2HSV)

        mask = cv2.inRange(converted_img, lower_b, upper_b)

        # if remove_noise:
        #     # Apply morphological transformations to remove noise
        kernel = ones((5, 5), uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

        # Apply the hsv_mask to the original image
        processed_converted = cv2.bitwise_and(converted_img, converted_img,
                                              mask=mask)
        inv_color_space_conv = "COLOR_" + self.cb_color_space_inv.currentText()
        print(f"inverse color conversion: {inv_color_space_conv}")
        masked_color_conv = getattr(cv2, inv_color_space_conv)
        # masked_image_bgr = cv2.cvtColor(masked_converted,
        #                                   masked_color_conv)
        # cv2.imwrite("test.png", masked_image_bgr)

        self.masked_image_rgb = cv2.cvtColor(processed_converted,
                                           masked_color_conv)

        self.image_canvas2.plot_np_array(self.masked_image_rgb)

        self.timer.stop()

    def on_save_image(self):
        folder, fullfilename = os.path.split(self.img_path)
        name, extension = os.path.splitext(fullfilename)
        suggested_name = os.path.join(folder, f"{name}_processed{extension}")
        save_path, _ = QFileDialog.getSaveFileName(self, 'Save Image',
                                                   suggested_name, "")
        if save_path == suggested_name:
            pass
        else:
            save_path += extension
        cv2.imwrite(save_path, cv2.cvtColor(self.masked_image_rgb, cv2.COLOR_RGB2BGR))



if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
