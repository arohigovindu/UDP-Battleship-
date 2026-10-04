class BattleshipGame:

    BOARD_SIZE = 5

    SHIPS = {
        "Ship1": 3,
        "Ship2": 2,
        "Ship3": 2
    }

    def __init__(self):
        self.reset()

    def reset(self):
        self.ships = {}
        self.occupied_cells = {}
        self.fired_cells = set()

    def _valid_cell(self, cell):
        if not isinstance(cell, str) or len(cell) != 2:
            return False

        column = cell[0].upper()
        row = cell[1]

        return column in "ABCDE" and row in "12345"

    def _cell_to_position(self, cell):
        cell = cell.upper()

        column = ord(cell[0]) - ord('A')
        row = int(cell[1]) - 1

        return row, column

    def _position_to_cell(self, row, column):
        return chr(ord('A') + column) + str(row + 1)

    def _get_ship_cells(self, start_cell, orientation, ship_size):
        row, column = self._cell_to_position(start_cell)

        cells = []

        for i in range(ship_size):
            if orientation == "H":
                new_row = row
                new_column = column + i
            else:
                new_row = row + i
                new_column = column

            if (
                new_row < 0
                or new_row >= self.BOARD_SIZE
                or new_column < 0
                or new_column >= self.BOARD_SIZE
            ):
                return None

            cells.append(
                self._position_to_cell(new_row, new_column)
            )

        return cells

    def place_ship(self, ship_name, start_cell, orientation):

        if ship_name not in self.SHIPS:
            return {
                "success": False,
                "ship": ship_name,
                "cells": [],
                "error": "INVALID_SHIP"
            }

        if ship_name in self.ships:
            return {
                "success": False,
                "ship": ship_name,
                "cells": [],
                "error": "SHIP_ALREADY_PLACED"
            }

        start_cell = start_cell.upper()

        if not self._valid_cell(start_cell):
            return {
                "success": False,
                "ship": ship_name,
                "cells": [],
                "error": "INVALID_CELL"
            }

        orientation = orientation.upper()

        if orientation not in ("H", "V"):
            return {
                "success": False,
                "ship": ship_name,
                "cells": [],
                "error": "INVALID_ORIENTATION"
            }

        ship_size = self.SHIPS[ship_name]

        cells = self._get_ship_cells(
            start_cell,
            orientation,
            ship_size
        )

        if cells is None:
            return {
                "success": False,
                "ship": ship_name,
                "cells": [],
                "error": "OUT_OF_BOUNDS"
            }

        for cell in cells:
            if cell in self.occupied_cells:
                return {
                    "success": False,
                    "ship": ship_name,
                    "cells": [],
                    "error": "SHIP_OVERLAP"
                }

        self.ships[ship_name] = {
            "cells": set(cells),
            "hits": set(),
            "orientation": orientation
        }

        for cell in cells:
            self.occupied_cells[cell] = ship_name

        return {
            "success": True,
            "ship": ship_name,
            "cells": cells,
            "error": None
        }

    def fire(self, cell):

        cell = cell.upper()

        if not self._valid_cell(cell):
            return {
                "result": "INVALID",
                "cell": cell,
                "ship": None,
                "sunk": False,
                "game_over": False,
                "error": "INVALID_CELL"
            }

        if cell in self.fired_cells:
            return {
                "result": "INVALID",
                "cell": cell,
                "ship": None,
                "sunk": False,
                "game_over": False,
                "error": "ALREADY_FIRED"
            }

        self.fired_cells.add(cell)

        if cell not in self.occupied_cells:
            return {
                "result": "MISS",
                "cell": cell,
                "ship": None,
                "sunk": False,
                "game_over": False,
                "error": None
            }

        ship_name = self.occupied_cells[cell]

        self.ships[ship_name]["hits"].add(cell)

        ship_cells = self.ships[ship_name]["cells"]
        ship_hits = self.ships[ship_name]["hits"]

        sunk = ship_cells == ship_hits
        game_over = self.all_ships_sunk()

        return {
            "result": "HIT",
            "cell": cell,
            "ship": ship_name,
            "sunk": sunk,
            "game_over": game_over,
            "error": None
        }

    def all_ships_sunk(self):

        if len(self.ships) != len(self.SHIPS):
            return False

        for ship_name in self.SHIPS:
            ship = self.ships[ship_name]

            if ship["cells"] != ship["hits"]:
                return False

        return True


if __name__ == "__main__":

    print("=== TEST 1: VALID HORIZONTAL PLACEMENT ===")
    game = BattleshipGame()
    print(game.place_ship("Ship1", "A1", "H"))

    print("\n=== TEST 2: VALID VERTICAL PLACEMENT ===")
    print(game.place_ship("Ship2", "C2", "V"))

    print("\n=== TEST 3: OUT OF BOUNDS ===")
    print(game.place_ship("Ship3", "E5", "H"))

    print("\n=== TEST 4: SHIP OVERLAP ===")
    print(game.place_ship("Ship3", "B1", "V"))

    print("\n=== TEST 5: DUPLICATE SHIP ===")
    print(game.place_ship("Ship1", "D4", "H"))

    print("\n=== TEST 6: INVALID COORDINATE ===")
    print(game.place_ship("Ship3", "Z9", "H"))

    print("\n=== TEST 7: INVALID ORIENTATION ===")
    print(game.place_ship("Ship3", "D4", "X"))

    print("\n=== TEST 8: HIT ===")
    print(game.fire("A1"))

    print("\n=== TEST 9: REPEATED SHOT ===")
    print(game.fire("A1"))

    print("\n=== TEST 10: MISS ===")
    print(game.fire("E5"))

    print("\n=== TEST 11: SUNK ===")
    print(game.fire("B1"))
    print(game.fire("C1"))

    print("\n=== TEST 12: RESET ===")
    game.reset()
    print("Game reset successfully.")

    print("\n=== TEST 13: ALL SHIPS SUNK / WIN ===")

    game = BattleshipGame()

    game.place_ship("Ship1", "A1", "H")
    game.place_ship("Ship2", "A2", "H")
    game.place_ship("Ship3", "A3", "H")

    print(game.fire("A1"))
    print(game.fire("B1"))
    print(game.fire("C1"))

    print(game.fire("A2"))
    print(game.fire("B2"))

    print(game.fire("A3"))
    print(game.fire("B3"))

    print("\nAll tests completed.")