import cv2
import imutils
import numpy as np
import string
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
import time
import re
import requests
import json
from paddleocr import PaddleOCR, draw_ocr
import re
from google.oauth2 import service_account
from google.auth.transport.requests import AuthorizedSession
from flask import Flask, request
import os
import shutil
from multiprocessing import Process
from operator import itemgetter
import time
import socket

pi_ip = '146.169.137.152'
port = 1050

def send_back_number(ip, port, numberplate):
    #Send the number plate string back to the pi
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((ip, port))
            
    message = numberplate
    client_socket.sendall(message.encode('utf-8'))
            
    client_socket.close()

db = "https://embedded-systems-cf93d-default-rtdb.europe-west1.firebasedatabase.app/"
keyfile = "C:\\Users\\Caidudu\\PycharmProjects\\ES-SyntaxError\\CameraScripts\\embedded-systems-cf93d-firebase-adminsdk-amky8-e0a50b80ba.json"
scopes = [
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/firebase.database"
]

credentials = service_account.Credentials.from_service_account_file(keyfile, scopes=scopes)
authed_session = AuthorizedSession(credentials)


def result_process(init_plate_number):
    #process OCR output number and put into UK Standard Regex test
    table = str.maketrans('', '', string.ascii_lowercase)
    init_plate_number = init_plate_number.translate(table)
    init_plate_number = init_plate_number.replace('\n', '').replace('\r', '').replace(' ', '').replace(':', '')
    init_plate_number = init_plate_number.upper()
    # print('re.findall(r"\d\d\d",init_plate_number[-4:-1]):',re.findall(r"\d\d\d",init_plate_number[-4:-1]))

    if len(init_plate_number) == 2:
        print('special plate detected:')
        if  init_plate_number[1]== 'I' or init_plate_number[1]== 'O':
            init_plate_number = init_plate_number.replace('I', '1',1)
            
            
            # print('on [1] I/O/B replaced')
            # print('plate numer for real is :',init_plate_number)
            # print('loaded plate type:',type(init_plate_number))
            
        if init_plate_number[1]== 'B':
             init_plate_number = init_plate_number.replace('B', '8', 1)   
        if init_plate_number[1]== 'O':
            init_plate_number = init_plate_number.replace('O', '0', 1)
        else:
            # print('no I/O/B impact')   
            # print('plate numer for real is :',init_plate_number)
            # print('loaded plate type:',type(init_plate_number))
            return init_plate_number
    


        
    if len(init_plate_number) == 7 and not re.findall(r"\d\d\d",init_plate_number[-4:-1]) :
        if  init_plate_number[2]== 'I' or init_plate_number[2]== 'O'or init_plate_number[2]== 'B':
            init_plate_number = init_plate_number.replace('I', '1',1)
            init_plate_number = init_plate_number.replace('O', '0', 1)
            init_plate_number = init_plate_number.replace('B', '8', 1)
            # print('on [2] I/O/B replaced')
            
        if  init_plate_number[3]== 'I' or init_plate_number[3]== 'O'or init_plate_number[3]== 'B':
            init_plate_number = init_plate_number.replace('I', '1',1)
            init_plate_number = init_plate_number.replace('O', '0', 1)
            init_plate_number = init_plate_number.replace('B', '8', 1)
            # print('on [3] I/O/B replaced')
            
        if  init_plate_number[4]== '0' or init_plate_number[5]== '0'or init_plate_number[6]== '0':
            
    
            init_plate_number = init_plate_number.replace('0', 'O')
            
            # print('on [4]/[5]/[6] I/O/B replaced')
        # else:
        #     print(' no impact')    
    if len(init_plate_number) == 7 and  re.findall(r"\d\d\d",init_plate_number[-4:-1]) :
            init_plate_number = init_plate_number.replace('\n', '1').replace('\r', '1').replace(' ', '1')
    
    processed_plate_number = init_plate_number[0:7]
    return processed_plate_number
        




def plate_rec(img_path):
    img = cv2.imread(img_path)
    # print('loaded img type:',type(img))

    # print('image imported')

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) #convert to grey scale
    gray = cv2.bilateralFilter(gray, 11, 17, 17) #Blur to reduce noise
    edged = cv2.Canny(gray, 30, 200) #Perform Edge detection



    cnts = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:10]

    screenCnt = None

    # print('image filtered')
    for c in cnts:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.018 * peri, True)
        if len(approx) == 4:
            screenCnt = approx

        if screenCnt is None: # curved plate cases
            detected = 0
            # print ("No contour detected, trying to crop and put into OCR anyway:")
            cv2.imwrite("./plate.png",img)
            

            #SimpleTex_OCR
            start = time.time()
            # print('loading OCR')
            api_url = "https://server.simpletex.cn/api/ocr/v1"
            header = {"token": "WdugS2SXnN1XslWJa30ow56dho9PcDKa8FY1oQigvd56U3eglQrbLc0WH2qhV8em"}
            file = []
            file.append(("file", ("test.png", open('./plate.png', 'rb'))))
            res = requests.post(api_url, files=file, headers=header)
            # print(res.status_code)
            # print(json.loads(res.text))
            res_dict = json.loads(res.text)
            # print('OCR Process finished')
            end = time.time()
            print('OCR Process time:', end - start)
        
            #process OCR output number and put into UK Standard Regex test
            init_plate_number = res_dict['res']['result']
            # print('contor not found! raw data',init_plate_number)
            # print('raw data len',len(init_plate_number))
            # print('raw data [4:6]',init_plate_number[-4:-1])
            
            processed_plate_number = result_process(init_plate_number)
        
            # print('processed number now is:',processed_plate_number)
            #UK car plate format: two letters, two numbers, a space and three further letters
            if re.findall(r"(^[A-Z]{2}[0-9]{2}\s?[A-Z]{3}$)|(^[A-Z][0-9]{1,3}[A-Z]{3}$)|(^[A-Z]{3}[0-9]{1,3}[A-Z]$)|(^[0-9]{1,4}[A-Z]{1,2}$)|(^[0-9]{1,3}[A-Z]{1,3}$)|(^[A-Z]{1,2}[0-9]{1,4}$)|(^[A-Z]{1,3}[0-9]{1,3}$)|(^[A-Z]{1,3}[0-9]{1,4}$)|(^[0-9]{3}[DX]{1}[0-9]{3}$)",processed_plate_number):
                # print('regex passed!')
                # print('plate numer for real is :',processed_plate_number)
                # print('loaded plate type:',type(processed_plate_number))
                return processed_plate_number
            else:
                return 0

            
        else:
            detected = 1


        if detected == 1:
            cv2.drawContours(img, [screenCnt], -1, (0, 255, 0), 3)
            mask = np.zeros(gray.shape,np.uint8)
            new_image = cv2.drawContours(mask,[screenCnt],0,255,-1,)
            new_image = cv2.bitwise_and(img,img,mask=mask)
            (x, y) = np.where(mask == 255)
            (topx, topy) = (np.min(x), np.min(y))
            (bottomx, bottomy) = (np.max(x), np.max(y))
            Cropped = gray[topx+5:bottomx-5, topy+5:bottomy-5]
            
            # text = pytesseract.image_to_string(Cropped, config='--psm 11 ')
            # text = text.replace('I','1')
            
            # cv2.imshow('number plate', Cropped)
            cv2.imwrite("./plate.png",Cropped)
            # cv2.waitKey(0)
            
            #SimpleTex_OCR
            start = time.time()
            print('loading SimpleTex OCR')
            api_url = "https://server.simpletex.cn/api/ocr/v1"
            header = {"token": "WdugS2SXnN1XslWJa30ow56dho9PcDKa8FY1oQigvd56U3eglQrbLc0WH2qhV8em"}
            file = []
            file.append(("file", ("test.png", open('./plate.png', 'rb'))))
            res = requests.post(api_url, files=file, headers=header)
            # print(res.status_code)
            # print(json.loads(res.text))
            res_dict = json.loads(res.text)
            print('Simpleyex OCR Process finished')
            end = time.time()
            print('OCR processing time:',end-start)
            
            # text = pytesseract.image_to_string(Cropped, config='--psm 11 ')
            
            #process OCR output number and put into UK Standard Regex test
            init_plate_number = res_dict['res']['result']
            # print('contor found! raw data',init_plate_number)
            
            processed_plate_number = result_process(init_plate_number)

        
            # print('processed number now is:',processed_plate_number)    

            
            #UK car plate format: two letters, two numbers, a space and three further letters
            if re.findall(r"(^[A-Z]{2}[0-9]{2}\s?[A-Z]{3}$)|(^[A-Z][0-9]{1,3}[A-Z]{3}$)|(^[A-Z]{3}[0-9]{1,3}[A-Z]$)|(^[0-9]{1,4}[A-Z]{1,2}$)|(^[0-9]{1,3}[A-Z]{1,3}$)|(^[A-Z]{1,2}[0-9]{1,4}$)|(^[A-Z]{1,3}[0-9]{1,3}$)|(^[A-Z]{1,3}[0-9]{1,4}$)|(^[0-9]{3}[DX]{1}[0-9]{3}$)",processed_plate_number):
                # print('regex passed!')
                # print('plate numer for real is :',processed_plate_number)
                # print('loaded plate type:',type(processed_plate_number))
                return processed_plate_number
            else:
                return 0
                
            
saveDir = "C:\\Users\\Caidudu\\PycharmProjects\\ES-SyntaxError\\CameraScripts\\loaded_imgs"
folder_name = "Scanned"
app = Flask(__name__)
@app.route("/upload", methods=["POST"])
def upload():
    image = request.files['image']
    dir = os.path.join(saveDir, image.filename)
    image.save(dir)
    return "Image uploaded successfully - " + image.filename


def runServer():
    app.run(debug=True, use_reloader=False, port=1004, host='146.169.169.71')


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
            print(plateIMG)
            numberplate = plate_rec(plateIMG)
            print(numberplate)
            
            send_back_number(pi_ip, port, str(numberplate))
           
            # Move processed image to another folder
            if not os.path.exists(folder_name):
                os.makedirs(folder_name)
            shutil.move(plateIMG, os.path.join(folder_name, imgFile))

        else:
            print("Waiting for images...")
            time.sleep(1)

if __name__ == '__main__':
    # filename = ('34d6a43e_2023-02-11_18t14t40.png')
    # numberplate = plate_rec(filename)
    # print(numberplate)
    
    p1 = Process(target=runServer)
    p2 = Process(target=loadANPR)
    p1.start()
    p2.start()








