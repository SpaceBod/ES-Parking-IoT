import socket
import os

dir = "/Users/admin/Desktop/piServer/"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('146.169.178.115', 1003))
print("Listening")
server.listen()

while True:

    try:
        client_socket, client_address = server.accept()
        print("Img Received")
        image_name = client_socket.recv(1024).decode()
        path = os.path.basename(image_name)
        print(path)
        file = open(dir + path, "wb")
        image_chunk = client_socket.recv(2048)
        
        while image_chunk:
            file.write(image_chunk)
            image_chunk = client_socket.recv(2048)
            
        file.close()
        
        print("file closed")
    

    except KeyboardInterrupt:
        if client_socket:
            print("Socket Closed")
            client_socket.close()
        break
