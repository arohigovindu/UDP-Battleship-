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
# BATTLESHIP GUI
# ============================================================

class BattleshipGUI:

    def __init__(self, root):

        self.root = root

        self.root.title("UDP Battleship")

        self.root.geometry("1150x800")

        self.root.resizable(False, False)

        # ----------------------------------------------------
        # UDP CLIENT
        # ----------------------------------------------------

        self.client = BattleshipClient(
            host="127.0.0.1",
            port=5000
        )

        # ----------------------------------------------------
        # CONNECTION STATE
        # ----------------------------------------------------

        self.player_id = None

        self.connected = False

        self.game_started = False

        self.ready_sent = False

        self.current_turn = None

        # ----------------------------------------------------
        # SHIP STATE
        # ----------------------------------------------------

        self.placed_ships = set()

        self.selected_start_cell = None

        self.pending_ship = None

        self.pending_cells = []

        # ----------------------------------------------------
        # BOARD STATE
        # ----------------------------------------------------

        self.own_cells = {}

        self.enemy_cells = {}

        # ----------------------------------------------------
        # CALLBACK STATE
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
        # WINDOW CLOSE
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

        title.pack(
            pady=10
        )

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
            text="Player Name:",
            font=("Arial", 11)
        ).grid(
            row=0,
            column=0,
            padx=5
        )

        self.name_entry = tk.Entry(
            connection_frame,
            width=20,
            font=("Arial", 11)
        )

        self.name_entry.grid(
            row=0,
            column=1,
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
            column=2,
            padx=5
        )

        self.player_label = tk.Label(
            connection_frame,
            text="Not connected",
            font=("Arial", 11, "bold")
        )

        self.player_label.grid(
            row=0,
            column=3,
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
        # BOARDS
        # ----------------------------------------------------

        boards_frame = tk.Frame(
            self.root
        )

        boards_frame.pack(
            pady=10
        )

        # ----------------------------------------------------
        # OWN BOARD
        # ----------------------------------------------------

        own_frame = tk.LabelFrame(
            boards_frame,
            text="Your Board",
            font=("Arial", 12, "bold"),
            padx=10,
            pady=10
        )

        own_frame.grid(
            row=0,
            column=0,
            padx=30
        )

        self.own_board = self.create_board(
            own_frame,
            self.own_cell_clicked
        )

        # ----------------------------------------------------
        # ENEMY BOARD
        # ----------------------------------------------------

        enemy_frame = tk.LabelFrame(
            boards_frame,
            text="Opponent Board",
            font=("Arial", 12, "bold"),
            padx=10,
            pady=10
        )

        enemy_frame.grid(
            row=0,
            column=1,
            padx=30
        )

        self.enemy_board = self.create_board(
            enemy_frame,
            self.enemy_cell_clicked
        )

        # ----------------------------------------------------
        # SHIP CONTROLS
        # ----------------------------------------------------

        controls = tk.LabelFrame(
            self.root,
            text="Ship Placement",
            font=("Arial", 11, "bold"),
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
            *SHIPS.keys()
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
            width=13,
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
            width=13,
            command=self.ready,
            state="disabled"
        )

        self.ready_button.grid(
            row=0,
            column=5,
            padx=10
        )

        # ----------------------------------------------------
        # PLACEMENT INFORMATION
        # ----------------------------------------------------

        self.placement_label = tk.Label(
            self.root,
            text="Place all 3 ships.",
            font=("Arial", 11)
        )

        self.placement_label.pack(
            pady=3
        )

        # ----------------------------------------------------
        # TURN
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
            font=("Arial", 10, "bold"),
            padx=5,
            pady=5
        )

        log_frame.pack(
            padx=30,
            pady=8,
            fill="x"
        )

        self.log_text = tk.Text(
            log_frame,
            height=9,
            width=125,
            state="disabled"
        )

        self.log_text.pack(
            side="left"
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
    # CREATE 5x5 BOARD
    # ========================================================

    def create_board(
        self,
        parent,
        callback
    ):

        board = {}

        # ----------------------------------------------------
        # COLUMN LABELS
        # ----------------------------------------------------

        for col in range(BOARD_SIZE):

            label = tk.Label(
                parent,
                text=chr(ord("A") + col),
                width=7,
                font=("Arial", 10, "bold")
            )

            label.grid(
                row=0,
                column=col + 1
            )

        # ----------------------------------------------------
        # ROW LABELS AND BUTTONS
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
                    width=7,
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

    def network_log(
        self,
        message
    ):

        try:

            self.root.after(
                0,
                self._network_log,
                message
            )

        except tk.TclError:

            pass


    def _network_log(
        self,
        message
    ):

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

        if not name:

            messagebox.showwarning(
                "Name Required",
                "Please enter your name."
            )

            return

        self.connect_button.config(
            state="disabled"
        )

        self.name_entry.config(
            state="disabled"
        )

        self.status_label.config(
            text="Connecting to UDP server..."
        )

        success = self.client.connect(
            name
        )

        if not success:

            self.connect_button.config(
                state="normal"
            )

            self.name_entry.config(
                state="normal"
            )

            self.status_label.config(
                text="Failed to send JOIN."
            )


    # ========================================================
    # WELCOME FROM SERVER
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

        self.placement_label.config(
            text="Place Ship1, Ship2 and Ship3."
        )


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

        if self.ready_sent:

            return

        self.selected_start_cell = cell

        self.status_label.config(
            text=f"Selected starting cell: {cell}"
        )

        self.placement_label.config(
            text=f"Selected {cell}. Choose ship/orientation and click Place Ship."
        )


    # ========================================================
    # CALCULATE SHIP CELLS
    # ========================================================

    def calculate_ship_cells(
        self,
        start_cell,
        orientation,
        size
    ):

        try:

            column = (
                ord(start_cell[0]) -
                ord("A")
            )

            row = (
                int(start_cell[1]) - 1
            )

        except (ValueError, IndexError):

            return None

        cells = []

        for i in range(size):

            if orientation == "H":

                new_row = row

                new_column = column + i

            elif orientation == "V":

                new_row = row + i

                new_column = column

            else:

                return None

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
    # PLACE SELECTED SHIP
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

        if self.ready_sent:

            return

        if self.selected_start_cell is None:

            messagebox.showwarning(
                "Select Starting Cell",
                "Click a cell on your board first."
            )

            return

        ship = self.ship_var.get()

        orientation = (
            self.orientation_var.get().upper()
        )

        # ----------------------------------------------------
        # MAKE SURE SHIP EXISTS
        # ----------------------------------------------------

        if ship not in SHIPS:

            messagebox.showwarning(
                "Invalid Ship",
                "Please select a valid ship."
            )

            return

        # ----------------------------------------------------
        # DON'T PLACE SAME SHIP TWICE
        # ----------------------------------------------------

        if ship in self.placed_ships:

            messagebox.showwarning(
                "Ship Already Placed",
                f"{ship} has already been placed."
            )

            return

        # ----------------------------------------------------
        # CALCULATE LOCAL CELLS
        # ----------------------------------------------------

        cells = self.calculate_ship_cells(
            self.selected_start_cell,
            orientation,
            SHIPS[ship]
        )

        if cells is None:

            messagebox.showerror(
                "Invalid Placement",
                "The ship goes outside the 5x5 board."
            )

            return

        # ----------------------------------------------------
        # LOCAL OVERLAP CHECK
        # ----------------------------------------------------

        for cell in cells:

            if cell in self.own_cells:

                messagebox.showerror(
                    "Invalid Placement",
                    f"The ship overlaps at {cell}."
                )

                return

        # ----------------------------------------------------
        # SAVE PENDING PLACEMENT
        # ----------------------------------------------------

        self.pending_ship = ship

        self.pending_cells = cells

        # ----------------------------------------------------
        # DISABLE PLACE BUTTON WHILE WAITING
        # ----------------------------------------------------

        self.place_button.config(
            state="disabled"
        )

        self.status_label.config(
            text=(
                f"Requesting placement: "
                f"{ship} at "
                f"{self.selected_start_cell} "
                f"({orientation})"
            )
        )

        # ----------------------------------------------------
        # SEND UDP REQUEST
        # ----------------------------------------------------

        self.client.place_ship(
            ship,
            self.selected_start_cell,
            orientation
        )


    # ========================================================
    # SERVER PLACEMENT RESULT
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

        # ----------------------------------------------------
        # SERVER ACCEPTED
        # ----------------------------------------------------

        if success:

            ship = self.pending_ship

            cells = list(
                self.pending_cells
            )

            # -----------------------------------------------
            # SAFETY CHECK
            # -----------------------------------------------

            if ship is None:

                self.place_button.config(
                    state="normal"
                )

                return

            # -----------------------------------------------
            # RECORD SHIP
            # -----------------------------------------------

            self.placed_ships.add(
                ship
            )

            # -----------------------------------------------
            # RECORD CELLS
            # -----------------------------------------------

            for cell in cells:

                self.own_cells[cell] = ship

                self.own_board[cell].config(
                    text=ship,
                    state="disabled"
                )

            # -----------------------------------------------
            # CLEAR PENDING
            # -----------------------------------------------

            self.pending_ship = None

            self.pending_cells = []

            self.selected_start_cell = None

            # -----------------------------------------------
            # UPDATE UI
            # -----------------------------------------------

            self.status_label.config(
                text=f"{ship} successfully placed."
            )

            self.placement_label.config(
                text=(
                    f"{len(self.placed_ships)}/3 ships placed."
                )
            )

            # -----------------------------------------------
            # ENABLE / DISABLE READY
            # -----------------------------------------------

            if len(self.placed_ships) == len(SHIPS):

                self.ready_button.config(
                    state="normal"
                )

                self.place_button.config(
                    state="disabled"
                )

                self.ship_menu.config(
                    state="disabled"
                )

                self.orientation_menu.config(
                    state="disabled"
                )

                self.placement_label.config(
                    text=(
                        "All 3 ships placed. "
                        "Click READY."
                    )
                )

                self.status_label.config(
                    text=(
                        "All ships placed. "
                        "You can now click READY."
                    )
                )

            else:

                self.place_button.config(
                    state="normal"
                )

                self.select_next_ship()

        # ----------------------------------------------------
        # SERVER REJECTED
        # ----------------------------------------------------

        else:

            self.status_label.config(
                text=f"Placement rejected: {error}"
            )

            self.place_button.config(
                state="normal"
            )

            self.pending_ship = None

            self.pending_cells = []

            messagebox.showerror(
                "Placement Rejected",
                str(error)
            )


    # ========================================================
    # SELECT NEXT UNPLACED SHIP
    # ========================================================

    def select_next_ship(self):

        for ship in SHIPS:

            if ship not in self.placed_ships:

                self.ship_var.set(
                    ship
                )

                return


    # ========================================================
    # READY
    # ========================================================

    def ready(self):

        if not self.connected:

            messagebox.showwarning(
                "Not Connected",
                "Connect to the server first."
            )

            return

        # ----------------------------------------------------
        # IMPORTANT CHECK
        # ----------------------------------------------------

        if len(self.placed_ships) != len(SHIPS):

            messagebox.showwarning(
                "Ships Missing",
                (
                    "You must successfully place "
                    "all 3 ships first."
                )
            )

            return

        if self.ready_sent:

            return

        # ----------------------------------------------------
        # SEND READY
        # ----------------------------------------------------

        self.ready_sent = True

        self.ready_button.config(
            state="disabled"
        )

        self.status_label.config(
            text="Sending READY to server..."
        )

        self.client.ready()


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

            self.status_label.config(
                text=(
                    "READY accepted. "
                    "Waiting for opponent..."
                )
            )

            self.placement_label.config(
                text=(
                    "You are ready. "
                    "Waiting for the other player."
                )
            )

        else:

            self.ready_sent = False

            self.ready_button.config(
                state="normal"
            )

            self.status_label.config(
                text=f"READY rejected: {error}"
            )

            messagebox.showerror(
                "READY Rejected",
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

        self.placement_label.config(
            text="All ships locked. Attack the opponent."
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

        self.turn_label.config(
            text="Game started. Waiting for turn..."
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
                text="YOUR TURN"
            )

            self.status_label.config(
                text=(
                    "Your turn. "
                    "Click a cell on the opponent board."
                )
            )

        else:

            self.turn_label.config(
                text=f"{player}'s TURN"
            )

            self.status_label.config(
                text=(
                    "Waiting for your opponent..."
                )
            )


    # ========================================================
    # ENEMY BOARD CLICK
    # ========================================================

    def enemy_cell_clicked(
        self,
        cell
    ):

        if not self.game_started:

            messagebox.showwarning(
                "Game Not Started",
                "The game has not started yet."
            )

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
                f"You already fired at {cell}."
            )

            return

        confirm = messagebox.askyesno(
            "Confirm Attack",
            f"Fire at {cell}?"
        )

        if not confirm:

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
                text=f"Your ship was hit at {cell}."
            )

        elif result == "MISS":

            self.own_board[cell].config(
                text="O"
            )

            self.status_label.config(
                text=f"Opponent missed at {cell}."
            )


    # ========================================================
    # SHIP SUNK
    # ========================================================

    def handle_sunk(
        self,
        ship
    ):

        self.root.after(
            0,
            self._show_sunk,
            ship
        )


    def _show_sunk(
        self,
        ship
    ):

        self.status_label.config(
            text=f"You sunk {ship}!"
        )


    # ========================================================
    # YOUR SHIP HIT
    # ========================================================

    def handle_ship_hit(
        self,
        ship
    ):

        self.root.after(
            0,
            self._show_ship_hit,
            ship
        )


    def _show_ship_hit(
        self,
        ship
    ):

        self.status_label.config(
            text=f"Your {ship} was hit!"
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
            text="Congratulations! You won!"
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
            text="Your opponent won the game."
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
    # CLOSE APPLICATION
    # ========================================================

    def close(self):

        try:

            self.client.stop()

        except Exception:

            pass

        self.root.destroy()


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    root = tk.Tk()

    app = BattleshipGUI(
        root
    )

    root.mainloop()

