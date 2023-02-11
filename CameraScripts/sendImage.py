import socket
import time

ip = '146.169.178.115'
port = 1003

def sendImage(ipAddress, portNum, img):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((ipAddress, portNum))
    print("Sending")
    image_name = img
    client.send(image_name.encode())
    file = open(image_name, 'rb')
    image_data = file.read(2048)
    while image_data:
        client.send(image_data)
        image_data = file.read(2048)
    file.close()
    client.close()

sendImage(ip, port, '/Users/admin/Desktop/piServer/img/img2.jpg')
