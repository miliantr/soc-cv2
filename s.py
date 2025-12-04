import socket
import struct

from detection import detection
from tracking import tracking

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

    #detection(filename)
    #tracking(filename)

    frame_count += 1


