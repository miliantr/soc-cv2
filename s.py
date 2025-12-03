import socket
import struct
import cv2
import numpy as np

HOST = "127.0.0.1"
PORT = 8888

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind((HOST, PORT))
print("UDP server listening on {}:{}".format(HOST, PORT))

frame_count = 0

while True:
    data, addr = server.recvfrom(65507)
    if len(data) < 4:
        print("Packet too small, skipping")
        continue

    size = struct.unpack("<I", data[:4])[0]
    payload = data[4:]

    filename = f"img/frame_{frame_count:04d}.jpg"
    with open(filename, "wb") as f:
        f.write(payload)
    
    img = cv2.imread(filename, cv2.IMREAD_GRAYSCALE)

    M = np.mean(img)
    if M < 174.0:
        print("detected")

    frame_count += 1
