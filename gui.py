import tkinter as tk
from tkinter import messagebox

from client import BattleshipClient


# ============================================================
# CONSTANTS
# ============================================================

BOARD_SIZE = 5

SHIPS = {
    "Ship1": 3,
    "Ship2": 2,
    "Ship3": 2
}


# ============================================================
# MAIN GUI
# ============================================================

class BattleshipGUI:

    def __init__(self, root):

        self.root = root
        self.root.title("UDP Battleship")
        self.root.geometry("1100x750")
        self.root.resizable(False, False)

        # ----------------------------------------------------
        # CLIENT
        # ----------------------------------------------------

        self.client = BattleshipClient(
            host="127.0.0.1",
            port=5000
        )

        # ----------------------------------------------------
        # GAME STATE
        # ----------------------------------------------------

        self.player_id = None

        self.connected = False

        self.game_started = False

        self.current_turn = None

        self.ready = False

        self.selected_ship = "Ship1"

        self.orientation = "H"

        self.placed_ships = set()

        self.own_cells = {}

        self.enemy_cells = {}

        # ----------------------------------------------------
        # CALLBACKS
        # ----------------------------------------------------

        self.client.on_welcome = self.handle_welcome

        self.client.on_place_result = self.handle_place_result

        self.client.on_ready_result = self.handle_ready_result

        self.client.on_game_start = self.handle_game_start

        self.client.on_turn = self.handle_turn

        self.client.on_result = self.handle_result

        self.client.on_attack = self.handle_attack

        self.client.on_sunk = self.handle_sunk

        self.client.on_ship_hit = self.handle_ship_hit

        self.client.on_win = self.handle_win

        self.client.on_lose = self.handle_lose

        self.client.on_error = self.handle_error

        self.client.set_message_callback(
            self.network_log
        )

        # ----------------------------------------------------
        # BUILD GUI
        # ----------------------------------------------------

        self.build_gui()

        # ----------------------------------------------------
        # CLOSE EVENT
        # ----------------------------------------------------

        self.root.protocol(
            "WM_DELETE_WINDOW",
            self.close
        )


    # ========================================================
    # BUILD GUI
    # ========================================================

    def build_gui(self):

        # ----------------------------------------------------
        # TITLE
        # ----------------------------------------------------

        title = tk.Label(
            self.root,
            text="UDP BATTLESHIP",
            font=("Arial", 24, "bold")
        )

        title.pack(pady=10)

        # ----------------------------------------------------
        # CONNECTION FRAME
        # ----------------------------------------------------

        connection_frame = tk.Frame(
            self.root
        )

        connection_frame.pack(
            pady=5
        )

        tk.Label(
            connection_frame,
            text="Player Name:"
        ).grid(
            row=0,
            column=0,
            padx=5
        )

        self.name_entry = tk.Entry(
            connection_frame,
            width=20
        )

        self.name_entry.grid(
            row=0,
            column=1,
            padx=5
        )

        tk.Label(
            connection_frame,
            text="Server IP:"
        ).grid(
            row=0,
            column=2,
            padx=5
        )

        self.server_ip_entry = tk.Entry(
            connection_frame,
            width=18
        )

        self.server_ip_entry.insert(
            0,
            "127.0.0.1"
        )

        self.server_ip_entry.grid(
            row=0,
            column=3,
            padx=5
        )

        self.connect_button = tk.Button(
            connection_frame,
            text="Connect",
            width=12,
            command=self.connect
        )

        self.connect_button.grid(
            row=0,
            column=4,
            padx=5
        )

        self.player_label = tk.Label(
            connection_frame,
            text="Not connected",
            font=("Arial", 10, "bold")
        )

        self.player_label.grid(
            row=0,
            column=5,
            padx=15
        )

        # ----------------------------------------------------
        # STATUS
        # ----------------------------------------------------

        self.status_label = tk.Label(
            self.root,
            text="Welcome to UDP Battleship.",
            font=("Arial", 12)
        )

        self.status_label.pack(
            pady=5
        )

        # ----------------------------------------------------
        # MAIN GAME FRAME
        # ----------------------------------------------------

        game_frame = tk.Frame(
            self.root
        )

        game_frame.pack(
            pady=10
        )

        # ----------------------------------------------------
        # OWN BOARD
        # ----------------------------------------------------

        own_frame = tk.LabelFrame(
            game_frame,
            text="Your Board",
            padx=10,
            pady=10
        )

        own_frame.grid(
            row=0,
            column=0,
            padx=25
        )

        self.own_board = self.create_board(
            own_frame,
            self.own_cell_clicked
        )

        # ----------------------------------------------------
        # ENEMY BOARD
        # ----------------------------------------------------

        enemy_frame = tk.LabelFrame(
            game_frame,
            text="Opponent Board",
            padx=10,
            pady=10
        )

        enemy_frame.grid(
            row=0,
            column=1,
            padx=25
        )

        self.enemy_board = self.create_board(
            enemy_frame,
            self.enemy_cell_clicked
        )

        # ----------------------------------------------------
        # CONTROLS
        # ----------------------------------------------------

        controls = tk.LabelFrame(
            self.root,
            text="Ship Placement",
            padx=15,
            pady=10
        )

        controls.pack(
            pady=5
        )

        tk.Label(
            controls,
            text="Ship:"
        ).grid(
            row=0,
            column=0,
            padx=5
        )

        self.ship_var = tk.StringVar(
            value="Ship1"
        )

        self.ship_menu = tk.OptionMenu(
            controls,
            self.ship_var,
            *SHIPS.keys(),
            command=self.ship_changed
        )

        self.ship_menu.grid(
            row=0,
            column=1,
            padx=5
        )

        tk.Label(
            controls,
            text="Orientation:"
        ).grid(
            row=0,
            column=2,
            padx=5
        )

        self.orientation_var = tk.StringVar(
            value="H"
        )

        self.orientation_menu = tk.OptionMenu(
            controls,
            self.orientation_var,
            "H",
            "V"
        )

        self.orientation_menu.grid(
            row=0,
            column=3,
            padx=5
        )

        self.place_button = tk.Button(
            controls,
            text="Place Ship",
            width=12,
            command=self.place_selected_ship
        )

        self.place_button.grid(
            row=0,
            column=4,
            padx=10
        )

        self.ready_button = tk.Button(
            controls,
            text="READY",
            width=12,
            command=self.ready
        )

        self.ready_button.grid(
            row=0,
            column=5,
            padx=10
        )

        # ----------------------------------------------------
        # TURN DISPLAY
        # ----------------------------------------------------

        self.turn_label = tk.Label(
            self.root,
            text="Waiting for players...",
            font=("Arial", 13, "bold")
        )

        self.turn_label.pack(
            pady=5
        )

        # ----------------------------------------------------
        # NETWORK LOG
        # ----------------------------------------------------

        log_frame = tk.LabelFrame(
            self.root,
            text="UDP Network Activity",
            padx=5,
            pady=5
        )

        log_frame.pack(
            fill="both",
            expand=False,
            padx=30,
            pady=10
        )

        self.log_text = tk.Text(
            log_frame,
            height=8,
            width=120,
            state="disabled"
        )

        self.log_text.pack(
            side="left",
            fill="both"
        )

        scrollbar = tk.Scrollbar(
            log_frame,
            command=self.log_text.yview
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        self.log_text.config(
            yscrollcommand=scrollbar.set
        )


    # ========================================================
    # CREATE BOARD
    # ========================================================

    def create_board(
        self,
        parent,
        callback
    ):

        board = {}

        # ----------------------------------------------------
        # COLUMN HEADERS
        # ----------------------------------------------------

        for col in range(BOARD_SIZE):

            label = tk.Label(
                parent,
                text=chr(
                    ord("A") + col
                ),
                width=5,
                font=("Arial", 10, "bold")
            )

            label.grid(
                row=0,
                column=col + 1
            )

        # ----------------------------------------------------
        # ROW HEADERS + CELLS
        # ----------------------------------------------------

        for row in range(BOARD_SIZE):

            label = tk.Label(
                parent,
                text=str(row + 1),
                width=3,
                font=("Arial", 10, "bold")
            )

            label.grid(
                row=row + 1,
                column=0
            )

            for col in range(BOARD_SIZE):

                cell = (
                    chr(ord("A") + col)
                    + str(row + 1)
                )

                button = tk.Button(
                    parent,
                    text="",
                    width=5,
                    height=2,
                    command=lambda c=cell: callback(c)
                )

                button.grid(
                    row=row + 1,
                    column=col + 1,
                    padx=1,
                    pady=1
                )

                board[cell] = button

        return board


    # ========================================================
    # NETWORK LOG
    # ========================================================

    def network_log(self, message):

        self.root.after(
            0,
            self._network_log,
            message
        )


    def _network_log(self, message):

        self.log_text.config(
            state="normal"
        )

        self.log_text.insert(
            "end",
            message + "\n"
        )

        self.log_text.see(
            "end"
        )

        self.log_text.config(
            state="disabled"
        )


    # ========================================================
    # CONNECT
    # ========================================================

    def connect(self):

        name = self.name_entry.get().strip()
        server_ip = self.server_ip_entry.get().strip()

        if not name:

            messagebox.showwarning(
                "Name Required",
                "Please enter your name."
            )

            return

        if not server_ip:

            messagebox.showwarning(
                "Server IP Required",
                "Please enter the server IP address."
            )

            return

        # Use the IP entered in the GUI before sending JOIN.
        self.client.host = server_ip

        self.status_label.config(
            text=f"Connecting to {server_ip}:5000..."
        )

        self.connect_button.config(
            state="disabled"
        )

        success = self.client.connect(
            name
        )

        if not success:

            self.status_label.config(
                text="Could not send JOIN."
            )

            self.connect_button.config(
                state="normal"
            )


    # ========================================================
    # WELCOME
    # ========================================================

    def handle_welcome(
        self,
        player_id
    ):

        self.root.after(
            0,
            self._handle_welcome,
            player_id
        )


    def _handle_welcome(
        self,
        player_id
    ):

        self.player_id = player_id

        self.connected = True

        self.player_label.config(
            text=f"You are {player_id}"
        )

        self.status_label.config(
            text="Connected. Place your ships."
        )

        self.network_log(
            f"Server assigned you as {player_id}."
        )


    # ========================================================
    # SHIP SELECTION
    # ========================================================

    def ship_changed(
        self,
        value
    ):

        self.selected_ship = value


    # ========================================================
    # OWN BOARD CLICK
    # ========================================================

    def own_cell_clicked(
        self,
        cell
    ):

        if not self.connected:
            return

        if self.game_started:
            return

        self.status_label.config(
            text=f"Selected {cell}"
        )

        self.selected_start_cell = cell


    # ========================================================
    # PLACE SHIP
    # ========================================================

    def place_selected_ship(self):

        if not self.connected:

            messagebox.showwarning(
                "Not Connected",
                "Connect to the server first."
            )

            return

        if self.game_started:

            messagebox.showwarning(
                "Game Started",
                "Ships can no longer be placed."
            )

            return

        ship = self.ship_var.get()

        orientation = (
            self.orientation_var.get()
        )

        if not hasattr(
            self,
            "selected_start_cell"
        ):

            messagebox.showwarning(
                "Select Cell",
                "Click a cell on your board first."
            )

            return

        start_cell = self.selected_start_cell

        if ship in self.placed_ships:

            messagebox.showwarning(
                "Already Placed",
                f"{ship} is already placed."
            )

            return

        # ----------------------------------------------------
        # LOCAL VALIDATION
        # ----------------------------------------------------

        cells = self.calculate_ship_cells(
            start_cell,
            orientation,
            SHIPS[ship]
        )

        if cells is None:

            messagebox.showerror(
                "Invalid Placement",
                "The ship goes outside the board."
            )

            return

        # ----------------------------------------------------
        # CHECK LOCAL OVERLAP
        # ----------------------------------------------------

        for cell in cells:

            if cell in self.own_cells:

                messagebox.showerror(
                    "Invalid Placement",
                    "The ship overlaps another ship."
                )

                return

        # ----------------------------------------------------
        # SEND TO SERVER
        # ----------------------------------------------------

        self.pending_ship = ship

        self.pending_cells = cells

        self.client.place_ship(
            ship,
            start_cell,
            orientation
        )


    # ========================================================
    # CALCULATE LOCAL SHIP CELLS
    # ========================================================

    def calculate_ship_cells(
        self,
        start_cell,
        orientation,
        size
    ):

        column = (
            ord(start_cell[0]) -
            ord("A")
        )

        row = int(
            start_cell[1]
        ) - 1

        cells = []

        for i in range(size):

            if orientation == "H":

                new_row = row

                new_column = (
                    column + i
                )

            else:

                new_row = (
                    row + i
                )

                new_column = column

            if (
                new_row < 0
                or new_row >= BOARD_SIZE
                or new_column < 0
                or new_column >= BOARD_SIZE
            ):

                return None

            cell = (
                chr(
                    ord("A") + new_column
                )
                + str(new_row + 1)
            )

            cells.append(cell)

        return cells


    # ========================================================
    # PLACE RESULT
    # ========================================================

    def handle_place_result(
        self,
        success,
        error
    ):

        self.root.after(
            0,
            self._handle_place_result,
            success,
            error
        )


    def _handle_place_result(
        self,
        success,
        error
    ):

        if success:

            ship = self.pending_ship

            cells = self.pending_cells

            for cell in cells:

                self.own_cells[cell] = ship

                self.own_board[cell].config(
                    text=ship,
                    state="disabled"
                )

            self.placed_ships.add(
                ship
            )

            self.status_label.config(
                text=f"{ship} placed successfully."
            )

            self.network_log(
                f"{ship} successfully placed."
            )

            self.update_ship_menu()

        else:

            self.status_label.config(
                text=f"Placement rejected: {error}"
            )

            messagebox.showerror(
                "Placement Rejected",
                str(error)
            )


    # ========================================================
    # UPDATE SHIP MENU
    # ========================================================

    def update_ship_menu(self):

        menu = self.ship_menu["menu"]

        menu.delete(
            0,
            "end"
        )

        remaining = []

        for ship in SHIPS:

            if ship not in self.placed_ships:

                remaining.append(ship)

                menu.add_command(
                    label=ship,
                    command=lambda s=ship:
                    self.ship_var.set(s)
                )

        if remaining:

            self.ship_var.set(
                remaining[0]
            )

        else:

            self.ship_var.set(
                "All Ships Placed"
            )


    # ========================================================
    # READY
    # ========================================================

    def ready(self):

        if not self.connected:

            messagebox.showwarning(
                "Not Connected",
                "Connect first."
            )

            return

        if len(self.placed_ships) != len(SHIPS):

            messagebox.showwarning(
                "Ships Missing",
                "Place all three ships first."
            )

            return

        self.client.ready()

        self.ready_button.config(
            state="disabled"
        )

        self.status_label.config(
            text="Ready. Waiting for opponent..."
        )


    # ========================================================
    # READY RESULT
    # ========================================================

    def handle_ready_result(
        self,
        success,
        error
    ):

        self.root.after(
            0,
            self._handle_ready_result,
            success,
            error
        )


    def _handle_ready_result(
        self,
        success,
        error
    ):

        if success:

            self.ready = True

            self.status_label.config(
                text="READY accepted. Waiting for opponent..."
            )

        else:

            self.ready_button.config(
                state="normal"
            )

            messagebox.showerror(
                "READY Error",
                str(error)
            )


    # ========================================================
    # GAME START
    # ========================================================

    def handle_game_start(self):

        self.root.after(
            0,
            self._handle_game_start
        )


    def _handle_game_start(self):

        self.game_started = True

        self.status_label.config(
            text="Game started!"
        )

        self.place_button.config(
            state="disabled"
        )

        self.ready_button.config(
            state="disabled"
        )

        self.ship_menu.config(
            state="disabled"
        )

        self.orientation_menu.config(
            state="disabled"
        )


    # ========================================================
    # TURN
    # ========================================================

    def handle_turn(
        self,
        player
    ):

        self.root.after(
            0,
            self._handle_turn,
            player
        )


    def _handle_turn(
        self,
        player
    ):

        self.current_turn = player

        if player == self.player_id:

            self.turn_label.config(
                text="YOUR TURN - Fire at opponent!"
            )

            self.status_label.config(
                text="Select a cell on the opponent board."
            )

        else:

            self.turn_label.config(
                text=f"{player}'s turn"
            )

            self.status_label.config(
                text="Waiting for opponent..."
            )


    # ========================================================
    # ENEMY CELL CLICK
    # ========================================================

    def enemy_cell_clicked(
        self,
        cell
    ):

        if not self.game_started:

            return

        if self.current_turn != self.player_id:

            messagebox.showwarning(
                "Not Your Turn",
                "Wait for your opponent's turn."
            )

            return

        if cell in self.enemy_cells:

            messagebox.showwarning(
                "Already Fired",
                "You already fired at this cell."
            )

            return

        answer = messagebox.askyesno(
            "Fire",
            f"Fire at {cell}?"
        )

        if not answer:

            return

        self.client.fire(
            cell
        )


    # ========================================================
    # SHOT RESULT
    # ========================================================

    def handle_result(
        self,
        result,
        cell,
        error
    ):

        self.root.after(
            0,
            self._handle_result,
            result,
            cell,
            error
        )


    def _handle_result(
        self,
        result,
        cell,
        error
    ):

        if result == "HIT":

            self.enemy_cells[cell] = "HIT"

            self.enemy_board[cell].config(
                text="X",
                state="disabled"
            )

            self.status_label.config(
                text=f"HIT at {cell}!"
            )

        elif result == "MISS":

            self.enemy_cells[cell] = "MISS"

            self.enemy_board[cell].config(
                text="O",
                state="disabled"
            )

            self.status_label.config(
                text=f"MISS at {cell}."
            )

        elif result == "INVALID":

            self.status_label.config(
                text=f"Invalid shot: {error}"
            )


    # ========================================================
    # OPPONENT ATTACK
    # ========================================================

    def handle_attack(
        self,
        result,
        cell
    ):

        self.root.after(
            0,
            self._handle_attack,
            result,
            cell
        )


    def _handle_attack(
        self,
        result,
        cell
    ):

        if result == "HIT":

            self.own_board[cell].config(
                text="X"
            )

            self.status_label.config(
                text=f"Your ship was hit at {cell}!"
            )

        elif result == "MISS":

            self.own_board[cell].config(
                text="O"
            )

            self.status_label.config(
                text=f"Opponent missed at {cell}."
            )


    # ========================================================
    # SUNK
    # ========================================================

    def handle_sunk(
        self,
        ship
    ):

        self.root.after(
            0,
            lambda: self.status_label.config(
                text=f"You sunk {ship}!"
            )
        )


    # ========================================================
    # SHIP HIT
    # ========================================================

    def handle_ship_hit(
        self,
        ship
    ):

        self.root.after(
            0,
            lambda: self.status_label.config(
                text=f"Your {ship} was hit!"
            )
        )


    # ========================================================
    # WIN
    # ========================================================

    def handle_win(
        self,
        player
    ):

        self.root.after(
            0,
            self._handle_win,
            player
        )


    def _handle_win(
        self,
        player
    ):

        self.game_started = False

        self.current_turn = None

        self.turn_label.config(
            text="YOU WIN!"
        )

        self.status_label.config(
            text="Congratulations! You won the game."
        )

        messagebox.showinfo(
            "Game Over",
            "YOU WIN!"
        )


    # ========================================================
    # LOSE
    # ========================================================

    def handle_lose(self):

        self.root.after(
            0,
            self._handle_lose
        )


    def _handle_lose(self):

        self.game_started = False

        self.current_turn = None

        self.turn_label.config(
            text="YOU LOSE"
        )

        self.status_label.config(
            text="Your opponent won."
        )

        messagebox.showinfo(
            "Game Over",
            "YOU LOSE!"
        )


    # ========================================================
    # SERVER ERROR
    # ========================================================

    def handle_error(
        self,
        error
    ):

        self.root.after(
            0,
            self._handle_error,
            error
        )


    def _handle_error(
        self,
        error
    ):

        self.status_label.config(
            text=f"Server error: {error}"
        )


    # ========================================================
    # CLOSE
    # ========================================================

    def close(self):

        try:

            self.client.stop()

        except Exception:
            pass

        self.root.destroy()


# ============================================================
# START APPLICATION
# ============================================================

if __name__ == "__main__":

    root = tk.Tk()

    app = BattleshipGUI(
        root
    )

    root.mainloop()
