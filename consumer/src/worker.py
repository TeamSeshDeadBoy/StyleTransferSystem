import base64
from dotenv.main import load_dotenv
import os

load_dotenv()
volume_path = os.environ["VOLUME_ADRESS"]

def calculator(x, y):
    return (x + y)

def picture(foldername):
    encoded_strings_arr = []
    for filename in os.listdir('/data/user_data/'+foldername):
        with open(volume_path+foldername+'/'+filename, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
            encoded_strings_arr.append(encoded_string)
    return encoded_strings_arr