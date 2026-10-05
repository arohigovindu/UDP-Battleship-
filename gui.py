import tkinter as tk
from tkinter import messagebox

from client import BattleshipClient


# ============================================================
# UDP BATTLESHIP
# COMPLETE GAME-STYLE GUI
# ============================================================

BOARD_SIZE = 5

SHIPS = {
    "Ship1": 3,
    "Ship2": 2,
    "Ship3": 2
}


# ============================================================
# DARK NAVY + TEAL THEME
# ============================================================

BG = "#071A2B"
PANEL = "#0B2438"
PANEL_LIGHT = "#10344A"

TEAL = "#18D6C5"
TEAL_DARK = "#0E9F96"
TEAL_LIGHT = "#7FFFEF"

WHITE = "#F4FAFA"
TEXT = "#C9D9DE"
MUTED = "#718A96"

GRID = "#16445A"
GRID_HOVER = "#1E6277"

WATER = "#09263A"
SHIP = "#147F7A"
SHIP_LIGHT = "#55E0D4"

HIT = "#FF5C5C"
MISS = "#5FA8C5"
SELECTED = "#D6B84C"

SUCCESS = "#49D17D"
WARNING = "#F0B44D"


# ============================================================
# MAIN GUI
# ============================================================

class BattleshipGUI:

    def __init__(self, root):

        self.root = root

        self.root.title("UDP Battleship")

        self.root.geometry("1250x900")

        self.root.minsize(1150, 820)

        self.root.configure(
            bg=BG
        )

        # ====================================================
        # UDP CLIENT
        # ====================================================

        self.client = BattleshipClient(
            host="127.0.0.1",
            port=5000
        )

        # ====================================================
        # CONNECTION / GAME STATE
        # ====================================================

        self.player_id = None

        self.connected = False

        self.game_started = False

        self.ready_sent = False

        self.current_turn = None

        # ====================================================
        # SHIP STATE
        # ====================================================

        self.placed_ships = set()

        self.selected_start_cell = None

        self.pending_ship = None

        self.pending_cells = []

        # ====================================================
        # BOARD STATE
        # ====================================================

        self.own_cells = {}

        self.enemy_cells = {}

        # ====================================================
        # CLIENT CALLBACKS
        # ====================================================

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

        # ====================================================
        # BUILD GUI
        # ====================================================

        self.build_gui()

        # ====================================================
        # WINDOW CLOSE
        # ====================================================

        self.root.protocol(
            "WM_DELETE_WINDOW",
            self.close
        )


    # ========================================================
    # BUILD GUI
    # ========================================================

    def build_gui(self):

        # ====================================================
        # HEADER
        # ====================================================

        header = tk.Frame(
            self.root,
            bg=BG
        )

        header.pack(
            fill="x",
            padx=30,
            pady=(18, 5)
        )

        title = tk.Label(
            header,
            text="UDP BATTLESHIP",
            font=("Arial", 28, "bold"),
            fg=TEAL,
            bg=BG
        )

        title.pack()

        subtitle = tk.Label(
            header,
            text="REAL-TIME NAVAL COMBAT  •  UDP NETWORK",
            font=("Arial", 9, "bold"),
            fg=MUTED,
            bg=BG
        )

        subtitle.pack(
            pady=(2, 0)
        )

        # ====================================================
        # CONNECTION PANEL
        # ====================================================

        connection = tk.Frame(
            self.root,
            bg=PANEL,
            highlightbackground=GRID,
            highlightthickness=1
        )

        connection.pack(
            fill="x",
            padx=30,
            pady=10
        )

        connection_inner = tk.Frame(
            connection,
            bg=PANEL
        )

        connection_inner.pack(
            pady=10
        )

        tk.Label(
            connection_inner,
            text="CALLSIGN",
            font=("Arial", 9, "bold"),
            fg=MUTED,
            bg=PANEL
        ).grid(
            row=0,
            column=0,
            padx=(10, 5)
        )

        self.name_entry = tk.Entry(
            connection_inner,
            width=18,
            font=("Arial", 11),
            bg="#061522",
            fg=WHITE,
            insertbackground=TEAL,
            relief="flat"
        )

        self.name_entry.grid(
            row=0,
            column=1,
            padx=5,
            ipady=5
        )

        self.connect_button = tk.Button(
            connection_inner,
            text="CONNECT",
            font=("Arial", 9, "bold"),
            fg=BG,
            bg=TEAL,
            activebackground=TEAL_LIGHT,
            activeforeground=BG,
            relief="flat",
            width=12,
            command=self.connect
        )

        self.connect_button.grid(
            row=0,
            column=2,
            padx=10,
            ipady=3
        )

        self.player_label = tk.Label(
            connection_inner,
            text="PLAYER: --",
            font=("Arial", 10, "bold"),
            fg=TEXT,
            bg=PANEL
        )

        self.player_label.grid(
            row=0,
            column=3,
            padx=20
        )

        self.connection_status = tk.Label(
            connection_inner,
            text="● OFFLINE",
            font=("Arial", 10, "bold"),
            fg=MUTED,
            bg=PANEL
        )

        self.connection_status.grid(
            row=0,
            column=4,
            padx=10
        )

        # ====================================================
        # MAIN STATUS
        # ====================================================

        self.status_frame = tk.Frame(
            self.root,
            bg=PANEL_LIGHT,
            highlightbackground=GRID,
            highlightthickness=1
        )

        self.status_frame.pack(
            fill="x",
            padx=30,
            pady=(5, 10)
        )

        self.status_label = tk.Label(
            self.status_frame,
            text="Welcome, Captain. Connect to the UDP server.",
            font=("Arial", 12, "bold"),
            fg=WHITE,
            bg=PANEL_LIGHT
        )

        self.status_label.pack(
            pady=9
        )

        # ====================================================
        # BOARDS CONTAINER
        # ====================================================

        boards_container = tk.Frame(
            self.root,
            bg=BG
        )

        boards_container.pack(
            pady=5
        )

        # ====================================================
        # YOUR FLEET
        # ====================================================

        own_panel = tk.Frame(
            boards_container,
            bg=PANEL,
            highlightbackground=TEAL_DARK,
            highlightthickness=1
        )

        own_panel.grid(
            row=0,
            column=0,
            padx=18
        )

        tk.Label(
            own_panel,
            text="YOUR FLEET",
            font=("Arial", 15, "bold"),
            fg=TEAL,
            bg=PANEL
        ).pack(
            pady=(10, 0)
        )

        tk.Label(
            own_panel,
            text="DEFEND YOUR FLEET",
            font=("Arial", 8, "bold"),
            fg=MUTED,
            bg=PANEL
        ).pack(
            pady=(1, 8)
        )

        self.own_board = self.create_board(
            own_panel,
            self.own_cell_clicked
        )

        # ====================================================
        # VS
        # ====================================================

        vs_frame = tk.Frame(
            boards_container,
            bg=BG
        )

        vs_frame.grid(
            row=0,
            column=1,
            padx=5
        )

        tk.Label(
            vs_frame,
            text="VS",
            font=("Arial", 18, "bold"),
            fg=MUTED,
            bg=BG
        ).pack()

        # ====================================================
        # ENEMY FLEET
        # ====================================================

        enemy_panel = tk.Frame(
            boards_container,
            bg=PANEL,
            highlightbackground=TEAL_DARK,
            highlightthickness=1
        )

        enemy_panel.grid(
            row=0,
            column=2,
            padx=18
        )

        tk.Label(
            enemy_panel,
            text="ENEMY FLEET",
            font=("Arial", 15, "bold"),
            fg=TEAL,
            bg=PANEL
        ).pack(
            pady=(10, 0)
        )

        tk.Label(
            enemy_panel,
            text="SELECT YOUR TARGET",
            font=("Arial", 8, "bold"),
            fg=MUTED,
            bg=PANEL
        ).pack(
            pady=(1, 8)
        )

        self.enemy_board = self.create_board(
            enemy_panel,
            self.enemy_cell_clicked
        )

        # ====================================================
        # TURN INDICATOR
        # ====================================================

        self.turn_frame = tk.Frame(
            self.root,
            bg=PANEL,
            highlightbackground=GRID,
            highlightthickness=1
        )

        self.turn_frame.pack(
            fill="x",
            padx=170,
            pady=12
        )

        self.turn_label = tk.Label(
            self.turn_frame,
            text="WAITING FOR PLAYERS",
            font=("Arial", 17, "bold"),
            fg=MUTED,
            bg=PANEL
        )

        self.turn_label.pack(
            pady=(8, 1)
        )

        self.turn_subtitle = tk.Label(
            self.turn_frame,
            text="Connect both players to begin.",
            font=("Arial", 9),
            fg=MUTED,
            bg=PANEL
        )

        self.turn_subtitle.pack(
            pady=(0, 8)
        )

        # ====================================================
        # FLEET DEPLOYMENT
        # ====================================================

        controls = tk.Frame(
            self.root,
            bg=PANEL,
            highlightbackground=GRID,
            highlightthickness=1
        )

        controls.pack(
            fill="x",
            padx=30,
            pady=5
        )

        tk.Label(
            controls,
            text="FLEET DEPLOYMENT",
            font=("Arial", 10, "bold"),
            fg=TEAL,
            bg=PANEL
        ).grid(
            row=0,
            column=0,
            columnspan=6,
            pady=(8, 5)
        )

        tk.Label(
            controls,
            text="SHIP",
            font=("Arial", 8, "bold"),
            fg=MUTED,
            bg=PANEL
        ).grid(
            row=1,
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

        self.ship_menu.config(
            bg="#09263A",
            fg=WHITE,
            activebackground=GRID_HOVER,
            activeforeground=WHITE,
            relief="flat",
            width=10
        )

        self.ship_menu["menu"].config(
            bg="#09263A",
            fg=WHITE,
            activebackground=TEAL_DARK,
            activeforeground=WHITE
        )

        self.ship_menu.grid(
            row=1,
            column=1,
            padx=5
        )

        tk.Label(
            controls,
            text="DIRECTION",
            font=("Arial", 8, "bold"),
            fg=MUTED,
            bg=PANEL
        ).grid(
            row=1,
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

        self.orientation_menu.config(
            bg="#09263A",
            fg=WHITE,
            activebackground=GRID_HOVER,
            activeforeground=WHITE,
            relief="flat",
            width=8
        )

        self.orientation_menu["menu"].config(
            bg="#09263A",
            fg=WHITE,
            activebackground=TEAL_DARK,
            activeforeground=WHITE
        )

        self.orientation_menu.grid(
            row=1,
            column=3,
            padx=5
        )

        self.place_button = tk.Button(
            controls,
            text="DEPLOY SHIP",
            font=("Arial", 9, "bold"),
            fg=BG,
            bg=TEAL,
            activebackground=TEAL_LIGHT,
            relief="flat",
            width=15,
            command=self.place_selected_ship
        )

        self.place_button.grid(
            row=1,
            column=4,
            padx=10,
            ipady=3
        )

        self.ready_button = tk.Button(
            controls,
            text="READY",
            font=("Arial", 9, "bold"),
            fg=WHITE,
            bg=TEAL_DARK,
            activebackground=TEAL,
            relief="flat",
            width=15,
            state="disabled",
            command=self.ready
        )

        self.ready_button.grid(
            row=1,
            column=5,
            padx=10,
            ipady=3
        )

        self.placement_label = tk.Label(
            controls,
            text="0 / 3 SHIPS DEPLOYED",
            font=("Arial", 9, "bold"),
            fg=MUTED,
            bg=PANEL
        )

        self.placement_label.grid(
            row=2,
            column=0,
            columnspan=6,
            pady=(6, 9)
        )

        # ====================================================
        # NETWORK LOG
        # ====================================================

        log_panel = tk.Frame(
            self.root,
            bg=PANEL,
            highlightbackground=GRID,
            highlightthickness=1
        )

        log_panel.pack(
            fill="x",
            padx=30,
            pady=(8, 15)
        )

        tk.Label(
            log_panel,
            text="NETWORK ACTIVITY",
            font=("Arial", 8, "bold"),
            fg=TEAL,
            bg=PANEL
        ).pack(
            anchor="w",
            padx=8,
            pady=(5, 2)
        )

        self.log_text = tk.Text(
            log_panel,
            height=6,
            bg="#061522",
            fg="#8FAEB8",
            insertbackground=TEAL,
            relief="flat",
            state="disabled",
            font=("Courier", 8)
        )

        self.log_text.pack(
            fill="x",
            padx=7,
            pady=(0, 7)
        )


    # ========================================================
    # CREATE BOARD
    #
    # IMPORTANT:
    # The title/subtitle use PACK in the parent.
    # The actual board gets its own child frame and uses GRID.
    #
    # This completely fixes:
    #
    # TclError:
    # cannot use geometry manager grid inside ... which
    # already has slaves managed by pack
    # ========================================================

    def create_board(
        self,
        parent,
        callback
    ):

        board_frame = tk.Frame(
            parent,
            bg=PANEL
        )

        board_frame.pack(
            padx=10,
            pady=(0, 12)
        )

        board = {}

        # ====================================================
        # COLUMN HEADERS
        # ====================================================

        for col in range(BOARD_SIZE):

            label = tk.Label(
                board_frame,
                text=chr(ord("A") + col),
                width=5,
                font=("Arial", 9, "bold"),
                fg=MUTED,
                bg=PANEL
            )

            label.grid(
                row=0,
                column=col + 1,
                pady=(0, 4)
            )

        # ====================================================
        # ROWS AND CELLS
        # ====================================================

        for row in range(BOARD_SIZE):

            row_label = tk.Label(
                board_frame,
                text=str(row + 1),
                width=2,
                font=("Arial", 9, "bold"),
                fg=MUTED,
                bg=PANEL
            )

            row_label.grid(
                row=row + 1,
                column=0,
                padx=(0, 4)
            )

            for col in range(BOARD_SIZE):

                cell = (
                    chr(ord("A") + col)
                    + str(row + 1)
                )

                button = tk.Button(
                    board_frame,
                    text="",
                    width=5,
                    height=2,
                    bg=WATER,
                    fg=WHITE,
                    activebackground=GRID_HOVER,
                    activeforeground=WHITE,
                    relief="flat",
                    highlightbackground=GRID,
                    highlightthickness=1,
                    font=("Arial", 12, "bold"),
                    command=lambda c=cell: callback(c)
                )

                button.grid(
                    row=row + 1,
                    column=col + 1,
                    padx=2,
                    pady=2
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
            str(message) + "\n"
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
                "Callsign Required",
                "Enter your player name first."
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

        try:

            success = self.client.connect(
                name
            )

        except Exception as e:

            success = False

            self.network_log(
                f"Client connection error: {e}"
            )

        if success is False:

            self.connect_button.config(
                state="normal"
            )

            self.name_entry.config(
                state="normal"
            )

            self.status_label.config(
                text="Unable to contact UDP server."
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
            text=f"PLAYER: {player_id}"
        )

        self.connection_status.config(
            text="● ONLINE",
            fg=SUCCESS
        )

        self.status_label.config(
            text="Connection established. Deploy your fleet."
        )

        self.placement_label.config(
            text="0 / 3 SHIPS DEPLOYED"
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

        if cell in self.own_cells:
            return

        self.selected_start_cell = cell

        self.status_label.config(
            text=f"Starting position selected: {cell}"
        )

        # Reset unoccupied cells
        for cell_name, button in self.own_board.items():

            if cell_name not in self.own_cells:

                button.config(
                    bg=WATER
                )

        self.own_board[cell].config(
            bg=SELECTED
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

        if not start_cell or len(start_cell) != 2:
            return None

        try:

            column = (
                ord(start_cell[0].upper())
                - ord("A")
            )

            row = (
                int(start_cell[1])
                - 1
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
                    ord("A")
                    + new_column
                )
                + str(new_row + 1)
            )

            cells.append(
                cell
            )

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
            return

        if self.ready_sent:
            return

        if self.selected_start_cell is None:

            messagebox.showwarning(
                "Select Position",
                "Click a starting cell on YOUR FLEET."
            )

            return

        ship = self.ship_var.get()

        orientation = (
            self.orientation_var.get().upper()
        )

        if ship in self.placed_ships:

            messagebox.showwarning(
                "Already Deployed",
                f"{ship} is already deployed."
            )

            return

        cells = self.calculate_ship_cells(
            self.selected_start_cell,
            orientation,
            SHIPS[ship]
        )

        if cells is None:

            messagebox.showerror(
                "Out of Bounds",
                "That ship does not fit on the board."
            )

            return

        # ====================================================
        # LOCAL OVERLAP CHECK
        # ====================================================

        for cell in cells:

            if cell in self.own_cells:

                messagebox.showerror(
                    "Fleet Overlap",
                    f"Another ship already occupies {cell}."
                )

                return

        # ====================================================
        # SAVE PENDING SHIP
        # ====================================================

        self.pending_ship = ship

        self.pending_cells = cells

        self.place_button.config(
            state="disabled"
        )

        self.status_label.config(
            text=(
                f"Deploying {ship} "
                f"from {self.selected_start_cell}..."
            )
        )

        # ====================================================
        # SEND UDP REQUEST
        # ====================================================

        try:

            self.client.place_ship(
                ship,
                self.selected_start_cell,
                orientation
            )

        except Exception as e:

            self.pending_ship = None

            self.pending_cells = []

            self.place_button.config(
                state="normal"
            )

            self.status_label.config(
                text="Unable to send placement request."
            )

            self.network_log(
                f"Placement error: {e}"
            )


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

            cells = list(
                self.pending_cells
            )

            if ship is None:

                self.place_button.config(
                    state="normal"
                )

                return

            # =================================================
            # CONFIRM SHIP
            # =================================================

            self.placed_ships.add(
                ship
            )

            for cell in cells:

                self.own_cells[cell] = ship

                self.own_board[cell].config(
                    text="▰",
                    fg=SHIP_LIGHT,
                    bg=SHIP,
                    state="disabled"
                )

            # =================================================
            # CLEAR PENDING
            # =================================================

            self.pending_ship = None

            self.pending_cells = []

            self.selected_start_cell = None

            # =================================================
            # UPDATE COUNT
            # =================================================

            count = len(
                self.placed_ships
            )

            self.placement_label.config(
                text=f"{count} / 3 SHIPS DEPLOYED"
            )

            self.status_label.config(
                text=f"{ship} successfully deployed."
            )

            # =================================================
            # ALL SHIPS DEPLOYED
            # =================================================

            if count == len(SHIPS):

                self.place_button.config(
                    state="disabled"
                )

                self.ready_button.config(
                    state="normal"
                )

                self.ship_menu.config(
                    state="disabled"
                )

                self.orientation_menu.config(
                    state="disabled"
                )

                self.placement_label.config(
                    text="3 / 3 SHIPS DEPLOYED • READY FOR BATTLE"
                )

                self.status_label.config(
                    text="Fleet deployed. Click READY."

                )

            else:

                self.place_button.config(
                    state="normal"
                )

                self.select_next_ship()

        else:

            self.pending_ship = None

            self.pending_cells = []

            self.place_button.config(
                state="normal"
            )

            error_text = (
                str(error)
                if error
                else "Unknown placement error"
            )

            self.status_label.config(
                text=f"Deployment rejected: {error_text}"
            )

            messagebox.showerror(
                "Deployment Rejected",
                error_text
            )


    # ========================================================
    # SELECT NEXT SHIP
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
            return

        if len(self.placed_ships) != len(SHIPS):

            messagebox.showwarning(
                "Fleet Not Ready",
                "Deploy all 3 ships first."
            )

            return

        if self.ready_sent:
            return

        self.ready_sent = True

        self.ready_button.config(
            state="disabled"
        )

        self.status_label.config(
            text="Fleet locked. Sending READY to server..."
        )

        self.placement_label.config(
            text="FLEET LOCKED • WAITING FOR ENEMY"
        )

        try:

            self.client.ready()

        except Exception as e:

            self.ready_sent = False

            self.ready_button.config(
                state="normal"
            )

            self.status_label.config(
                text="Could not send READY."
            )

            self.network_log(
                f"READY error: {e}"
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

            self.status_label.config(
                text="READY confirmed by server."
            )

            self.placement_label.config(
                text="FLEET LOCKED • WAITING FOR ENEMY"
            )

        else:

            self.ready_sent = False

            self.ready_button.config(
                state="normal"
            )

            error_text = (
                str(error)
                if error
                else "Unknown READY error"
            )

            self.status_label.config(
                text=f"READY rejected: {error_text}"
            )

            messagebox.showerror(
                "READY Rejected",
                error_text
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

        self.place_button.config(
            state="disabled"
        )

        self.ready_button.config(
            state="disabled"
        )

        self.status_label.config(
            text="Battle stations active!"
        )

        self.placement_label.config(
            text="FLEET LOCKED • BATTLE IN PROGRESS"
        )

        self.turn_label.config(
            text="BATTLE STARTED",
            fg=TEAL
        )

        self.turn_subtitle.config(
            text="Awaiting turn assignment...",
            fg=MUTED
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

            self.turn_frame.config(
                highlightbackground=TEAL
            )

            self.turn_label.config(
                text="YOUR TURN",
                fg=TEAL
            )

            self.turn_subtitle.config(
                text="Choose a target on the enemy fleet.",
                fg=TEAL_LIGHT
            )

            self.status_label.config(
                text="Select an enemy cell to attack."
            )

        else:

            self.turn_frame.config(
                highlightbackground=GRID
            )

            self.turn_label.config(
                text="ENEMY'S TURN",
                fg=WARNING
            )

            self.turn_subtitle.config(
                text="Stand by... waiting for enemy attack.",
                fg=MUTED
            )

            self.status_label.config(
                text="Enemy is choosing a target..."
            )


    # ========================================================
    # ENEMY BOARD CLICK
    # ========================================================

    def enemy_cell_clicked(
        self,
        cell
    ):

        if not self.game_started:

            return

        if self.current_turn != self.player_id:

            messagebox.showwarning(
                "Enemy's Turn",
                "Wait until it is your turn."
            )

            return

        if cell in self.enemy_cells:

            messagebox.showwarning(
                "Already Targeted",
                f"You already fired at {cell}."
            )

            return

        confirm = messagebox.askyesno(
            "Confirm Strike",
            f"Fire at enemy position {cell}?"
        )

        if not confirm:

            return

        try:

            self.client.fire(
                cell
            )

        except Exception as e:

            self.network_log(
                f"Fire error: {e}"
            )


    # ========================================================
    # FIRE RESULT
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
                text="✦",
                fg=HIT,
                bg="#351C29",
                state="disabled"
            )

            self.status_label.config(
                text=f"DIRECT HIT at {cell}!"
            )

        elif result == "MISS":

            self.enemy_cells[cell] = "MISS"

            self.enemy_board[cell].config(
                text="~",
                fg=MISS,
                bg="#102E42",
                state="disabled"
            )

            self.status_label.config(
                text=f"MISS at {cell}."
            )

        elif result == "INVALID":

            error_text = (
                str(error)
                if error
                else "Invalid target"
            )

            self.status_label.config(
                text=f"Invalid strike: {error_text}"
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

        if cell not in self.own_board:

            return

        if result == "HIT":

            self.own_board[cell].config(
                text="✦",
                fg=HIT,
                bg="#351C29"
            )

            self.status_label.config(
                text=f"WARNING • Your fleet was hit at {cell}!"
            )

        elif result == "MISS":

            self.own_board[cell].config(
                text="~",
                fg=MISS,
                bg="#102E42"
            )

            self.status_label.config(
                text=f"Enemy attack missed at {cell}."
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
            self._show_sunk,
            ship
        )


    def _show_sunk(
        self,
        ship
    ):

        self.status_label.config(
            text=f"TARGET DESTROYED • {ship} SUNK"
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
            self._show_ship_hit,
            ship
        )


    def _show_ship_hit(
        self,
        ship
    ):

        self.status_label.config(
            text=f"WARNING • YOUR {ship} HAS BEEN HIT"
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

        self.turn_frame.config(
            highlightbackground=SUCCESS
        )

        self.turn_label.config(
            text="VICTORY",
            fg=SUCCESS
        )

        self.turn_subtitle.config(
            text="Enemy fleet destroyed.",
            fg=SUCCESS
        )

        self.status_label.config(
            text="MISSION COMPLETE • YOU WIN"
        )

        messagebox.showinfo(
            "VICTORY",
            "Enemy fleet destroyed!\n\nYOU WIN!"
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

        self.turn_frame.config(
            highlightbackground=HIT
        )

        self.turn_label.config(
            text="DEFEAT",
            fg=HIT
        )

        self.turn_subtitle.config(
            text="Your fleet has been destroyed.",
            fg=HIT
        )

        self.status_label.config(
            text="MISSION FAILED • ENEMY WINS"
        )

        messagebox.showinfo(
            "DEFEAT",
            "Your fleet has been destroyed.\n\nYOU LOSE!"
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
            text=f"SERVER ERROR: {error}"
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
# MAIN
# ============================================================

if __name__ == "__main__":

    root = tk.Tk()

    app = BattleshipGUI(
        root
    )

    root.mainloop()