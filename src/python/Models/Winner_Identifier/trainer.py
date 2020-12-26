"""

Author: Arthur wesley

"""

import os

import numpy as np
from tensorflow.keras.preprocessing import image_dataset_from_directory

from src.python import constants


def numpy_from_filename(filename):
    """

    filename of a labeled image

    :param filename: name of the file that you want to get the label from
    :return: numpy array colors the file uses
    """

    # get the colors
    color_string = filename.split("-")[0]
    colors = colors_from_color_string(color_string)

    result = np.zeros(12)

    for color in colors:
        result[constants.color_codes[color]] = 1

    return result


def colors_from_color_string(color_string):
    """

    generates a list of all the colors in a given color string (2 letter color codes
    concatenated together)

    :param color_string: 2 letter color codes concatanated together
    :return: list of two letter color codes
    """

    color_codes = []

    for i in range(0, len(color_string), 2):
        color_codes.append(color_string[i:i+2])

    return color_codes


def get_labels(directory):
    """

    gets the labels for all of the files in the given directory

    :param directory: directory to get the labels for
    :return: labels in order, sorted by name
    """

    files = sorted(os.listdir(os.path.join(directory, "ext")))

    return list(map(numpy_from_filename, files))


def gen_dataset(directory):
    """

    generates a winner identifier dataset from a given directory

    :param directory: directory to generate ethe labels from
    :return: winner identifier dataset
    """

    labels = get_labels(directory)

    return image_dataset_from_directory(directory,
                                        image_size=constants.dimensions,
                                        labels=labels)


def main():
    """

    main method

    :return: None
    """

    print(numpy_from_filename("RDBLPKORYLWTPRLM-846990283-2349.jpg"))

    dataset = gen_dataset(os.path.join("Data", "Winner Identifier", "Training Data"))

    print(dataset)


if __name__ == "__main__":
    main()
