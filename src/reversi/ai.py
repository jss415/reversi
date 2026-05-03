import random
import time

from .settings import BOARD_SIZE, BLACK, WHITE, opponent

INFINITY = float("inf")
MAX_DEPTH = 10

CORNER_POSITIONS = [(0, 0), (0, BOARD_SIZE - 1), (BOARD_SIZE - 1, 0), (BOARD_SIZE - 1, BOARD_SIZE - 1)]


def _is_edge_non_corner(row, col):
    on_edge = row == 0 or row == BOARD_SIZE - 1 or col == 0 or col == BOARD_SIZE - 1
    return on_edge and (row, col) not in CORNER_POSITIONS


EDGE_POSITIONS = [(r, c) for r in range(BOARD_SIZE) for c in range(BOARD_SIZE) if _is_edge_non_corner(r, c)]


class AlphaBetaPruner:
    def __init__(self, timeout_seconds=2.0, rng=None):
        self.timeout_seconds = timeout_seconds
        self._rng = rng or random.Random()
        self._timed_out = False

    def find_best_move(self, board, color):
        legal_moves = board.legal_moves_for(color)
        if not legal_moves:
            return None
        deadline = time.monotonic() + self.timeout_seconds

        best_move_completed = self._rng.choice(legal_moves)
        best_value_completed = -INFINITY

        for depth_limit in range(1, MAX_DEPTH + 1):
            self._timed_out = False
            best_move_this_iter = None
            best_value_this_iter = -INFINITY
            alpha = -INFINITY
            beta = INFINITY

            for move in legal_moves:
                child = board.apply_move(color, *move)
                value = self._min_value(child, opponent(color), color, 1, depth_limit, alpha, beta, deadline)
                if self._timed_out:
                    break
                if value > best_value_this_iter:
                    best_value_this_iter = value
                    best_move_this_iter = move
                if best_value_this_iter > alpha:
                    alpha = best_value_this_iter

            if not self._timed_out and best_move_this_iter is not None:
                best_move_completed = best_move_this_iter
                best_value_completed = best_value_this_iter

            if self._timed_out or time.monotonic() >= deadline:
                break

        return best_move_completed

    def _max_value(self, board, current_color, root_color, depth, depth_limit, alpha, beta, deadline):
        if time.monotonic() >= deadline:
            self._timed_out = True
            return self._evaluate(board, root_color)
        if depth >= depth_limit or board.is_game_over():
            return self._evaluate(board, root_color)
        legal_moves = board.legal_moves_for(current_color)
        if not legal_moves:
            opp_legal = board.legal_moves_for(opponent(current_color))
            if not opp_legal:
                return self._evaluate(board, root_color)
            return self._min_value(board, opponent(current_color), root_color, depth + 1, depth_limit, alpha, beta, deadline)
        value = -INFINITY
        for move in legal_moves:
            child = board.apply_move(current_color, *move)
            value = max(value, self._min_value(child, opponent(current_color), root_color, depth + 1, depth_limit, alpha, beta, deadline))
            if self._timed_out:
                return value
            if value >= beta:
                return value
            alpha = max(alpha, value)
        return value

    def _min_value(self, board, current_color, root_color, depth, depth_limit, alpha, beta, deadline):
        if time.monotonic() >= deadline:
            self._timed_out = True
            return self._evaluate(board, root_color)
        if depth >= depth_limit or board.is_game_over():
            return self._evaluate(board, root_color)
        legal_moves = board.legal_moves_for(current_color)
        if not legal_moves:
            opp_legal = board.legal_moves_for(opponent(current_color))
            if not opp_legal:
                return self._evaluate(board, root_color)
            return self._max_value(board, opponent(current_color), root_color, depth + 1, depth_limit, alpha, beta, deadline)
        value = INFINITY
        for move in legal_moves:
            child = board.apply_move(current_color, *move)
            value = min(value, self._max_value(child, opponent(current_color), root_color, depth + 1, depth_limit, alpha, beta, deadline))
            if self._timed_out:
                return value
            if value <= alpha:
                return value
            beta = min(beta, value)
        return value

    def _evaluate(self, board, color):
        opp = opponent(color)

        my_pieces = sum(1 for p in board.pieces if p.state == color)
        their_pieces = sum(1 for p in board.pieces if p.state == opp)
        piece_diff = my_pieces - their_pieces

        my_corners = sum(1 for r, c in CORNER_POSITIONS if board.cell_at(r, c).state == color)
        their_corners = sum(1 for r, c in CORNER_POSITIONS if board.cell_at(r, c).state == opp)
        corner_diff = my_corners - their_corners

        my_edges = sum(1 for r, c in EDGE_POSITIONS if board.cell_at(r, c).state == color)
        their_edges = sum(1 for r, c in EDGE_POSITIONS if board.cell_at(r, c).state == opp)
        edge_diff = my_edges - their_edges

        return 2.0 * piece_diff + 1.5 * corner_diff + 1.2 * edge_diff
