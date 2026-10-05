import socket
from game import BattleshipGame

print("GAME FILE:", __import__("game").__file__)

HOST = "0.0.0.0"
PORT = 5000

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((HOST, PORT))

players = {}
ready = {"P1": False, "P2": False}
games = {
    "P1": BattleshipGame(),
    "P2": BattleshipGame()
}
current_turn = None

print("UDP Battleship Server started")
print(f"Listening on port {PORT}...")
print("Waiting for players...")

while True:
    try:
        data, address = server_socket.recvfrom(1024)
    except ConnectionResetError:
        print("UDP connection reset received. Continuing server...")
        continue

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
            players["P1"] = {
                "name": player_name,
                "address": address
            }
            server_socket.sendto("WELCOME|P1".encode(), address)
            print(f"Player {player_name} joined as Player 1")

        elif len(players) == 1:
            players["P2"] = {
                "name": player_name,
                "address": address
            }
            server_socket.sendto("WELCOME|P2".encode(), address)
            print(f"Player {player_name} joined as Player 2")
            print("Two players connected!")

        else:
            server_socket.sendto("ERROR|ROOM_FULL".encode(), address)

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

        result = games[player_id].place_ship(
            ship_name,
            start_cell,
            orientation
        )

        if result["success"]:
            server_socket.sendto("PLACE|OK".encode(), address)
            print(
                f"{player_id} placed {ship_name} "
                f"at {start_cell} ({orientation})"
            )
        else:
            server_socket.sendto(
                f"PLACE|ERROR|{result['error']}".encode(),
                address
            )
            print(
                f"{player_id} failed to place {ship_name}: "
                f"{result['error']}"
            )

    elif command == "READY":
        player_id = None

        if players.get("P1", {}).get("address") == address:
            player_id = "P1"
        elif players.get("P2", {}).get("address") == address:
            player_id = "P2"

        if player_id is None:
            server_socket.sendto("ERROR|PLAYER_NOT_FOUND".encode(), address)
            continue

        if len(games[player_id].ships) != len(BattleshipGame.SHIPS):
            server_socket.sendto(
                "READY|ERROR|NOT_ALL_SHIPS_PLACED".encode(),
                address
            )
            print(f"{player_id} is not ready: all ships are not placed")
            continue

        ready[player_id] = True

        server_socket.sendto("READY|OK".encode(), address)
        print(f"{player_id} is ready")

        if ready["P1"] and ready["P2"]:
            current_turn = "P1"

            p1_address = players["P1"]["address"]
            p2_address = players["P2"]["address"]

            server_socket.sendto("START".encode(), p1_address)
            server_socket.sendto("START".encode(), p2_address)
            server_socket.sendto("TURN|P1".encode(), p1_address)
            server_socket.sendto("TURN|P1".encode(), p2_address)

            print("Both players are ready. Game started!")

    elif command == "FIRE":
        if len(parts) != 2:
            server_socket.sendto("ERROR|BAD_FIRE_MESSAGE".encode(), address)
            continue

        cell = parts[1].upper()

        player_id = None

        if players.get("P1", {}).get("address") == address:
            player_id = "P1"
        elif players.get("P2", {}).get("address") == address:
            player_id = "P2"

        if player_id is None:
            server_socket.sendto("ERROR|PLAYER_NOT_FOUND".encode(), address)
            continue

        if current_turn != player_id:
            server_socket.sendto("ERROR|NOT_YOUR_TURN".encode(), address)
            continue

        opponent_id = "P2" if player_id == "P1" else "P1"
        opponent_address = players[opponent_id]["address"]
        opponent_game = games[opponent_id]

        result = opponent_game.fire(cell)

        print(f"{player_id} fired at {cell}: {result['result']}")

        if result["result"] == "INVALID":
            server_socket.sendto(
                f"RESULT|INVALID|{cell}|{result['error']}".encode(),
                address
            )
            continue

        if result["result"] == "MISS":
            server_socket.sendto(
                f"RESULT|MISS|{cell}".encode(),
                address
            )
            server_socket.sendto(
                f"ATTACK|MISS|{cell}".encode(),
                opponent_address
            )

        elif result["result"] == "HIT":
            server_socket.sendto(
                f"RESULT|HIT|{cell}".encode(),
                address
            )
            server_socket.sendto(
                f"ATTACK|HIT|{cell}".encode(),
                opponent_address
            )

            if result["sunk"]:
                server_socket.sendto(
                    f"SUNK|{result['ship']}".encode(),
                    address
                )
                server_socket.sendto(
                    f"SHIP_HIT|{result['ship']}".encode(),
                    opponent_address
                )

        if result["game_over"]:
            server_socket.sendto(
                f"WIN|{player_id}".encode(),
                address
            )
            server_socket.sendto(
                "LOSE".encode(),
                opponent_address
            )
            current_turn = None
            print(f"{player_id} won the game!")
            continue

        current_turn = "P2" if player_id == "P1" else "P1"

        server_socket.sendto(
            f"TURN|{current_turn}".encode(),
            players["P1"]["address"]
        )
        server_socket.sendto(
            f"TURN|{current_turn}".encode(),
            players["P2"]["address"]
        )

    else:
        server_socket.sendto(
            "ERROR|INVALID_COMMAND".encode(),
            address
        )