import base64


def calculator(x, y):
    return (x + y)

def picture(filename):
    with open('/data/'+filename, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    return encoded_string