import base64
import os

def calculator(x, y):
    return (x + y)

def picture(foldername):
    encoded_strings_arr = []
    for filename in os.listdir('../../data/'+foldername):
        with open('../../data/'+foldername+'/'+filename, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
            encoded_strings_arr.append(encoded_string)
    return encoded_strings_arr