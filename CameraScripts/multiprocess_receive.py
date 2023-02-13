import multiprocessing
import socket
import os
import time

dir = "J://image_receive_test/"

folder = "J://image_receive_test/"

def receive_image():
	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server.bind(('192.168.0.58', 1003))
	server.listen()

	while True:
		try:
			print("Listening")
			client_socket, client_address = server.accept()
			print("Receiving")
			image_name = client_socket.recv(1024).decode('latin-1')
			path = os.path.basename(image_name)
			print(path)
			with open(dir + path, 'wb') as f:
				while True:
					data = client_socket.recv(1024)
					if not data:
						break
					f.write(data)

			client_socket.close()
			print('socket closed')
			# image_name = client_socket.recv(1024).decode()
			# print("Img Received")
			# path = os.path.basename(image_name)
			# print(path)
			# file = open(dir + path, "wb")
			# image_chunk = client_socket.recv(2048)
			#
			# while image_chunk:
			# 	file.write(image_chunk)
			# 	image_chunk = client_socket.recv(2048)
			#
			# file.close()
			#
			# print("file closed")


			#encodedMessage = bytes("hello back", 'utf-8')
			# send the data via the socket to the server
			#client_socket.send(encodedMessage)
			#print("sent back")

		except KeyboardInterrupt:
			if client_socket:
				print("Socket Closed")
				client_socket.close()
			break


def check_new_files():
	before = set(os.listdir(folder))
	while True:
		time.sleep(5)
		after = set(os.listdir(folder))
		new_files = after - before
		if new_files:
			for new_file in new_files:
				print("New file：", new_file)  #这里改成调用OCR
				time.sleep(5)
			before = after

#check_new_files("/path/to/folder")

if __name__ == '__main__':
	# 创建两个进程
	process1 = multiprocessing.Process(target=receive_image)
	process2 = multiprocessing.Process(target=check_new_files)

	# 启动两个进程
	process1.start()
	process2.start()

	# 等待两个进程结束
	process1.join()
	process2.join()

	print("Both functions have finished.")
