#ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
#update_config=1
#country=GB



import socket

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("client socket")
client.connect(('172.20.10.6', 1003))

print("connected")
file = open('/home/pi/python/pictures/img.jpg', 'rb')
image_data = file.read(2048)

while image_data:
    client.send(image_data)
    image_data = file.read(2048)

file.close()
client.close()
