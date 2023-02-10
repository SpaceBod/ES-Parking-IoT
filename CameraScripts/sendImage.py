identity="jw2720"
        password=hash:e7d47745cecfb1318f59dba532b7ac9a


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
