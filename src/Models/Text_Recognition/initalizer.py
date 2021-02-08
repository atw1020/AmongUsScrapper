"""

Author: Arthur Wesley

"""

import os
import random

from tensorflow.keras import Model
from tensorflow.keras import layers

from tensorflow.keras.utils import plot_model
from tensorflow.keras.optimizers import Adam

from tensorflow.keras import backend as K

from kerastuner import HyperParameters

from src import constants
from src.Models.Text_Recognition import trainer


def repeat_vector(args):
    layer_to_repeat = args[0]
    sequence_layer = args[1]
    return layers.RepeatVector(K.shape(sequence_layer)[1])(layer_to_repeat)


def init_hyperparameters():
    """

    initializes the hyperparameters for the model

    :return:
    """

    hp = HyperParameters()
    hp.Fixed("embedding dim", 512)

    hp.Fixed("conv_1 size", 18)
    hp.Fixed("conv_1 stride", 4)

    hp.Fixed("conv_2 size", 18)
    hp.Fixed("conv_2 stride", 4)

    hp.Fixed("conv_3 size", 18)
    hp.Fixed("conv_3 stride", 4)

    hp.Fixed("conv_4 size", 18)
    hp.Fixed("conv_4 stride", 4)

    hp.Fixed("lstm depth", 2)
    hp.Fixed("lstm breadth", 256)

    hp.Fixed("end depth", 1)
    hp.Fixed("end breadth", 256)

    hp.Fixed("learning rate", 0.001)
    hp.Fixed("dropout", 0.2)

    return hp


def init_nn(vocab,
            hp=None):
    """

    creates the neural network

    :param vocab: vocabulary to use
    :param hp: hyperparameters used
    :return: initialized model
    """

    if hp is None:
        hp = init_hyperparameters()

    embedding_dim = 512  # hp.Int("embedding dim", 256, 1024, 64)

    conv_1_size = 18  # hp.Int("conv_1 size", 5, 17, 2)
    conv_1_stride = 4  # hp.Int("conv_1 stride", 2, 5)

    conv_2_size = 18  # hp.Int("conv_2 size", 5, 17, 2)
    conv_2_stride = 4  # hp.Int("conv_2 stride", 2, 5)

    conv_3_size = 18  # hp.Int("conv_3 size", 5, 17, 2)
    conv_3_stride = 4  # hp.Int("conv_3 stride", 2, 5)

    conv_4_size = 18  # hp.Int("conv_4 size", 5, 17, 2)
    conv_4_stride = 4  # hp.Int("conv_4 stride", 2, 5)

    lstm_depth = 2  # hp.Int("lstm depth", 1, 10)
    lstm_breadth = 256  # hp.Int("lstm breadth", 512, 2048, 128)

    end_depth = 1  # hp.Int("end depth", 1, 10)
    end_breadth = 256  # hp.Int("end breadth", 512, 2048, 128)
    lr = 0.001  # 10 ** hp.Float("learning rate", -3, -2)

    dropout_rate = hp.Float("dropout", 0.1, 0.5)

    # reset the session
    K.clear_session()

    # convert booleans from integers to booleans
    pool_1 = bool(0)
    pool_2 = bool(0)

    # get the size of the vocabulary
    vocab_size = len(vocab.keys()) + 2

    # CNN

    image_input_layer = layers.Input(shape=constants.meeting_dimensions + (3,))
    batch_norm = layers.BatchNormalization()(image_input_layer)

    convolution = layers.Conv2D(filters=16,
                                kernel_size=conv_1_size,
                                strides=conv_1_stride,
                                activation="relu",
                                padding="same")(batch_norm)
    dropout = layers.Dropout(rate=constants.text_rec_dropout)(convolution)
    batch_norm = layers.BatchNormalization()(dropout)

    convolution = layers.Conv2D(filters=32,
                                kernel_size=conv_2_size,
                                strides=conv_2_stride,
                                activation="relu",
                                padding="same")(batch_norm)
    dropout = layers.Dropout(rate=constants.text_rec_dropout)(convolution)
    batch_norm = layers.BatchNormalization()(dropout)

    temp = batch_norm

    if pool_1:
        temp = layers.MaxPooling2D(pool_size=2,
                                   strides=2)(temp)

    convolution = layers.Conv2D(filters=64,
                                kernel_size=conv_3_size,
                                strides=conv_3_stride,
                                activation="relu",
                                padding="same")(temp)
    dropout = layers.Dropout(rate=constants.text_rec_dropout)(convolution)
    batch_norm = layers.BatchNormalization()(dropout)

    convolution = layers.Conv2D(filters=128,
                                kernel_size=conv_4_size,
                                strides=conv_4_stride,
                                activation="relu",
                                padding="same")(batch_norm)
    dropout = layers.Dropout(rate=constants.text_rec_dropout)(convolution)
    batch_norm = layers.BatchNormalization()(dropout)

    temp = batch_norm

    if pool_2:
        temp = layers.MaxPooling2D(pool_size=2,
                                   strides=2)(temp)

    flatten = layers.Flatten()(temp)

    # RNN input layer
    rnn_input = layers.Input(shape=(None,))

    embedding = layers.Embedding(input_dim=vocab_size,
                                 output_dim=embedding_dim)(rnn_input)

    temp = embedding

    dense = layers.Dense(lstm_breadth,
                         activation="relu",)(flatten)

    for i in range(lstm_depth - 1):
        GRU = layers.GRU(lstm_breadth,
                         activation="relu",
                         recurrent_dropout=constants.text_rec_dropout,
                         return_sequences=True)(temp,
                                                initial_state=dense)
        dropout = layers.Dropout(rate=constants.text_rec_dropout)(GRU)
        batch_norm = layers.BatchNormalization()(dropout)

        temp = batch_norm

    GRU = layers.GRU(lstm_breadth,
                     activation="relu",
                     recurrent_dropout=constants.text_rec_dropout,
                     return_sequences=True)(temp,
                                            initial_state=dense)

    temp = GRU

    dropout = layers.Dropout(rate=constants.text_rec_dropout)(temp)
    batch_norm = layers.BatchNormalization()(dropout)

    for i in range(end_depth):
        dense = layers.Dense(units=end_breadth,
                             activation="relu")(batch_norm)
        dropout = layers.Dropout(rate=constants.text_rec_dropout)(dense)
        batch_norm = layers.BatchNormalization()(dropout)

    dense = layers.Dense(units=vocab_size,
                         activation="sigmoid")(batch_norm)

    output = layers.Softmax()(dense)

    model = Model(inputs=[image_input_layer, rnn_input],
                  outputs=output,
                  name="Text_Reader")

    opt = Adam(lr=lr)

    model.compile(loss="sparse_categorical_crossentropy",
                  optimizer=opt,
                  metrics=["accuracy"])

    return model


def main():
    """

    main method

    :return:
    """

    vocab = trainer.get_vocab(os.path.join("Data",
                                            "Meeting Identifier",
                                            "Training data"))

    model = init_nn(vocab)
    model.summary()
    plot_model(model, to_file="RNN.png")


if __name__ == "__main__":
    main()
