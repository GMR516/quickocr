import os
from subprocess import call
from PIL import Image, ImageEnhance, ImageFilter
from mss import mss
import numpy as np
import pyautogui
import string
import time
import cv2
import pytesseract
from secure_delete import secure_delete
import pyperclip
from pynput.keyboard import Key, Listener

ShouldRun = True

secure_delete.secure_random_seed_init()
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

screen_shot = mss()

# crop screenshot of screen so it is only the top left
def return_screenshot(mon={"top": 100, "left": 50, "width": 1820, "height": 750}):
    screen_shot.get_pixels(mon)
    img = Image.frombytes("RGB", (screen_shot.width, screen_shot.height), screen_shot.image)
    img = np.array(img)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return img


def on_press(key):
    #print('{0} pressed'.format(key))
    if key == Key.shift_r:
        return False

def on_release(key):
    global ShouldRun
    #print('{0} release'.format(key))
    if key == Key.esc:
        ShouldRun = False
        return False


print("Press RIGHT shift to capture | ESC to exit")
while(ShouldRun):
    print("Ready")
    with Listener(on_press=on_press,
    on_release=on_release) as listener:
        listener.join()

    #Would be set false if we just set it 
    if ShouldRun is False:
        break

    cv2.imwrite("cap.png", return_screenshot())

    # bash call for tessract to analyze image
    #call(["tesseract", "picture.png", "read_this", "--psm 6"])
    imageToProcess = Image.open('cap.png')

    #imageToProcess = imageToProcess.filter(ImageFilter.MedianFilter())

    #enhancer = ImageEnhance.Contrast#(imageToProcess)
    #imageToProcess = enhancer.enhance(5)
    #
    #colorChangerEnhancer = ImageEnhance.Color#(imageToProcess)
    #imageToProcess = colorChangerEnhancer.#enhance(0.2)
    #
    #brightness = ImageEnhance.Brightness#(imageToProcess)
    #imageToProcess = brightness.enhance(0.9)
    #
    #sharpness = ImageEnhance.Sharpness#(imageToProcess)
    #imageToProcess = sharpness.enhance(20)
    #
    ##imageToProcess = imageToProcess.convert#('1')
    #imageToProcess.save('cap.png')
    #

    textToType = pytesseract.image_to_string(imageToProcess, lang='eng', config='--psm 1 --oem 3') #needed space at end

    #with open('read_this.txt', 'w') as filehandle:
    #    filehandle.write(textToType)
    #
    ## read analyzed picture-text back in 
    #with open("read_this.txt", "r") as file:
    #    type_out = file.read()

    #type_out = clean_typos(type_out)
    type_out = textToType

    #print("\n" + type_out)

    pyperclip.copy(type_out)

    # type the text
    #pyautogui.typewrite(type_out, interval=SPEED)

    #keep a log NOT SECURE
    #with open("log.txt", "a") as file:
    #    file.write("\n" + type_out)


    secure_delete.secure_delete('cap.png')
    secure_delete.secure_delete('log.txt')