"""

Author: Arthur Wesley

"""

import os

from PIL import Image

import pytesseract

from src import constants


def crop_end_screen(path, start_size, box):
    """

    crops an image down to just the cremates

    :param path: path to the PIL image
    :param start_size: initial size of the image
    :param box: the box to crop the image
    :return: Cropped PIL image
    """

    im = Image.open(path)

    assert start_size == im.size

    im = im.crop(box)

    return im


def crop_crewmates(image):
    """

    crop the crewmates out of the image

    :param image: image to crop
    :return: List of Cropped images
    """

    boxes = [
        (95, 15, 150, 90),
        (140, 20, 195, 95),
        (195, 25, 250, 100),
        (260, 30, 315, 105),
        (305, 25, 360, 100),
        (365, 20, 420, 95),
        (415, 10, 470, 85),
        (460, 5, 515, 80)
    ]

    crops = []

    for i in range(len(boxes)):

        crops.append(image.crop(boxes[i]))

    return crops


def crop_meeting(image):
    """

    crop the members out of the given meeting image

    :param image: image to crop crewmates from
    :return: cropped images
    """

    boxes = [
        (85, 65, 305, 110),
        (305, 65, 525, 110),
        (85, 110, 305, 155),
        (305, 110, 525, 155),
        (85, 155, 305, 200),
        (305, 155, 525, 200),
        (85, 200, 305, 245),
        (305, 200, 525, 245),
        (85, 245, 305, 290),
        (305, 245, 525, 290)
    ]

    crops = []

    for i in range(len(boxes)):
        crops.append(image.crop(boxes[i]))

    return crops


def crop_meeting_480p(image):
    """

    crop the members out of the given meeting image (480p version)

    :param image: image to crop crewmates from
    :return: cropped images
    """

    boxes = [
        (115, 90, 405, 150),
        (405, 90, 695, 150),
        (115, 150, 405, 210),
        (405, 150, 695, 210),
        (115, 210, 405, 270),
        (405, 210, 695, 270),
        (115, 270, 405, 330),
        (405, 270, 695, 330),
        (115, 330, 405, 390),
        (405, 330, 695, 390)
    ]

    crops = []

    for i in range(len(boxes)):
        crops.append(image.crop(boxes[i]))

    return crops


def crop_all_crewmates(directory, output_directory):
    """

    crops all of the crewmates in specified directory

    :param directory: directory to get the images from
    :param output_directory: directory to output the images to
    :return: None
    """

    files = os.listdir(directory)

    for file in files:

        path = os.path.join(directory, file)

        im = Image.open(path)

        crops = crop_crewmates(im)

        for i in range(len(crops)):

            new_name = "Crewmate-" + str(i) + "-" + os.path.basename(path)

            crops[i].save(os.path.join(output_directory, new_name))


def crop_images(directory):
    """

    crops all of the images in a specified directory

    :param directory: directory to crop all the images in
    :return: None
    """

    files = os.listdir(directory)

    for file in files:

        path = os.path.join(directory, file)

        try:
            crop_end_screen(path,
                            path,
                            constants.dimensions,
                            constants.winner_identifier_cropping)
        except AssertionError:
            print("Error Image in " + file + " had incorrect dimensions")
            continue

    print("finished cropping", directory)


def crop_all_meetings(directory):
    """

    crops all the meetings in th specified directory and saves the up
    two directories

    :param directory: directory to get the images from
    :return: None
    """

    files = os.listdir(directory)

    for file in files:

        if file == ".DS_Store":
            continue

        path = os.path.join(directory, file)

        image = Image.open(path)
        crops = crop_meeting_480p(image)

        for i, crop in enumerate(crops):
            # save the file two directories up
            crop.save(os.path.join(directory,
                                   str(i) + "-" + file))

        os.remove(path)


def main():
    """

    main method

    crops all images in the winner identifier

    :return:
    """

    """
    crop_all_crewmates(os.path.join("Data",
                                    "Winner Identifier",
                                    "Test Data",
                                    "ext"),
                       os.path.join("Data",
                                    "Crewmate Identifier",
                                    "Crude Data"))
                                    """

    crop_all_meetings(os.path.join("Data",
                                   "High Res Test Data Images"))


if __name__ == "__main__":
    main()
