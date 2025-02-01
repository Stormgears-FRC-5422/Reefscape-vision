import matplotlib.pyplot as plt
import numpy as np


def plot_img(raw, title, ch=-1):
    # Sample grayscale image data
    shape = raw.shape
    if len(shape) == 2 or ch not in [0, 1, 2]:
        # Create a figure with 1 row and 2 columns of subplots
        # image = raw[:, :]
        fig, axes = plt.subplots(1, 1)

        # Display the first image in the first subplot
        axes.imshow(raw, cmap='afmhot')
        axes.set_title(title)
    elif shape[2] == 3 and ch in [0, 1, 2]:
        # Create a figure with 1 row and 2 columns of subplots
        # image = raw[:, :]
        fig, axes = plt.subplots(1, 1)

        # Display the first image in the first subplot
        axes.imshow(raw[:, :, ch], cmap='afmhot')
        axes.set_title(title)

    elif shape[2] == 3 and ch == -1:
        image1 = raw[:, :, 0]
        image2 = raw[:, :, 1]
        image3 = raw[:, :, 2]
        fig, axes = plt.subplots(2, 2)
        fig.suptitle(title)
        axes[0, 0].imshow(raw, cmap='afmhot')
        axes[0, 0].set_title(title)
        axes[0, 1].imshow(image1, cmap='afmhot')
        axes[0, 1].set_title("Color / Channel 1")
        axes[1, 0].imshow(image2, cmap='afmhot')
        axes[1, 0].set_title("Color / Channel 2")
        axes[1, 1].imshow(image3, cmap='afmhot')
        axes[1, 1].set_title("Color / Channel 3")
        plt.subplots_adjust(bottom=0.1, right=0.8, top=0.9)
        # ... other subplots

    # Show the plot
    # fig.show()
    return fig, axes


def disp_value(image):

    def on_move(event):
        if event.inaxes:
            x, y = round(event.xdata), round(event.ydata)
            ch0 = image[y, x, 0]
            ch1 = image[y, x, 1]
            ch2 = image[y, x, 2]
            plt.title(f'x={x}, y={y}, ch0={ch0}, '
                      f'ch0={ch1}, ch0={ch2}')
            crosshair.set_data([x, x], [y, y])
            plt.draw()

    fig, ax = plt.subplots()
    ax.imshow(image)

    # Create crosshair lines
    crosshair, = ax.plot([0, 0], [0, 0], color='red', lw=1)

    # Connect the 'on_move' function to the 'motion_notify_event'
    plt.connect('motion_notify_event', on_move)

    plt.show()


