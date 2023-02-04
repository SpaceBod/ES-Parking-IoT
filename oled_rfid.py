import board
import busio
from digitalio import DigitalInOut
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import sh1106
from adafruit_pn532.i2c import PN532_I2C
import time

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

title = 'Login'
UID_title = 'User: '

def run():
    with canvas(device) as draw:
        draw.text((0, 20), title, fill="white")
        draw.text((0, 30), (UID_title + "1204124") , fill="white")
        
def main():
    print("Waiting for RFID/NFC card...")
    while True:
        with canvas(device) as draw:
            draw.text((0, 20), title, fill="white")
            draw.text((0, 30), (UID_title + "Null") , fill="white")
        # Check if a card is available to read
        uid = pn532.read_passive_target(timeout=0.5)
        print(".", end="")
        # Try again if no card is available.
        if uid is None:
            continue
        print("Found card with UID:", [hex(i) for i in uid])
        uid = [hex(i) for i in uid]
        print(uid)
        uid_string = ''.join(format(int(i, 16), '02x') for i in uid)

        with canvas(device) as draw:
            draw.text((0, 20), title, fill="white")
            draw.text((0, 30), (UID_title + uid_string) , fill="white")
        time.sleep(2)
main()