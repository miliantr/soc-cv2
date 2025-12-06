import socket
import struct
import cv2

from imgDstr import imgDstr
from detection import detection
#from tracking import tracking

imgDstr()

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

    img, cnt, M = detection(filename)

    x, y, w, h = cv2.boundingRect(cnt)
    reply = (x.to_bytes(4, "little") + y.to_bytes(4, "little") +
              w.to_bytes(4, "little") + h.to_bytes(4, "little"))
    server.sendto(reply, addr)
    #tracking(filename)

    frame_count += 1


