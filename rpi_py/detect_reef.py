import os
import cv2
from numpy import copy, array, uint8, ones, zeros, uint16, around, pi, \
    radians, cos, sin
import random as rng
import matplotlib.pyplot as plt

from plot_image import plot_img, disp_value
import globals


def filter_reef(image):
    """
    Filters an image by setting pixels to dark where the red channel value is less than the blue channel value.

    Parameters:
        image (numpy.ndarray): Input image as a NumPy array (H x W x 3 for RGB).

    Returns:
        numpy.ndarray: Processed image with filtered pixels.
    """
    IMAGE_ONLY = globals.IMAGE_ONLY
    DEBUG = globals.DEBUG
    DEBUG1 = globals.DEBUG1

    # Ensure the image is in the correct format (H x W x 3)
    assert image.ndim == 3 and image.shape[2] == 3, "Input image must be an HxWx3 array for RGB."

    # image = cv2.blur(image, (11, 11))

    # Convert the image to HSV color space
    converted_img = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    # Define the range of color you want to filter (e.g., blue)
    lower_magenta = array([130, 50, 128])
    upper_magenta = array([160, 255, 255])
    lower_magenta = array([150, 120, 177])
    upper_magenta = array([165, 255, 255])
    lower_magenta = array([140, 120, 128])
    upper_magenta = array([165, 255, 255])

    hsv_mask = cv2.inRange(converted_img, lower_magenta, upper_magenta)

    lab2lrgb = cv2.cvtColor(image, cv2.COLOR_LAB2LRGB)
    lab2lrgb_mask = cv2.inRange(lab2lrgb[:, :, 1], (127), (255))

    combined_mask = cv2.bitwise_and(lab2lrgb_mask, hsv_mask)

    # Apply morphological operations to refine the mask
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, kernel)
    combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_OPEN, kernel)
    masked_image = cv2.bitwise_and(image, image,
                                   mask=combined_mask)

    if DEBUG1:
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
            if 1000 < area < 4000:
                color = (rng.randint(0, 256), rng.randint(0, 256), rng.randint(0, 256))
                # contour
                cv2.drawContours(drawing, contours, i, color, thickness=-1)


        fig1, axes1 = plot_img(image, 'Original Image')
        fig2, axes2 = plot_img(masked_image, 'masked image')
        fig3, axes3 = plot_img(combined_mask, 'combined mask')
        fig4, axes4 = plot_img(drawing, 'contours')
        fig1.canvas.manager.window.setGeometry(0, 0, 800, 400)
        fig2.canvas.manager.window.setGeometry(800, 0, 800, 400)
        fig3.canvas.manager.window.setGeometry(0, 400, 800, 400)
        fig4.canvas.manager.window.setGeometry(800, 400, 800, 400)
        plt.show(block=False)
        plt.pause(5)
        plt.close('all')


    # Detect contours in the mask
    contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL,
                                   cv2.CHAIN_APPROX_SIMPLE)

    for i, c in enumerate(contours):
        area = cv2.contourArea(c)
        # color = (
        #     rng.randint(0, 256), rng.randint(0, 256), rng.randint(0, 256))
        # # contour
        # cv2.drawContours(drawing, contours, i, color, thickness=2)

        if c.shape[0] > 5 and 100 < area < 1000:
            # (x, y), (MA, ma), angle = cv2.fitEllipse(c)
            # cv2.ellipse(drawing, minEllipse[i], color, 2)
            #
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
            if circularity > 0.7 and filling_ratio > 0.8:
                cv2.ellipse(masked_image, ellipse, (0, 255, 0), 4)

    if DEBUG:
        print(f"there are {len(contours)} contours")
        # drawing = zeros((image.shape[0], image.shape[1], 3),
        #                    dtype=uint8)
        drawing = masked_image

        inside = []
        outside = []
        unique_ellipses = []
        for i, c in enumerate(contours):
            area = cv2.contourArea(c)
            color = (
                rng.randint(0, 256), rng.randint(0, 256), rng.randint(0, 256))
            # contour
            cv2.drawContours(drawing, contours, i, color, thickness=2)

            if c.shape[0] > 5:
                # (x, y), (MA, ma), angle = cv2.fitEllipse(c)
                # cv2.ellipse(drawing, minEllipse[i], color, 2)
                #
                ellipse = cv2.fitEllipse(c)

                (x, y), (MA, ma), angle = ellipse
                if MA < ma:
                    major_axis = ma
                    minor_axis = MA
                    angle += 90
                else:
                    major_axis = MA
                    minor_axis = ma
                rounded_ellipse = [(round(x), round(y)), (round(major_axis),
                                           round(minor_axis)), round(angle)]
                if rounded_ellipse in unique_ellipses:
                    pass
                else:
                    unique_ellipses.append(rounded_ellipse)
                perimeter = cv2.arcLength(c, True)
                circularity = minor_axis / major_axis
                filling_ratio = 4 * area / (pi * minor_axis * major_axis)
                interested = [(1553, 623), (1828, 645), (1537, 927), (1808, 953)]
                for point in interested:
                    result = cv2.pointPolygonTest(c, point, False)
                    print(f"result={result}")
                    if result > 0:
                        print(f"In contour {c} point {point}.")
                        inside.append([ellipse, area, circularity, filling_ratio])
                    elif result < 0:
                        print(f"Not in contour {c} point {point}.")
                        outside.append(
                            [ellipse, area, circularity, filling_ratio])
                    elif result == 0:
                        print(f"On contour {c} point {point}.")


                # Draw the ellipse on the image
                cv2.ellipse(drawing, ellipse, (0, 255, 0), 3)

        print(f"There are {len(unique_ellipses)} unique ellipses.")
        print(unique_ellipses)
        print(f"Inside: {inside}")
        print(f"Outside: {outside}")
        disp_value(masked_image)

        # fig1, axes1 = plot_img(image, 'Original Image')
        fig2, axes2 = plot_img(masked_image, 'masked image')
        # fig3, axes3 = plot_img(combined_mask, 'combined mask')
        # fig4, axes4 = plot_img(drawing, 'contours')
        # fig1.canvas.manager.window.setGeometry(0, 0, 720, 400)
        # fig2.canvas.manager.window.setGeometry(760, 0, 720, 400)
        # fig3.canvas.manager.window.setGeometry(0, 400, 720, 400)
        # fig4.canvas.manager.window.setGeometry(760, 400, 720, 400)
        plt.show(block=False)
        plt.pause(15)
        plt.close('all')

    if DEBUG1:
        # Iterate through contours and filter by circularity
        for contour in contours:
            # Calculate area and perimeter
            area = cv2.contourArea(contour)
            perimeter = cv2.arcLength(contour, True)
            if perimeter == 0:  # Avoid division by zero
                continue
            circularity = 4 * pi * (area / (perimeter ** 2))

            # Filter contours based on circularity and size
            if 0.75 < circularity < 1.25 and 20 < area < 1000:  # Adjust
                # thresholds as
                # needed
                # Draw the contour and circle
                (x, y), radius = cv2.minEnclosingCircle(contour)
                center = (int(x), int(y))
                radius = int(radius)

                cv2.circle(masked_image, center, radius, (0, 255, 255),
                           5)  # Green circle
                if DEBUG:
                    print(f"Circle. area = {area}, circularity={circularity}")
            else:
                if DEBUG:
                    (x, y), radius = cv2.minEnclosingCircle(contour)
                    center = (int(x), int(y))
                    radius = int(radius)

                    cv2.circle(masked_image, center, radius, (0, 255, 0),
                               5)  # Green circle


                    print(f"Not a circle. area = {area}, circularity={circularity}")
                pass

    if DEBUG:
        fig1, axes1 = plot_img(image, 'Original Image')
        fig2, axes2 = plot_img(masked_image, 'masked image')
        # fig3, axes3 = plot_img(combined_mask, 'combined mask')
        # fig4, axes4 = plot_img(drawing, 'contours')
        fig1.canvas.manager.window.setGeometry(0, 0, 720, 400)
        fig2.canvas.manager.window.setGeometry(760, 0, 720, 400)
        # fig3.canvas.manager.window.setGeometry(0, 400, 720, 400)
        # fig4.canvas.manager.window.setGeometry(760, 400, 720, 400)
        plt.show(block=False)
        plt.pause(10)
        plt.close('all')

    return masked_image

def is_inside_ellipse(ellipse, point):
    """
    Check if a point is inside an ellipse.

    Args:
        ellipse (tuple): (x_center, y_center, major_axis, minor_axis, angle)
        point (tuple): (x, y)

    Returns:
        bool: True if inside, False otherwise
    """

    (x_center, y_center), (major_axis, minor_axis), angle = ellipse
    x, y = point

    angle_rad = radians(angle)

    term1 = ((x - x_center) * cos(angle_rad) + (y - y_center) * sin(angle_rad)) ** 2 / (major_axis / 2) ** 2
    term2 = ((x - x_center) * sin(angle_rad) - (y - y_center) * cos(angle_rad)) ** 2 / (minor_axis / 2) ** 2

    if term1 + term2 <= 1:
        inside = True
    else:
        inside = False
    return inside


def process_video(input_path, output_path):
    # Open the input video
    cap = cv2.VideoCapture(input_path)

    # Check if video opened successfully
    if not cap.isOpened():
        print("Error opening video file")
        return

    # Get video properties
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    combined_frame = zeros((height * 2, width * 2, 3), dtype=uint8)


    # Create a VideoWriter object to save the processed video
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Use 'mp4v' for MP4 output
    out = cv2.VideoWriter(output_path, fourcc, fps, (width * 2, height * 2))

    frame_num = 0
    while True:
        # Read a frame from the video
        print(f"Frame No.: {frame_num}")
        ret, input_frame = cap.read()

        if not ret:
            break  # End of video
        else:
            frame_num += 1

        # reef_frame = copy(frame)

        # Process the frame here (e.g., apply filters, transformations, etc.)
        # Example: Convert to grayscale
        # processed_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        reef_frame = filter_reef(input_frame)

        # Write the processed frame to the output video
        out.write(combined_frame)


if __name__ == "__main__":
    IMAGE_ONLY = globals.IMAGE_ONLY
    DEBUG = globals.DEBUG
    DEBUG1 = globals.DEBUG1


    input_video = r"C:\Users\ryany\Downloads\2025ReefScape\2025 Kickoff - REEFSCAPE presented by Haas - overview.mkv"

    if IMAGE_ONLY:
        directory_path = r'C:\_WorkingCopy\Reefscape-vision\tests\data'
        files = os.listdir(directory_path)

        for file in files:
            #
            # sample_image = r'2025 Kickoff - REEFSCAPE presented by Haas - ' \
            #                r'overview3.png'
            sample_image = os.path.join(directory_path, file)
            print(sample_image)
            input_img = cv2.imread(sample_image)
            reef = filter_reef(input_img)
            # fig1, axes1 = plot_img(reef, 'Reef Image')
            # fig2, axes2 = plot_img(masked_image, 'masked image')
            # fig3, axes3 = plot_img(combined_mask, 'combined mask')
            # fig4, axes4 = plot_img(drawing, 'contours')
            # fig1.canvas.manager.window.setGeometry(0, 0, 720, 400)
            # fig2.canvas.manager.window.setGeometry(720, 0, 720, 400)
            # fig3.canvas.manager.window.setGeometry(0, 400, 720, 400)
            # fig4.canvas.manager.window.setGeometry(720, 400, 720, 400)
            # plt.show(block=True)
            # plt.pause(8)
            # plt.close('all')
    else:
        output_video = "reef_video1.mp4"
        process_video(input_video, output_video)




        # coral = filter_coral(input_img)
        # combined_frame = combine_output(input_img, reef, algae, coral)
        # cv2.imshow('Combined', combined_frame)
        # cv2.imwrite("combined_output.png", combined_frame)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
