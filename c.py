import socket

HOST = "127.0.0.1"
PORT = 8888

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

file = open("soc-cv2/img.jpg", "rb")
f = open("tmp.txt", "wb")

while file:
    f.write(file)

img_data = file.read(2048)

client.send(img_data)

while img_data:
    client.send(img_data)
    img_data = file.read(1024)

file.close()
client.close()

