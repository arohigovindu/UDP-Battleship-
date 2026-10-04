class BattleshipGame:

    BOARD_SIZE = 5

    SHIPS = {
        "Ship1": 3,
        "Ship2": 2,
        "Ship3": 2
    }

    def __init__(self):
        self.reset()

    # =========================================================
    # RESET GAME
    # =========================================================

    def reset(self):
        self.ships = {}
        self.occupied_cells = {}
        self.fired_cells = set()

    # =========================================================
    # CHECK VALID CELL
    # =========================================================

    def _valid_cell(self, cell):

        if not isinstance(cell, str):
            return False

        cell = cell.upper()

        if len(cell) != 2:
            return False

        column = cell[0]
        row = cell[1]

        return (
            column in "ABCDE"
            and row in "12345"
        )

    # =========================================================
    # CELL TO POSITION
    # =========================================================

    def _cell_to_position(self, cell):

        cell = cell.upper()

        column = ord(cell[0]) - ord("A")
        row = int(cell[1]) - 1

        return row, column

    # =========================================================
    # POSITION TO CELL
    # =========================================================

    def _position_to_cell(self, row, column):

        return (
            chr(ord("A") + column)
            + str(row + 1)
        )

    # =========================================================
    # GET SHIP CELLS
    # =========================================================

    def _get_ship_cells(
        self,
        start_cell,
        orientation,
        ship_size
    ):

        row, column = self._cell_to_position(start_cell)

        cells = []

        for i in range(ship_size):

            # HORIZONTAL
            # A1 -> A2 -> A3

            if orientation == "H":

                new_row = row
                new_column = column + i

            # VERTICAL
            # A1 -> B1 -> C1

            elif orientation == "V":

                new_row = row + i
                new_column = column

            else:

                return None

            # CHECK BOARD LIMITS

            if (
                new_row < 0
                or new_row >= self.BOARD_SIZE
                or new_column < 0
                or new_column >= self.BOARD_SIZE
            ):

                return None

            # CONVERT POSITION TO CELL

            cell = self._position_to_cell(
                new_row,
                new_column
            )

            cells.append(cell)

        return cells

    # =========================================================
    # PLACE SHIP
    # =========================================================

    def place_ship(
        self,
        ship_name,
        start_cell,
        orientation
    ):

        # CHECK SHIP NAME

        if ship_name not in self.SHIPS:

            return {
                "success": False,
                "ship": ship_name,
                "cells": [],
                "error": "INVALID_SHIP"
            }

        # CHECK DUPLICATE SHIP

        if ship_name in self.ships:

            return {
                "success": False,
                "ship": ship_name,
                "cells": [],
                "error": "SHIP_ALREADY_PLACED"
            }

        # NORMALIZE INPUT

        start_cell = start_cell.upper()
        orientation = orientation.upper()

        # CHECK CELL

        if not self._valid_cell(start_cell):

            return {
                "success": False,
                "ship": ship_name,
                "cells": [],
                "error": "INVALID_CELL"
            }

        # CHECK ORIENTATION

        if orientation not in ("H", "V"):

            return {
                "success": False,
                "ship": ship_name,
                "cells": [],
                "error": "INVALID_ORIENTATION"
            }

        # GET SHIP SIZE

        ship_size = self.SHIPS[ship_name]

        # CALCULATE CELLS

        cells = self._get_ship_cells(
            start_cell,
            orientation,
            ship_size
        )

        # CHECK OUT OF BOUNDS

        if cells is None:

            return {
                "success": False,
                "ship": ship_name,
                "cells": [],
                "error": "OUT_OF_BOUNDS"
            }

        # CHECK OVERLAP

        for cell in cells:

            if cell in self.occupied_cells:

                return {
                    "success": False,
                    "ship": ship_name,
                    "cells": [],
                    "error": "SHIP_OVERLAP"
                }

        # SAVE SHIP

        self.ships[ship_name] = {
            "cells": set(cells),
            "hits": set(),
            "orientation": orientation
        }

        # SAVE OCCUPIED CELLS

        for cell in cells:

            self.occupied_cells[cell] = ship_name

        return {
            "success": True,
            "ship": ship_name,
            "cells": cells,
            "error": None
        }

    # =========================================================
    # FIRE
    # =========================================================

    def fire(self, cell):

        cell = cell.upper()

        # CHECK VALID CELL

        if not self._valid_cell(cell):

            return {
                "result": "INVALID",
                "cell": cell,
                "ship": None,
                "sunk": False,
                "game_over": False,
                "error": "INVALID_CELL"
            }

        # CHECK REPEATED SHOT

        if cell in self.fired_cells:

            return {
                "result": "INVALID",
                "cell": cell,
                "ship": None,
                "sunk": False,
                "game_over": False,
                "error": "ALREADY_FIRED"
            }

        # RECORD SHOT

        self.fired_cells.add(cell)

        # MISS

        if cell not in self.occupied_cells:

            return {
                "result": "MISS",
                "cell": cell,
                "ship": None,
                "sunk": False,
                "game_over": False,
                "error": None
            }

        # HIT

        ship_name = self.occupied_cells[cell]

        self.ships[ship_name]["hits"].add(cell)

        ship_cells = self.ships[ship_name]["cells"]
        ship_hits = self.ships[ship_name]["hits"]

        # CHECK SUNK

        sunk = ship_cells == ship_hits

        # CHECK GAME OVER

        game_over = self.all_ships_sunk()

        return {
            "result": "HIT",
            "cell": cell,
            "ship": ship_name,
            "sunk": sunk,
            "game_over": game_over,
            "error": None
        }

    # =========================================================
    # CHECK ALL SHIPS SUNK
    # =========================================================

    def all_ships_sunk(self):

        if len(self.ships) != len(self.SHIPS):
            return False

        for ship_name in self.SHIPS:

            ship = self.ships[ship_name]

            if ship["cells"] != ship["hits"]:
                return False

        return True


# =============================================================
# DIRECT TEST
# =============================================================

if __name__ == "__main__":

    print("===================================")
    print("UDP BATTLESHIP - GAME TEST")
    print("===================================")

    game = BattleshipGame()

    print("\nShip1: A1 H")

    result = game.place_ship(
        "Ship1",
        "A1",
        "H"
    )

    print(result)

    print("\nShip2: C1 V")

    result = game.place_ship(
        "Ship2",
        "C1",
        "V"
    )

    print(result)

    print("\nShip3: A5 V")

    result = game.place_ship(
        "Ship3",
        "A5",
        "V"
    )

    print(result)

    print("\n===================================")
    print("OCCUPIED CELLS")
    print("===================================")

    print(game.occupied_cells)

    print("\n===================================")
    print("GAME TEST COMPLETE")
    print("===================================")