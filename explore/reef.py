import cv2
from numpy import copy, array, uint8, ones, zeros, uint16, around, pi
import random as rng

import matplotlib.pyplot as plt

from plot_image import plot_img
from detect_algae import filter_algae2
from detect_reef import filter_reef
import globals

def filter_coral(image):
    """
    Filters an image by setting pixels to dark where the red channel value is less than the blue channel value.

    Parameters:
        image (numpy.ndarray): Input image as a NumPy array (H x W x 3 for RGB).

    Returns:
        numpy.ndarray: Processed image with filtered pixels.
    """
    # Ensure the image is in the correct format (H x W x 3)
    assert image.ndim == 3 and image.shape[2] == 3, "Input image must be an HxWx3 array for RGB."

    processed_img = copy(image)

    img_HLS = cv2.cvtColor(image, cv2.COLOR_BGR2HSV_FULL)

    """
    Purple has a hue angle of 276.9 degrees, a saturation of 87.4% and a lightness of 53.3%.
    """

    # Create a hsv_mask where red channel is less than blue channel
    mask_bg1 = processed_img[:, :, 0] * 0.85 > processed_img[:, :, 1]
    mask_bg2 = processed_img[:, :, 1] * 0.85 > processed_img[:, :, 0]
    mask_gr1 = processed_img[:, :, 1] * 0.85 > processed_img[:, :, 2]
    mask_gr2 = processed_img[:, :, 2] * 0.85 > processed_img[:, :, 1]
    mask_rb1 = processed_img[:, :, 2] * 0.85 > processed_img[:, :, 0]
    mask_rb2 = processed_img[:, :, 0] * 0.85 > processed_img[:, :, 2]

    # and image[:, :, 1] * 0.6 < \
    #     image[:, :, 0]

    # Set those pixels to dark (e.g., [0, 0, 0])
    processed_img[mask_bg1] = [0, 0, 0]
    processed_img[mask_bg2] = [0, 0, 0]
    processed_img[mask_gr1] = [0, 0, 0]
    processed_img[mask_gr2] = [0, 0, 0]
    processed_img[mask_rb1] = [0, 0, 0]
    processed_img[mask_rb2] = [0, 0, 0]

    return processed_img


def filter_img(image, lower_b, upper_b, remove_noise=True,
               color_space=cv2.COLOR_BGR2HSV):
    # Convert to HSV color space for better color segmentation
    hsv = cv2.cvtColor(image, color_space)

    # Create a hsv_mask for the purple color
    mask = cv2.inRange(hsv, lower_b, upper_b)

    if remove_noise:
        # Apply morphological transformations to remove noise
        kernel = ones((5, 5), uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    # Apply the hsv_mask to the original image
    processed_img = cv2.bitwise_and(image, image, mask=mask)

    return processed_img


def filter_video(video_file):
    # Create a VideoCapture object
    cap = cv2.VideoCapture(video_file)

    # Check if the video opened successfully
    if not cap.isOpened():
        print("Error opening video file")

    # Read and display frames until the end of the video
    while cap.isOpened():
        # Read a frame from the video
        ret, frame = cap.read()

        # If the frame was successfully read
        if ret:
            # Display the frame
            cv2.imshow("Frame", frame)

            # Wait for a key press (25ms delay)
            if cv2.waitKey(25) & 0xFF == ord('q'):
                break
        else:
            # Break the loop if the end of the video is reached
            break

    # Release the VideoCapture object
    cap.release()

    # Close all OpenCV windows
    cv2.destroyAllWindows()

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
        reef_frame = filter_reef(input_frame)
        algae_frame = filter_algae2(input_frame)
        coral_frame = filter_coral(input_frame)

        # Process the frame here (e.g., apply filters, transformations, etc.)
        # Example: Convert to grayscale
        # processed_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Write the processed frame to the output video

        # combined_frame = hstack((frame, reef_frame))
        combined_frame = combine_output(input_frame, reef_frame, algae_frame,
                                  coral_frame)
        combined_frame[0:height, 0:width, :] = input_frame
        combined_frame[0:height, width:width*2, :] = reef_frame
        combined_frame[height:height*2, 0:width, :] = algae_frame
        combined_frame[height:height*2, width:width*2, :] = coral_frame
        out.write(combined_frame)

        # # Display the frame (optional)
        # cv2.imshow('Frame', combined_frame)
        # if cv2.waitKey(1) == ord('q'):
        #     break

    # Release resources
    cap.release()
    out.release()
    cv2.destroyAllWindows()

def combine_output(input_frame, reef_frame, algae_frame,
                                  coral_frame):
    combined_frame = cv2.hconcat([input_frame, reef_frame, algae_frame,
                                  coral_frame])
    top_combined_frame = cv2.hconcat([input_frame, reef_frame])
    bottom_combined_frame = cv2.hconcat([algae_frame, coral_frame])
    combined_frame = cv2.vconcat([top_combined_frame, bottom_combined_frame])
    return combined_frame


if __name__ == "__main__":
    IMAGE_ONLY = globals.IMAGE_ONLY
    DEBUG = globals.DEBUG
    DEBUG1 = globals.DEBUG1

    # Load the image
    # image = cv2.imread(r'C:\Users\ryany\Downloads\2025ReefScape\2025 Kickoff - reef.png')
    # sample_image = r'C:\Users\ryany\Downloads\2025ReefScape\2025 REEFSCAPE_reef_bright_bkgd2.png'
    sample_image = r'2025 Kickoff - REEFSCAPE presented by Haas - overview3.png'
    # input_video = r"C:\Users\ryany\Downloads\2025ReefScape\2025 Kickoff - " \
    #                   r"REEFSCAPE presented by Haas - reef.mkv"
    # input_video = r"C:\Users\ryany\Downloads\2025ReefScape\2025 Kickoff - " \
    #                   r"REEFSCAPE presented by Haas - reef.mkv"
    input_video = r"C:\Users\ryany\Downloads\2025ReefScape\2025 Kickoff - REEFSCAPE presented by Haas - overview.mkv"
    rng.seed(35657)

    if IMAGE_ONLY:
        input_img = cv2.imread(sample_image)
        reef = filter_reef(input_img)
        algae = filter_algae2(input_img)
        coral = filter_coral(input_img)
        fig1, axes1 = plot_img(reef, 'Reef Image')
        # fig2, axes2 = plot_img(masked_image, 'masked image')
        # fig3, axes3 = plot_img(combined_mask, 'combined mask')
        # fig4, axes4 = plot_img(drawing, 'contours')
        # fig1.canvas.manager.window.setGeometry(0, 0, 800, 480)
        # fig2.canvas.manager.window.setGeometry(960, 0, 800, 480)
        # fig3.canvas.manager.window.setGeometry(0, 480, 800, 480)
        # fig4.canvas.manager.window.setGeometry(960, 480, 800, 480)
        plt.show(block=True)
        plt.pause(8)
        plt.close('all')

        combined_frame = combine_output(input_img, reef, algae, coral)
        cv2.imwrite("combined_output.png", combined_frame)

        # cv2.imshow('Combined', combined_frame)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
    else:
        output_video = "test_video1.mp4"
        process_video(input_video, output_video)
