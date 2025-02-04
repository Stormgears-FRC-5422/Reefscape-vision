import os
import cv2
from numpy import copy, array, uint8, ones, zeros, uint16, around, pi
import random as rng
import matplotlib.pyplot as plt

from explore.plot_image import plot_img, disp_value
from explore import globals


def filter_algae2(image):
    """
    Filters an image by setting pixels to dark where the red channel value is less than the blue channel value.

    Parameters:
        image (numpy.ndarray): Input image as a NumPy array (H x W x 3 for RGB).

    Returns:
        numpy.ndarray: Processed image with filtered pixels.
    """
    IMAGE_ONLY = globals.IMAGE_ONLY
    DEBUG = globals.DEBUG

    # Ensure the image is in the correct format (H x W x 3)
    assert image.ndim == 3 and image.shape[2] == 3, "Input image must be an HxWx3 array for RGB."

    # image = cv2.blur(image, (11, 11))

    # Convert the image to HSV color space
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Define the range for cyan color in HSV
    lower_cyan = array([53, 78, 0])  # Adjust based on testing
    upper_cyan = array([130, 255, 255])  # Adjust based on testing

    # Create a binary mask for cyan color
    hsv_mask = cv2.inRange(hsv, lower_cyan, upper_cyan)

    # Convert the image using LRGB2LAB
    # TODO convert cv2.COLOR_LRGB2LAB, and choose channel 1 with value 100 - 110
    lrgb2lab = cv2.cvtColor(image, cv2.COLOR_LRGB2LAB)

    # Define the range for cyan color in HSV
    lower_lrgb2lab = array([0, 100, 0])  # Adjust based on testing
    upper_lrgb2lab = array([255, 120, 255])  # Adjust based on testing

    # Create a binary mask for cyan color
    lrgb2lab_mask = cv2.inRange(lrgb2lab, lower_lrgb2lab, upper_lrgb2lab)

    combined_mask = cv2.bitwise_and(hsv_mask, lrgb2lab_mask)

    # Apply morphological operations to refine the mask
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, kernel)
    combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_OPEN, kernel)

    masked_image = cv2.bitwise_and(image, image,
                                   mask=combined_mask)

    if DEBUG:
        threshold = 30
        gray = cv2.cvtColor(masked_image, cv2.COLOR_BGR2GRAY)

        # canny_output = cv2.Canny(gray, threshold, 255)
        #
        # # Find contours with hierarchy information
        # contours, hierarchy = cv2.findContours(canny_output, cv2.RETR_TREE,
        #                                        cv2.CHAIN_APPROX_NONE)

        thresh = cv2.adaptiveThreshold(gray, threshold, cv2.ADAPTIVE_THRESH_MEAN_C,
                                       cv2.THRESH_BINARY, 11, 2)

        # Find contours
        contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL,
                                               cv2.CHAIN_APPROX_SIMPLE)

        print(f"there are {len(contours)} contours")
        drawing = zeros((gray.shape[0], gray.shape[1], 3),
                           dtype=uint8)

        for i, c in enumerate(contours):
            area = cv2.contourArea(c)
            if area > 3000:
                color = (rng.randint(0, 256), rng.randint(0, 256), rng.randint(0, 256))
                # contour
                cv2.drawContours(drawing, contours, i, color, thickness=-1)


        fig1, axes1 = plot_img(image, 'Original Image')
        fig2, axes2 = plot_img(masked_image, 'masked image')
        fig3, axes3 = plot_img(combined_mask, 'combined mask')
        fig4, axes4 = plot_img(drawing, 'contours')
        fig1.canvas.manager.window.setGeometry(0, 0, 800, 480)
        fig2.canvas.manager.window.setGeometry(960, 0, 800, 480)
        fig3.canvas.manager.window.setGeometry(0, 480, 800, 480)
        fig4.canvas.manager.window.setGeometry(960, 480, 800, 480)
        plt.show(block=False)
        plt.pause(8)
        plt.close('all')


    # Detect contours in the mask
    contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL,
                                   cv2.CHAIN_APPROX_SIMPLE)

    # Iterate through contours and filter by circularity
    for c in contours:
        area = cv2.contourArea(c)
        if c.shape[0] > 5 and area > 3000: #old value was 4000
            # Calculate area and perimeter
            ellipse = cv2.fitEllipse(c)

            (x, y), (MA, ma), angle = ellipse
            if MA < ma:
                major_axis = ma
                minor_axis = MA
                angle += 90
            else:
                major_axis = MA
                minor_axis = ma

            # perimeter = cv2.arcLength(c, True)
            circularity = minor_axis / major_axis
            filling_ratio = 4 * area / (pi * minor_axis * major_axis)
            # interested = [(1553, 623), (1828, 645), (1537, 927), (1808, 953)]
            # Draw the ellipse on the
            if circularity > 0.9 and filling_ratio > 0.8: # Minimal area
                # criterion is at above
                cv2.ellipse(masked_image, ellipse, (0, 255, 255), 3)


            # perimeter = cv2.arcLength(contour, True)
            # if perimeter == 0:  # Avoid division by zero
            #     continue
            # circularity = 4 * pi * (area / (perimeter ** 2))
            #
            # # Filter contours based on circularity and size
            # if 0.5 < circularity < 1.5 and area > 4000:  # Adjust thresholds as
            #     # needed
            #     # Draw the contour and circle
            #     (x, y), radius = cv2.minEnclosingCircle(contour)
            #     center = (int(x), int(y))
            #     radius = int(radius)
            #
            #     cv2.circle(masked_image, center, radius, (0, 255, 255),
            #                5)  # Green circle
            #     if DEBUG:
            #         print(f"Circle. area = {area}, circularity={circularity}")
            # else:
            #     if DEBUG:
            #         print(f"Not a circle. area = {area}, circularity={circularity}")
            #     pass

    return masked_image

if __name__ == "__main__":
    IMAGE_ONLY = globals.IMAGE_ONLY
    DEBUG = globals.DEBUG
    if IMAGE_ONLY:
        directory_path = r'C:\_WorkingCopy\Reefscape-vision\tests\data'
        files = os.listdir(directory_path)

        for file in files:
            #
            # sample_image = r'2025 Kickoff - REEFSCAPE presented by Haas - ' \
            #                r'overview3.png'
            sample_image = os.path.join(directory_path, file)
            input_img = cv2.imread(sample_image)
            algae = filter_algae2(input_img)
            # coral = filter_coral(input_img)
            # combined_frame = combine_output(input_img, reef, algae, coral)
            # cv2.imshow('Combined', combined_frame)
            # cv2.imwrite("combined_output.png", combined_frame)
            # cv2.waitKey(0)
            # cv2.destroyAllWindows()
