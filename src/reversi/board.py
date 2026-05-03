from .piece import Piece
from .settings import (
    BOARD_SIZE,
    DIRECTIONS,
    BLACK,
    WHITE,
    EMPTY,
    HINT,
    in_bounds,
    opponent,
)


class Board:
    def __init__(self, pieces=None):
        if pieces is None:
            pieces = [Piece(EMPTY) for _ in range(BOARD_SIZE * BOARD_SIZE)]
            mid = BOARD_SIZE // 2
            pieces[(mid - 1) * BOARD_SIZE + (mid - 1)].state = WHITE
            pieces[ mid      * BOARD_SIZE +  mid     ].state = WHITE
            pieces[(mid - 1) * BOARD_SIZE +  mid     ].state = BLACK
            pieces[ mid      * BOARD_SIZE + (mid - 1)].state = BLACK
        self.pieces = pieces

    def cell_at(self, row, col):
        return self.pieces[row * BOARD_SIZE + col]

    def opponent_of(self, color):
        return opponent(color)

    def number_of_flips_for_move(self, color, row, col):
        if not in_bounds(row, col):
            return 0
        if not self.cell_at(row, col).is_empty():
            return 0
        return len(self.pieces_flipped_by_move(color, row, col))

    def pieces_flipped_by_move(self, color, row, col):
        if not in_bounds(row, col) or not self.cell_at(row, col).is_empty():
            return []
        other = opponent(color)
        flipped_positions = []
        for dr, dc in DIRECTIONS:
            run = []
            x, y = row + dr, col + dc
            while in_bounds(x, y) and self.cell_at(x, y).state == other:
                run.append((x, y))
                x += dr
                y += dc
            if run and in_bounds(x, y) and self.cell_at(x, y).state == color:
                flipped_positions.extend(run)
        return flipped_positions

    def legal_moves_for(self, color):
        moves = []
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if self.cell_at(row, col).is_empty() and self.pieces_flipped_by_move(color, row, col):
                    moves.append((row, col))
        return moves

    def apply_move(self, color, row, col):
        flipped_positions = self.pieces_flipped_by_move(color, row, col)
        if not flipped_positions:
            raise ValueError("illegal move ({}, {}) for {}".format(row, col, color))
        new_pieces = [Piece(p.state if p.state != HINT else EMPTY) for p in self.pieces]
        for fr, fc in flipped_positions:
            new_pieces[fr * BOARD_SIZE + fc].state = color
        new_pieces[row * BOARD_SIZE + col].state = color
        return Board(new_pieces)

    def mark_legal_moves_as_hints(self, color):
        self.clear_move_hints()
        for row, col in self.legal_moves_for(color):
            self.pieces[row * BOARD_SIZE + col].state = HINT

    def clear_move_hints(self):
        for p in self.pieces:
            if p.state == HINT:
                p.state = EMPTY

    def count_pieces(self):
        black_count = sum(1 for p in self.pieces if p.state == BLACK)
        white_count = sum(1 for p in self.pieces if p.state == WHITE)
        return black_count, white_count

    def is_game_over(self):
        return not self.legal_moves_for(BLACK) and not self.legal_moves_for(WHITE)

    def winner(self):
        black_count, white_count = self.count_pieces()
        if black_count > white_count:
            return BLACK
        if white_count > black_count:
            return WHITE
        return None

    def as_2d_state_grid(self):
        grid = []
        for row in range(BOARD_SIZE):
            grid_row = []
            for col in range(BOARD_SIZE):
                state = self.cell_at(row, col).state
                grid_row.append(state if state in (BLACK, WHITE) else EMPTY)
            grid.append(grid_row)
        return grid
