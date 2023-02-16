import random

import board
import busio
import RPi.GPIO as GPIO
from digitalio import DigitalInOut
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import sh1106
from adafruit_pn532.i2c import PN532_I2C
import time
import socket
from datetime import datetime, date
import json
import requests
import numpy as np
from picamera import PiCamera
from google.oauth2 import service_account
from google.auth.transport.requests import AuthorizedSession
import os
import re

# ANPR Server
ip = '192.168.43.52'
port = 1003

# DB
db = "https://embedded-systems-cf93d-default-rtdb.europe-west1.firebasedatabase.app/"

# Define the private key file (change to use your private key)
keyfile = "/home/pi/python/embedded-systems-cf93d-firebase-adminsdk-amky8-e0a50b80ba.json"

# Define the required scopes
scopes = [
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/firebase.database"
]

# Authenticate a credential with the service account (change to use your private key)
credentials = service_account.Credentials.from_service_account_file(keyfile, scopes=scopes)

# Use the credentials object to authenticate a Requests session.
authed_session = AuthorizedSession(credentials)

onlineUsers = set()


camera = PiCamera()

senddate = 0
sendtime = 0

buttonpress = False

url = "http://146.169.161.19:1004/upload"
imgDir = "/pictures"
# Create a socket object
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Bind to the port
get_ip = requests.get("https://api.ipify.org").content.decode('utf8')
print("Device IP:", get_ip)
s.bind((str(get_ip), 1050)) #ip of pi

# Add RFID
def rfiduserinout(card, inout):
    global senddate
    senddate = date.today()
    global sendtime
    sendtime = datetime.now().strftime("%H:%M:%S")
    path = f"rfidcards/{card}/{senddate}.json"

    read = authed_session.get(db + path)

    if read.json() is not None:
        data = read.json()
        if "Out" not in list(read.json().keys()):
            data["Out"] = []
        if "In" not in list(read.json().keys()):
            data["In"] = []


    else:
        data = {"In":[], "Out":[]}



    if inout == "in":

        data["In"].append(sendtime)

    else:
        data["Out"].append(sendtime)

    #print(data)
    resp = authed_session.put(db + path, json=data)

    if resp.ok:
        print("Ok")
    else:
        raise

def button_callback(channel):
    global buttonpress
    buttonpress = True
    print("Button pressed.")

# LEDs
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(27,GPIO.OUT)
GPIO.setup(17,GPIO.OUT)
GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.add_event_detect(18,GPIO.RISING,callback=button_callback, bouncetime=1000) # Setup event on pin 7 (GPIO 4) rising edge
red_led = 17
green_led = 27
high = GPIO.HIGH
low = GPIO.LOW

# RFID
i2cRFID = busio.I2C(board.SCL, board.SDA)
reset_pin = DigitalInOut(board.D6)
req_pin = DigitalInOut(board.D12)
pn532 = PN532_I2C(i2cRFID, debug=False, reset=reset_pin, req=req_pin)


# Configure PN532 to communicate with MiFare cards
pn532.SAM_configuration()


# Display
serial = i2c(port=1, address=0x3C)
device = sh1106(serial, rotate=0)

title1 = 'Welcome!'
title2 = 'Please scan ID...'
title3 = 'ACCEPTED'
title4 = 'PROCEED'
title5 = 'GOODBYE!'
titleNotAllowed1 = 'NUMBER PLATE'
titleNotAllowed2 = 'NOT IN SYSTEM'
titleIN = 'Status: IN'
titleRecommended = 'RECOMMENDED'
titleSpace = 'SPACE:'

UID_title = 'ID: '

def takePicture(uid):
    global senddate
    global sendtime
    sendtime = re.sub(":", "t", sendtime)

    camera.capture("pictures/{}_{}_{}.jpg".format(uid, senddate, sendtime))
    print("IMG Taken.")


def ANPR(uid):
    takePicture(uid)


    image_name = "pictures/{}_{}_{}.jpg".format(uid, senddate, sendtime)

    sendImage(image_name)

    plate = listen_for_response()
    print("num plate", plate)
    return plate

def led(colour, status):
    GPIO.output(colour, status)

def checkSignIn(uid):
    # Checks if signing in / out
    # If ID already signed in, remove ID from set
    if uid in onlineUsers:
        print('ID:', uid, '\tSigned Out')
        onlineUsers.remove(uid)
        return False
    # Else add ID to set
    else:
        print('ID:', uid, '\tSigned In')
        onlineUsers.add(uid)
        return True


def listen_for_response():
    # Start listening for incoming connections
    s.listen(1)

    # Wait for a connection
    print("Waiting for connection...")
    conn, addr = s.accept()
    print("Connection established from: ", addr)
    data = conn.recv(1024).decode()
    print("Received data: ", data)
    # Close the connection
    return data


def sendImage(path):
    name = os.path.basename(path)
    image = {"image": (name, open(path, "rb"), "image/jpeg")}
    response = requests.post(url, files=image)
    print(response)

def getfreetype(type_):
    path = "parkingspaces.json"
    query = "?orderBy=\"Free\"&equalTo=\"True\""
    resp = authed_session.get(db+path+query)
    free = resp.json()
    filtered = {}
    for space in free:
        if free[space]["Type"] == type_:
            filtered[space] = free[space]["Location"]
    return filtered


def getpreftype(card):
    prefpath = f"rfidcards/{card}/Preference.json"
    prefresp = authed_session.get(db + prefpath)
    pref = prefresp.json()
    if pref is None:
        pref = "Exit"
    typepath = f"rfidcards/{card}/Type.json"
    typeresp = authed_session.get(db + typepath)
    type_ = typeresp.json()
    if type_ is None:
        type_ = "Normal"
    return pref, type_


def recommendspace(pref, type_):
    spaces = getfreetype(type_)

    locations =[[0, 18], [36,18], [36,9]]
    if pref == "Exit":
        exit = np.array(locations[0])
    elif pref == "Car Park Entrance":
        exit = np.array(locations[1])
    else:
        exit = np.array(locations[2])

    mindist = 9999
    mindistspace = -1
    nums = list(spaces.keys())

    for num in nums:
        dist = np.linalg.norm(np.array(spaces[num]) - exit)
        if dist < mindist:
            mindist = dist
            mindistspace = num
    return mindistspace

def rfiduserinoutplate(card, inout, plate):
    date_ = date.today()
    path = f"rfidcards/{card}/{date_}.json"

    global sendtime
    sendtime = re.sub("t", ":", sendtime)

    read = authed_session.get(db + path)
    if read.json() is not None:
        data = read.json()
        if "Out" not in list(data.keys()):
            data["Out"] = []
        if "In" not in list(data.keys()): #not sure how this could happen
            data["In"] = []


    else:
        data = {"In":[], "Out":[]}

    if inout == "in":

        data["In"]  += [sendtime+"_"+plate] #data["In"].append(...)

    else:
        data["Out"] += [sendtime]
    print("sending back to db for card ",card, ": ", data)
    resp = authed_session.patch(db + path, json=data)

    if resp.ok:
        print("Ok")
    else:
        print(resp.json())
        raise

def getrfid(user):
    path = f"users/{user}/card.json"
    resp = authed_session.get(db+path)
    card = resp.json()
    return card

def numplateentry(plate):

    platepath = "numberplates.json"
    plateresp = authed_session.get(db+platepath)
    platedata = plateresp.json()
    plates = set(platedata.keys())
    if plate in plates:
        allowedplate = plate
        alloweduser = platedata[allowedplate]
    else:
        print("not allowed in")
        return False, None #user not allowed in

    # ALLOW USER IN
    rfid = getrfid(alloweduser)
    print("allowed")
    return True, rfid




def main():
    print("Waiting for RFID/NFC card...")
    led(red_led, high)

    while True:
        now = datetime.now().strftime("%H:%M")
        with canvas(device) as draw:
            draw.rectangle(device.bounding_box, outline="white", fill="black")
            draw.text((90, 8), now, fill="white")
            draw.text((10, 20), title1, fill="white")
            draw.text((10, 30), title2 , fill="white")

        # Check if a card is available to read
        uid = pn532.read_passive_target(timeout=0.5)

        #if button is pressed for ANPR:
        global buttonpress
        global sendtime
        global senddate
        signin = False
        if buttonpress:
            sendtime = datetime.now().strftime("%H:%M:%S")
            senddate = date.today()
            plate = ANPR(str(random.randrange(1,10000))) #get plate
            allowed, rfid = numplateentry(plate)
            if allowed:
                signin = checkSignIn(plate)
            
            if allowed and signin: #if allowed in and entering
                rfiduserinoutplate(rfid, "in", plate)
                led(green_led, high)
                led(red_led, low)
                pref, type_ = getpreftype(rfid)
                space = recommendspace(pref, type_) #get recommended space

                #Accepted Display
                with canvas(device) as draw:
                    draw.rectangle(device.bounding_box, outline="white", fill="black")
                    draw.text((90, 8), now, fill="white")
                    draw.text((40, 25), title3, fill="white")
                time.sleep(0.5)
                # Accepted + Proceed Display
                with canvas(device) as draw:
                    draw.rectangle(device.bounding_box, outline="white", fill="black")
                    draw.text((90, 8), now, fill="white")
                    draw.text((40, 25), title3, fill="white")
                    draw.text((44, 35), title4, fill="white")
                time.sleep(1)
                # Recommend space
                with canvas(device) as draw:
                    draw.rectangle(device.bounding_box, outline="white", fill="black")
                    draw.text((90, 8), now, fill="white")
                    draw.text((30, 25), titleRecommended, fill="white")
                    draw.text((40, 35), titleSpace + str(space), fill="white")
                time.sleep(5)

            elif allowed and not signin: # Allowed and exiting
                print('Exiting')
                led(green_led, high)
                led(red_led, low)
                rfiduserinout(rfid, "out")
                with canvas(device) as draw:
                    draw.rectangle(device.bounding_box, outline="white", fill="black")
                    draw.text((90, 8), now, fill="white")
                    draw.text((40, 25), title4, fill="white")
                    draw.text((44, 35), title5, fill="white")
                time.sleep(5)

            elif not allowed: # not allowed in
                print('Not Permitted')
                with canvas(device) as draw:
                    draw.rectangle(device.bounding_box, outline="white", fill="black")
                    draw.text((90, 8), now, fill="white")
                    draw.text((22, 25), titleNotAllowed1, fill="white")
                    draw.text((20, 35), titleNotAllowed2, fill="white")
                time.sleep(3)

            #set button to false at end

            buttonpress = False
            led(green_led, low)
            led(red_led, high)
            continue


        # Try again if no card is available.
        if uid is None:
            continue

        # If card is detected:
        # Set Green LED ON and Red LED OFF
        led(green_led, high)
        led(red_led, low)

        # Convert User ID into string format
        uid = [hex(i) for i in uid]
        uid_string = ''.join(format(int(i, 16), '02x') for i in uid)

        # Accepted Display
        with canvas(device) as draw:
            draw.rectangle(device.bounding_box, outline="white", fill="black")
            draw.text((90, 8), now, fill="white")
            draw.text((40, 25), title3, fill="white")
        time.sleep(0.5)

        # Accepted + Proceed Display
        with canvas(device) as draw:
            draw.rectangle(device.bounding_box, outline="white", fill="black")
            draw.text((90, 8), now, fill="white")
            draw.text((40, 25), title3, fill="white")
            draw.text((44, 35), title4, fill="white")

        # Checks Status IN/OUT
        if checkSignIn(uid_string) == True:
            titleIN = "Status: IN"
            goingin = True
            pref, type_ = getpreftype(uid_string)
            space = recommendspace(pref, type_)
        else:
            titleIN = "Status: OUT"
            rfiduserinout(uid_string, "out")
            goingin = False

        # Status IN/OUT Displayed
        with canvas(device) as draw:
            draw.rectangle(device.bounding_box, outline="white", fill="black")
            draw.text((90, 8), now, fill="white")
            draw.text((33, 30), titleIN , fill="white")
        time.sleep(1)

        # Recommended Space
        if titleIN == "Status: IN":
            with canvas(device) as draw:
                draw.rectangle(device.bounding_box, outline="white", fill="black")
                draw.text((90, 8), now, fill="white")
                draw.text((30, 25), titleRecommended , fill="white")
                draw.text((40, 35), titleSpace + str(space), fill="white")

            sendtime = datetime.now().strftime("%H:%M:%S")
            senddate = date.today()

            plate = ANPR(uid_string)
            if goingin:
                print("here")
                rfiduserinoutplate(uid_string, "in", plate)
            time.sleep(2)

        led(green_led, low)
        led(red_led, high)
main()
