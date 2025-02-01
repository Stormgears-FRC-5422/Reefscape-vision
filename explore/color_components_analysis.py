import sys
import numpy as np
import inspect
import cv2
import os
import time

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QRadioButton, QScrollArea,
    QButtonGroup, QGridLayout, QLabel, QGroupBox, QFileDialog)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

valid_color_spaces = \
    ['COLOR_BGR2BGR555',
     'COLOR_BGR2BGR565',
     'COLOR_BGR2BGRA',
     # 'COLOR_BGR2GRAY',
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


class ScrollableWindow(QWidget):
    def __init__(self, ):
        super().__init__()
        self.setWindowTitle("Grid Layout with Scrollbar")
        self.setGeometry(0, 0, 1900, 1000)
        # Create a grid layout
        grid_layout = QGridLayout()

        # Create a scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        # Create a widget to hold the grid
        grid_widget = QWidget()
        grid_widget.setLayout(grid_layout)

        img_file, _ = QFileDialog.getOpenFileName(self, 'Select Image', "",
                                                  "Images (*.png *.jpg *.jpeg *.gif)")

        input_img = cv2.imread(img_file)
        print(input_img.shape)

        for j in range(input_img.shape[2]):  # 3 subplots in each row
            cell_layout = self.create_cell_layout(input_img, 0, j, "Input")
            grid_layout.addLayout(cell_layout, 0, j)

        # Loop to create subplots and RadioButtons for each row
        page_start = 0
        for i in range(len(valid_color_spaces)):
            # Create a horizontal layout to hold the 3 plots and RadioButtons
            row_layout = QHBoxLayout()
            color_space = valid_color_spaces[i]
            print(color_space)
            src2dest_color_conv = getattr(cv2, valid_color_spaces[i])
            converted_img = cv2.cvtColor(input_img, src2dest_color_conv)
            print(converted_img.shape)
            # if len(converted_img.shape) in [3,4]:
            if len(converted_img.shape) <= 2:
                pass
            else:
                for j in range(converted_img.shape[2]):  # 3 subplots in each row
                    cell_layout = self.create_cell_layout(converted_img, i,
                                                          j, color_space[6:])
                    grid_layout.addLayout(cell_layout, i+1, j)

        # Set the grid widget as the scroll area's widget
        scroll_area.setWidget(grid_widget)
        # Set the scroll area as the main layout
        self.setLayout(QGridLayout())
        self.layout().addWidget(scroll_area)

    # Callback function for radio button selection
    def radio_selected(self, checked, value, subplot_index):
        if checked:
            print(
                f"RadioButton {value} selected for subplot row {subplot_index}")

    def create_cell_layout(self, img, row, col, color_space):
        fig = Figure()
        canvas = FigureCanvas(fig)
        fig.clear()
        ax = fig.add_subplot(111)  # 1 row, 1 column, subplot 1

        ax.imshow(img[:, :, col], cmap='afmhot') #cmap='viridis'
        fig.tight_layout()
        canvas.draw()

        # Button group to manage radio buttons
        choice_layout = QGridLayout()
        choice_group_box = QGroupBox(color_space)
        # choice_group_box = QGroupBox("GroupBox Example")
        choice_group_box.setCheckable(False)

        # Create and add three RadioButtons for each row
        # Create a vertical layout for the RadioButtons
        radio_group_layout = QVBoxLayout()
        choice_group_box.setLayout(radio_group_layout)
        button_group = QButtonGroup(self)
        # radio_group_layout.addWidget(QLabel(valid_color_spaces[i]))
        for k, label in enumerate(["+1",
                                   "0",
                                   "-1"]):
            radio_btn = QRadioButton(label)
            radio_btn.setMinimumHeight(120)
            button_group.addButton(radio_btn)
            radio_btn.toggled.connect(
                lambda checked, val=f"Option {k + 1}",
                       idx=row: self.radio_selected(
                    checked, val, idx))
            if k == 1:
                radio_btn.setChecked(True)
            else:
                radio_btn.setChecked(False)
            radio_group_layout.addWidget(radio_btn)

        # Add the RadioButtons layout to the right side of the row
        cell_layout = QHBoxLayout()
        cell_layout.addWidget(canvas)
        cell_layout.addWidget(choice_group_box)

        return cell_layout


def get_all_inspect_functions():
    inspect_all_types = []
    for name in dir(inspect):
        component = getattr(inspect, name)
        if inspect.isfunction(component):
            if name.startswith("is"):
                print(f"Function: {name}")
                inspect_all_types.append(name)
    return inspect_all_types


def get_all_opencv_components(inspect_object_types):
    color_spaces = []
    for name in dir(cv2):
        component = getattr(cv2, name)
        found_type = False
        for inspect_type in inspect_object_types:
            if eval("inspect."+inspect_type)(component):
                print(f"{inspect_type}: {name}")
                found_type = True
                break
        if not found_type:
            print(f"Other: {name}")

        if name.startswith("COLOR_"):
            color_spaces.append(name)

    print("\n\n\n\nThe following are color spaces")
    print(color_spaces)
    return color_spaces

def get_img_color_spaces_conv(img_file):
    input_img = cv2.imread(img_file)
    inspect_object_types = get_all_inspect_functions()
    all_color_spaces = get_all_opencv_components(inspect_object_types)

    valid_color_space = []
    for color_space in all_color_spaces:
        src2dest_color_conv = getattr(cv2, color_space)
        try:
            new_img = cv2.cvtColor(input_img, src2dest_color_conv)
            valid_color_space.append(color_space)
            print(f"Color space image generated.")
        except Exception as e:
            # Handle any exception
            print("An error occurred:", e)
        print("sleep 1 sec.")
        time.sleep(1)
    print("\n\n\n\nValid color spaces are: ")
    print(valid_color_space)
    return valid_color_space


if __name__ == '__main__':
    # img_file = os.path.join(r"C:\Users\ryany\Pictures\temp5",
    #                         "original_001.png")
    # img_file = os.path.join(r"C:\Users\ryany\Downloads\2025ReefScape",
    #                         "2025 Kickoff - reef.png")
    #
    app = QApplication(sys.argv)
    window = ScrollableWindow()
    window.show()
    sys.exit(app.exec_())
