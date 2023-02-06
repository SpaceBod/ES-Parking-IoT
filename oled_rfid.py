import board
import busio
from digitalio import DigitalInOut
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import sh1106
from adafruit_pn532.i2c import PN532_I2C
import time
from datetime import datetime


# RFID setup
i2cRFID = busio.I2C(board.SCL, board.SDA)
reset_pin = DigitalInOut(board.D6)
req_pin = DigitalInOut(board.D12)
pn532 = PN532_I2C(i2cRFID, debug=False, reset=reset_pin, req=req_pin)
# Configure PN532 to communicate with MiFare cards
pn532.SAM_configuration()


# Display setup
serial = i2c(port=1, address=0x3C)
device = sh1106(serial, rotate=0)

# Text for display
title1 = 'Welcome!'
title2 = 'Please scan ID...'
title3 = 'ACCEPTED'
title4 = 'PROCEED'
titleIN = 'Status: IN'

# Checks if ID card is already signed in
def checkSignIn(uid):

    with open('status.txt', 'r') as file:
        content = file.read()
        file.close()
    
    # If ID already signed in, remove ID from status.txt
    if uid in content:
        print('Signed Out')
        new_content = content.replace(uid, '')
        with open('status.txt', 'w') as file:
            file.write(new_content)
            file.close()
        return False
    # Else add ID to status.txt
    else:
        print('Signed In')
        with open('status.txt', 'a') as file:
            file.write(uid)
            file.close()
        return True


def main():

    with open('status.txt', 'w') as f:
        pass
        
    print("Waiting for RFID/NFC card...")
    
    statusFile = open('status.txt', 'a')
    
    while True:
        now = datetime.now().strftime("%H:%M")
        
        # Idle screen
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
            
        uid = [hex(i) for i in uid]
        uid_string = ''.join(format(int(i, 16), '02x') for i in uid)
        print("UID:", uid_string)
        
        # Accepted screen
        with canvas(device) as draw:
            draw.rectangle(device.bounding_box, outline="white", fill="black")
            draw.text((90, 8), now, fill="white")
            draw.text((40, 25), title3, fill="white")
        time.sleep(0.5)
        
        # Accpeted + Proceed screen
        with canvas(device) as draw:
            draw.rectangle(device.bounding_box, outline="white", fill="black")
            draw.text((90, 8), now, fill="white")
            draw.text((40, 25), title3, fill="white")
            draw.text((44, 35), title4, fill="white")
        time.sleep(1)
        
        # Get ID status
        if checkSignIn(uid_string) == True:
            titleIN = "Status: IN"
        else:
            titleIN = "Status: OUT"
        
        # Status screen
        with canvas(device) as draw:
            draw.rectangle(device.bounding_box, outline="white", fill="black")
            draw.text((90, 8), now, fill="white")
            draw.text((36, 30), titleIN , fill="white")
        time.sleep(2)
main()
