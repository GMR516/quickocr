import os
import re
from subprocess import call
from PIL import Image, ImageEnhance, ImageFilter
from mss import mss
import numpy as np
import pyautogui
import string
import time
import cv2
import pytesseract
import pyperclip
from pynput.keyboard import Key, Listener
import subprocess
from urllib.parse import quote

StopProgram = False
ShouldRun = False

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# crop screenshot of screen so it is only the top left
#def return_screenshot(mon={"top": 100, "left": 50, "width": 1820, "height": 750}):
def return_screenshot():
    with mss() as sct:
        # The screen part to capture
        monitor = {"top": 290, "left": 40, "width": 380, "height": 170}
        # Grab the data
        sct_img = sct.grab(monitor)
        img = Image.frombytes("RGB", (sct_img.width, sct_img.height), sct_img.rgb)
        img = np.array(img)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        return img


def on_press(key):
    #print('{0} pressed'.format(key))
    # this stops the processing of everything and prevents the key from being typed
    if key == Key.f12:
        ShouldRun = False
        # doesn't pass press to on_release
        #return False

def on_release(key):
    global ShouldRun, StopProgram
    ShouldRun = False
    #print('{0} release'.format(key))
    # handle right shift taking a sc and text searching
    if key == Key.shift_r:
        ShouldRun = True
        return False

    # ... then since we would reset the variable here anyway on release
    if key == Key.f12:
        StopProgram = True
        return False


print("Press RIGHT shift to capture | ESC to exit")
while(StopProgram == False):
    print("Ready")
    with Listener(on_press=on_press,
    on_release=on_release) as listener:
        listener.join()
    if StopProgram == True:
        break
    if ShouldRun == False: 
        continue

    cv2.imwrite("cap.png", return_screenshot())

    # bash call for tessract to analyze image
    #call(["tesseract", "picture.png", "read_this", "--psm 6"])
    imageToProcess = Image.open('cap.png')

    #imageToProcess = imageToProcess.filter(ImageFilter.MedianFilter())

    enhancer = ImageEnhance.Contrast(imageToProcess)
    imageToProcess = enhancer.enhance(2)
    
    colorChangerEnhancer = ImageEnhance.Color(imageToProcess)
    imageToProcess = colorChangerEnhancer.enhance(2)
    #
    #brightness = ImageEnhance.Brightness(imageToProcess)
    #imageToProcess = brightness.enhance(0.5)
    #
    #sharpness = ImageEnhance.Sharpness#(imageToProcess)
    #imageToProcess = sharpness.enhance(20)
    #
    ##imageToProcess = imageToProcess.convert#('1')
    imageToProcess.save('cap.png')
    #

    textToType = pytesseract.image_to_string(imageToProcess, lang='eng', config='--psm 1 --oem 3') #needed space at end
    #textToType = pytesseract.image_to_string(imageToProcess, lang='eng')
    #with open('read_this.txt', 'w') as filehandle:
    #    filehandle.write(textToType)
    #
    ## read analyzed picture-text back in 
    #with open("read_this.txt", "r") as file:
    #    type_out = file.read()

    #type_out = clean_typos(type_out)
    type_out = textToType.strip()

    #print("\n" + type_out)
    print(type_out)
    # use regular expression to extract the middle portion of the text
    the_question_text = re.search(r'\n\n(.(?:.|\n)+\?)', type_out)
    if the_question_text:
        the_question_text = the_question_text.group(1)
    else:
        the_question_text = type_out
    # check if the middle portion ends with a question mark
    ends_with_question = the_question_text.strip().endswith('?')
    # fix line breaks, if line broken in image means they used a space and it went to next line
    the_question_text = the_question_text.replace('\n', ' ').replace('\r', ' ')
    # remove last character from the_question_text if it ends with a question mark
    print(the_question_text)
    if ends_with_question == True:
        print("WTF??")
        the_question_text = the_question_text[:-1]
        print(the_question_text)
    print(f"{the_question_text}\nEnds with a question mark: {ends_with_question}")
    # type the text
    #pyautogui.typewrite(type_out, interval=SPEED)
    pyperclip.copy(the_question_text)
    url = "https://www.google.com/search?q=" + the_question_text
    #url = "https://www.google.com/search?q=" + quote(the_question_text)
    print(url)
    subprocess.Popen(['explorer', url])