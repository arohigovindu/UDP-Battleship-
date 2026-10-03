import socket

HOST = "0.0.0.0"
PORT = 5000

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((HOST, PORT))
players = {}
print("UDP Battleship Server started")
print(f"Listening on port {PORT}...")
print("Waiting for players...")

while True:
    data, address = server_socket.recvfrom(1024)
    message = data.decode()
    parts = message.split("|")
    command = parts[0]
    if command == "JOIN":
        if len(parts) < 2:
            server_socket.sendto("ERROR|BAD_MESSAGE".encode(), address)
            continue

        player_name = parts[1]

        if len(players) == 0:
            players["P1"] = {"name": player_name, "address": address}
            server_socket.sendto("WELCOME|P1".encode(), address)
            print(f"Player {player_name} joined as Player 1")
        elif len(players) == 1:
            players["P2"] = {"name": player_name, "address": address}
            server_socket.sendto("WELCOME|P2".encode(), address)
            print(f"Player {player_name} joined as Player 2")
        else:
            server_socket.sendto("ERROR|GAME_FULL".encode(), address)
            continue

        if len(players) == 2:
            p1_address = players["P1"]["address"]
            p2_address = players["P2"]["address"]
            server_socket.sendto("START|WAITING_FOR_READY".encode(), p1_address)
            server_socket.sendto("START|WAITING_FOR_READY".encode(), p2_address)
            print("Two players connected!")
    else:
        server_socket.sendto("ERROR|INVALID_COMMAND".encode(), address)
