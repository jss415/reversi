import time
from collections import deque

from .board import Board
from .controllers import GameAborted
from .settings import BLACK


class Game:
    def __init__(self, ui, controllers, post_move_pause=0.7):
        self.ui = ui
        self.controllers = list(controllers)
        self.post_move_pause = post_move_pause
        self.board = Board()
        self._turn_order = deque(
            sorted(self.controllers, key=lambda c: 0 if c.color == BLACK else 1)
        )

    def run(self):
        consecutive_passes = 0
        aborted = False

        try:
            while not self.board.is_game_over() and consecutive_passes < 2:
                current = self._turn_order[0]
                available_moves = self.board.legal_moves_for(current.color)
                self.ui.render(self.board, current, self.controllers, available_moves)

                if not available_moves:
                    consecutive_passes += 1
                    self.ui.flash_status("{} passes".format(current.name))
                    self._pause(0.8)
                else:
                    consecutive_passes = 0
                    move = current.choose_move(self.board, self.ui)
                    self.board = self.board.apply_move(current.color, *move)
                    self.ui.render(self.board, current, self.controllers, available_moves)
                    self.ui.announce_move(current, *move)
                    self._pause(self.post_move_pause)

                self._turn_order.rotate(-1)
        except GameAborted:
            aborted = True

        winner = None if aborted else self.board.winner()
        self.ui.show_game_over(self.board, winner, self.controllers)
        if not aborted:
            self._wait_for_keypress()
        return winner, self.board, aborted

    def _pause(self, seconds):
        end = time.monotonic() + seconds
        while time.monotonic() < end:
            if self.ui.is_quit_requested():
                raise GameAborted()
            time.sleep(0.05)

    def _wait_for_keypress(self):
        self.ui.stdscr.nodelay(False)
        self.ui.stdscr.timeout(-1)
        self.ui.stdscr.getch()
