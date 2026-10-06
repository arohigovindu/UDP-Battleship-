import socket
import threading
import time


class BattleshipClient:

    def __init__(
        self,
        host="127.0.0.1",
        port=5000
    ):

        self.host = host
        self.port = port

        # -------------------------------------------------
        # UDP SOCKET
        # -------------------------------------------------

        self.socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_DGRAM
        )

        self.socket.settimeout(0.5)

        # -------------------------------------------------
        # CLIENT STATE
        # -------------------------------------------------

        self.player_id = None
        self.player_name = None

        self.connected = False
        self.game_started = False
        self.current_turn = None
        self.running = False

        # -------------------------------------------------
        # RECEIVE THREAD
        # -------------------------------------------------

        self.receive_thread = None

        # -------------------------------------------------
        # MESSAGE CALLBACK
        # -------------------------------------------------

        self.message_callback = None

        # -------------------------------------------------
        # NETWORK ANIMATION CALLBACKS
        # -------------------------------------------------

        self.on_network_send = None
        self.on_network_receive = None

        # -------------------------------------------------
        # EVENT CALLBACKS
        # -------------------------------------------------

        self.on_welcome = None
        self.on_place_result = None
        self.on_ready_result = None
        self.on_game_start = None
        self.on_turn = None
        self.on_result = None
        self.on_attack = None
        self.on_sunk = None
        self.on_ship_hit = None
        self.on_win = None
        self.on_lose = None
        self.on_error = None
        self.on_reset = None

        # -------------------------------------------------
        # CONNECTION LOCK
        # -------------------------------------------------

        self.lock = threading.Lock()

    # =====================================================
    # SET CALLBACK
    # =====================================================

    def set_message_callback(self, callback):

        self.message_callback = callback

    # =====================================================
    # START RECEIVING
    # =====================================================

    def start_receiver(self):

        if self.running:
            return

        self.running = True

        self.receive_thread = threading.Thread(
            target=self._receive_loop,
            daemon=True
        )

        self.receive_thread.start()

    # =====================================================
    # STOP CLIENT
    # =====================================================

    def stop(self):

        self.running = False

        self.connected = False
        self.game_started = False
        self.current_turn = None

        try:
            self.socket.close()
        except OSError:
            pass

    # =====================================================
    # SEND MESSAGE
    # =====================================================

    def _send(self, message):

        if not self.running:
            return False

        try:

            data = message.encode("utf-8")

            self.socket.sendto(
                data,
                (self.host, self.port)
            )

            self._log(
                f"{message} -> UDP -> Server"
            )

            # Trigger packet animation
            if self.on_network_send:

                try:
                    self.on_network_send(message)
                except Exception:
                    pass

            return True

        except OSError as error:

            self._log(
                f"UDP send error: {error}"
            )

            return False

    # =====================================================
    # LOG MESSAGE
    # =====================================================

    def _log(self, message):

        if self.message_callback:

            try:
                self.message_callback(message)
            except Exception:
                pass

    # =====================================================
    # CONNECT / JOIN
    # =====================================================

    def connect(self, player_name):

        if not player_name:
            return False

        player_name = player_name.strip()

        if not player_name:
            return False

        self.player_name = player_name

        self.start_receiver()

        self._log(
            f"Connecting to UDP server "
            f"{self.host}:{self.port}"
        )

        self._log(
            f"JOIN|{player_name}"
        )

        return self._send(
            f"JOIN|{player_name}"
        )

    # =====================================================
    # PLACE SHIP
    # =====================================================

    def place_ship(
        self,
        ship_name,
        start_cell,
        orientation
    ):

        start_cell = start_cell.upper()
        orientation = orientation.upper()

        message = (
            f"PLACE|{ship_name}|"
            f"{start_cell}|{orientation}"
        )

        self._log(
            f"Requesting placement: "
            f"{ship_name} at "
            f"{start_cell} ({orientation})"
        )

        return self._send(message)

    # =====================================================
    # READY
    # =====================================================

    def ready(self):

        self._log(
            "Sending READY request"
        )

        return self._send("READY")

    # =====================================================
    # FIRE
    # =====================================================

    def fire(self, cell):

        cell = cell.upper()

        self._log(
            f"Firing at {cell}"
        )

        return self._send(
            f"FIRE|{cell}"
        )

    # =====================================================
    # RESET GAME
    # =====================================================

    def reset_game(self):

        if not self.connected:

            self._log(
                "Cannot reset: not connected to server."
            )

            return False

        self._log(
            "Requesting game reset..."
        )

        return self._send("RESET")

    # =====================================================
    # RECEIVE LOOP
    # =====================================================

    def _receive_loop(self):

        while self.running:

            try:

                data, address = self.socket.recvfrom(
                    4096
                )

            except socket.timeout:

                continue

            except OSError:

                break

            except ConnectionResetError:

                continue

            # -------------------------------------------------
            # DECODE MESSAGE
            # -------------------------------------------------

            try:

                message = data.decode(
                    "utf-8"
                )

            except UnicodeDecodeError:

                self._log(
                    "Received invalid UDP data"
                )

                continue

            self._log(
                f"<- Server: {message}"
            )

            # Trigger packet animation
            if self.on_network_receive:

                try:
                    self.on_network_receive(message)
                except Exception:
                    pass

            # -------------------------------------------------
            # PROCESS MESSAGE
            # -------------------------------------------------

            try:

                self._handle_message(
                    message
                )

            except Exception as error:

                self._log(
                    f"Message handling error: {error}"
                )

    # =====================================================
    # HANDLE SERVER MESSAGE
    # =====================================================

    def _handle_message(self, message):

        parts = message.split("|")

        if not parts:
            return

        command = parts[0]

        # =================================================
        # WELCOME
        # =================================================

        if command == "WELCOME":

            if len(parts) < 2:
                return

            self.player_id = parts[1]
            self.connected = True

            self._log(
                f"Server assigned you as "
                f"{self.player_id}."
            )

            if self.on_welcome:

                self.on_welcome(
                    self.player_id
                )

        # =================================================
        # PLACE
        # =================================================

        elif command == "PLACE":

            if len(parts) >= 2:

                status = parts[1]

                if status == "OK":

                    self._log(
                        "Server accepted ship placement."
                    )

                    if self.on_place_result:

                        self.on_place_result(
                            True,
                            None
                        )

                elif status == "ERROR":

                    error = (
                        parts[2]
                        if len(parts) >= 3
                        else "UNKNOWN_ERROR"
                    )

                    self._log(
                        f"Placement rejected: "
                        f"{error}"
                    )

                    if self.on_place_result:

                        self.on_place_result(
                            False,
                            error
                        )

        # =================================================
        # READY
        # =================================================

        elif command == "READY":

            if len(parts) >= 2:

                status = parts[1]

                if status == "OK":

                    self._log(
                        "Server accepted READY."
                    )

                    if self.on_ready_result:

                        self.on_ready_result(
                            True,
                            None
                        )

                elif status == "ERROR":

                    error = (
                        parts[2]
                        if len(parts) >= 3
                        else "UNKNOWN_ERROR"
                    )

                    self._log(
                        f"READY rejected: "
                        f"{error}"
                    )

                    if self.on_ready_result:

                        self.on_ready_result(
                            False,
                            error
                        )

        # =================================================
        # START
        # =================================================

        elif command == "START":

            self.game_started = True

            self._log(
                "Game started!"
            )

            if self.on_game_start:

                self.on_game_start()

        # =================================================
        # TURN
        # =================================================

        elif command == "TURN":

            if len(parts) < 2:
                return

            self.current_turn = parts[1]

            self._log(
                f"Current turn: "
                f"{self.current_turn}"
            )

            if self.on_turn:

                self.on_turn(
                    self.current_turn
                )

        # =================================================
        # RESULT
        # =================================================

        elif command == "RESULT":

            if len(parts) < 3:
                return

            result = parts[1]
            cell = parts[2]

            error = (
                parts[3]
                if len(parts) >= 4
                else None
            )

            if result == "HIT":

                self._log(
                    f"HIT at {cell}"
                )

            elif result == "MISS":

                self._log(
                    f"MISS at {cell}"
                )

            elif result == "INVALID":

                self._log(
                    f"Invalid shot at "
                    f"{cell}: {error}"
                )

            if self.on_result:

                self.on_result(
                    result,
                    cell,
                    error
                )

        # =================================================
        # ATTACK
        # =================================================

        elif command == "ATTACK":

            if len(parts) < 3:
                return

            result = parts[1]
            cell = parts[2]

            self._log(
                f"Opponent attacked "
                f"{cell}: {result}"
            )

            if self.on_attack:

                self.on_attack(
                    result,
                    cell
                )

        # =================================================
        # SUNK
        # =================================================

        elif command == "SUNK":

            if len(parts) < 2:
                return

            ship_name = parts[1]

            self._log(
                f"You sunk "
                f"{ship_name}"
            )

            if self.on_sunk:

                self.on_sunk(
                    ship_name
                )

        # =================================================
        # SHIP HIT
        # =================================================

        elif command == "SHIP_HIT":

            if len(parts) < 2:
                return

            ship_name = parts[1]

            self._log(
                f"Your "
                f"{ship_name} "
                f"was hit."
            )

            if self.on_ship_hit:

                self.on_ship_hit(
                    ship_name
                )

        # =================================================
        # WIN
        # =================================================

        elif command == "WIN":

            winner = (
                parts[1]
                if len(parts) >= 2
                else None
            )

            self.current_turn = None
            self.game_started = False

            self._log(
                f"You win! "
                f"Winner: {winner}"
            )

            if self.on_win:

                self.on_win(
                    winner
                )

        # =================================================
        # LOSE
        # =================================================

        elif command == "LOSE":

            self.current_turn = None
            self.game_started = False

            self._log(
                "You lost the game."
            )

            if self.on_lose:

                self.on_lose()

        # =================================================
        # RESET
        # =================================================

        elif command == "RESET":

            status = (
                parts[1]
                if len(parts) >= 2
                else "OK"
            )

            if status == "OK":

                self.game_started = False
                self.current_turn = None

                self._log(
                    "Server reset the game."
                )

                if self.on_reset:

                    self.on_reset()

        # =================================================
        # ERROR
        # =================================================

        elif command == "ERROR":

            error = (
                parts[1]
                if len(parts) >= 2
                else "UNKNOWN_ERROR"
            )

            self._log(
                f"Server error: {error}"
            )

            if self.on_error:

                self.on_error(
                    error
                )

        # =================================================
        # UNKNOWN COMMAND
        # =================================================

        else:

            self._log(
                f"Unknown server message: "
                f"{message}"
            )


# =============================================================
# SIMPLE TERMINAL TEST
# =============================================================

if __name__ == "__main__":

    print()
    print("======================================")
    print("       UDP BATTLESHIP CLIENT")
    print("======================================")
    print()

    name = input(
        "Enter your name: "
    ).strip()

    if not name:

        print(
            "Name cannot be empty."
        )

        raise SystemExit

    client = BattleshipClient()

    def welcome(player_id):
        print(f"\nAssigned as {player_id}")

    def placement_result(success, error):

        if success:
            print("Placement accepted.")
        else:
            print(f"Placement rejected: {error}")

    def ready_result(success, error):

        if success:
            print("READY accepted.")
        else:
            print(f"READY rejected: {error}")

    def game_start():
        print("\nGame started!")

    def turn(player):
        print(f"\nCurrent turn: {player}")

    def result(result_type, cell, error):

        print(
            f"\nShot result: "
            f"{result_type} at {cell}"
        )

        if error:
            print(f"Error: {error}")

    def attack(result_type, cell):

        print(
            f"\nOpponent attack: "
            f"{result_type} at {cell}"
        )

    def sunk(ship):
        print(f"\nShip sunk: {ship}")

    def ship_hit(ship):
        print(f"\nYour ship was hit: {ship}")

    def win(player):
        print(f"\nYOU WIN! Winner: {player}")

    def lose():
        print("\nYOU LOSE!")

    def reset():
        print("\nGAME RESET!")

    def error(message):
        print(f"\nSERVER ERROR: {message}")

    client.on_welcome = welcome
    client.on_place_result = placement_result
    client.on_ready_result = ready_result
    client.on_game_start = game_start
    client.on_turn = turn
    client.on_result = result
    client.on_attack = attack
    client.on_sunk = sunk
    client.on_ship_hit = ship_hit
    client.on_win = win
    client.on_lose = lose
    client.on_reset = reset
    client.on_error = error

    client.connect(name)

    try:

        while client.running:

            time.sleep(0.5)

    except KeyboardInterrupt:

        print("\nStopping client...")

        client.stop()