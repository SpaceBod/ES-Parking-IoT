import os.path
import socket
import time

ip = '192.168.0.58'
port = 1003

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def sendImage(ipAddress, portNum, img):
    client.connect((ip, port))
    print("Sending")
    image_name = img
    print(img)
    #send the filename
    client.sendall(image_name.encode('latin-1'))

    # Send the file data
    with open(image_name, 'rb') as f:
        while True:
            data = f.read(1024)
            if not data:
                break
            client.sendall(data)
    client.close()
    # file = open(image_name, 'rb')
    # image_data = file.read(2048)
    # while image_data:
    #     client.send(image_data)
    #     image_data = file.read(2048)
    # file.close()


if __name__ == '__main__':
    # for i in range(111):
    #     sendImage(ip, port, 'J://images/{}.jpg'.format(i))
    #     time.sleep(5)
    sendImage(ip, port, 'J://images/77.jpg')
