import socket

HOST = "0.0.0.0"
PORT = 5000

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((HOST, PORT))

print("UDP Server started")
print(f"Listening on port {PORT}...")
print("Waiting for messages...")

while True:
    data, address = server_socket.recvfrom(1024)

    message = data.decode()
    print(f"Received from {address}: {message}")

    response = "Message received!"
    server_socket.sendto(response.encode(), address)
