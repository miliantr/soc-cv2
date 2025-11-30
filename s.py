import socket
import numpy as np
import cv2

HOST = "127.0.0.1"
PORT = 8888

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

client_socket, client_address = server.accept()

#file = open("acc_img.jpg", "wb")
#image_chunk = client_socket.recv(1024)
#while image_chunk:
#    file.write(image_chunk)

while server.connect:
    image_chunk = client_socket.recv(1024)

M = np.mean(image_chunk)

if (M < 174.7):
    print("detected")
else:
    print("undetected")

#server.sendall()
#file.close()

client_socket.close()

"""
src = 'image0012.png'
src1 = 'image0000.png'
img = cv2.imread(src, cv2.IMREAD_GRAYSCALE)
img1 = cv2.imread(src1, cv2.IMREAD_GRAYSCALE)
img_buffer = img

M = np.mean(img)
M1 = np.mean(img1)

if (M < 174.7):
    print("detected")
else:
    print("undetected")
"""