import json
import threading
from random import randint
from tkinter import *

import model

COLOUR_DATA_FILE_NAME = "colour_data.json"
VARIABLES_FILE_NAME = "variables.json"
VARIABLES_COLOUR_DATA_CHANGE_NAME = "colour_data_change"


def show_colour(colour, window):
    window.title("Colour")
    window.geometry("400x400")
    window.configure(background=colour)
    window.resizable(0, 0)
    window.attributes("-topmost", True)
    window.after(5000, window.destroy)
    window.mainloop()


def read_colour_data():
    colour_data = {}

    try:
        colour_data_file = open(COLOUR_DATA_FILE_NAME, "r")
        colour_data = json.load(colour_data_file)
        colour_data_file.close()
    except FileNotFoundError:
        pass
    except json.decoder.JSONDecodeError:
        print("{} may have been corrupted. It will be discarded when the next response is recorded."
              .format(COLOUR_DATA_FILE_NAME))

    return colour_data


def read_variables_data():
    variables_data = {}
    try:
        variables_data_file = open(VARIABLES_FILE_NAME, "r")
        variables_data = json.load(variables_data_file)
        variables_data_file.close()
    except FileNotFoundError:
        pass
    except json.decoder.JSONDecodeError:
        print("{} may have been corrupted. It will be overwritten.".format(VARIABLES_FILE_NAME))

    return variables_data


def set_colour_data_change(value):
    variables_data = read_variables_data()
    variables_data[VARIABLES_COLOUR_DATA_CHANGE_NAME] = value

    variables_data_file = open(VARIABLES_FILE_NAME, "w+")
    variables_data_file.write(json.dumps(variables_data))
    variables_data_file.close()


def write_colour_data(colour_data):
    colour_data_file = open(COLOUR_DATA_FILE_NAME, "w+")
    colour_data_file.write(json.dumps(colour_data))
    colour_data_file.close()

    set_colour_data_change(True)


def random_colour():
    return '#%02X%02X%02X' % (randint(0, 255), randint(0, 255), randint(0, 255))


def get_light_dark_response():
    response = input("Options:\n[D]ark\n[L]ight\n").lower()
    while response != "d" and response != "l":
        response = input("Invalid input. Type D for dark or L for light\n")

    return response


def light_dark_response(result):
    result = get_light_dark_response()


def get_and_log_colour_response(colour):
    colour_data = read_colour_data()
    print("Do you think this colour is dark or light?")

    window = Tk()
    response = ""
    thread = threading.Thread(target=light_dark_response, args=(response,))
    thread.start()

    show_colour(colour, window)
    thread.join()

    colour_data[colour] = "dark" if response == "d" else "light"
    write_colour_data(colour_data)

    print("Response logged\n")


def use():
    variables_data = read_variables_data()
    loop = True

    try:
        if variables_data[VARIABLES_COLOUR_DATA_CHANGE_NAME]:
            print("Updating neural network...")
            model.delete_and_replace_model(model.new_trained_model())
            set_colour_data_change(False)
    except KeyError:
        print("No training data found. Train the neural network before using it.")
        loop = False

    if loop:
        m = model.load_newest_model()

    while loop:
        colour = random_colour()

        prediction = model.prediction_from_colour(m, colour)
        prediction_text = "dark" if round(prediction) else "light"
        certainty = prediction if prediction > 0.5 else 1 - prediction

        print("The neural network thinks this colour is {}. It is {:.0%} certain".format(prediction_text, certainty))

        get_and_log_colour_response(colour)

        response = input("Options:\n[U]pdate Neural Network\n[Q]uit to main menu\n"
                         "Type anything else to continue without updating\n").lower()

        if response == "u":
            print("Updating neural network...")
            model.delete_and_replace_model(model.new_trained_model())
            m = model.load_newest_model()
            set_colour_data_change(False)
        elif response == "q":
            loop = False


def train():
    loop = True
    while loop:
        colour_data = read_colour_data()

        colour = random_colour()
        while colour in colour_data.keys():
            colour = random_colour()

        get_and_log_colour_response(colour)

        loop = ("q" != input("[Q]uit main menu?\n(Type Q to return or hit enter to continue)\n").lower())


while True:
    choice = input("Main Menu\nOptions:\n[T]rain neural network\n[U]se neural network\n[Q]uit\n").lower()
    while choice != "t" and choice != "u" and choice != "q":
        choice = input("Invalid input. Type T to train or U to use or Q to quit\n").lower()

    if choice == "t":
        train()
    elif choice == "u":
        use()
    elif choice == "q":
        break
