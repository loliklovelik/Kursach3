import random

from models.Direction import Direction
from models.ShootType import ShootType

FIELD_LEN = 10

FIELD_ROW = [str(i) for i in range(FIELD_LEN)]
FIELD_COLUMN = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"[:FIELD_LEN]

SHIPS = {1: 4, 2: 3, 3: 2, 4: 1}
CHECKS = (0, -1, 1)
CHECKS_SHOOT = (-1, 1)
MAX_ATTEMPTS = 100

WATER_SYMBOL = "*"
STRIKE_WATER_SYMBOL = "@"
SHIP_SYMBOL = "#"
STRIKE_SHIP_SYMBOL = "$"


def coordinates_to_index(coordinates: str) -> (int, int):
    return int(coordinates[1]), FIELD_COLUMN.index(coordinates[0].upper())


def check_index(row, col) -> bool:
    return 0 <= row < FIELD_LEN and 0 <= col < FIELD_LEN


class PlayingField:
    def __init__(self):
        self.matrix: list[list[str]] = []
        # generate empty matrix
        for i in range(FIELD_LEN):
            self.matrix.append([])
            for j in range(FIELD_LEN):
                self.matrix[i].append(WATER_SYMBOL)
        self.__generate_ships()

    def __str__(self):
        # generate str in markdown
        ans = "```   " + " ".join(FIELD_COLUMN) + "\n"
        for i in range(len(self.matrix)):
            ans += " " + FIELD_ROW[i] + " " + " ".join(self.matrix[i]) + "\n"

        return ans + "```"

    def __generate_ships(self):
        need_regenerate = True
        while need_regenerate:
            # clear matrix
            for i in range(FIELD_LEN):
                for j in range(FIELD_LEN):
                    self.matrix[i][j] = WATER_SYMBOL
            need_regenerate = False
            # add ships from biggest to lowest
            for ship_len, count in sorted(SHIPS.items(), reverse=True):
                for _ in range(count):
                    is_placed = False
                    """
                    try to add ship to matrix
                    because it's random, try MAX_ATTEMPTS times
                    if it's not success, regenerate matrix and try from the beginning
                    """
                    attempts = 0
                    while not is_placed:
                        attempts += 1
                        if attempts > MAX_ATTEMPTS:
                            need_regenerate = True
                            break
                        # get random start row, column and direction
                        row = random.randint(0, FIELD_LEN - 1)
                        col = random.randint(0, FIELD_LEN - 1)
                        direction = Direction(random.randint(0, 3))
                        row_increment = 0
                        col_increment = 0
                        if direction == Direction.TOP:
                            row_increment = -1
                        elif direction == Direction.BOTTOM:
                            row_increment = 1
                        elif direction == Direction.LEFT:
                            col_increment = -1
                        else:
                            col_increment = 1

                        # checking that the ship fits
                        if not check_index(row + row_increment * ship_len, col + col_increment * ship_len):
                            continue

                        # checking that the ship does not intersect with another ship
                        can_place = True
                        for i in range(ship_len):
                            if not self.__check_field(row + row_increment * i, col + col_increment * i):
                                can_place = False
                                break

                        # placing the ship
                        if can_place:
                            for i in range(ship_len):
                                self.matrix[row + row_increment * i][col + col_increment * i] = SHIP_SYMBOL
                            is_placed = True
                    if need_regenerate:
                        break
                if need_regenerate:
                    break

    def __check_field(self, row, col) -> bool:
        for check_row in CHECKS:
            for check_col in CHECKS:
                row_i = row + check_row
                col_i = col + check_col
                if check_index(row_i, col_i) and self.matrix[row_i][col_i] == SHIP_SYMBOL:
                    return False
        return True

    def can_shoot(self, coordinates: str) -> bool:
        index = coordinates_to_index(coordinates)
        symbol = self.matrix[index[0]][index[1]]
        return symbol != STRIKE_WATER_SYMBOL and symbol != STRIKE_SHIP_SYMBOL

    async def shoot(self, coordinates: str) -> ShootType:
        index = coordinates_to_index(coordinates)
        self.matrix[index[0]][index[1]] = \
            STRIKE_WATER_SYMBOL if self.matrix[index[0]][index[1]] == WATER_SYMBOL else STRIKE_SHIP_SYMBOL

        if self.matrix[index[0]][index[1]] == STRIKE_WATER_SYMBOL:
            return ShootType.MISS

        # check the ship is destroyed
        is_destroyed = True

        for is_column in range(2):
            for inc in CHECKS_SHOOT:
                row = index[0]
                col = index[1]
                symbol = STRIKE_SHIP_SYMBOL
                while symbol != WATER_SYMBOL and symbol != STRIKE_WATER_SYMBOL:
                    if is_column == 1:
                        col += inc
                    else:
                        row += inc
                    if not check_index(row, col):
                        break

                    symbol = self.matrix[row][col]

                    if symbol == SHIP_SYMBOL:
                        is_destroyed = False
                        break

        if is_destroyed:
            #  fill the water around the ship
            for is_column in range(2):
                for inc in CHECKS_SHOOT:
                    row = index[0]
                    col = index[1]
                    symbol = STRIKE_SHIP_SYMBOL
                    while symbol == STRIKE_SHIP_SYMBOL:
                        for row_inc in CHECKS:
                            for col_inc in CHECKS:
                                row_i = row + row_inc
                                col_i = col + col_inc
                                if check_index(row_i, col_i) and self.matrix[row_i][col_i] == WATER_SYMBOL:
                                    self.matrix[row_i][col_i] = STRIKE_WATER_SYMBOL

                        if is_column == 1:
                            col += inc
                        else:
                            row += inc
                        if not check_index(row, col):
                            break

                        symbol = self.matrix[row][col]

            return ShootType.DESTROY

        return ShootType.HIT

    def check_win(self) -> bool:
        for i in self.matrix:
            if SHIP_SYMBOL in i:
                return False
        return True

    def blured(self) -> str:
        return "".join(
            list(
                map(
                    lambda symbol: symbol if symbol != SHIP_SYMBOL else WATER_SYMBOL,
                    str(self),
                )
            )
        )
