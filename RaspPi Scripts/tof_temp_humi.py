# import libraries
import board
import busio
import adafruit_tca9548a
import time
import json
import smbus2
import adafruit_vl53l0x
import adafruit_si7021

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

# initiate I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# initiate TCA9548A (multiplexer)
tca = adafruit_tca9548a.TCA9548A(i2c)
tca1 = tca[1]
tca5 = tca[5]
tca6 = tca[6]

# initiate VL53L0X sensor
vl53_1 = adafruit_vl53l0x.VL53L0X(tca1)
vl53_5 = adafruit_vl53l0x.VL53L0X(tca5)
vl53_6 = adafruit_vl53l0x.VL53L0X(tca6)

# initiate temperature & humidity sensor
si7021_ADD = 0x40 #Add the I2C bus address for the sensor here
si7021_READ_TEMPERATURE = 0xF3 #Add the command to read temperature here\
si7021_READ_HUMIDITY = 0xF5

bus = smbus2.SMBus(1)

# set up a write transaction that sends the command to measure temperature
cmd_meas_temp = smbus2.i2c_msg.write(si7021_ADD,[si7021_READ_TEMPERATURE])

cmd_meas_humd = smbus2.i2c_msg.write(si7021_ADD,[si7021_READ_HUMIDITY])

# set up a read transaction that reads two bytes of data
read_result = smbus2.i2c_msg.read(si7021_ADD,4)

# define the function to change the status of parking spots in the database
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


# define the function to upload temperature and humidity
def statstodb(temp, hum):
    path = "stats.json"
    data = {"temp": str(temp), "humidity": str(hum)}
    resp = authed_session.patch(db+path, json=data)
    if resp.ok:
        print("added", data)
    else:
        print(resp.json())

# initiate the parking spots as vacant ('true')
flag_1 = 'true'
flag_5 = 'true'
flag_6 = 'true'

# read VL53L0X data and update parking spots vacancy status
while True:
    flag1 = flag_1
    flag5 = flag_5
    flag6 = flag_6

    distance_1 = vl53_1.range
    distance_5 = vl53_5.range
    distance_6 = vl53_6.range
    
    if distance_1 < 1000:
        flag_1 = 'false'

        if flag_1 != flag1:
            print('1 becomes occupied')
            updatefree(1, flag_1)
    else:
        flag_1 = 'true'
        if flag_1 != flag1:
            print('1 becomes vacant')
            updatefree(1, flag_1)
    
    if distance_5 < 1000:
        flag_5 = 'false'

        if flag_5 != flag5:
            print('2 becomes occupied')
            updatefree(5, flag_5)
    else:
        flag_5 = 'true'
        if flag_5 != flag5:
            print('2 becomes vacant')
            updatefree(5, flag_5)

    if distance_6 < 1000:
        flag_6 = 'false'

        if flag_6 != flag6:
            print('3 becomes occupied')
            updatefree(6, flag_6)
    else:
        flag_6 = 'true'
        if flag_6 != flag6:
            print('3 becomes vacant')
            updatefree(6, flag_6)
    
    
    # set up a write transaction that sends the command to measure temperature
    cmd_meas_temp = smbus2.i2c_msg.write(si7021_ADD,[si7021_READ_TEMPERATURE])
    # set up a read transaction that reads two bytes of data
    read_temperature = smbus2.i2c_msg.read(si7021_ADD,2)
    # execute the two transactions with a small delay between them
    bus.i2c_rdwr(cmd_meas_temp)
    time.sleep(0.1)
    bus.i2c_rdwr(read_temperature)
    # convert the result to an int
    temperature = int.from_bytes(read_temperature.buf[0]+read_temperature.buf[1],'big')
    celcius = round((temperature*175.72)/65536 -46.85, 1)

    # set up a write transaction that sends the command to measure humidity
    cmd_meas_humidity = smbus2.i2c_msg.write(si7021_ADD,[si7021_READ_HUMIDITY])
    # set up a read transaction that reads two bytes of data
    read_humidity = smbus2.i2c_msg.read(si7021_ADD,2)
    # execute the two transactions with a small delay between them
    bus.i2c_rdwr(cmd_meas_temp)
    time.sleep(0.1)
    bus.i2c_rdwr(read_humidity)
    # read the humidity from Si7021 sensor using the I2C protocol
    humidity = int.from_bytes(read_humidity.buf[0]+read_humidity.buf[1],'big')
    # round the result to 1 decimal place
    humidity_normal = round((humidity*125)/65536 - 14, 1)


    print("Temp: ", celcius, "\tHumidity: ", humidity_normal)
    # update the temperatue and humidity data into database
    statstodb(celcius, humidity_normal)

    

    time.sleep(5)
