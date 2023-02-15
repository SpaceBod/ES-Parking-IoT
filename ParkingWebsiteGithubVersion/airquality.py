from smbus2 import SMBus
import time
from google.oauth2 import service_account
from google.auth.transport.requests import AuthorizedSession
db = "https://embedded-systems-cf93d-default-rtdb.europe-west1.firebasedatabase.app/"
keyfile = "embedded-systems-cf93d-firebase-adminsdk-amky8-e0a50b80ba.json"
scopes = [
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/firebase.database"
]

credentials = service_account.Credentials.from_service_account_file(keyfile, scopes=scopes)

authed_session = AuthorizedSession(credentials)

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

def statstodb(temp, hum, co2, tvoc):
    path = "stats.json"
    data = {"temp": str(temp), "humidity": str(hum), "co2": str(co2), "tvoc": str(tvoc)}
    resp = authed_session.patch(db+path, json=data)
    if resp.ok:
        print("added", data)
    else:
        print(resp.json())


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
            oldco2 = eC02
        if TVOC is not None:
            oldtvoc = TVOC

        statstodb(1, 2, oldco2, oldtvoc)
    else:
        statstodb(1, 2, oldco2, oldtvoc)  # give old vals if not ready
    return oldco2, oldtvoc

if __name__ == '__main__':
    oldco2 = 0
    oldtvoc = 0
    startup() #startup air quality sensor
    while True:        
        oldco2, oldtvoc = airquality(50, 25, oldco2, oldtvoc) #change 50 for current humidity and 25 for current temp
        time.sleep(30) #dont need to update this particularly often


