BOARD_SIZE = 8

DIRECTIONS = [
    (-1, -1), (-1, 0), (-1, 1),
    ( 0, -1),          ( 0, 1),
    ( 1, -1), ( 1, 0), ( 1, 1),
]

BLACK = "B"
WHITE = "W"
EMPTY = " "
HINT = "*"


class NoMovesError(Exception):
    pass


def in_bounds(r, c):
    return 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE


def opponent(color):
    if color == BLACK:
        return WHITE
    if color == WHITE:
        return BLACK
    raise ValueError(color)


def coord_to_alg(r, c):
    return "{}{}".format(chr(ord("a") + c), r + 1)


def alg_to_coord(s):
    s = s.strip().lower()
    if len(s) != 2:
        raise ValueError(s)
    col = ord(s[0]) - ord("a")
    row = int(s[1]) - 1
    if not in_bounds(row, col):
        raise ValueError(s)
    return row, col
