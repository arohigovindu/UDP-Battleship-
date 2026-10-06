import socket
import sys

SERVER_IP = "127.0.0.1"
SERVER_PORT = 5000

player_name = sys.argv[1]
player_id = sys.argv[2]

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

client_socket.sendto(
    f"JOIN|{player_name}".encode(),
    (SERVER_IP, SERVER_PORT)
)

data, address = client_socket.recvfrom(1024)
print("Server:", data.decode())

placements = [
    "PLACE|Ship1|A1|H",
    "PLACE|Ship2|A2|H",
    "PLACE|Ship3|A3|H"
]

for message in placements:
    client_socket.sendto(message.encode(), (SERVER_IP, SERVER_PORT))
    data, address = client_socket.recvfrom(1024)
    print("Server:", data.decode())

client_socket.sendto("READY".encode(), (SERVER_IP, SERVER_PORT))
data, address = client_socket.recvfrom(1024)
print("Server:", data.decode())

print("Waiting for turn...")

while True:
    data, address = client_socket.recvfrom(1024)
    message = data.decode()
    print("Server:", message)

    if message == f"TURN|{player_id}":
        break

print("It is my turn. Firing at A1...")

client_socket.sendto(
    "FIRE|A1".encode(),
    (SERVER_IP, SERVER_PORT)
)

while True:
    data, address = client_socket.recvfrom(1024)
    message = data.decode()
    print("Server:", message)

    if message.startswith("TURN|") or message.startswith("WIN|") or message == "LOSE":
        break

client_socket.close()
