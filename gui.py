import tkinter as tk
from tkinter import messagebox

from client import BattleshipClient


# ============================================================
# UDP BATTLESHIP - GAME STYLE GUI
# ============================================================

BOARD_SIZE = 5

SHIPS = {
    "Ship1": 3,
    "Ship2": 2,
    "Ship3": 2
}


# ============================================================
# THEME
# ============================================================

BG = "#061522"
PANEL = "#0A2235"
PANEL_LIGHT = "#0E3047"

TEAL = "#18D6C5"
TEAL_DARK = "#0E9F96"
TEAL_LIGHT = "#7FFFEF"

WHITE = "#F4FAFA"
TEXT = "#C9D9DE"
MUTED = "#718A96"

GRID = "#16445A"
GRID_HOVER = "#1E6277"

WATER = "#09263A"
WATER_HOVER = "#10465C"

HIT = "#FF5757"
HIT_DARK = "#5A202A"

MISS = "#62B6D9"
MISS_DARK = "#123B52"

SUCCESS = "#49D17D"
WARNING = "#F0B44D"

SELECTED = "#D6B84C"

SHIP_COLORS = {
    "Ship1": "#168F87",
    "Ship2": "#14756F",
    "Ship3": "#1C5F78"
}

SHIP_TEXT = {
    "Ship1": "▰",
    "Ship2": "▰",
    "Ship3": "▰"
}


# ============================================================
# MAIN GUI
# ============================================================

class BattleshipGUI:

    def __init__(self, root):

        self.root = root

        self.root.title("UDP Battleship")
        self.root.geometry("1550x900")
        self.root.minsize(1450, 850)
        self.root.configure(bg=BG)

        # ====================================================
        # CLIENT
        # ====================================================

        self.client = BattleshipClient(
            host="127.0.0.1",
            port=5000
        )

        # ====================================================
        # GAME STATE
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
        # ANIMATION STATE
        # ====================================================

        self.packet_animation_id = None

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

        if hasattr(self.client, "on_reset"):
            self.client.on_reset = self.handle_reset

        self.client.set_message_callback(
            self.network_log
        )

        # ====================================================
        # BUILD GUI
        # ====================================================

        self.build_gui()

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
            pady=(14, 4)
        )

        tk.Label(
            header,
            text="⚓ UDP BATTLESHIP",
            font=("Arial", 26, "bold"),
            fg=TEAL,
            bg=BG
        ).pack()

        tk.Label(
            header,
            text="REAL-TIME NAVAL COMBAT  •  UDP NETWORK",
            font=("Arial", 9, "bold"),
            fg=MUTED,
            bg=BG
        ).pack(
            pady=(1, 0)
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
            pady=8
        )

        connection_inner = tk.Frame(
            connection,
            bg=PANEL
        )

        connection_inner.pack(
            pady=8
        )

        tk.Label(
            connection_inner,
            text="CALLSIGN",
            font=("Arial", 8, "bold"),
            fg=MUTED,
            bg=PANEL
        ).grid(
            row=0,
            column=0,
            padx=(8, 4)
        )

        self.name_entry = tk.Entry(
            connection_inner,
            width=14,
            font=("Arial", 10),
            bg="#061522",
            fg=WHITE,
            insertbackground=TEAL,
            relief="flat"
        )

        self.name_entry.grid(
            row=0,
            column=1,
            padx=4,
            ipady=4
        )

        tk.Label(
            connection_inner,
            text="SERVER ADDRESS",
            font=("Arial", 8, "bold"),
            fg=MUTED,
            bg=PANEL
        ).grid(
            row=0,
            column=2,
            padx=(12, 4)
        )

        self.server_ip_entry = tk.Entry(
            connection_inner,
            width=15,
            font=("Arial", 10),
            bg="#061522",
            fg=WHITE,
            insertbackground=TEAL,
            relief="flat"
        )

        self.server_ip_entry.insert(
            0,
            "127.0.0.1"
        )

        self.server_ip_entry.grid(
            row=0,
            column=3,
            padx=4,
            ipady=4
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
            width=11,
            command=self.connect
        )

        self.connect_button.grid(
            row=0,
            column=4,
            padx=8,
            ipady=2
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
            column=5,
            padx=14
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
            column=6,
            padx=6
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
            pady=(4, 8)
        )

        self.status_label = tk.Label(
            self.status_frame,
            text="Welcome, Captain. Connect to the UDP server.",
            font=("Arial", 11, "bold"),
            fg=WHITE,
            bg=PANEL_LIGHT
        )

        self.status_label.pack(
            pady=7
        )

        # ====================================================
        # MAIN CONTENT
        # ====================================================

        main_content = tk.Frame(
            self.root,
            bg=BG,
            width=1350,
            height=550
        )

        main_content.pack(
            fill="x",
            padx=30,
            pady=(0, 12)
        )

        main_content.pack_propagate(False)

        main_content.grid_columnconfigure(
            0,
            minsize=980,
            weight=0
        )

        main_content.grid_columnconfigure(
            1,
            minsize=360,
            weight=0
        )

        main_content.grid_rowconfigure(
            0,
            weight=1
        )

        # ====================================================
        # LEFT COLUMN
        # ====================================================

        left_column = tk.Frame(
            main_content,
            bg=BG,
            width=980
        )

        left_column.grid(
            row=0,
            column=0,
            sticky="nw",
            padx=(0, 12)
        )

        left_column.grid_propagate(False)

        # ====================================================
        # BOARDS
        # ====================================================

        boards_container = tk.Frame(
            left_column,
            bg=BG
        )

        boards_container.pack(
            pady=2
        )

        # ====================================================
        # YOUR BOARD
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
            padx=10
        )

        tk.Label(
            own_panel,
            text="YOUR FLEET",
            font=("Arial", 14, "bold"),
            fg=TEAL,
            bg=PANEL
        ).pack(
            pady=(8, 0)
        )

        tk.Label(
            own_panel,
            text="DEFEND YOUR FLEET",
            font=("Arial", 8, "bold"),
            fg=MUTED,
            bg=PANEL
        ).pack(
            pady=(1, 2)
        )

        self.own_event_label = tk.Label(
            own_panel,
            text="● FLEET STATUS: WAITING",
            font=("Arial", 9, "bold"),
            fg=MUTED,
            bg=PANEL,
            width=30
        )

        self.own_event_label.pack(
            pady=(2, 4)
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
            padx=2
        )

        tk.Label(
            vs_frame,
            text="VS",
            font=("Arial", 18, "bold"),
            fg=MUTED,
            bg=BG
        ).pack()

        # ====================================================
        # ENEMY BOARD
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
            padx=10
        )

        tk.Label(
            enemy_panel,
            text="ENEMY FLEET",
            font=("Arial", 14, "bold"),
            fg=TEAL,
            bg=PANEL
        ).pack(
            pady=(8, 0)
        )

        tk.Label(
            enemy_panel,
            text="SELECT YOUR TARGET",
            font=("Arial", 8, "bold"),
            fg=MUTED,
            bg=PANEL
        ).pack(
            pady=(1, 2)
        )

        self.enemy_event_label = tk.Label(
            enemy_panel,
            text="● TARGET STATUS: WAITING",
            font=("Arial", 9, "bold"),
            fg=MUTED,
            bg=PANEL,
            width=30
        )

        self.enemy_event_label.pack(
            pady=(2, 4)
        )

        self.enemy_board = self.create_board(
            enemy_panel,
            self.enemy_cell_clicked
        )

        # ====================================================
        # TURN INDICATOR
        # ====================================================

        self.turn_frame = tk.Frame(
            left_column,
            bg=PANEL,
            highlightbackground=GRID,
            highlightthickness=1
        )

        self.turn_frame.pack(
            fill="x",
            padx=120,
            pady=8
        )

        self.turn_label = tk.Label(
            self.turn_frame,
            text="WAITING FOR PLAYERS",
            font=("Arial", 15, "bold"),
            fg=MUTED,
            bg=PANEL
        )

        self.turn_label.pack(
            pady=(7, 0)
        )

        self.turn_subtitle = tk.Label(
            self.turn_frame,
            text="Connect both players to begin.",
            font=("Arial", 9),
            fg=MUTED,
            bg=PANEL
        )

        self.turn_subtitle.pack(
            pady=(0, 6)
        )

        # ====================================================
        # DEPLOYMENT CONTROLS
        # ====================================================

        controls = tk.Frame(
            left_column,
            bg=PANEL,
            highlightbackground=GRID,
            highlightthickness=1
        )

        controls.pack(
            fill="x",
            padx=24,
            pady=2
        )

        tk.Label(
            controls,
            text="FLEET DEPLOYMENT",
            font=("Arial", 9, "bold"),
            fg=TEAL,
            bg=PANEL
        ).grid(
            row=0,
            column=0,
            columnspan=6,
            pady=(6, 4)
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
            padx=4
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
            width=9
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
            padx=4
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
            padx=4
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
            width=7
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
            padx=4
        )

        self.place_button = tk.Button(
            controls,
            text="DEPLOY SHIP",
            font=("Arial", 8, "bold"),
            fg=BG,
            bg=TEAL,
            activebackground=TEAL_LIGHT,
            relief="flat",
            width=13,
            command=self.place_selected_ship
        )

        self.place_button.grid(
            row=1,
            column=4,
            padx=6,
            ipady=2
        )

        self.ready_button = tk.Button(
            controls,
            text="READY",
            font=("Arial", 8, "bold"),
            fg=WHITE,
            bg=TEAL_DARK,
            activebackground=TEAL,
            relief="flat",
            width=13,
            state="disabled",
            command=self.ready
        )

        self.ready_button.grid(
            row=1,
            column=5,
            padx=6,
            ipady=2
        )

        self.placement_label = tk.Label(
            controls,
            text="0 / 3 SHIPS DEPLOYED",
            font=("Arial", 8, "bold"),
            fg=MUTED,
            bg=PANEL
        )

        self.placement_label.grid(
            row=2,
            column=0,
            columnspan=6,
            pady=(5, 7)
        )

        # ====================================================
        # RIGHT SIDE - SCROLLABLE NETWORK PANEL
        # ====================================================

        right_container = tk.Frame(
            main_content,
            bg=BG,
            width=360,
            height=535
        )

        right_container.grid(
            row=0,
            column=1,
            sticky="nsew"
        )

        right_container.grid_propagate(False)

        right_container.grid_rowconfigure(
            0,
            weight=1
        )

        right_container.grid_columnconfigure(
            0,
            weight=1
        )

        # ====================================================
        # NETWORK CANVAS
        # ====================================================

        self.network_canvas = tk.Canvas(
            right_container,
            bg=PANEL,
            highlightbackground=GRID,
            highlightthickness=1,
            bd=0
        )

        self.network_canvas.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        # ====================================================
        # NETWORK SCROLLBAR
        # ====================================================

        self.network_scrollbar = tk.Scrollbar(
            right_container,
            orient="vertical",
            command=self.network_canvas.yview,
            bg=PANEL_LIGHT,
            troughcolor=BG,
            activebackground=TEAL,
            highlightthickness=0,
            bd=0
        )

        self.network_scrollbar.grid(
            row=0,
            column=1,
            sticky="ns"
        )

        self.network_canvas.configure(
            yscrollcommand=self.network_scrollbar.set
        )

        # ====================================================
        # ACTUAL SCROLLABLE CONTENT
        # ====================================================

        log_panel = tk.Frame(
            self.network_canvas,
            bg=PANEL,
            width=340
        )

        self.network_window = self.network_canvas.create_window(
            (0, 0),
            window=log_panel,
            anchor="nw"
        )

        self.network_log_panel = log_panel

        # ====================================================
        # UPDATE SCROLL REGION
        # ====================================================

        log_panel.bind(
            "<Configure>",
            self._update_network_scrollregion
        )

        self.network_canvas.bind(
            "<Configure>",
            self._resize_network_content
        )

        # ====================================================
        # MOUSE WHEEL SCROLLING
        # ====================================================

        self.network_canvas.bind(
            "<Enter>",
            self._enable_network_mousewheel
        )

        self.network_canvas.bind(
            "<Leave>",
            self._disable_network_mousewheel
        )

        # ====================================================
        # NETWORK HEADER
        # ====================================================

        tk.Label(
            log_panel,
            text="NETWORK ACTIVITY",
            font=("Consolas", 13, "bold"),
            fg=TEAL,
            bg=PANEL
        ).pack(
            anchor="w",
            padx=12,
            pady=(10, 1)
        )

        tk.Label(
            log_panel,
            text="UNDERSTANDING UDP IN REAL TIME",
            font=("Consolas", 8, "bold"),
            fg=MUTED,
            bg=PANEL
        ).pack(
            anchor="w",
            padx=12,
            pady=(0, 6)
        )

        # ====================================================
        # UDP WORKING PRINCIPLE
        # ====================================================

        udp_info = tk.Frame(
            log_panel,
            bg="#071B2A",
            highlightbackground=GRID,
            highlightthickness=1
        )

        udp_info.pack(
            fill="x",
            padx=10,
            pady=(0, 7)
        )

        tk.Label(
            udp_info,
            text="UDP Working Principle",
            font=("Consolas", 9, "bold"),
            fg=TEAL,
            bg="#071B2A"
        ).pack(
            anchor="w",
            padx=9,
            pady=(6, 2)
        )

        tk.Label(
            udp_info,
            text=(
                "Each game action is sent as a UDP datagram.\n"
                "The client sends it to the server, and the\n"
                "server forwards the result to the players.\n"
                "UDP is fast and lightweight, but does not\n"
                "guarantee delivery."
            ),
            font=("Arial", 8),
            fg=TEXT,
            bg="#071B2A",
            justify="left",
            anchor="w"
        ).pack(
            anchor="w",
            padx=9,
            pady=(0, 7)
        )

        # ====================================================
        # PACKET FLOW TITLE
        # ====================================================

        tk.Label(
            log_panel,
            text="LIVE UDP PACKET FLOW",
            font=("Consolas", 9, "bold"),
            fg=TEAL,
            bg=PANEL
        ).pack(
            anchor="w",
            padx=12,
            pady=(1, 3)
        )

        # ====================================================
        # PACKET CANVAS
        # ====================================================

        self.packet_canvas = tk.Canvas(
            log_panel,
            width=330,
            height=125,
            bg="#061522",
            highlightbackground=GRID,
            highlightthickness=1
        )

        self.packet_canvas.pack(
            padx=10,
            pady=(0, 5)
        )

        # ====================================================
        # NETWORK NODES
        # ====================================================

        # YOU
        self.packet_canvas.create_oval(
            12,
            38,
            64,
            90,
            fill=TEAL_DARK,
            outline=TEAL,
            width=2,
            tags="node"
        )

        self.packet_canvas.create_text(
            38,
            64,
            text="YOU",
            fill=WHITE,
            font=("Consolas", 8, "bold"),
            tags="node"
        )

        # SERVER
        self.packet_canvas.create_oval(
            139,
            38,
            191,
            90,
            fill="#17465C",
            outline=TEAL,
            width=2,
            tags="node"
        )

        self.packet_canvas.create_text(
            165,
            64,
            text="SERVER",
            fill=WHITE,
            font=("Consolas", 7, "bold"),
            tags="node"
        )

        # ENEMY
        self.packet_canvas.create_oval(
            266,
            38,
            318,
            90,
            fill="#17465C",
            outline=TEAL,
            width=2,
            tags="node"
        )

        self.packet_canvas.create_text(
            292,
            64,
            text="ENEMY",
            fill=WHITE,
            font=("Consolas", 8, "bold"),
            tags="node"
        )

        # ====================================================
        # CONNECTION LINES
        # ====================================================

        self.packet_canvas.create_line(
            64,
            64,
            139,
            64,
            fill=GRID,
            width=2,
            arrow="last",
            arrowshape=(8, 10, 4),
            tags="connection"
        )

        self.packet_canvas.create_line(
            191,
            64,
            266,
            64,
            fill=GRID,
            width=2,
            arrow="last",
            arrowshape=(8, 10, 4),
            tags="connection"
        )

        # ====================================================
        # UDP LABELS
        # ====================================================

        self.packet_canvas.create_text(
            101,
            48,
            text="UDP",
            fill=MUTED,
            font=("Consolas", 7, "bold"),
            tags="connection"
        )

        self.packet_canvas.create_text(
            229,
            48,
            text="UDP",
            fill=MUTED,
            font=("Consolas", 7, "bold"),
            tags="connection"
        )

        # ====================================================
        # PACKET STATUS
        # ====================================================

        self.packet_status_label = tk.Label(
            log_panel,
            text="● WAITING FOR UDP TRAFFIC",
            font=("Consolas", 8, "bold"),
            fg=MUTED,
            bg=PANEL
        )

        self.packet_status_label.pack(
            pady=(0, 5)
        )

        # ====================================================
        # RESET
        # ====================================================

        self.reset_button = tk.Button(
            log_panel,
            text="↻  RESET GAME",
            font=("Arial", 9, "bold"),
            fg=WHITE,
            bg="#7A2630",
            activebackground=HIT,
            activeforeground=WHITE,
            relief="flat",
            width=18,
            command=self.reset_game
        )

        self.reset_button.pack(
            pady=(0, 8),
            ipady=2
        )

        # ====================================================
        # LOG TITLE
        # ====================================================

        tk.Label(
            log_panel,
            text="PACKET / GAME LOG",
            font=("Consolas", 8, "bold"),
            fg=MUTED,
            bg=PANEL
        ).pack(
            anchor="w",
            padx=12,
            pady=(0, 3)
        )

        # ====================================================
        # LOG CONTAINER
        # ====================================================

        log_container = tk.Frame(
            log_panel,
            bg="#061522",
            height=180
        )

        log_container.pack(
            fill="x",
            padx=10,
            pady=(0, 10)
        )

        log_container.pack_propagate(False)

        self.log_text = tk.Text(
            log_container,
            bg="#061522",
            fg="#A9D1D8",
            insertbackground=TEAL,
            relief="flat",
            state="disabled",
            font=("Consolas", 9),
            wrap="word"
        )

        self.log_text.pack(
            side="left",
            fill="both",
            expand=True,
            padx=5,
            pady=5
        )

        log_scrollbar = tk.Scrollbar(
            log_container,
            command=self.log_text.yview
        )

        log_scrollbar.pack(
            side="right",
            fill="y"
        )

        self.log_text.config(
            yscrollcommand=log_scrollbar.set
        )

        # Make sure initial scroll region is correct.
        self.root.after(
            100,
            self._update_network_scrollregion
        )


    # ========================================================
    # NETWORK PANEL SCROLLING
    # ========================================================

    def _update_network_scrollregion(
        self,
        event=None
    ):

        try:

            self.network_canvas.configure(
                scrollregion=self.network_canvas.bbox("all")
            )

        except tk.TclError:

            pass


    def _resize_network_content(
        self,
        event
    ):

        try:

            self.network_canvas.itemconfig(
                self.network_window,
                width=event.width
            )

            self._update_network_scrollregion()

        except tk.TclError:

            pass


    def _enable_network_mousewheel(
        self,
        event=None
    ):

        self.network_canvas.bind_all(
            "<MouseWheel>",
            self._on_network_mousewheel
        )

        # Linux support
        self.network_canvas.bind_all(
            "<Button-4>",
            self._on_network_mousewheel_linux_up
        )

        self.network_canvas.bind_all(
            "<Button-5>",
            self._on_network_mousewheel_linux_down
        )


    def _disable_network_mousewheel(
        self,
        event=None
    ):

        self.network_canvas.unbind_all(
            "<MouseWheel>"
        )

        self.network_canvas.unbind_all(
            "<Button-4>"
        )

        self.network_canvas.unbind_all(
            "<Button-5>"
        )


    def _on_network_mousewheel(
        self,
        event
    ):

        try:

            if event.delta:

                self.network_canvas.yview_scroll(
                    int(-1 * (event.delta / 120)),
                    "units"
                )

        except tk.TclError:

            pass


    def _on_network_mousewheel_linux_up(
        self,
        event
    ):

        try:

            self.network_canvas.yview_scroll(
                -1,
                "units"
            )

        except tk.TclError:

            pass


    def _on_network_mousewheel_linux_down(
        self,
        event
    ):

        try:

            self.network_canvas.yview_scroll(
                1,
                "units"
            )

        except tk.TclError:

            pass


    # ========================================================
    # CREATE BOARD
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
        # COLUMN LABELS
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
        # BOARD CELLS
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
                    height=1,
                    bg=WATER,
                    fg=WHITE,
                    activebackground=WATER_HOVER,
                    activeforeground=WHITE,
                    relief="flat",
                    highlightbackground=GRID,
                    highlightthickness=1,
                    font=("Arial", 12, "bold"),
                    command=lambda c=cell: callback(c)
                )

                button.bind(
                    "<Enter>",
                    lambda event, b=button:
                    self.cell_enter(b)
                )

                button.bind(
                    "<Leave>",
                    lambda event, b=button:
                    self.cell_leave(b)
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
    # CELL HOVER
    # ========================================================

    def cell_enter(
        self,
        button
    ):

        try:

            if str(button["state"]) == "disabled":
                return

            button.config(
                bg=WATER_HOVER
            )

        except tk.TclError:

            pass


    def cell_leave(
        self,
        button
    ):

        try:

            if str(button["state"]) == "disabled":
                return

            button.config(
                bg=WATER
            )

        except tk.TclError:

            pass


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

            message_text = str(message)

            # =================================================
            # CLIENT -> SERVER
            # =================================================

            if "-> UDP -> Server" in message_text:

                if "FIRE|" in message_text:

                    self.animate_packet(
                        "to_server",
                        "FIRE DATAGRAM"
                    )

                    self.root.after(
                        2900,
                        self.animate_server_to_enemy
                    )

                else:

                    self.animate_packet(
                        "to_server",
                        "CLIENT DATAGRAM"
                    )

            # =================================================
            # SERVER -> CLIENT
            # =================================================

            elif "<- Server:" in message_text:

                self.animate_packet(
                    "from_server",
                    "SERVER RESPONSE"
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
    # UDP PACKET ANIMATION
    # ========================================================

    def animate_packet(
        self,
        direction="to_server",
        message="UDP DATAGRAM"
    ):

        try:

            self.root.after(
                0,
                self._animate_packet,
                direction,
                message
            )

        except tk.TclError:

            pass


    def animate_server_to_enemy(
        self
    ):

        try:

            self._animate_packet(
                "server_to_enemy",
                "FORWARDING TO ENEMY"
            )

        except tk.TclError:

            pass


    def _animate_packet(
        self,
        direction,
        message
    ):

        if not hasattr(
            self,
            "packet_canvas"
        ):
            return

        canvas = self.packet_canvas
        status_label = self.packet_status_label

        # ====================================================
        # ROUTE
        # ====================================================

        if direction == "to_server":

            start_x = 64
            end_x = 139
            status = "YOU  →  SERVER"

        elif direction == "from_server":

            start_x = 191
            end_x = 266
            status = "SERVER  →  YOU"

        elif direction == "server_to_enemy":

            start_x = 191
            end_x = 266
            status = "SERVER  →  ENEMY"

        elif direction == "enemy_to_server":

            start_x = 266
            end_x = 191
            status = "ENEMY  →  SERVER"

        else:

            start_x = 64
            end_x = 139
            status = "UDP DATAGRAM"

        # ====================================================
        # CANCEL PREVIOUS PACKET
        # ====================================================

        try:

            canvas.delete(
                "packet"
            )

            canvas.delete(
                "packet_trail"
            )

        except tk.TclError:

            return

        # ====================================================
        # STATUS
        # ====================================================

        status_label.config(
            text=f"● {status}   •   {message}",
            fg=TEAL
        )

        # ====================================================
        # TRAIL
        # ====================================================

        trail = canvas.create_line(
            start_x,
            64,
            start_x,
            64,
            fill=TEAL_DARK,
            width=5,
            tags="packet_trail"
        )

        # ====================================================
        # OUTER GLOW
        # ====================================================

        glow_outer = canvas.create_oval(
            start_x - 11,
            53,
            start_x + 11,
            75,
            fill="#0A3947",
            outline="",
            tags="packet"
        )

        # ====================================================
        # INNER GLOW
        # ====================================================

        glow_inner = canvas.create_oval(
            start_x - 8,
            56,
            start_x + 8,
            72,
            fill="#0E6A6A",
            outline="",
            tags="packet"
        )

        # ====================================================
        # MAIN PACKET
        # ====================================================

        packet = canvas.create_oval(
            start_x - 5,
            59,
            start_x + 5,
            69,
            fill=TEAL_LIGHT,
            outline=WHITE,
            width=1,
            tags="packet"
        )

        # ====================================================
        # PACKET LABEL
        # ====================================================

        packet_text = canvas.create_text(
            start_x,
            35,
            text="UDP",
            fill=TEAL_LIGHT,
            font=("Consolas", 7, "bold"),
            tags="packet"
        )

        # ====================================================
        # ANIMATION SETTINGS
        # ====================================================

        total_steps = 65
        delay = 45

        def move_packet(
            step=0
        ):

            if step >= total_steps:

                try:

                    canvas.delete(
                        "packet"
                    )

                    canvas.delete(
                        "packet_trail"
                    )

                    if direction == "server_to_enemy":

                        status_label.config(
                            text="● PACKET DELIVERED TO ENEMY",
                            fg=SUCCESS
                        )

                    elif direction == "from_server":

                        status_label.config(
                            text="● SERVER RESPONSE RECEIVED",
                            fg=SUCCESS
                        )

                    else:

                        status_label.config(
                            text="● UDP PACKET DELIVERED",
                            fg=SUCCESS
                        )

                    self.root.after(
                        1000,
                        self.reset_packet_status
                    )

                except tk.TclError:

                    pass

                return

            # =================================================
            # SMOOTH EASE-IN / EASE-OUT
            # =================================================

            progress = (
                step / total_steps
            )

            smooth_progress = (
                3 * progress * progress
                - 2 * progress * progress * progress
            )

            x = (
                start_x
                + (end_x - start_x)
                * smooth_progress
            )

            try:

                canvas.coords(
                    glow_outer,
                    x - 11,
                    53,
                    x + 11,
                    75
                )

                canvas.coords(
                    glow_inner,
                    x - 8,
                    56,
                    x + 8,
                    72
                )

                canvas.coords(
                    packet,
                    x - 5,
                    59,
                    x + 5,
                    69
                )

                canvas.coords(
                    packet_text,
                    x,
                    35
                )

                canvas.coords(
                    trail,
                    start_x,
                    64,
                    x,
                    64
                )

                self.packet_animation_id = (
                    self.root.after(
                        delay,
                        move_packet,
                        step + 1
                    )
                )

            except tk.TclError:

                return

        move_packet()


    def reset_packet_status(
        self
    ):

        try:

            self.packet_status_label.config(
                text="● WAITING FOR UDP TRAFFIC",
                fg=MUTED
            )

        except tk.TclError:

            pass


    # ========================================================
    # CONNECT
    # ========================================================

    def connect(
        self
    ):

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

        server_ip = (
            self.server_ip_entry.get().strip()
        )

        if not server_ip:
            server_ip = "127.0.0.1"

        self.client.host = server_ip

        self.status_label.config(
            text=f"Connecting to UDP server at {server_ip}..."
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

        self.own_event_label.config(
            text="● FLEET STATUS: DEPLOYING",
            fg=TEAL
        )

        self.enemy_event_label.config(
            text="● TARGET STATUS: WAITING",
            fg=MUTED
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

        except (
            ValueError,
            IndexError
        ):

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
                chr(ord("A") + new_column)
                + str(new_row + 1)
            )

            cells.append(
                cell
            )

        return cells


    # ========================================================
    # PLACE SHIP
    # ========================================================

    def place_selected_ship(
        self
    ):

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

        for cell in cells:

            if cell in self.own_cells:

                messagebox.showerror(
                    "Fleet Overlap",
                    f"Another ship already occupies {cell}."
                )

                return

        self.pending_ship = ship
        self.pending_cells = cells

        self.place_button.config(
            state="disabled"
        )

        self.status_label.config(
            text=f"Deploying {ship}..."
        )

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

            self.placed_ships.add(
                ship
            )

            ship_color = SHIP_COLORS.get(
                ship,
                SHIP_COLORS["Ship1"]
            )

            ship_symbol = SHIP_TEXT.get(
                ship,
                "▰"
            )

            for cell in cells:

                self.own_cells[cell] = ship

                self.own_board[cell].config(
                    text=ship_symbol,
                    fg=TEAL_LIGHT,
                    bg=ship_color,
                    activebackground=ship_color,
                    disabledforeground=TEAL_LIGHT,
                    state="disabled",
                    relief="sunken",
                    bd=2,
                    font=("Arial", 16, "bold")
                )

            self.pending_ship = None
            self.pending_cells = []
            self.selected_start_cell = None

            count = len(
                self.placed_ships
            )

            self.placement_label.config(
                text=f"{count} / 3 SHIPS DEPLOYED"
            )

            self.own_event_label.config(
                text=f"⚓ {ship.upper()} DEPLOYED",
                fg=TEAL
            )

            self.status_label.config(
                text=f"{ship} successfully deployed."
            )

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

                self.own_event_label.config(
                    text="⚓ FLEET READY",
                    fg=SUCCESS
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
    # NEXT SHIP
    # ========================================================

    def select_next_ship(
        self
    ):

        for ship in SHIPS:

            if ship not in self.placed_ships:

                self.ship_var.set(
                    ship
                )

                return


    # ========================================================
    # READY
    # ========================================================

    def ready(
        self
    ):

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
            text="Fleet locked. Sending READY..."
        )

        self.placement_label.config(
            text="FLEET LOCKED • WAITING FOR ENEMY"
        )

        self.own_event_label.config(
            text="⚓ FLEET LOCKED",
            fg=SUCCESS
        )

        try:

            self.client.ready()

        except Exception as e:

            self.ready_sent = False

            self.ready_button.config(
                state="normal"
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
                text="READY confirmed. Waiting for enemy..."
            )

            self.own_event_label.config(
                text="⚓ READY • WAITING FOR ENEMY",
                fg=SUCCESS
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

    def handle_game_start(
        self
    ):

        self.root.after(
            0,
            self._handle_game_start
        )


    def _handle_game_start(
        self
    ):

        self.game_started = True

        self.place_button.config(
            state="disabled"
        )

        self.ready_button.config(
            state="disabled"
        )

        self.status_label.config(
            text="⚔ BATTLE STATIONS ACTIVE!"
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

        self.own_event_label.config(
            text="⚓ FLEET ACTIVE",
            fg=TEAL
        )

        self.enemy_event_label.config(
            text="🎯 TARGET ACQUIRED",
            fg=TEAL
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
                highlightbackground=TEAL,
                highlightthickness=2
            )

            self.turn_label.config(
                text="⚔ YOUR TURN",
                fg=TEAL
            )

            self.turn_subtitle.config(
                text="Choose a target on the enemy fleet.",
                fg=TEAL_LIGHT
            )

            self.status_label.config(
                text="🎯 Select an enemy cell to attack."
            )

        else:

            self.turn_frame.config(
                highlightbackground=WARNING,
                highlightthickness=2
            )

            self.turn_label.config(
                text="⏳ ENEMY'S TURN",
                fg=WARNING
            )

            self.turn_subtitle.config(
                text="Stand by... enemy is choosing a target.",
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

        self.enemy_board[cell].config(
            bg=SELECTED
        )

        confirm = messagebox.askyesno(
            "Confirm Strike",
            f"Fire at enemy position {cell}?"
        )

        if not confirm:

            if cell not in self.enemy_cells:

                self.enemy_board[cell].config(
                    bg=WATER
                )

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
        error=None
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

        cell = cell.upper()

        if result == "HIT":

            self.enemy_cells[cell] = "HIT"

            self.enemy_board[cell].config(
                text="✖",
                fg=WHITE,
                bg=HIT_DARK,
                activebackground=HIT_DARK,
                disabledforeground=WHITE,
                state="disabled",
                relief="sunken",
                bd=2,
                font=("Arial", 15, "bold")
            )

            self.enemy_event_label.config(
                text=f"🎯 ENEMY SHIP HIT • {cell}",
                fg=HIT
            )

            self.status_label.config(
                text=f"🎯 ENEMY SHIP HIT • {cell}"
            )

        elif result == "MISS":

            self.enemy_cells[cell] = "MISS"

            self.enemy_board[cell].config(
                text="≈",
                fg=MISS,
                bg=MISS_DARK,
                activebackground=MISS_DARK,
                disabledforeground=MISS,
                state="disabled",
                relief="sunken",
                bd=2,
                font=("Arial", 18, "bold")
            )

            self.enemy_event_label.config(
                text=f"💦 ENEMY SHIP MISS • {cell}",
                fg=MISS
            )

            self.status_label.config(
                text=f"💦 ENEMY SHIP MISS • {cell}"
            )

        elif result == "INVALID":

            error_text = (
                str(error)
                if error
                else "Invalid target"
            )

            self.enemy_board[cell].config(
                bg=WATER
            )

            self.enemy_event_label.config(
                text="⚠ INVALID TARGET",
                fg=WARNING
            )

            self.status_label.config(
                text=f"⚠ INVALID STRIKE • {error_text}"
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

        cell = cell.upper()

        if cell not in self.own_board:
            return

        if result == "HIT":

            self.own_board[cell].config(
                text="✖",
                fg=WHITE,
                bg=HIT_DARK,
                activebackground=HIT_DARK,
                disabledforeground=WHITE,
                relief="sunken",
                bd=2,
                font=("Arial", 15, "bold")
            )

            self.own_event_label.config(
                text=f"🔥 SHIP HIT • {cell}",
                fg=HIT
            )

            self.status_label.config(
                text=f"🔥 SHIP HIT • YOUR FLEET AT {cell}!"
            )

        elif result == "MISS":

            self.own_board[cell].config(
                text="≈",
                fg=MISS,
                bg=MISS_DARK,
                activebackground=MISS_DARK,
                disabledforeground=MISS,
                relief="sunken",
                bd=2,
                font=("Arial", 18, "bold")
            )

            self.own_event_label.config(
                text=f"🌊 SHIP MISS • {cell}",
                fg=MISS
            )

            self.status_label.config(
                text=f"🌊 SHIP MISS • ENEMY ATTACK AT {cell}"
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

        ship_name = str(
            ship
        ).upper()

        self.enemy_event_label.config(
            text=f"💥 ENEMY SHIP SUNK • {ship_name}",
            fg=SUCCESS
        )

        self.status_label.config(
            text=f"💥 ENEMY {ship_name} DESTROYED!"
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

        ship_name = str(
            ship
        ).upper()

        self.own_event_label.config(
            text=f"🔥 SHIP HIT • {ship_name}",
            fg=HIT
        )

        self.status_label.config(
            text=f"🔥 YOUR {ship_name} HAS BEEN HIT!"
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
            highlightbackground=SUCCESS,
            highlightthickness=3
        )

        self.turn_label.config(
            text="🏆 VICTORY",
            fg=SUCCESS,
            font=("Arial", 18, "bold")
        )

        self.turn_subtitle.config(
            text="Enemy fleet completely destroyed!",
            fg=SUCCESS
        )

        self.enemy_event_label.config(
            text="🏆 ENEMY FLEET DESTROYED",
            fg=SUCCESS
        )

        self.own_event_label.config(
            text="⚓ YOUR FLEET SURVIVED",
            fg=TEAL
        )

        self.status_label.config(
            text="🏆 ENEMY FLEET DESTROYED — YOU WIN!",
            fg=SUCCESS,
            font=("Arial", 13, "bold")
        )

        messagebox.showinfo(
            "🏆 VICTORY!",
            "══════════════════════\n"
            "       🏆 VICTORY!       \n"
            "══════════════════════\n\n"
            "ENEMY FLEET DESTROYED!\n\n"
            "⚓ All enemy ships have been sunk.\n\n"
            "🏆 YOU WIN!\n"
        )


    # ========================================================
    # LOSE
    # ========================================================

    def handle_lose(
        self
    ):

        self.root.after(
            0,
            self._handle_lose
        )


    def _handle_lose(
        self
    ):

        self.game_started = False
        self.current_turn = None

        self.turn_frame.config(
            highlightbackground=HIT,
            highlightthickness=3
        )

        self.turn_label.config(
            text="☠ DEFEAT",
            fg=HIT,
            font=("Arial", 18, "bold")
        )

        self.turn_subtitle.config(
            text="Your fleet has been completely destroyed.",
            fg=HIT
        )

        self.own_event_label.config(
            text="☠ YOUR FLEET DESTROYED",
            fg=HIT
        )

        self.enemy_event_label.config(
            text="🏆 ENEMY FLEET SURVIVED",
            fg=SUCCESS
        )

        self.status_label.config(
            text="☠ YOUR FLEET WAS DESTROYED — YOU LOSE!",
            fg=HIT,
            font=("Arial", 13, "bold")
        )

        messagebox.showinfo(
            "☠ DEFEAT",
            "══════════════════════\n"
            "        ☠ DEFEAT        \n"
            "══════════════════════\n\n"
            "YOUR FLEET HAS BEEN DESTROYED!\n\n"
            "⚓ The enemy sank all your ships.\n\n"
            "☠ YOU LOSE!\n"
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
            text=f"SERVER ERROR: {error}",
            fg=HIT
        )


    # ========================================================
    # RESET GAME
    # ========================================================

    def reset_game(
        self
    ):

        if not self.connected:

            messagebox.showwarning(
                "Not Connected",
                "Connect to the server first."
            )

            return

        confirm = messagebox.askyesno(
            "Reset Game",
            "Reset the current game?\n\n"
            "Both players will need to deploy "
            "their ships again."
        )

        if not confirm:
            return

        self.status_label.config(
            text="↻ RESETTING GAME...",
            fg=WARNING
        )

        self.packet_status_label.config(
            text="● RESET REQUEST",
            fg=WARNING
        )

        try:

            self.client.reset_game()

        except Exception as e:

            self.network_log(
                f"Reset error: {e}"
            )

            self.status_label.config(
                text=f"Reset failed: {e}",
                fg=HIT
            )


    # ========================================================
    # RESET CONFIRMED BY SERVER
    # ========================================================

    def handle_reset(
        self
    ):

        self.root.after(
            0,
            self._handle_reset
        )


    def _handle_reset(
        self
    ):

        # ====================================================
        # RESET GAME STATE
        # ====================================================

        self.game_started = False
        self.ready_sent = False
        self.current_turn = None

        self.placed_ships.clear()

        self.selected_start_cell = None

        self.pending_ship = None
        self.pending_cells = []

        self.own_cells.clear()
        self.enemy_cells.clear()

        # ====================================================
        # RESET OWN BOARD
        # ====================================================

        for cell, button in self.own_board.items():

            button.config(
                text="",
                bg=WATER,
                fg=WHITE,
                activebackground=WATER_HOVER,
                activeforeground=WHITE,
                state="normal",
                relief="flat",
                bd=1,
                font=("Arial", 12, "bold")
            )

        # ====================================================
        # RESET ENEMY BOARD
        # ====================================================

        for cell, button in self.enemy_board.items():

            button.config(
                text="",
                bg=WATER,
                fg=WHITE,
                activebackground=WATER_HOVER,
                activeforeground=WHITE,
                state="normal",
                relief="flat",
                bd=1,
                font=("Arial", 12, "bold")
            )

        # ====================================================
        # RESET CONTROLS
        # ====================================================

        self.ship_var.set(
            "Ship1"
        )

        self.orientation_var.set(
            "H"
        )

        self.ship_menu.config(
            state="normal"
        )

        self.orientation_menu.config(
            state="normal"
        )

        self.place_button.config(
            state="normal"
        )

        self.ready_button.config(
            state="disabled"
        )

        self.placement_label.config(
            text="0 / 3 SHIPS DEPLOYED"
        )

        # ====================================================
        # RESET EVENT LABELS
        # ====================================================

        self.own_event_label.config(
            text="⚓ FLEET STATUS: DEPLOYING",
            fg=TEAL
        )

        self.enemy_event_label.config(
            text="🎯 TARGET STATUS: WAITING",
            fg=MUTED
        )

        # ====================================================
        # RESET TURN
        # ====================================================

        self.turn_frame.config(
            highlightbackground=GRID,
            highlightthickness=1
        )

        self.turn_label.config(
            text="WAITING FOR PLAYERS",
            fg=MUTED,
            font=("Arial", 15, "bold")
        )

        self.turn_subtitle.config(
            text="Deploy your fleet again.",
            fg=MUTED
        )

        # ====================================================
        # RESET STATUS
        # ====================================================

        self.status_label.config(
            text="↻ GAME RESET • DEPLOY YOUR FLEET",
            fg=WARNING,
            font=("Arial", 11, "bold")
        )

        self.packet_status_label.config(
            text="● RESET COMPLETE",
            fg=SUCCESS
        )

        self.root.after(
            1200,
            self.reset_packet_status
        )

        self.network_log(
            "RESET confirmed by server. Game state cleared."
        )


    # ========================================================
    # CLOSE
    # ========================================================

    def close(
        self
    ):

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