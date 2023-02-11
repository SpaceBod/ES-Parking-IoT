import multiprocessing
import socket
import os
import time

dir = "J:"

folder = "J:"

def receive_image():
	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server.bind(('146.169.194.185', 1003))
	server.listen()
	print("Listening")
	client_socket, client_address = server.accept()

	while True:
		try:
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
		#time.sleep(5)
		after = set(os.listdir(folder))
		new_files = after - before
		if new_files:
			for new_file in new_files:
				print("New file：", new_file)  #change this line to OCR afterwards
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
