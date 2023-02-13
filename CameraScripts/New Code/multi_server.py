from flask import Flask, request
import os
import shutil
from multiprocessing import Process
from operator import itemgetter
import time

saveDir = "/Users/admin/Desktop/piServer/Downloads"
folder_name = "Scanned"

app = Flask(__name__)
@app.route("/upload", methods=["POST"])

def upload():
    image = request.files['image']
    dir = os.path.join(saveDir, image.filename)
    image.save(dir)
    return "Image uploaded successfully - " + image.filename

def runServer():
    app.run(debug=True, use_reloader=False)


def getOldestFile(dir):
    # Get a list of all files in the directory
    files = [f for f in os.listdir(dir) if os.path.isfile(os.path.join(dir, f))]
    # Get the creation time of each file
    file_info = [(f, os.path.getctime(os.path.join(dir, f))) for f in files]
    # Sort the files by their creation time
    sorted_files = sorted(file_info, key=itemgetter(1))
    return sorted_files[0][0]

def loadANPR():
    while True:
        if len(os.listdir(saveDir)) > 0:
            imgFile = getOldestFile(saveDir)
            
            # RUN PLACE REC FUNCTION
            plateIMG = os.path.join(saveDir, imgFile)
            print(f"Running ANPR on {imgFile}")
            # ----> insert plate function + remove time.sleep(0.5)
            time.sleep(0.5)
            
            # Move processed image to another folder
            if not os.path.exists(folder_name):
                os.makedirs(folder_name)
            shutil.move(plateIMG, os.path.join(folder_name, imgFile))
        
        else:
            print("Waiting for images...")
            time.sleep(1)

if __name__ == "__main__":
    p1 = Process(target=runServer)
    p2 = Process(target=loadANPR)
    p1.start()
    p2.start()



