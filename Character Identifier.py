#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ______________________________________________________________________________________________________
# |                                                                                                    |
# |                                        CHARACTER IDENTIFIER                                        |
# |____________________________________________________________________________________________________|
#
# This program is a simple image processing software that gets an image and identifies the characters in the image.
# It uses PySimpleGUI to create a simple but useful GUI and uses Pillow and NumPy to process the image.
# The algorithm is explained on top of each method respectively.



# PLATFORM CONTROL
# ------------------------------
# This section checks the platform for being Windows because the program works only on it for some limitations of UNIX-based systems.

import platform

if platform.system() != 'Windows':
    print("\nThis program is designed to work only on Windows systems.")
    input("Press \"Enter\" key to terminate the program.")
    print()
    exit()


# AUTO DEPENDENCY INSTALLER
# ------------------------------
# This part of the code checks the system and gets all the modules installed. If required modules are not installed, prompts user for installing them.
# If user agrees, installs are missing modules.

import os
import pkg_resources
import subprocess
import time
import sys

# Required dependicies list
dependencies = ['Pillow', 'PySimpleGUI', 'NumPy']

# Gets installed modules
packages = pkg_resources.working_set
package_list = sorted([i.key for i in packages])

# Adds missing dependencies to a list
not_installed = []

for i in dependencies:
    if i.casefold() not in package_list:
        not_installed.append(i)

# If there are some missing modules, prompt user.
if len(not_installed) != 0:
    print("There are some modules that are required to run this program.\n\nThese modules are not installed on your computer:")
    for i in not_installed:
        print("[*] " + i)
    
    # Keeps asking until there is a valid answer
    while True:
        yes_no = input("\nDo you want to install them? (y/n): ")

        if yes_no.casefold() == "yes" or yes_no.casefold() == 'y':
            # Installs every module one-by-one by calling a "pip install" command
            for i in not_installed:
                print("\n____________________________________________________________________________________________________\n\nInstalling " + i + "...\n____________________________________________________________________________________________________\n")
                subprocess.check_call([sys.executable, "-m", "pip", "install", i])
            print("\n____________________________________________________________________________________________________\n\nDone installing the modules. Launching the program...\n____________________________________________________________________________________________________\n")
            time.sleep(1)
            break
        elif yes_no.casefold() == "no" or yes_no.casefold() == 'n':
            exit()
        else:
            print("Please enter a valid answer.")


# INITIALIZE FUNCTIONALITY
# ------------------------------
# This part of the code contains the required variables and imports to give functionality to program.

# Hides the terminal
import ctypes
ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

# Clears the terminal and prints a welcome text
os.system('cls')
print("____________________________________________________________________________________________________\n|                                                                                                  |\n|                                 Welcome to Character Identifier!                                 |\n|__________________________________________________________________________________________________|\n")

# Imports remaining required modules
from PIL import Image, ImageFont, ImageDraw, ImageTk
import shutil
import subprocess
import tempfile
import threading
from datetime import datetime
import PySimpleGUI as sg
import numpy as np
import traceback

# Gets user's temporary folder and adds a new subdirectory name
dir = tempfile.gettempdir() + '\\Character Identifier\\'

# A counter for total process count
process_count = [1]


# GUI
# ------------------------------
# This continuous part of the code creates the GUI and adds all the functional elements to it.

# Set the theme of GUI
sg.change_look_and_feel('DarkGrey9')
sg.theme_button_color((sg.theme_text_color(), sg.theme_background_color()))
sg.theme_input_text_color(sg.theme_text_color())

# Initialize the first column of the upper part of GUI
first_column = [
                [sg.Frame("Control Panel", title_location='n', layout=[
                    [sg.Text("File Name:", size=(24,1), pad=((5,5),(6,0))), sg.FileBrowse('Browse', target='-INPUT-', key='-BROWSE-', file_types=[("Image Files", "*.bmp *.jpeg *.jpg *.png *.jfif *.gif *.j2p *.eps *.icns *.ico *.im *.jpx *.msp *.pcx *.pbm *.pgm *.ppm *.sgi *.tiff *.webp *.xbm")], size=(7,1), auto_size_button=False, pad=((5,0),(3,0)))],
                    [sg.Input(default_text='Please select an image.', readonly=True, disabled_readonly_background_color=sg.theme_input_background_color(), key='-INPUT-', size=(38,1), justification='center', enable_events=True, pad=((5,5),(5,0)))],
                    [sg.Text("Threshold:", size=(26,1), pad=((5,5),(12,0))), sg.Input("220", disabled_readonly_background_color=sg.theme_input_background_color(), key='-VALUE-', size=(5,1), justification='center', enable_events=True, pad=((14,0),(16,0)))],
                    [sg.Slider(range=(1,255), default_value=220, orientation='horizontal', size=(30,20), key='-THRESHOLD-', disable_number_display=True, enable_events=True, pad=((5,5),(4,0)), )],
                    [sg.Text("Labeling Type:", size=(15,1),  pad=((5,5),(13,0)))],
                    [sg.Radio("4-Connected", "LABELING", size=(10,1), key='-FOUR-', pad=((32,5),(5,0))), sg.Radio("8-Connected", "LABELING", default=True, key="-EIGHT-",  pad=((5,15),(5,0)))],
                    [sg.Button('Start Process', key='-PROCESS-',pad=((8,0),(16,5)), disabled=True, size=(32,2), bind_return_key=True)]])
                    ]
                ]

# Initialize the second column of the upper part of GUI
second_column = [
                [sg.Frame("System Log", title_location='n', layout=[
                    [sg.Multiline(size=(200,15), font=('Consolas', 10), autoscroll=True, auto_refresh=True, key='-LOG-', disabled=True, write_only=True, pad=((5,5),(5,5)), echo_stdout_stderr=True, reroute_stdout=True)]])]
                ]

# Initialize the image column of the outputs part of GUI
image_column = [[sg.Image(data=None, size=(756,450), key='-OUTPUT-')]]

# Initialize the report column of the outputs part of GUI
text_column = [[sg.Multiline(size=(45,27), auto_refresh=True, font=('Consolas', 10), key='-REPORT-', disabled=True, write_only=True, autoscroll=False, pad=((5,5),(5,8)))]]

# Initialize the full layout
layout = [
            [sg.Column(first_column), sg.Column(second_column)],
            [sg.Frame("Outputs", pad=((10,0),(0,0)),title_location='n', layout=[
                [sg.Frame("Image Preview", pad=((5,5),(5,8)), title_location='n', layout=[[sg.Column(image_column)]]), sg.Column([[sg.Frame("Report", pad=((5,5),(0,8)), title_location='n', layout=text_column)],
                [sg.Button('Open Outputs Directory', key='-OPEN-',size=(42,1), pad=((8,0),(5,5)))]], pad=((4,0),(5,5)))]])]
        ]

# Initialize the window with the full layout
window = sg.Window('Character Identifier', layout, size=(1200,810), enable_close_attempted_event=True, finalize=True)


# GET IMAGE DATA
# ------------------------------
# This method gets a PIL image and converts it into a data stream with given sizes.

def get_img_data(img, maxsize=(756,450)):
    thumb = img.copy()
    thumb.thumbnail(maxsize)
    return ImageTk.PhotoImage(thumb)


# MAIN METHOD
# ------------------------------
# Inside main, the main directory is created and the main loop of the GUI is started. Loop checks the GUI in every iteration and reads the events of GUI.

def main():
    
    # Deletes the directory if there is one
    if os.path.exists(dir):
        shutil.rmtree(dir)

    # Creates the directory
    os.makedirs(dir)

    # Shows a popup that has the introduction and instructions
    intro = "____________________________________________________________________________________________________\n|                                                                                                  |\n|                                 Welcome to Character Identifier!                                 |\n|__________________________________________________________________________________________________|\n\nPlease note that this program only identifies characters A, B, C, and 1.*\nUnknown characters will be misidentified or identified as ?.\n\nThe HQ output image and the process report are saved temporarily, and they are in this directory:\n____________________________________________________________________________________________________\n\n" + dir[:-1] + "\n____________________________________________________________________________________________________\n\nThis directory will be deleted after the program is terminated, so to keep the outputs,\nyou have to copy them from the outputs directory. You can easily access it by pressing the\n\"Open Outputs Directory\" button.\n\nWhen you are ready, select an image via the \"Browse\" button, set the threshold and labeling type,\nand start the process.\n\n[*] The accuracy of seperating C and 1 is ~90%. They may be misidentified.\n"
    sg.Popup(intro, line_width=300, no_titlebar=True, font=('Consolas', 10), background_color='lightgray', text_color='black', button_color=('white','gray'), grab_anywhere=True, any_key_closes=True)
    
    # Initiates the main loop
    while True:
        # Reads the windows
        event, values = window.read()
        
        # If there is an attempt to close the window, terminates the process thread, unhides the terminal, deletes the directory, and breaks the loop
        if event == sg.WINDOW_CLOSE_ATTEMPTED_EVENT:
            if threading.active_count() != 1:
                stop_process()

            ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 1)
            shutil.rmtree(dir)
            break
        # If user selects an image, set the image name to the path indicator
        elif event == '-INPUT-':
            filename = values['-BROWSE-']

            if filename == '':
                continue
            
            window['-INPUT-'].Update(filename[filename.rindex("/") + 1:])
            window['-PROCESS-'].Update(disabled=False)
        # If user presses the process button, checks if there is a process running. If there is, aborts the process. Starts the process thread otherwise.
        elif event == '-PROCESS-':
            text = window['-PROCESS-'].get_text()
            
            if text == 'Start Process':
                filename = values['-BROWSE-']

                if filename == '':
                    continue

                thr = threading.Thread(target=process, args=[values], kwargs={}, daemon=True, name="Identify Process")
                thr.start()
            else:
                stop_process()
        # If user wants to open the directory, checks the directory. If the directory is deleted somehow, creates it again. Then starts the directory.
        elif event == '-OPEN-':
            if not os.path.exists(dir):
                print("[" + datetime.now().strftime("%d/%m/%Y %H:%M:%S") + "] Directory not found. Creating a new one...")
                os.makedirs(dir)

            os.startfile(dir)
        # These 2 elif blocks syncs the slider and the input box of the threshold
        elif event == '-THRESHOLD-':
            window.Element('-VALUE-').Update(int(values['-THRESHOLD-']))
        elif event == '-VALUE-':
            input = values['-VALUE-']

            if input.isdigit():
                value = int(input)

                if value < 1:
                    value = 1
                elif value > 255:
                    value = 255
            else:
                value = 1

            window.Element('-THRESHOLD-').Update(value)
            window.Element('-VALUE-').Update(value)


# PROCESS METHOD
# ------------------------------
# This method contains all the image processing elements init. It is the main component of this program.
# It gets an image, binarizes it with the given threshold, labels it with the given labeling type, gets coordinates of
# each character, identifies them, writes a report, and shows all the outputs.

def process(values):
    # Gets the current process count
    counter = process_count[0]

    # Creates a name for the current process directory
    process_dir = dir + 'Process #' + str(counter) + '/'

    # Creates a name for the process steps directory
    steps_dir = process_dir + 'Steps/'

    # A try/except block for maintaining the process up and running
    try:
        print("[" + datetime.now().strftime("%d/%m/%Y %H:%M:%S") + "] Process #" + str(counter) + " has been started.")

        # Disables the elements of GUI
        element_control(disable=True)

        # Gets the file path from GUI
        filename = values['-BROWSE-']

        # Creates the directories
        os.makedirs(process_dir)
        os.makedirs(steps_dir)

        # Initializes a step counter
        step_counter = 1
        
        # Gets the image from path, copies it, and shows it on GUI
        original = Image.open(filename)
        img = original.copy()
        window['-OUTPUT-'].Update(data=get_img_data(img), size=(756,450))
        window['-REPORT-'].Update('')

        # Gets the threshold value and labeling type from GUI
        thres = int(values['-THRESHOLD-'])
        eight_connected = values['-EIGHT-']

        print("[" + datetime.now().strftime("%d/%m/%Y %H:%M:%S") + "] Selected image: " + filename)  
        print("[" + datetime.now().strftime("%d/%m/%Y %H:%M:%S") + "] Binarizing threshold value: " + str(thres))
        print("[" + datetime.now().strftime("%d/%m/%Y %H:%M:%S") + "] Selected labeling type: " + ("8-Connected" if eight_connected else "4-Connected"))

        # Check the image for having alpha channel
        has_alpha = True if img.mode == 'RGBA' else False
        background_type = ""

        # If photo has an alpha channel, cleans the alpha channel, shows it, and saves it under the steps directory
        if has_alpha:
            print("[" + datetime.now().strftime("%d/%m/%Y %H:%M:%S") + "] Cleaning up the alpha channel...")
            img, background_type = alpha_cleanup(img)

            if not os.path.exists(steps_dir):
                os.makedirs(steps_dir)

            img.save(steps_dir + str(step_counter) + '.Alpha Cleanup.png')
            window['-OUTPUT-'].Update(data=get_img_data(img), size=(756,450))
            step_counter += 1

        # Converts the image to grayscale, shows it, and saves it
        print("[" + datetime.now().strftime("%d/%m/%Y %H:%M:%S") + "] Converting image to grayscale...")
        img_gray = img.convert('L')

        if not os.path.exists(steps_dir):
            os.makedirs(steps_dir)

        img_gray.save(steps_dir + str(step_counter) + '.Grayscale.png')
        window['-OUTPUT-'].Update(data=get_img_data(img_gray), size=(756,450))
        step_counter += 1

        # Binarizes the image with the given threshold, shows the binarized image, and saves it
        print("[" + datetime.now().strftime("%d/%m/%Y %H:%M:%S") + "] Binarizing image...")
        a_bin, dark = binarize(img_gray, thres)
        binarized = Image.fromarray(a_bin)
        binarized = binarized.convert('RGB')

        if not os.path.exists(steps_dir):
            os.makedirs(steps_dir)

        binarized.save(steps_dir + str(step_counter) + '.Binarized.png')
        window['-OUTPUT-'].Update(data=get_img_data(binarized), size=(756,450))
        step_counter += 1
        
        # Sets the background type via the returned dark value
        if background_type == "":
                background_type = "Dark" if dark else "Light"

        # Labels image with the given labeling type, shows the labeled image, and saves it
        print("[" + datetime.now().strftime("%d/%m/%Y %H:%M:%S") + "] Labeling characters...")
        labeled_array, labels, colored = label_image(a_bin, eight_connected) #labels 4-connected components

        if not os.path.exists(steps_dir):
            os.makedirs(steps_dir)

        colored.save(steps_dir + str(step_counter) + '.Colored Blobs.png')
        window['-OUTPUT-'].Update(data=get_img_data(colored), size=(756,450))
        colored = colored.convert('RGBA')
        step_counter += 1

        # Gets coordinates of each characters and the alpha layer that has the frames, combines the alpha layer with the labeled image,
        # shows the composition, and saves it
        print("[" + datetime.now().strftime("%d/%m/%Y %H:%M:%S") + "] Getting coordinates of each character...")
        coordinates, alpha = get_coordinates(labeled_array, labels, colored)

        if not os.path.exists(steps_dir):
            os.makedirs(steps_dir)

        Image.alpha_composite(colored, alpha).save(steps_dir + str(step_counter) + '.Framed Blobs.png')
        window['-OUTPUT-'].Update(data=get_img_data(Image.alpha_composite(colored, alpha)), size=(756,450))
        step_counter += 1

        # Identifies characters and gets the alpha layer that has the frames and the character indicators. Than combines the alpha layer
        # with the labeled image, shows the composition, and saves it
        print("[" + datetime.now().strftime("%d/%m/%Y %H:%M:%S") + "] Identifying characters...")
        characters, alpha = identify_characters(labeled_array, eight_connected, coordinates, step_counter, steps_dir, alpha, colored)
        
        # Combines the alpha layer with the original image and saves it
        print("[" + datetime.now().strftime("%d/%m/%Y %H:%M:%S") + "] Finalizing the output...")
        original = original.convert('RGBA')
        output = Image.alpha_composite(original, alpha)

        if not os.path.exists(process_dir):
            os.makedirs(process_dir)

        output.save(process_dir + 'Output.png')

        # Generates the process report
        print("[" + datetime.now().strftime("%d/%m/%Y %H:%M:%S") + "] Done!")
        report = output_text(filename, coordinates, characters, background_type, thres, eight_connected, has_alpha)

        if not os.path.exists(process_dir):
            os.makedirs(process_dir)

        # Creates the report file and writes the output text into it
        f = open(process_dir + 'Report.txt', 'w', encoding='utf-8')
        f.write(report)
        f.close()

        # Shows all the outputs on GUI
        window['-REPORT-'].Update(report)
        window['-OUTPUT-'].Update(data=get_img_data(output), size=(756,450))

        if len(coordinates) == 0:
            print("[" + datetime.now().strftime("%d/%m/%Y %H:%M:%S") + "] No characters seem to be detected. Maybe changing the threshold can help.")

        process_count[0] += 1
    # If there is an SystemExit attempt which means user aborted the process, reverts all the process
    except SystemExit:
        print("[" + datetime.now().strftime("%d/%m/%Y %H:%M:%S") + "] Reverting all changes and aborting...")
        window['-OUTPUT-'].Update(data="", size=(756,450))
        window['-REPORT-'].Update("")
        shutil.rmtree(process_dir)
    # If there is an exception that is caused from an error, prints the stack trace and reverts all the process
    except:
        print("[" + datetime.now().strftime("%d/%m/%Y %H:%M:%S") + "] An exception has occured. Reverting all changes and aborting...")
        print("\n--------------------------------------------STACK TRACE--------------------------------------------\n")
        print(traceback.format_exc())
        print("---------------------------------------------------------------------------------------------------\n")
        window['-OUTPUT-'].Update(data="", size=(756,450))
        window['-REPORT-'].Update("")
        shutil.rmtree(process_dir)
    # Enables all the elements
    element_control(disable=False)


# ELEMENT CONTROL
# ------------------------------
# This method is used to enable and disable the GUI elements in one line

def element_control(disable=None):
    window['-PROCESS-'].Update('Start Process' if disable == False else 'Abort Process')
    window['-BROWSE-'].Update(disabled=disable)
    window['-VALUE-'].Update(disabled=disable)
    window['-THRESHOLD-'].Update(disabled=disable)
    window['-FOUR-'].Update(disabled=disable)
    window['-EIGHT-'].Update(disabled=disable)


# STOP PROCESS
# ------------------------------
# This method checks all the threads' names. If it catches a process named "Identify Process", sends and SystemExit exception to the thread.

def stop_process():
    for id, thread in threading._active.items():
        if thread.name == "Identify Process":
            ctypes.pythonapi.PyThreadState_SetAsyncExc(id , ctypes.py_object(SystemExit))


# BINARIZE
# ------------------------------
# This method checks the background first for identifying the one and zero values. Than gives zero to the pixels that is under the threshold, but
# gives one to the pixel that is over the threshold.

def binarize(img,T):
    # Creates an array from the image
    im = np.asarray(img)
    (nrows, ncols) = im.shape

    # Checks the image for having a dark background
    dark = check_dark(img, T)

    # Initializes the one and zero values
    ONE = 255 if not dark else 0
    ZERO = 0 if not dark else 255

    # Creates a new array full of zeros
    im_out = np.zeros(shape = im.shape)

    # Iterates over every pixel and check them vie the threshold
    for i in range(nrows):
        for j in range(ncols):
            if abs(im[i][j]) <  T :
                im_out[i][j] = ONE
            else:
                im_out[i][j] = ZERO
    
    # Returns the binarized array and the dark boolean
    return im_out, dark


# LABEL IMAGE
# ------------------------------
# This method checks connected pixels and gives them a unique label. It checks the connection via checking certain pixels. In 4-connected labeling,
# it checks the upper and left pixels, but in 8-connected labeling, it checks the upper left and upper right pixels as well. 

def label_image(bim, eight_connected):
    max_label = int(10000)
    nrow = bim.shape[0]
    ncol = bim.shape[1]

    # Creates a new array that will hold the labels and that has the same shape with the binarized array
    im = np.full(shape=(nrow,ncol), dtype = int, fill_value=max_label)

    # Creates an label holder array
    a = np.arange(0,max_label, dtype = int)

    # Creates the color mapper array
    color_map = np.zeros(shape = (max_label,3), dtype= np.uint8)

    # Creates the colored labels array
    color_im = np.zeros(shape = (nrow, ncol,3), dtype= np.uint8)

    # Initializes the color mapper randomly
    for i in range(max_label):
        color_map[i][0] = np.random.randint(0,255,1,dtype = np.uint8)
        color_map[i][1] = np.random.randint(0,255,1,dtype = np.uint8)
        color_map[i][2] = np.random.randint(0,255,1,dtype = np.uint8)

    k = 0
    
    # Starts labeling by checking connected pixels
    for i in range(1, nrow - 1):
        for j in range(1, ncol - 1):
                # Gets the related pixels
                c   = bim[i][j]
                label_u  = im[i-1][j]
                label_l  = im[i][j-1]

                if eight_connected:
                    label_ul  = im[i-1][j-1]
                    label_ur  = im[i-1][j+1]

                # Checks the pixel for being white
                if c == 255:
                    # Gets the minimum labeled pixel around the current one
                    min_label = min(label_u, label_l, label_ur, label_ul) if eight_connected else min(label_u, label_l)
                    
                    # If the minimum labeled pixel has the maximum label value, give it a temp value
                    # Else, update the array with the label
                    if min_label == max_label:  # u = l = 0
                        k += 1
                        im[i][j] = k
                    else:
                        im[i][j] = min_label
                        if min_label != label_u and label_u != max_label  :
                            update_array(a, min_label, label_u)

                        if min_label != label_l and label_l != max_label  :
                            update_array(a, min_label, label_l)

                        if eight_connected:
                            if min_label != label_ur and label_ur != max_label  :
                                update_array(a, min_label, label_ur)
                            
                            if min_label != label_ul and label_ul != max_label  :
                                update_array(a, min_label, label_ul)

    # Initializes an array for labels
    labels = []

    # Final reduction in the label array, also adds the labels into the label list
    for i in range(k+1):
        index = i
        while a[index] != index:
            index = a[index]
        a[i] = a[index]
        labels.append(a[i])

    # Removes duplicates drom the list
    labels = list(dict.fromkeys(labels))
    labels.pop(0)
  
    # Second pass to resolve labels and give every cell the label colors
    for i in range(nrow):
        for j in range(ncol):
            if bim[i][j] == 255 and im[i][j] != max_label:
                im[i][j] = a[im[i][j]]
                color_im[i][j][0] = color_map[im[i][j],0]
                color_im[i][j][1] = color_map[im[i][j],1]
                color_im[i][j][2] = color_map[im[i][j],2]
            else:
                im[i][j] = 0
                color_im[i][j][0] = 0
                color_im[i][j][1] = 0
                color_im[i][j][2] = 0
    
    # Creates an image from the array
    image = Image.fromarray(np.uint8(color_im))

    # Returns the labeled array, label list, and the colored image
    return im, labels, image


# UPDATE ARRAY
# ------------------------------
# A method for updating the equivalent labels array by merging label1 and label2 that are determined to be equivalent.

def update_array(a, label1, label2) :
    index = lab_small = lab_large = 0
    if label1 < label2 :
        lab_small = label1
        lab_large = label2
    else :
        lab_small = label2
        lab_large = label1
    index = lab_large
    while index > 1 and a[index] != lab_small:
        if a[index] < lab_small:
            temp = index
            index = lab_small
            lab_small = a[temp]
        elif a[index] > lab_small:
            temp = a[index]
            a[index] = lab_small
            index = temp
        else:
            break


# GET COORDINATES
# ------------------------------
# This method finds the coordinates of each character by checking every line of the array and the clockwised version of the array.
# It also creates an alpha layer to draw the frames of characters.

def get_coordinates(labeled_image, labels, colored):
    # Creates the alpha layer
    alpha = Image.new('RGBA', colored.size, (255,255,255,0))

    # Turns the array clockwise
    clockwise = list(zip(*labeled_image[::-1]))

    # Gets the shape of the array
    nrow = len(labeled_image)
    ncol = len(labeled_image[0])

    # Creates a dictionary to hold the coordinates of every label
    dict = {}

    # A loop goes through every label
    for i in range(len(labels)):
        label = labels[i]

        # Placeholders for coordinates
        min_x = -1
        min_y = -1
        max_x = -1
        max_y = -1

        # Checks the minimum y value by checking the rows from top to bottom
        for j in range(nrow):
            if label in labeled_image[j]:
                min_y = j
                break
        
        # Checks the minimum x value by checking the rows from left to right
        for j in range(ncol):
            if label in clockwise[j]:
                min_x = j
                break
        
        # Checks the maximum y value by checking the rows from bottom to top
        for j in reversed(range(nrow)):
            if label in labeled_image[j]:
                max_y = j
                break
        
        # Checks the maximum x value by checking the rows from top to bottom
        for j in reversed(range(ncol)):
            if label in clockwise[j]:
                max_x = j
                break
        
        # Enlarges the boundaries by 2 pixels
        min_x -= 2
        min_y -= 2
        max_x += 2
        max_y += 2

        # If there is boundaries, draws the rectangles to the alpha layer and adds to coordinates to the dictionary
        if min_x != -1 and min_y != -1 and max_x != -1 and max_y != -1:
            dict[label] = ((min_x,min_y),(max_x,max_y))
            alpha = draw_rect_to_alpha(alpha, min_xy=(min_x, min_y), max_xy=(max_x, max_y))
            window['-OUTPUT-'].Update(data=get_img_data(Image.alpha_composite(colored, alpha)), size=(756,450))

    # Returns the dictionary and the alpha layer
    return dict, alpha


# IDENTIFY CHARACTERS
# ------------------------------
# This method identifies the characters by cutting blobs out of the labeled array and binarizes them by the label of the character.
# If the pixel's label is equal to the current label, makes it zero. Otherwise, makes it one. Then, sends the blobs into labeling again.
# If the blob has 3 labels, it is B. If it has 2 labels, it is A. If it has 1 label, a different filtering sequence started to distinguish
# C and 1.

def identify_characters(image, eight_connected, coordinates, step_counter, steps_dir, alpha, colored):
    # Creates a dictionary for storing the character value for each label
    dict = {}

    # Gets a list of labels
    labels = list(coordinates.keys())

    # A loop goes through all labels
    for i in range(len(coordinates)):
        label = labels[i]

        # Gets the coordinates for each label
        min_x = coordinates.get(label)[0][0]
        min_y = coordinates.get(label)[0][1]
        max_x = coordinates.get(label)[1][0]
        max_y = coordinates.get(label)[1][1]
        
        # Creates an array filled with zeros that has the same shape of the blob
        blob = np.zeros((max_y-min_y+1,max_x-min_x+1))

        # Binarizes the image by the label, it the pixel has the current label, makes it zero.
        # Otherwise, makes it one.
        row_counter = 0
        for j in range(min_y, max_y+1):
            col_counter = 0
            for r in range(min_x, max_x+1):
                if image[j][r] != label:
                    blob[row_counter][col_counter] = 255
                else:
                    blob[row_counter][col_counter] = 0
                col_counter += 1
            row_counter += 1

        # Sends the blob to labeling again
        labeled_blob, blob_labels, colored_blob = label_image(blob, eight_connected)

        # Gets the label count
        blob_count = len(blob_labels)

        # If the blob has only 1 label, sends it into a nested if/else combination to distinguish C and 1
        if blob_count == 1:
            limits = check_limits(blob)

            if limits >= 3:
                counter_zero, counter_one = check_inside_count(blob, 5)

                if counter_zero != 0:
                    counter_x, counter_y = check_all_matrix(blob)

                    if (counter_x == 2 and counter_y == 2):
                        inner_zero, inner_one = check_inside_count(blob, 3)

                        if inner_zero != 0:
                            inner_total_zero, inner_total_one = check_all_count(blob)

                            if (inner_total_zero > inner_total_one) or ((inner_zero / (inner_zero + inner_one)) <= 0.025):
                                char = 'C'
                            else:
                                char = '1'
                        else:
                            char = 'C'
                    else:
                        origin_x, origin_y = check_matrix_center(blob)

                        if (origin_x == 2 and origin_y == 1) or (origin_x == 1 and origin_y == 2):
                            deep_inner_zero, deep_inner_one = check_inside_count(blob, 3)

                            if deep_inner_zero != 0:
                                if deep_inner_zero / (deep_inner_one + deep_inner_zero) <= 0.025:
                                    char = 'C'
                                else:
                                    char = '1'
                            else:
                                char = 'C'
                        else:
                            char = '1'
                else:
                    char = 'C'
            else:
                limit_zero, limit_one = check_all_count(blob)

                if limit_zero > limit_one:
                    char = 'C'
                else:
                    lowest_zero, lowest_one = check_inside_count(blob, 5)

                    if lowest_zero / (lowest_zero + lowest_one) > 0.025:
                        char = '1'
                    else:
                        lowest_x, lowest_y = check_all_matrix(blob)

                        if lowest_x == 2 and lowest_y == 2:
                            char = 'C'
                        else:
                            char = '1'
        # If the label count is 3, it is B. If the label count is 2, it is A. If the count is something else, it is unknown, so it is ?.
        else:
            char = 'B' if blob_count == 3 else ('A' if blob_count == 2 else '?')

        # Adds the character value to the dictionary
        dict[label] = char

        # Draws the character to the alpha layer and updates the GUI
        alpha = draw_char_to_alpha(alpha, min_xy=(min_x, min_y), max_xy=(max_x, max_y), char=char, label=label)
        window['-OUTPUT-'].Update(data=get_img_data(Image.alpha_composite(colored, alpha)), size=(756,450))

    # Creates a composition of alpha layer and the colored blobs image and saves it
    if not os.path.exists(steps_dir):
        os.makedirs(steps_dir)
        
    Image.alpha_composite(colored, alpha).save(steps_dir + str(step_counter) + '.Identified Blobs.png')

    # Returns the character dictionary and the alpha layer
    return dict, alpha


# CHECK LIMITS
# ------------------------------
# A method to check the limits of character on all sides.

def check_limits(arr):
    (nrows, ncols) = arr.shape
    index_y = int(nrows / 2.5)
    index_x = int(ncols / 2.5)

    limit_count = 0
    for i in range(int(nrows/3)):
        has_limit = False
        for j in range(index_x, ncols - index_x):
            if arr[i][j] == 0 and arr[i+1][j] == 255:
                has_limit = True
                break
        if has_limit:
            limit_count += 1
            break

    for i in reversed(range(int(nrows/3), nrows)):
        has_limit = False
        for j in range(index_x, ncols - index_x):
            if arr[i][j] == 0 and arr[i-1][j] == 255:
                has_limit = True
                break
        if has_limit:
            limit_count += 1
            break
    
    for i in range(int(ncols/3)):
        has_limit = False
        for j in range(index_y, nrows - index_y):
            if arr[j][i] == 0 and arr[j][i+1] == 255:
                has_limit = True
                break
        if has_limit:
            limit_count += 1
            break

    for i in reversed(range(int(ncols/3), ncols)):
        has_limit = False
        for j in range(index_y, nrows - index_y):
            if arr[j][i] == 0 and arr[j][i-1] == 255:
                has_limit = True
                break
        if has_limit:
            limit_count += 1
            break

    return limit_count


# CHECK ALL MATRIX
# ------------------------------
# A method to check how many encounters to the character are there in both axises.

def check_all_matrix(arr):
    (nrows, ncols) = arr.shape
    counter_x = 0
    counter_y = 0
                        
    for j in range(nrows):
        counter = 0
        for r in range(1, ncols):
            if arr[j][r - 1] == 255 and arr[j][r] == 0:
                counter += 1
        if counter > counter_x:
            counter_x = counter
                        
    for j in range(ncols):
        counter = 0
        for r in range(1, nrows):
            if arr[r - 1][j] == 255 and arr[r][j] == 0:
                counter += 1
        if counter > counter_y:
            counter_y = counter

    return counter_x, counter_y


# CHECK MATRIX CENTER
# ------------------------------
# A method to check how many encounters to the character are there in only the center line and column.

def check_matrix_center(arr):
    (nrows, ncols) = arr.shape
    counter_x = 0
    counter_y = 0

    for j in range(1, nrows):
        if arr[j - 1][int(ncols / 2)] == 255 and arr[j][int(ncols / 2)] == 0:
            counter_x += 1
                            
    for j in range(1, ncols):
        if arr[int(nrows / 2)][j - 1] == 255 and arr[int(nrows / 2)][j] == 0:
            counter_y += 1
    
    return counter_x, counter_y


# CHECK INSIDE COUNT
# ------------------------------
# A method to check how many one and zeros are there in a limited rectangle in the blob.

def check_inside_count(arr, denominator):
    (nrows, ncols) = arr.shape
    
    zero_count = 0
    one_count = 0

    index_y = int(nrows / denominator)
    index_x = int(ncols / denominator)

    for i in range(index_y, nrows - index_y):
        for j in range(index_x, ncols - index_x):
            if arr[i][j] == 0:
                zero_count += 1
            else:
                one_count += 1

    return zero_count, one_count


# CHECK ALL COUNT
# ------------------------------
# A method to check how many one and zeros are there in the blob.

def check_all_count(arr):
    (nrows, ncols) = arr.shape

    zero_count = 0
    one_count = 0

    for i in range(nrows):
        for j in range(ncols):
            if arr[i][j] == 0:
                zero_count += 1
            else:
                one_count += 1

    return zero_count, one_count


# ALPHA CLEANUP
# ------------------------------
# This method cleans the alpha channel if there is one.
# First, checks if there is a background. If there is, fills the alpha layer with the background color.
# If there is not, fills the alpha layer with the opposite color of the foreground color.

def alpha_cleanup(image):
    # Copies the image and converts it into a grayscale image with an alpha layer
    img = image.copy()
    img = img.convert('LA')

    # Converts the image into an array
    arr = np.copy(np.asarray(img))
    (nrows, ncols, channels) = arr.shape

    # Gets the alpha value of corners of the image
    ul = arr[0][0][1]
    bl = arr[0][ncols-1][1]
    ur = arr[nrows - 1][0][1]
    br = arr[nrows - 1][ncols - 1][1]

    # Checks every corner for being transparent
    alpha_counter = 0

    if ul == 0:
        alpha_counter += 1
    
    if bl == 0:
        alpha_counter += 1
    
    if ur == 0:
        alpha_counter += 1
    
    if br == 0:
        alpha_counter += 1

    background_type = ""

    # If the number of transparent pixels is higher than 2, that means there is no background
    if alpha_counter > 2:
        # Gets the maximum color value of the foregrıund image
        maximum = -1
        for i in range(nrows):
            for j in range(ncols):
                if arr[i][j][0] > maximum and arr[i][j][1] != 0:
                    maximum = arr[i][j][0]

        # Paints the background with the opposite color of the maximum color value
        color = 255 if maximum <= 128 else 0
        img = paint_alpha(img, color)

        # Sets the background type to none
        background_type = "None"
    # If there is a background
    else:
        # Gets the maximum color value of corners and paints the alpha layer with that color
        ul = arr[0][0][0]
        bl = arr[0][ncols-1][0]
        ur = arr[nrows - 1][0][0]
        br = arr[nrows - 1][ncols - 1][0]
        bg_color = max(ul, bl, ur, br)
        img = paint_alpha(img, bg_color)
    
    # Returns the cleaned image and the background type
    return img, background_type


# DRAW RECTANGLE TO ALPHA
# ------------------------------
# This method is used to draw a rectangle to given alpha layer with the minimum and maximum x and y values.

def draw_rect_to_alpha(alpha, min_xy=None, max_xy=None):
    draw = ImageDraw.Draw(alpha)

    # Sets the line width dynamically by the shortest side of the image
    line_width = round(min(alpha.size) / 250) if round(min(alpha.size) / 250) >= 2 else 2

    # Sets the values
    min_x = min_xy[0] + 2 - line_width
    min_y = min_xy[1] + 2 - line_width
    max_x = max_xy[0] - 2 + line_width
    max_y = max_xy[1] - 2 + line_width
    
    # Draws the rectangle into the alpha layer
    draw.rectangle(xy=((min_x, min_y), (max_x, max_y)), outline=(255,0,0,255), width=line_width)

    # Returns the alpha layer
    return alpha


# DRAW CHARACTER TO ALPHA
# ------------------------------
# This method is used to draw the character and the label to given alpha layer with the minimum and maximum x and y values.

def draw_char_to_alpha(alpha, min_xy=None, max_xy=None, char=None, label=None):
    draw = ImageDraw.Draw(alpha)

    # Sets the line width dynamically by the shortest side of the image
    line_width = round(min(alpha.size) / 250) if round(min(alpha.size) / 250) >= 2 else 2

    # Sets the values
    min_x = min_xy[0] - 2 - line_width
    min_y = min_xy[1] - 2 - line_width
    max_x = max_xy[0] + 2 + line_width
    max_y = max_xy[1] + 2 + line_width

    # Sets the fonts and the size of it dynamically by the side that the character will be put on
    # Minimum value of the font size is 20
    x_rounded = round((max_x - min_x) / 3)
    y_rounded = round((max_y - min_y) / 3)

    x_char_font_size = x_rounded if x_rounded > 20 else 20
    x_char_font = ImageFont.truetype("consola.ttf", x_char_font_size)

    x_lbl_font_size = int(x_char_font_size / 1.5)
    x_lbl_font = ImageFont.truetype("consola.ttf", x_lbl_font_size)

    y_char_font_size = y_rounded if y_rounded > 20 else 20
    y_char_font = ImageFont.truetype("consola.ttf", y_char_font_size)

    y_lbl_font_size = int(y_char_font_size / 1.5)
    y_lbl_font = ImageFont.truetype("consola.ttf", y_lbl_font_size)
    
    # If top of the blob is empty, draw the indicators on top of it
    if (x_char_font_size / 1.33) < min_y:
        draw.text(xy=(min_x + 4, min_y), anchor='lb', text=f"{char}", fill=(255,0,0), font=x_char_font)
        draw.text(xy=(max_x - 4, min_y), anchor='rb', text=f"{label}", fill=(255,0,0,150), font=x_lbl_font)
    # If right side of the blob is empty, draw the indicators on right side of it
    elif (y_char_font_size / 1.33) < alpha.width - max_x:
        draw.text(xy=(max_x, min_y + 4), anchor='lt', text=f"{char}", fill=(255,0,0), font=y_char_font)
        draw.text(xy=(max_x, max_y - 4), anchor='lb', text=f"{label}", fill=(255,0,0,150), font=y_lbl_font)
    # If bottom of the blob is empty, draw the indicators on bottom of it
    elif (x_char_font_size / 1.33) < alpha.height - max_y:
        draw.text(xy=(min_x + 4, max_y), anchor='lt', text=f"{char}", fill=(255,0,0), font=x_char_font)
        draw.text(xy=(max_x - 4, max_y), anchor='rt', text=f"{label}", fill=(255,0,0,150), font=x_lbl_font)
    # If left side of the blob is empty, draw the indicators on left side of it
    elif (y_char_font_size / 1.33) < min_x:
        draw.text(xy=(min_x, min_y + 4), anchor='rt', text=f"{char}", fill=(255,0,0), font=y_char_font)
        draw.text(xy=(min_x, max_y - 4), anchor='rb', text=f"{label}", fill=(255,0,0,150), font=y_lbl_font)
    # If the blob is not empty on all sides, draw the indicators inside of it
    else:
        inside_char_font_size = x_rounded if (x_rounded > 20 and x_rounded < (max_y - min_y)) else 20
        inside_char_font = ImageFont.truetype("consola.ttf", inside_char_font_size)

        inside_lbl_font_size = int(inside_char_font_size / 1.5)
        inside_lbl_font = ImageFont.truetype("consola.ttf", inside_lbl_font_size)
        
        draw.text(xy=(min_x + 8, min_y + 8), anchor='lt', text=f"{char}", fill=(255,0,0), font=inside_char_font)
        draw.text(xy=(max_x - 8, min_y + 8), anchor='rt', text=f"{label}", fill=(255,0,0,150), font=inside_lbl_font)
    
    # Returns the alpha layer
    return alpha


# CHECK DARK
# ------------------------------
# This method checks the corners of the image for being under or over the threshold.

def check_dark(image, threshold):
    # Converts the image into grayscale
    gray = image.convert('L')

    # Creates an array from the image and gets the shape of it
    arr = np.asarray(gray)
    (nrows, ncols) = arr.shape

    # Checks every corner of the character
    # If the pixel is below threshold, increases the counter
    counter = 0

    ul = arr[0][0]
    bl = arr[0][ncols-1]
    ur = arr[nrows - 1][0]
    br = arr[nrows - 1][ncols - 1]

    if ul < threshold:
        counter += 1
    
    if bl < threshold:
        counter += 1
    
    if ur < threshold:
        counter += 1
    
    if br < threshold:
        counter += 1

    # Returns True if the counter is higher than 2, False otherwise
    return True if counter > 2 else False


# PAINT ALPHA
# ------------------------------
# A method for painting the alpha channel with the given value and setting the opacity to maximum.

def paint_alpha(image, value):
    # Creates an array from image, copies it, and gets the shape of it
    arr = np.copy(np.asarray(image))
    (nrows, ncols, channels) = arr.shape

    # Goes through of all pixels and if the pixel is transparent, update the pixel
    for i in range(nrows):
        for j in range(ncols):
            if arr[i][j][1] == 0:
                arr[i][j][0] = value
                arr[i][j][1] = 255

    # Return the painted image
    return Image.fromarray(np.uint8(arr)).convert('RGB')


# OUTPUT TEXT
# ------------------------------
# This method returns a output text (a.k.a process report) that is generated with the given values in a stylish way.

def output_text(filename, coordinates, characters, background_type, thres, eight_connected, has_alpha):
    
    # Gets the labels from a dictionary and gets the length of it as well
    labels = list(characters.keys())
    label_count = len(characters)

    # Creates a dictionary for storing characters' counts and goes through all the characters
    count = {}
    
    for i in range(label_count):
        label = labels[i]
        character = characters.get(label)

        if character not in count.keys():
            count[character] = 1
        else:
            count[character] += 1

    # Initializes the text that has the path, the threshold, the labeling type, the existance of alpha layer, and the background type
    text = "____________________________________________\n|                                          |\n|           Character Identifier           |\n|              Process Report              |\n|                                          |\n|           [" + datetime.now().strftime("%d/%m/%Y %H:%M:%S") + "]          |\n|__________________________________________|\n\n____________________________________________\n|                                          |\n|              Input File Path             |\n|__________________________________________|\n\n" + filename + "\n\n____________________________________________\n|                                          |\n|             Process Arguments            |\n|__________________________________________|\n\nThreshold       : " + str(thres) + "\nLabeling Type   : " + ("8-Connected" if eight_connected else "4-Connected") + "\nAlpha Channel   : " + ("Exists" if has_alpha else "Not Exists") + "\nBackground Type : " + background_type + "\n\n____________________________________________\n|                                          |\n|             Character Counts             |\n|__________________________________________|\n\n"

    # If there is no characters, adds the conclusion into the text and returns it
    if len(count.keys()) == 0:
        text += "No characters were identified.\n\n"
        return text
    
    # Adds the counts of each character to the text
    character_counts = ""
    for i in sorted(count.keys()):
        character_counts += i + " : " + str(count.get(i)) + "\n"
        
    # Adds specifications (character, coordinates) of each label to the text
    text += character_counts + "\n____________________________________________\n|                                          |\n|     Bounding Boxes of Each Character     |\n|__________________________________________|\n\n"
   
    for i in range(label_count):
        label = labels[i]
        min_x = coordinates.get(label)[0][0]
        min_y = coordinates.get(label)[0][1]
        max_x = coordinates.get(label)[1][0]
        max_y = coordinates.get(label)[1][1]
        char = characters.get(label)

        text += "Label " + str(label) + "\n---------------\nIdentified Character: " + char + "\nUpper Left Corner   : (" + str(min_x) + ", " + str(min_y) + ")\nLower Right Corner  : (" + str(max_x) + ", " + str(max_y) + ")\n\n"
    
    # Returns the text
    return text




# Calls the main method after defining all methods
if __name__=='__main__':
    main()
