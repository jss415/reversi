import curses
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from reversi.controllers import AiController
from reversi.game import Game
from reversi.settings import BLACK, WHITE
from reversi.ui import UI


TIMEOUT_SECONDS = 2.0
POST_MOVE_PAUSE = 0.7


def main(stdscr):
    ui = UI(stdscr)
    black_ctrl = AiController("Player 1", BLACK, timeout_seconds=TIMEOUT_SECONDS)
    white_ctrl = AiController("Player 2", WHITE, timeout_seconds=TIMEOUT_SECONDS)
    game = Game(ui, [black_ctrl, white_ctrl], post_move_pause=POST_MOVE_PAUSE)
    return game.run()


def run():
    winner, board, aborted = curses.wrapper(main)
    black_count, white_count = board.count_pieces()
    if aborted:
        print("Game aborted.")
    else:
        print("Final score -- Black: {}  White: {}".format(black_count, white_count))
        if winner == BLACK:
            print("Player 1 (Black) wins!")
        elif winner == WHITE:
            print("Player 2 (White) wins!")
        else:
            print("Tie game.")


if __name__ == "__main__":
    run()
