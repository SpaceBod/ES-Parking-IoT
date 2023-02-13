import requests
import os

url = "http://127.0.0.1:5000/upload"
imgDir = "/Users/admin/Desktop/piServer/img"

def sendImage(path):
    name = os.path.basename(path)
    image = {"image": (name, open(path, "rb"), "image/jpeg")}
    response = requests.post(url, files=image)
    print(response.text)

# Code Testing - send all images in folder
images = [f for f in os.listdir(imgDir) if os.path.isfile(os.path.join(imgDir, f))]
for image in images:
    image_path = os.path.join(imgDir, image)
    sendImage(image_path)
