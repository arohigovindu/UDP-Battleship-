import socket
from game import BattleshipGame

print("GAME FILE:", __import__("game").__file__)

HOST = "0.0.0.0"
PORT = 5000

server_socket = socket.socket(
    socket.AF_INET,
    socket.SOCK_DGRAM
)

server_socket.bind((HOST, PORT))

players = {}

ready = {
    "P1": False,
    "P2": False
}

games = {
    "P1": BattleshipGame(),
    "P2": BattleshipGame()
}

current_turn = None

print("UDP Battleship Server started")
print(f"Listening on port {PORT}...")
print("Waiting for players...")


def get_player_id(address):

    if players.get("P1", {}).get("address") == address:
        return "P1"

    if players.get("P2", {}).get("address") == address:
        return "P2"

    return None


def reset_game():

    global current_turn

    print()
    print("======================================")
    print("RESETTING GAME")
    print("======================================")

    # Completely recreate both game objects.
    # This clears ships, hits, misses and all
    # previous game state.

    games["P1"] = BattleshipGame()
    games["P2"] = BattleshipGame()

    # Players remain connected, but they must
    # place their ships and press READY again.

    ready["P1"] = False
    ready["P2"] = False

    current_turn = None

    print("Game state cleared.")
    print("Players remain connected.")
    print("Waiting for new ship placements...")


while True:

    try:

        data, address = server_socket.recvfrom(1024)

    except ConnectionResetError:

        print(
            "UDP connection reset received. "
            "Continuing server..."
        )

        continue

    try:

        message = data.decode()

    except UnicodeDecodeError:

        print(
            f"Invalid UDP data received "
            f"from {address}"
        )

        continue

    print(
        f"Received from {address}: "
        f"{message}"
    )

    parts = message.split("|")

    if not parts:
        continue

    command = parts[0]

    # =====================================================
    # JOIN
    # =====================================================

    if command == "JOIN":

        if len(parts) < 2:

            server_socket.sendto(
                "ERROR|BAD_MESSAGE".encode(),
                address
            )

            continue

        player_name = parts[1]

        # -------------------------------------------------
        # Player 1
        # -------------------------------------------------

        if len(players) == 0:

            players["P1"] = {
                "name": player_name,
                "address": address
            }

            server_socket.sendto(
                "WELCOME|P1".encode(),
                address
            )

            print(
                f"Player {player_name} "
                f"joined as Player 1"
            )

        # -------------------------------------------------
        # Player 2
        # -------------------------------------------------

        elif len(players) == 1:

            players["P2"] = {
                "name": player_name,
                "address": address
            }

            server_socket.sendto(
                "WELCOME|P2".encode(),
                address
            )

            print(
                f"Player {player_name} "
                f"joined as Player 2"
            )

            print(
                "Two players connected!"
            )

        # -------------------------------------------------
        # Room full
        # -------------------------------------------------

        else:

            server_socket.sendto(
                "ERROR|ROOM_FULL".encode(),
                address
            )

    # =====================================================
    # RESET
    # =====================================================

    elif command == "RESET":

        player_id = get_player_id(address)

        if player_id is None:

            server_socket.sendto(
                "ERROR|PLAYER_NOT_FOUND".encode(),
                address
            )

            continue

        print(
            f"{player_id} requested game reset."
        )

        reset_game()

        # -------------------------------------------------
        # Tell both connected players
        # -------------------------------------------------

        for player in ("P1", "P2"):

            if player in players:

                server_socket.sendto(
                    "RESET|OK".encode(),
                    players[player]["address"]
                )

        print(
            "RESET|OK sent to connected players."
        )

    # =====================================================
    # PLACE SHIP
    # =====================================================

    elif command == "PLACE":

        if len(parts) != 4:

            server_socket.sendto(
                "ERROR|BAD_PLACE_MESSAGE".encode(),
                address
            )

            continue

        ship_name = parts[1]
        start_cell = parts[2]
        orientation = parts[3]

        player_id = get_player_id(address)

        if player_id is None:

            server_socket.sendto(
                "ERROR|PLAYER_NOT_FOUND".encode(),
                address
            )

            continue

        result = games[player_id].place_ship(
            ship_name,
            start_cell,
            orientation
        )

        if result["success"]:

            server_socket.sendto(
                "PLACE|OK".encode(),
                address
            )

            print(
                f"{player_id} placed "
                f"{ship_name} "
                f"at {start_cell} "
                f"({orientation})"
            )

        else:

            server_socket.sendto(
                f"PLACE|ERROR|{result['error']}".encode(),
                address
            )

            print(
                f"{player_id} failed to place "
                f"{ship_name}: "
                f"{result['error']}"
            )

    # =====================================================
    # READY
    # =====================================================

    elif command == "READY":

        player_id = get_player_id(address)

        if player_id is None:

            server_socket.sendto(
                "ERROR|PLAYER_NOT_FOUND".encode(),
                address
            )

            continue

        if len(games[player_id].ships) != len(
            BattleshipGame.SHIPS
        ):

            server_socket.sendto(
                "READY|ERROR|NOT_ALL_SHIPS_PLACED".encode(),
                address
            )

            print(
                f"{player_id} is not ready: "
                f"all ships are not placed"
            )

            continue

        ready[player_id] = True

        server_socket.sendto(
            "READY|OK".encode(),
            address
        )

        print(
            f"{player_id} is ready"
        )

        # -------------------------------------------------
        # BOTH READY
        # -------------------------------------------------

        if ready["P1"] and ready["P2"]:

            current_turn = "P1"

            p1_address = players["P1"]["address"]
            p2_address = players["P2"]["address"]

            server_socket.sendto(
                "START".encode(),
                p1_address
            )

            server_socket.sendto(
                "START".encode(),
                p2_address
            )

            server_socket.sendto(
                "TURN|P1".encode(),
                p1_address
            )

            server_socket.sendto(
                "TURN|P1".encode(),
                p2_address
            )

            print(
                "Both players are ready. "
                "Game started!"
            )

    # =====================================================
    # FIRE
    # =====================================================

    elif command == "FIRE":

        if len(parts) != 2:

            server_socket.sendto(
                "ERROR|BAD_FIRE_MESSAGE".encode(),
                address
            )

            continue

        cell = parts[1].upper()

        player_id = get_player_id(address)

        if player_id is None:

            server_socket.sendto(
                "ERROR|PLAYER_NOT_FOUND".encode(),
                address
            )

            continue

        if current_turn != player_id:

            server_socket.sendto(
                "ERROR|NOT_YOUR_TURN".encode(),
                address
            )

            continue

        opponent_id = (
            "P2"
            if player_id == "P1"
            else "P1"
        )

        opponent_address = players[
            opponent_id
        ]["address"]

        opponent_game = games[
            opponent_id
        ]

        result = opponent_game.fire(cell)

        print(
            f"{player_id} fired at "
            f"{cell}: "
            f"{result['result']}"
        )

        # -------------------------------------------------
        # INVALID
        # -------------------------------------------------

        if result["result"] == "INVALID":

            server_socket.sendto(
                f"RESULT|INVALID|{cell}|{result['error']}".encode(),
                address
            )

            continue

        # -------------------------------------------------
        # MISS
        # -------------------------------------------------

        if result["result"] == "MISS":

            server_socket.sendto(
                f"RESULT|MISS|{cell}".encode(),
                address
            )

            server_socket.sendto(
                f"ATTACK|MISS|{cell}".encode(),
                opponent_address
            )

        # -------------------------------------------------
        # HIT
        # -------------------------------------------------

        elif result["result"] == "HIT":

            server_socket.sendto(
                f"RESULT|HIT|{cell}".encode(),
                address
            )

            server_socket.sendto(
                f"ATTACK|HIT|{cell}".encode(),
                opponent_address
            )

            # -------------------------------------------------
            # SHIP SUNK
            # -------------------------------------------------

            if result["sunk"]:

                server_socket.sendto(
                    f"SUNK|{result['ship']}".encode(),
                    address
                )

                server_socket.sendto(
                    f"SHIP_HIT|{result['ship']}".encode(),
                    opponent_address
                )

        # -------------------------------------------------
        # GAME OVER
        # -------------------------------------------------

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

            print(
                f"{player_id} won the game!"
            )

            continue

        # -------------------------------------------------
        # CHANGE TURN
        # -------------------------------------------------

        current_turn = (
            "P2"
            if player_id == "P1"
            else "P1"
        )

        server_socket.sendto(
            f"TURN|{current_turn}".encode(),
            players["P1"]["address"]
        )

        server_socket.sendto(
            f"TURN|{current_turn}".encode(),
            players["P2"]["address"]
        )

    # =====================================================
    # INVALID COMMAND
    # =====================================================

    else:

        server_socket.sendto(
            "ERROR|INVALID_COMMAND".encode(),
            address
        )