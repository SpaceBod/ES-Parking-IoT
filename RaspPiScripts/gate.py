import board
import busio
import RPi.GPIO as GPIO
from digitalio import DigitalInOut
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import sh1106
from adafruit_pn532.i2c import PN532_I2C
import time
from datetime import datetime, date
import json
import requests
import numpy as np
from google.oauth2 import service_account
from google.auth.transport.requests import AuthorizedSession
from picamera import PiCamera
from RPi import GPIO
import socket

#camera settings
camera = PiCamera()
#camera.brightness = 55
camera.awb_mode = 'incandescent' 
camera.iso = 200
camera.contrast = 70
camera.shutter_speed = 6000 # 0.006 seconds
camera.exposure_mode = 'off'

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

# Add RFID
def rfiduserinout(card, inout):
    date_ = date.today()
    path = f"rfidcards/{card}/{date_}.json"

    read = requests.get(db + path)

    if read.json() is not None:
        data = read.json()
        if "Out" not in list(read.json().keys()):
            data["Out"] = []
        if "In" not in list(read.json().keys()):
            data["In"] = []
    else:
        data = {"In":[], "Out":[]}

    if inout == "in":

        data["In"].append(datetime.now().strftime("%H:%M:%S"))

    else:
        data["Out"].append(datetime.now().strftime("%H:%M:%S"))
    
    #print(data)
    resp = requests.put(db + path, json=data)

    if resp.ok:
        print("Ok")
    else:
        raise

# LEDs
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(27,GPIO.OUT)
GPIO.setup(17,GPIO.OUT)
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
titleIN = 'Status: IN'
titleRecommended = 'RECOMMENDED'
titleSpace = 'SPACE:'

UID_title = 'ID: '

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


def getfree():
    path = "parkingspaces.json"
    query = "?orderBy=\"Free\"&equalTo=\"True\""
    resp = requests.get(db + path + query)
    free = resp.json()
    num = free.keys()
    num = list(map(int, num))
    num.sort()
    #print(spaces)
    #for space in spaces:
        #print(free[space])
    return free, num
    

def getpref(card):
    path = f"rfidcards/{card}.json"
    resp = authed_session.get(db + path)
    pref = resp.json()["Preference"]
    return pref

def recommendspace(pref):
    free, num = getfree()
    rec = {}
    locations =[[0, 18], [36,18], [36,9]]
    if pref == "Exit":
        exit = np.array(locations[0])
    elif pref == "Car Park Entrance":
        exit = np.array(locations[1])
    else:
        exit = np.array(locations[2])
    for n in num:
        rec[n] = free[str(n)]['Location']
    rec = np.array(rec)
    mindist = 9999
    mindistspace = -1
    for i in rec:
        dist = np.linalg.norm(rec[i] - exit)
        if dist < mindist:
            mindist = dist
            mindistspace = i
    return mindistspace


def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("client socket")
    client.connect(('172.20.10.6', 1003))
    print("connected")
    
    
    print("Waiting for RFID/NFC card...")
    led(red_led, high)
    
    while True:
        image_number = 0
        
        now = datetime.now().strftime("%H:%M")
        with canvas(device) as draw:
            draw.rectangle(device.bounding_box, outline="white", fill="black")
            draw.text((90, 8), now, fill="white")
            draw.text((10, 20), title1, fill="white")
            draw.text((10, 30), title2 , fill="white")
            
        # Check if a card is available to read
        uid = pn532.read_passive_target(timeout=0.5)
        
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
            rfiduserinout(uid_string, "in")
            space = recommendspace(getpref(uid))
        else:
            titleIN = "Status: OUT"
            rfiduserinout(uid_string, "out")
        
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
            
            camera.capture("/home/pi/python/pictures/{}.jpg".format(image_number))
            time.sleep(0.5)
            
            file = open('/home/pi/python/pictures/{}.jpg'.format(image_number), 'rb')
            image_data = file.read()

            while image_data:
                client.sendall(image_data)
                #image_data = file.read()

            file.close()
   #         client.close()
            image_number += 1
            
        led(green_led, low)
        led(red_led, high)
main()
