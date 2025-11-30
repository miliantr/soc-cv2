import socket
import numpy as np
import cv2

HOST = "127.0.0.1"
PORT = 8888

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

file = open("img.jpg", "rb")
img_data = file.read(2048)

while img_data:
    client.send(img_data)
    img_data = file.read(2048)

file.close()
client.close()

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