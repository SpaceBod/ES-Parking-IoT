print("Temp + Humidity Sensor")
import time
import smbus2

si7021_ADD = 0x40 #Add the I2C bus address for the sensor here
si7021_READ_TEMPERATURE = 0xF3 #Add the command to read temperature here
si7021_READ_HUMIDITY = 0xF5

bus = smbus2.SMBus(1)

for x in range(0,100):
    #Set up a write transaction that sends the command to measure temperature
    cmd_meas_temp = smbus2.i2c_msg.write(si7021_ADD,[si7021_READ_TEMPERATURE])
    #Set up a read transaction that reads two bytes of data
    read_temperature = smbus2.i2c_msg.read(si7021_ADD,2)
    #Execute the two transactions with a small delay between them
    bus.i2c_rdwr(cmd_meas_temp)
    time.sleep(0.1)
    bus.i2c_rdwr(read_temperature)
    #convert the result to an int
    temperature = int.from_bytes(read_temperature.buf[0]+read_temperature.buf[1],'big')
    celcius = (temperature*175.72)/65536 -46.85

    #Set up a write transaction that sends the command to measure humidity
    cmd_meas_humidity = smbus2.i2c_msg.write(si7021_ADD,[si7021_READ_HUMIDITY])
    #Set up a read transaction that reads two bytes of data
    read_humidity = smbus2.i2c_msg.read(si7021_ADD,2)
    #Execute the two transactions with a small delay between them
    bus.i2c_rdwr(cmd_meas_temp)
    time.sleep(0.1)
    bus.i2c_rdwr(read_humidity)
    #convert the result to an int
    humidity = int.from_bytes(read_humidity.buf[0]+read_humidity.buf[1],'big')
    humidity_normal = (humidity*125)/65536 -6


    print("Temp: ", celcius, "\tHumidity: ", humidity_normal)
    time.sleep(0.5)
