import socket

HOST = "127.0.0.1"
PORT = 8888

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

client_socket, client_address = server.accept()

file = open("acc_img.jpg", "wb")
image_chunk = client_socket.recv(1024)

while image_chunk:
    file.write(image_chunk)
    image_chunk = client_socket.recv(1024)

#server.sendall()

file.close()
client_socket.close()