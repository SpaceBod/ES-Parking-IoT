# import libraries
import board
import busio
import adafruit_tca9548a
import time
import json
from smbus2 import SMBus
import adafruit_vl53l0x

# define database parameters
from google.oauth2 import service_account
from google.auth.transport.requests import AuthorizedSession
db = "https://embedded-systems-cf93d-default-rtdb.europe-west1.firebasedatabase.app/"
keyfile = "embedded-systems-cf93d-firebase-adminsdk-amky8-e0a50b80ba.json"
scopes = [
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/firebase.database"
]

# use service account credentials to access the database
credentials = service_account.Credentials.from_service_account_file(keyfile, scopes=scopes)

authed_session = AuthorizedSession(credentials)

# define the sensor register addresses
STATUS_REG = 0x00
MEAS_MODE_REG = 0x01
ALG_RESULT_DATA_REG = 0x02
ENV_DATA_REG = 0x05
APP_START_REG = 0xF4
ONE_SECOND = 0x01

bus = SMBus(1)
address = 0x5b

eCO2 = 0
TVOC = 0

trackco2 = [0,0,0]
tracktvoc = [0,0,0]


# initiate I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# initiate TCA9548A (multiplexer)
tca = adafruit_tca9548a.TCA9548A(i2c)
tca0 = tca[0]
tca1 = tca[1]
tca2 = tca[2]

# initiate VL53L0X sensors
vl53_0 = adafruit_vl53l0x.VL53L0X(tca0)
vl53_1 = adafruit_vl53l0x.VL53L0X(tca1)
vl53_2 = adafruit_vl53l0x.VL53L0X(tca2)


# define the function to update the status of parking spaces in the database
def updatefree(space, status):
    path = f"parkingspaces/{space}.json"

    if status == 'true':
        update = {"Free": "True"}
    else:
        update = {"Free": "False"}
        
    resp = authed_session.patch(db + path, json=update)

    if resp.ok:
        print("Updated free status of space {}".format(space))
    else:
        raise


# define the function to upload air quality data
def statstodb(co2, tvoc):
    path = "stats.json"
    data = {"co2": str(co2), "tvoc": str(tvoc)}
    resp = authed_session.patch(db+path, json=data)
    if resp.ok:
        print("added", data)
    else:
        print(resp.json())

        
# define the function to retrieve temperature and humidity data
def gettemphum():
    path = "stats.json"
    resp = authed_session.get(db+path)
    respjson = resp.json()
    temp = respjson['temp']
    hum = respjson['humidity']
    return float(temp), float(hum)

# set up the air quality sensor
def startup():
    bus.write_i2c_block_data(address, APP_START_REG, []) #start into firmware mode
    meas_mode = (ONE_SECOND << 4) | (0 << 3)  # every 1 second, dont want interrupts
    bus.write_byte_data(address, MEAS_MODE_REG, meas_mode)

# compensate for temp & humidity
def compensate(hum ,temp):

    h = int(hum * 512)
    t = int((temp + 25) * 512)
    env = [(h >> 8), (h & 0xFF), (t >> 8), (t & 0xFF)]
    try:
        bus.write_i2c_block_data(address, ENV_DATA_REG, env)
    except:
        print("error in compensating")

# see if sensor is ready to give data:
def ready():
    try:
        stat = bus.read_byte_data(address, STATUS_REG)
    except:
        print('error in ready')
        return False
    ready = 0b00001000 & stat
    if ready == 0:
        return False
    else:
        return True

# read data from the air quality sensor using the I2C communication protocol
def read():
    try:
        data = bus.read_i2c_block_data(address, ALG_RESULT_DATA_REG, 8)
    except:
        print('error in reading')
        return None, None
    co2 = (data[0] << 8) | (data[1])
    tvoc = (data[2] << 8) | (data[3])

    if 400 <= co2 <=8192: #values can be out of sensor range, idk why
        eCO2 = co2
    else:
        eCO2 = None
    if 0 <= tvoc <= 1187:
        TVOC = tvoc
    else:
        TVOC = None

    return eCO2, TVOC

def airquality(cur_hum, cur_temp, oldco2, oldtvoc):
    compensate(cur_hum, cur_temp)  # defaults:  humidity, temp
    if ready():
        eC02, TVOC = read()
        if eC02 is not None:  # if reading hasnt gone wrong, update values
            trackco2.pop()
            trackco2.insert(0,eC02)
            sortedc = trackco2.copy()
            sortedc.sort()
            oldco2 = sortedc[1] #median filter to remove erraneous values
        if TVOC is not None:
            tracktvoc.pop()
            tracktvoc.insert(0, TVOC)
            sortedt = tracktvoc.copy()
            sortedt.sort()
            oldtvoc = sortedt[1]

        statstodb(oldco2, oldtvoc)
    else:
        statstodb(oldco2, oldtvoc)  # give old vals if not ready
    return oldco2, oldtvoc

# initiate the parking spots as vacant ('true')
flag_0 = 'true'
flag_1 = 'true'
flag_2 = 'true'

oldco2 = 0
oldtvoc = 0
startup() #startup air quality sensor

# read VL53L0X data and update the vacancy status of the parking spots
while True:
    flag0 = flag_0
    flag1 = flag_1
    flag2 = flag_2

    try:
        distance_0 = vl53_0.range #this sensor seems to be failing, others are fine
        distance_1 = vl53_1.range
        distance_2 = vl53_2.range
    except:
        print('error in reading range sensors')
    
    if distance_0 < 1000:
        flag_0 = 'false'

        if flag_0 != flag0:
            print('11 becomes occupied')
            updatefree(11, flag_0)
    else:
        flag_0 = 'true'
        if flag_0 != flag0:
            print('11 becomes vacant')
            updatefree(11, flag_0)
    
    if distance_1 < 1000:
        flag_1 = 'false'

        if flag_1 != flag1:
            print('2 becomes occupied')
            updatefree(2, flag_1)
    else:
        flag_1 = 'true'
        if flag_1 != flag1:
            print('2 becomes vacant')
            updatefree(2, flag_1)

    if distance_2 < 1000:
        flag_2 = 'false'

        if flag_2 != flag2:
            print('3 becomes occupied')
            updatefree(3, flag_2)
    else:
        flag_2 = 'true'
        if flag_2 != flag2:
            print('3 becomes vacant')
            updatefree(3, flag_2)
    
    # read temperature and humidity data from database
    curr_temp, curr_hum = gettemphum()
    # update the air quality data into database
    oldco2, oldtvoc = airquality(curr_hum, curr_temp, oldco2, oldtvoc)

    time.sleep(5)
