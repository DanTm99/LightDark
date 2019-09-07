import json
import os
from glob import glob

from keras.layers import *
from keras.models import Sequential
from keras.models import load_model
from numpy import asarray

TRAINING_DATA_FILE_NAME = "colour_data.json"


def model_exists():
    return os.path.exists("model.h5")


def delete_and_replace_model(new_model):
    if os.path.exists("model.h5"):
        os.remove("model.h5")

    new_model.save("model.h5")


def rename_and_replace_model(new_model):
    if os.path.exists("model.h5"):
        highest_model_number = 0
        for filename in glob("model_old*.h5"):
            model_number = int(filename[9:-3])
            if model_number < highest_model_number:
                highest_model_number = model_number

        os.rename("model.h5", "model_old{}.h5".format(highest_model_number + 1))

    new_model.save("model.h5")


def create_new_model():
    model = Sequential()
    model.add(Dense(3, input_dim=3, activation="relu", name="layer_1"))
    model.add(Dense(2, activation="relu", name="layer_2"))
    model.add(Dense(1, activation="linear", name="output_layer"))
    model.compile(loss="mean_squared_error", optimizer="adam")

    return model


def save_new_model():
    rename_and_replace_model(create_new_model())


def load_and_preprocess_data():
    colour_data = {}
    try:
        colour_data_file = open(TRAINING_DATA_FILE_NAME, "r")
        colour_data = json.load(colour_data_file)
        colour_data_file.close()
    except FileNotFoundError:
        pass
    except json.decoder.JSONDecodeError:
        print("Error loading training data. {} may have been corrupted.".format(TRAINING_DATA_FILE_NAME))

    colours, results = [], []

    for colour in colour_data.keys():
        colours.append(hexcode_to_normalised_array(colour))
        results.append(float(colour_data[colour]))

    return [asarray(colours), asarray(results)]


def new_trained_model(verbose=0):
    model = create_new_model()
    x, y = load_and_preprocess_data()
    model.fit(x, y, epochs=10, shuffle=True, verbose=verbose)

    return model


def load_newest_model():
    return load_model("model.h5")


def hexcode_to_normalised_array(hexcode):
    return [int(hexcode.lstrip("#")[i:i + 2], 16) / 255 for i in (0, 2, 4)]


def prediction_from_colour(model, colour):
    x = asarray([hexcode_to_normalised_array(colour)])
    return model.predict(x)[0][0]
