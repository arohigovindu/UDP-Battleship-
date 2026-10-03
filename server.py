import socket

HOST = "0.0.0.0"
PORT = 5000

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((HOST, PORT))

players = {}
placements = {"P1": [], "P2": []}
ready = {"P1": False, "P2": False}

print("UDP Battleship Server started")
print(f"Listening on port {PORT}...")
print("Waiting for players...")

while True:
    data, address = server_socket.recvfrom(1024)
    message = data.decode()
    print(f"Received from {address}: {message}")

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
            server_socket.sendto("ERROR|ROOM_FULL".encode(), address)
            continue

        if len(players) == 2:
            print("Two players connected!")

    elif command == "PLACE":
        if len(parts) != 4:
            server_socket.sendto("ERROR|BAD_PLACE_MESSAGE".encode(), address)
            continue

        ship_name = parts[1]
        start_cell = parts[2]
        orientation = parts[3]
        player_id = None

        if players.get("P1", {}).get("address") == address:
            player_id = "P1"
        elif players.get("P2", {}).get("address") == address:
            player_id = "P2"

        if player_id is None:
            server_socket.sendto("ERROR|PLAYER_NOT_FOUND".encode(), address)
            continue

        placements[player_id].append({
            "ship_name": ship_name,
            "start_cell": start_cell,
            "orientation": orientation,
        })
        server_socket.sendto("PLACE|OK".encode(), address)
        print(f"{player_id} placed {ship_name} at {start_cell} ({orientation})")

    elif command == "READY":
        player_id = None

        if players.get("P1", {}).get("address") == address:
            player_id = "P1"
        elif players.get("P2", {}).get("address") == address:
            player_id = "P2"

        if player_id is None:
            server_socket.sendto("ERROR|PLAYER_NOT_FOUND".encode(), address)
            continue

        ready[player_id] = True
        server_socket.sendto("READY|OK".encode(), address)
        print(f"{player_id} is ready")

        if ready["P1"] and ready["P2"]:
            p1_address = players["P1"]["address"]
            p2_address = players["P2"]["address"]
            server_socket.sendto("START".encode(), p1_address)
            server_socket.sendto("START".encode(), p2_address)
            server_socket.sendto("TURN|P1".encode(), p1_address)
            server_socket.sendto("TURN|P1".encode(), p2_address)
            print("Both players are ready. Game started!")

    else:
        server_socket.sendto("ERROR|INVALID_COMMAND".encode(), address)