# import required libraries
import os
import math
import time

import cv2
import numpy as np
import copy

import matplotlib.pyplot as plt
# from matplotlib.backend_bases import MouseEvent

import random as rng

if os.name == 'nt':
    src_folder = r"C:\Users\ryany\Downloads\2025ReefScape"
    dest_folder = r"C:\Users\ryany\Pictures\temp4"
    IMAGE_PATH = r"C:\Users\ryany\Pictures\apriltags_lab"
    for folder in [src_folder, dest_folder, IMAGE_PATH]:
        if os.path.isdir(folder):
            pass
        else:
            os.mkdir(folder)
    LINUX = False
else:
    LINUX = True
    src_folder = r"/home/pi/Downloads/music_notes_img/"
    dest_folder = r"/home/pi/Downloads/music_notes_img_proc"
    IMAGE_PATH = r"/home/pi/Downloads/raw"
    for folder in [src_folder, dest_folder, IMAGE_PATH]:
        if os.path.isdir(folder):
            pass
        else:
            os.mkdir(folder)

    # preview_width = 800
    # preview_height = 600
    # bw = 160
    # bh = 34
    # ft = int(bh / 2.2)
    # fv = int(bh / 2.2)


rng.seed(12345)
PLOT_IMAGE = True
DEBUG = False
DETAILED_DEBUG = True
IMAGE_FILE = r".\images\original_640 x 360 @ 30_13.png"
# IMAGE_FILE = r"C:\Users\ryany\Downloads\note_detection_sample_images\move\original_160 x 90 @ 30_2.png"
# IMAGE_FILE = r"C:\Users\ryany\Downloads\note_detection_sample_images\move\original_320 x 180 @ 30_27.png"
MAX_H = 50
MIN_S = 200
MIN_WIDTH_RATIO = 0.03
MAX_WIDTH_RATIO = 0.5
MIN_HEIGHT_RATIO = 0.02
MAX_HEIGHT_RATIO = 0.5

# The camera is about 20 degree tilt down.

# the contour of an ellipse has more than following # of straightline edges.
CONTOUR_STRAIGHT_LINE_EDGES = 20

# function to display the coordinates of
# of the points clicked on the image
def click_event(event, x, y, flags, params):
    img_bkup = globals()['img']
    converted_img = globals()['converted_img']
    font = cv2.FONT_HERSHEY_SIMPLEX
    # checking for left mouse clicks
    if event == cv2.EVENT_MOUSEMOVE:
        # displaying the coordinates
        # on the Shell
        print(x, ' ', y)
        img = copy.deepcopy(img_bkup)
        # hls_bkup = copy.deepcopy(converted_img)
        # displaying the coordinates
        # on the image window

        # cv2.putText(img, str(x) + ',' +
        #             str(y), (x,y), font,
        #             1, (255, 0, 0), 2)
        # h = hls_bkup[y, x, 0]
        # l = hls_bkup[y, x, 1]
        # s = hls_bkup[y, x, 2]
        # display_str = "h=" + str(h) + ",l=" + str(l) + ",s=" + str(s)
        display_str = f"ch1={converted_img[y, x, 0]}, ch2=" \
                      f"{converted_img[y, x, 1]}, ch3={converted_img[y, x, 2]}"

        cv2.putText(img, display_str, (x,y), font,
                    1, (255, 255, 0), 2)

        cv2.imshow('Source', img)
        print(display_str)

    # checking for right mouse clicks
    if event==cv2.EVENT_RBUTTONDOWN:

        # displaying the coordinates
        # on the Shell
        print(x, ' ', y)

        # displaying the coordinates
        # on the image window
        font = cv2.FONT_HERSHEY_SIMPLEX
        b = img[y, x, 0]
        g = img[y, x, 1]
        r = img[y, x, 2]
        cv2.putText(img, str(b) + ',' +
                    str(g) + ',' + str(r),
                    (x,y), font, 1,
                    (255, 255, 0), 2)
        cv2.imshow('image', img)

# def thresh_callback(threshold):
#     # threshold = val
#     # global src_gray, masked_hls, masked_hls_bkup, converted_img
#
#     canny_output = cv2.Canny(src_gray, threshold, threshold * 1.5)
#
#     # contours, hierarchy = cv2.findContours(canny_output, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
#     contours, hierarchy = cv2.findContours(canny_output, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
#
#     masked_hls_bkup = copy.deepcopy(masked_hls)
#
#     cv2.drawContours(masked_hls, contours, -1, (0, 255, 0), 1)
#
#
#     # cv2.imshow('Contours', masked_hls)
#
#     # Find the rotated rectangles and ellipses for each contour
#     minRect = [None] * len(contours)
#     minEllipse = [None] * len(contours)
#     for i, c in enumerate(contours):
#         for attr in dir(c):
#             if attr.startswith("__"):
#                 pass
#             else:
#                 print("obj.%s = %r" % (attr, getattr(c, attr)))
#
#         minRect[i] = cv2.minAreaRect(c)
#         print(minRect[i])
#         # print("dir(c) is: ",dir(c))
#         print("c.shape is: ", c.shape)
#         print("minRect[i] is: ")
#         print(minRect[i])
#         print("minRect[i] end.")
#         if c.shape[0] > CONTOUR_STRAIGHT_LINE_EDGES:
#             minEllipse[i] = cv2.fitEllipse(c)
#
#         for i in range(len(c.real[:-1])):
#             print(c.real[i],c.real[i+1])
#             cv2.line(masked_hls_bkup, c.real[i][0], c.real[i + 1][0], (rng.randint(0, 256), rng.randint(0, 256), rng.randint(0, 256)), 1)
#     # cv2.namedWindow('Contours by line', cv2.WINDOW_NORMAL)
#     # cv2.imshow('Contours by line', masked_hls_bkup)
#
#     print(f"total number of ellipse is: {len(minEllipse)}.")
#     print(minEllipse)
#
#     for ellipse in minEllipse:
#         if ellipse:
#             (xc, yc), (d1, d2), angle = ellipse
#             print(f"xc={xc},yc={yc},d1={d1},d2={d2},angle={angle}")
#
#     # Draw contours + rotated rects + ellipses
#     drawing = np.zeros((canny_output.shape[0], canny_output.shape[1], 3), dtype=np.uint8)
#
#     for i, c in enumerate(contours):
#         # print(type(c))
#         # print(dir(c))
#         # if hierarchy[0][i][2] > 0 and hierarchy[0][i][3] < 0:
#         if True:
#             print(i,hierarchy[0][i])
#             parent_contour = i
#             color = (rng.randint(0, 256), rng.randint(0, 256), rng.randint(0, 256))
#             # contour
#             cv2.drawContours(drawing, contours, i, color)
#             # ellipse
#             if c.shape[0] > CONTOUR_STRAIGHT_LINE_EDGES:
#                 cv2.ellipse(drawing, minEllipse[i], color, 2)
#             # rotated rectangle
#             box = cv2.boxPoints(minRect[i])
#             box = np.intp(box)  # np.intp: Integer used for indexing (same as C ssize_t; normally either int32 or int64)
#             cv2.drawContours(drawing, [box], 0, color)
#             # break
#
#     for i, c in enumerate(contours):
#         if True:
#         # if hierarchy[0][i][3] == parent_contour:
#             color = (rng.randint(0, 256), rng.randint(0, 256), rng.randint(0, 256))
#             # contour
#             cv2.drawContours(drawing, contours, i, color)
#             # ellipse
#             if c.shape[0] > CONTOUR_STRAIGHT_LINE_EDGES:
#                 cv2.ellipse(drawing, minEllipse[i], color, 2)
#             # rotated rectangle
#             box = cv2.boxPoints(minRect[i])
#             box = np.intp(box)  # np.intp: Integer used for indexing (same as C ssize_t; normally either int32 or int64)
#             cv2.drawContours(drawing, [box], 0, color)
#
#     # cv2.namedWindow('Contours', cv2.WINDOW_NORMAL)
#     # cv2.imshow('Contours', drawing)


class BlittedCursor:
    """
    A cross-hair cursor using blitting for faster redraw.
    """
    def __init__(self, ax):
        self.ax = ax
        self.background = None
        self.horizontal_line = ax.axhline(color='k', lw=0.8, ls='--')
        self.vertical_line = ax.axvline(color='k', lw=0.8, ls='--')
        # text location in axes coordinates
        self.text = ax.text(0.72, 0.9, '', transform=ax.transAxes)
        self._creating_background = False
        ax.figure.canvas.mpl_connect('draw_event', self.on_draw)

    def on_draw(self, event):
        self.create_new_background()

    def set_cross_hair_visible(self, visible):
        need_redraw = self.horizontal_line.get_visible() != visible
        self.horizontal_line.set_visible(visible)
        self.vertical_line.set_visible(visible)
        self.text.set_visible(visible)
        return need_redraw

    def create_new_background(self):
        if self._creating_background:
            # discard calls triggered from within this function
            return
        self._creating_background = True
        self.set_cross_hair_visible(False)
        self.ax.figure.canvas.draw()
        self.background = self.ax.figure.canvas.copy_from_bbox(self.ax.bbox)
        self.set_cross_hair_visible(True)
        self._creating_background = False

    def on_mouse_move(self, event):
        if self.background is None:
            self.create_new_background()
        if not event.inaxes:
            need_redraw = self.set_cross_hair_visible(False)
            if need_redraw:
                self.ax.figure.canvas.restore_region(self.background)
                self.ax.figure.canvas.blit(self.ax.bbox)
        else:
            self.set_cross_hair_visible(True)
            # update the line positions
            x, y = event.xdata, event.ydata
            self.horizontal_line.set_ydata([y])
            self.vertical_line.set_xdata([x])
            self.text.set_text(f'x={x:1.2f}, y={y:1.2f}')

            self.ax.figure.canvas.restore_region(self.background)
            self.ax.draw_artist(self.horizontal_line)
            self.ax.draw_artist(self.vertical_line)
            self.ax.draw_artist(self.text)
            self.ax.figure.canvas.blit(self.ax.bbox)

# def apply_HLS_mask(img, h_mask_boundary=None, l_mask_boundary=None, s_mask_boundary=None):
#     # This function is about 1/4 slower than apply_HLS_mask2().
#     global hls_bkup
#     hls = cv2.cvtColor(img, cv2.COLOR_BGR2HLS)
#     hls_bkup = copy.deepcopy(hls)
#     assert (h_mask_boundary is not None) or (l_mask_boundary is not None) or (s_mask_boundary is not None), \
#             'h, l, or s hsv_mask cannot all be none.'
#
#     if h_mask_boundary:
#         # Threshold the HSV image to get only h channel < MAX_S.
#         lower_h = np.array([h_mask_boundary[0], 0, 0])
#         upper_h = np.array([h_mask_boundary[1], 255, 255])
#         # Create a hsv_mask.
#         h_mask = cv2.inRange(hls, lower_h, upper_h)
#
#     if l_mask_boundary:
#         # Threshold the HSV image to get only s channel > MAX_S.
#         lower_s = np.array([0, l_mask_boundary[0], 0])
#         upper_s = np.array([255, l_mask_boundary[1], 255])
#         # Create a hsv_mask
#         l_mask = cv2.inRange(hls, lower_s, upper_s)
#
#     if s_mask_boundary:
#         # Threshold the HSV image to get only s channel > MAX_S.
#         lower_s = np.array([0, 0, s_mask_boundary[0]])
#         upper_s = np.array([255, 255, s_mask_boundary[1]])
#         # Create a hsv_mask
#         s_mask = cv2.inRange(hls, lower_s, upper_s)
#
#     # Bitwise-AND hsv_mask and original image
#     masked_hls = copy.deepcopy(hls)
#     if h_mask_boundary:
#         masked_hls = cv2.bitwise_and(masked_hls, masked_hls, hsv_mask= h_mask)
#     if l_mask_boundary:
#         masked_hls = cv2.bitwise_and(masked_hls, masked_hls, hsv_mask= l_mask)
#     if s_mask_boundary:
#         masked_hls = cv2.bitwise_and(masked_hls, masked_hls, hsv_mask= s_mask)
#     return masked_hls
#
# def apply_HLS_mask2(img, h_mask_boundary=None, l_mask_boundary=None, s_mask_boundary=None):
#     # Convert BGR to HSV
#     global hls_bkup
#     hls = cv2.cvtColor(img, cv2.COLOR_BGR2HLS)
#     hls_bkup = copy.deepcopy(hls)
#     assert (h_mask_boundary is not None) or (l_mask_boundary is not None) or (s_mask_boundary is not None), \
#             'h, l, or s hsv_mask cannot all be none.'
#
#     if h_mask_boundary:
#         min_h = h_mask_boundary[0]
#         max_h = h_mask_boundary[1]
#     else:
#         min_h = 0
#         max_h = 255
#
#     if l_mask_boundary:
#         min_l = l_mask_boundary[0]
#         max_l = l_mask_boundary[1]
#     else:
#         min_l = 0
#         max_l = 255
#
#     if s_mask_boundary:
#         min_s = s_mask_boundary[0]
#         max_s = s_mask_boundary[1]
#     else:
#         min_s = 0
#         max_s = 255
#
#     hls_mask = cv2.inRange(hls, (min_h, min_l, min_s), (max_h, max_l, max_s))
#
#     # Bitwise-AND hsv_mask and original image
#     masked_hls = copy.deepcopy(hls)
#     masked_hls = cv2.bitwise_and(masked_hls, masked_hls, hsv_mask=hls_mask)
#
#     return masked_hls
#
# def find_all_music_notes(src_gray,threshold_min,threshold_max):
#     print("shape of src_gray: ",src_gray.shape)
#     img_width = src_gray.shape[1]
#     img_height = src_gray.shape[0]
#     min_width = MIN_WIDTH_RATIO * img_width
#     max_width = MAX_WIDTH_RATIO * img_width
#     min_height = MIN_HEIGHT_RATIO * img_height
#     max_height = MAX_HEIGHT_RATIO * img_height
#
#     canny_output = cv2.Canny(src_gray, threshold_min, threshold_max)
#     # contours, hierarchy = cv2.findContours(canny_output, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
#     contours, hierarchy = cv2.findContours(canny_output, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
#     if DEBUG:
#         print("hierarchy")
#         print(hierarchy)
#         print("contours")
#         print(type(contours))
#         print(contours)
#
#     if hierarchy is None:
#         assert len(contours) == 0, "contours should be a empty tuple."
#         return [], contours
#
#     all_ellipses = []
#     for idx, hierarchy_element in enumerate(hierarchy[0]):
#         if DEBUG:
#             print("hierarchy_element")
#             print(hierarchy_element)
#         note_candidacy = True
#         criterion = 0
#         while note_candidacy:
#             if criterion == 0:
#                 pass
#                 # if hierarchy_element[2] != -1:
#                 #     note_candidacy = False
#             elif criterion == 1:
#                 if contours[idx].shape[0] <= CONTOUR_STRAIGHT_LINE_EDGES:
#                     note_candidacy = False
#             elif criterion == 2:
#                 x, y, w, h = cv2.boundingRect(contours[idx])
#                 if h > w or w < min_width or w > max_width or\
#                         h < min_height or h > max_height:
#                     note_candidacy = False
#             else:
#                 break
#
#             criterion += 1
#
#             #TODO two notes overlap physically, two notes overlap in image.
#
#         if note_candidacy:
#             ellipse = cv2.fitEllipse(contours[idx])
#             # print("Multiple ellipses can be fit.", len(ellipse))
#             # print(ellipse)
#             if ellipse:
#                 (xc, yc), (d1, d2), angle = ellipse
#                 if math.isnan(d1) or math.isnan(d2):
#                     print("ellipse parameter error. throw away following:")
#                 else:
#                     all_ellipses.append(ellipse)
#                 print(f"xc={xc},yc={yc},d1={d1},d2={d2},angle={angle}")
#
#
#     unique_ellipse_idx = range(len(all_ellipses))
#
#     for i in range(len(all_ellipses)):
#         (xc_i, yc_i), (d1_i, d2_i), angle_i = all_ellipses[i]
#         if d1_i > d2_i:
#             major_axis_i = d1_i
#             minor_axis_i = d2_i
#         else:
#             major_axis_i = d2_i
#             minor_axis_i = d1_i
#             angle_i = angle_i - 90
#
#         for j in range(i+1,len(all_ellipses)):
#             (xc_j, yc_j), (d1_j, d2_j), angle_j = all_ellipses[j]
#
#             if abs(int(xc_i) - int(xc_j)) < min_width and \
#                 abs(int(yc_i) - int(yc_j)) < min_height:
#                 if d1_j > d2_j:
#                     major_axis_j = d1_j
#                     minor_axis_j = d2_j
#                 else:
#                     major_axis_j = d2_j
#                     minor_axis_j = d1_j
#                     angle_j = angle_j - 90
#
#                 if (abs(angle_i-angle_j) < 10 or abs(angle_i-angle_j) > 170) \
#                         and (major_axis_i - major_axis_j) < min_width and \
#                         (minor_axis_i - minor_axis_j) < min_height:
#                     # no_overlap_ellipse_idx.pop(j)
#                     unique_ellipse_idx = [x for x in
#                                               unique_ellipse_idx if x != i]
#                     print(f"Ellipses {i} and {j} are the same.")
#                     print(xc_i, xc_j)
#                     print(yc_i, yc_j)
#                     print(major_axis_i,major_axis_j)
#                     print(minor_axis_i, minor_axis_j)
#                     print(angle_i, angle_j)
#                     print(f"element {i} will be removed, "
#                           f"no_overlap_ellipse_idx is: ")
#                     print(unique_ellipse_idx)
#                     break
#                 else:
#                     print(f"Ellipses {i} and {j} are not the same."
#                           f"no_overlap_ellipse_idx is: ")
#                     print(unique_ellipse_idx)
#                     print(xc_i, xc_j)
#                     print(yc_i, yc_j)
#                     print(major_axis_i,major_axis_j)
#                     print(minor_axis_i, minor_axis_j)
#                     print(angle_i, angle_j)
#
#     unique_ellipses = []
#     for i in unique_ellipse_idx:
#         (xc_i, yc_i), (d1_i, d2_i), angle_i = all_ellipses[i]
#         if d1_i > d2_i:
#             major_axis_i = d1_i
#             minor_axis_i = d2_i
#         else:
#             major_axis_i = d2_i
#             minor_axis_i = d1_i
#             angle_i = angle_i - 90
#
#         unique_ellipses.append(((xc_i,yc_i),(major_axis_i,minor_axis_i),
#                 angle_i))
#     return unique_ellipses, contours


# def process_image(src,dest):
#     global src_gray, img, img_bkup, masked_hls, converted_img
#     assert os.path.isfile(src)
#     img = cv2.imread(src)
#     print("img.shape is: ", img.shape)
#     img_bkup = copy.deepcopy(img)
#
#     if DEBUG:
#         start = time.time()
#         for i in range(100):
#             masked_hls = apply_HLS_mask(img, h_mask_boundary=[0,MAX_H], s_mask_boundary=[MIN_S,255])
#         end = time.time()
#         print(f"Duration1 is {end-start}s.")
#         start = time.time()
#         for i in range(100):
#             masked_hls2 = apply_HLS_mask2(img, h_mask_boundary=[0,MAX_H], s_mask_boundary=[MIN_S,255])
#         end = time.time()
#         print(f"Duration2 is {end-start}s.")
#         assert (masked_hls == masked_hls2).all(), "masked raw are not the same."
#
#     masked_hls = apply_HLS_mask2(img, h_mask_boundary=[0, MAX_H], s_mask_boundary=[MIN_S, 255])
#
#     converted_img = cv2.cvtColor(masked_hls, cv2.COLOR_HLS2BGR)
#     print("converted_img.shape is: ", converted_img.shape)
#     dest1 = src.replace("original_", "converted_img_")
#     print("converted_img will be saved at: ", dest1)
#     # cv2.imwrite(dest1, converted_img)
#     # assert os.path.isfile(dest1)
#     converted_img_bkup = copy.deepcopy(converted_img)
#
#     if PLOT_IMAGE:
#         # display the original and masked image
#         source_window = 'Source'
#         cv2.namedWindow(source_window, cv2.WINDOW_NORMAL)
#         cv2.imshow(source_window, img)
#         cv2.setMouseCallback(source_window, click_event)
#
#         # masked_image_window = 'Masked Image - bgr'
#         # cv2.namedWindow(masked_image_window, cv2.WINDOW_NORMAL)
#         # cv2.imshow(masked_image_window,converted_img)
#
#     src_gray = cv2.cvtColor(converted_img, cv2.COLOR_BGR2GRAY)
#
#     src_gray = cv2.blur(src_gray, (3, 3))
#     max_thresh = 255
#     thresh = 100  # initial threshold
#     all_ellipses, contours = find_all_music_notes(src_gray, thresh, max_thresh)
#
#     drawing = np.zeros((img.shape[0], img.shape[1] * 4, 3),
#                        dtype=np.uint8)
#
#     drawing[:, img.shape[1]*0:img.shape[1]*1, :] = img[:, :, :]
#     drawing[:, 3*img.shape[1]:4*img.shape[1], :] = converted_img_bkup[:, :, :]
#
#     if (len(all_ellipses) > 0):
#         print(f"Following {len(all_ellipses)} unique ellipses were found.")
#         print(all_ellipses)
#         for ellipse in all_ellipses:
#             color = (
#             rng.randint(0, 256), rng.randint(0, 256), rng.randint(0, 256))
#             drawing_m = drawing[:, 1*img.shape[1]:2*img.shape[1], :]
#             print(ellipse)
#             ellipse_drawing = cv2.ellipse(drawing_m, ellipse, color, 1)
#             # drawing_r[:, img.shape[1]:, :] = ellipse_drawing[:,:,:]
#             cv2.line(drawing, (2 * img.shape[1], 0),
#                      (2 * img.shape[1], img.shape[0]),
#                      (0, 255, 0), 1)
#     else:
#         print("No ellipse were found.")
#         cv2.line(drawing, (2 * img.shape[1], 0),
#                  (2 * img.shape[1], img.shape[0]),
#                  (0, 0, 255), 1)
#
#     for i, c in enumerate(contours):
#         color = (rng.randint(0, 256), rng.randint(0, 256), rng.randint(0, 256))
#         # contour
#         drawing_r = drawing[:, 2*img.shape[1]:3*img.shape[1], :]
#         cv2.drawContours(drawing_r, contours, i, color)
#
#     cv2.imwrite(dest,drawing)
#
#     # if PLOT_IMAGE:
#     #     cv2.waitKey(0)
#     #     cv2.destroyAllWindows()
#
#     val = {}
#     val['threshold'] = thresh
#     val['src_gray'] = src_gray
#     val['masked_hls'] = masked_hls
#
#     # cv2.createTrackbar('Canny Thresh:', source_window, thresh, max_thresh, thresh_callback)
#     # thresh_callback(thresh)
#     # cv2.waitKey()
#
#     x = np.arange(0, 1, 0.01)
#     y = np.sin(2 * 2 * np.pi * x)
#
#
#     # # displaying the image
#     # cv2.imshow('image', img)
#     # cv2.setMouseCallback('image', click_event)
#     # # wait for a key to be pressed to exit
#     cv2.waitKey(0)
#
#     # close the window
#     cv2.destroyAllWindows()
#
#
#     fig, ax = plt.subplots()
#     ax.set_title('Blitted cursor')
#     ax.imshow(img)
#     blitted_cursor = BlittedCursor(ax)
#     fig.canvas.mpl_connect('motion_notify_event', blitted_cursor.on_mouse_move)
#     plt.show()


def display_color(src, dest, new_color_space=cv2.COLOR_BGR2HSV):
    global src_gray, img, converted_img
    assert os.path.isfile(src)
    print(new_color_space.__str__())
    img = cv2.imread(src)
    print("img.shape is: ", img.shape)
    # img_bkup = copy.deepcopy(img)

    converted_img = cv2.cvtColor(img, new_color_space)

    # display the original and masked image
    source_window = 'Source'
    cv2.namedWindow(source_window, cv2.WINDOW_NORMAL)
    cv2.imshow(source_window, img)
    cv2.setMouseCallback(source_window, click_event)

    # # wait for a key to be pressed to exit
    cv2.waitKey(0)

    # close the window
    cv2.destroyAllWindows()


    fig, ax = plt.subplots()
    ax.set_title('Blitted cursor')
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    ax.imshow(img_rgb)
    blitted_cursor = BlittedCursor(ax)
    fig.canvas.mpl_connect('motion_notify_event', blitted_cursor.on_mouse_move)
    plt.show()


def main():
    print(f"src_folder is {src_folder}")
    for root, dirs, files in os.walk(src_folder):
        for file in files:
            if file.endswith(".png"):
                src = os.path.join(root, file)
                name, extension = os.path.splitext(file)
                dest = os.path.join(dest_folder, name.replace("original_","processed_")
                                    + ".png")
                # process_image(src,dest)


if __name__ == '__main__':
    if DETAILED_DEBUG:
        # input = os.path.join(src_folder, "2025 REEFSCAPE Kickoff - overview - bright background.png")
        input = r"..\tests\data\2025 Kickoff - REEFSCAPE presented by Haas - " \
                r"overview - reef0.png"
        # input = r"2025 Kickoff - REEFSCAPE presented by Haas - overview6_cyan.png"
        dest = os.path.join(src_folder, "processed_2025 Kickoff - reef.png")
        print(input)
        # process_image(input, dest)
        display_color(input, dest, new_color_space=cv2.COLOR_LRGB2LAB)
    else:
        main()


