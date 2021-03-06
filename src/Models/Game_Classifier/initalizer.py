"""

Author: Arthur wesley, Gregory Ghiroli

"""

from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.preprocessing import image

from src import constants

import os


def init_nn():
    """

    initializes the neural network

    :return: game classifier neural network
    """

    # input layer
    input_layer = layers.Input(shape=constants.dimensions + (3,))

    # 2D convolutions
    convolution =   layers.Conv2D(filters=8, kernel_size=11, strides=5, padding="same")(input_layer)
    relu        =   layers.LeakyReLU()(convolution)
    dropout     =   layers.Dropout(rate=constants.classifier_dropout)(relu)
    # pooling     =   layers.MaxPooling2D(pool_size=2)(classifier_dropout)
    convolution =   layers.Conv2D(filters=16, kernel_size=11, strides=5, padding="same")(dropout)
    relu        =   layers.LeakyReLU()(convolution)
    dropout2    =   layers.Dropout(rate=constants.classifier_dropout)(relu)
    convolution =   layers.Conv2D(filters=32, kernel_size=11, strides=5, padding="same")(dropout2)
    relu        =   layers.LeakyReLU()(convolution)
    dropout3    =   layers.Dropout(rate=constants.classifier_dropout)(relu)

    # flatten & feed into fully connected layers
    flatten = layers.Flatten()(dropout3)
    dense = layers.Dense(units=200, activation="relu")(flatten)
    dropout4 = layers.Dropout(rate=constants.classifier_dropout)(dense)
    dense2 = layers.Dense(units=100, activation="relu")(dropout4)
    dropout5 = layers.Dropout(rate=constants.classifier_dropout)(dense2)
    dense3 = layers.Dense(units=5, activation="relu")(dropout5)
    output = layers.Softmax()(dense3)

    opt = Adam(learning_rate=0.0001)

    model = keras.Model(inputs=input_layer,
                        outputs=output,
                        name="Game_Classifier")
    model.compile(loss="sparse_categorical_crossentropy",
                  optimizer=opt,
                  metrics=["accuracy"])

    return model


def import_image(file_path):
    """

    converts an image from a file path to a numpy array

    https://machinelearningmastery.com/how-to-normalize-center-and-standardize-images-with-the-imagedatagenerator-in-keras/

    :param file_path: path to the image
    :return: numpy array representation of the image
    """

    return image.img_to_array(image.load_img(file_path, target_size=constants.dimensions))


def main():
    """

    test method

    :return:
    """

    model = init_nn()
    model.summary()


if __name__ == "__main__":
    main()
