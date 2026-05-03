import curses

from .settings import BOARD_SIZE, BLACK, WHITE, HINT, coord_to_alg


CELL_WIDTH = 4
BOARD_WIN_HEIGHT = BOARD_SIZE + 2
BOARD_WIN_WIDTH = BOARD_SIZE * CELL_WIDTH + 4

PANEL_HEIGHT = 3
PANEL_WIDTH = 32
PANEL_GAP = 1

MOVES_HEIGHT = 1
ANNOUNCE_HEIGHT = 1
GAMEOVER_HEIGHT = 2
HELP_HEIGHT = 1


PAIR_EMPTY_CELL = 1
PAIR_BLACK_DISC = 2
PAIR_WHITE_DISC = 3
PAIR_HINT = 4
PAIR_PANEL_DEFAULT = 5
PAIR_PANEL_ACTIVE = 6
PAIR_THINK_A = 7
PAIR_THINK_B = 8
PAIR_THINK_C = 9
PAIR_DONE = 10


class UI:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        curses.curs_set(0)
        stdscr.nodelay(True)
        stdscr.timeout(50)

        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(PAIR_EMPTY_CELL,    curses.COLOR_BLACK,   curses.COLOR_GREEN)
        curses.init_pair(PAIR_BLACK_DISC,    curses.COLOR_BLACK,   curses.COLOR_GREEN)
        curses.init_pair(PAIR_WHITE_DISC,    curses.COLOR_WHITE,   curses.COLOR_GREEN)
        curses.init_pair(PAIR_HINT,          curses.COLOR_YELLOW,  curses.COLOR_GREEN)
        curses.init_pair(PAIR_PANEL_DEFAULT, curses.COLOR_WHITE,   -1)
        curses.init_pair(PAIR_PANEL_ACTIVE,  curses.COLOR_BLACK,   curses.COLOR_YELLOW)
        curses.init_pair(PAIR_THINK_A,       curses.COLOR_CYAN,    -1)
        curses.init_pair(PAIR_THINK_B,       curses.COLOR_YELLOW,  -1)
        curses.init_pair(PAIR_THINK_C,       curses.COLOR_MAGENTA, -1)
        curses.init_pair(PAIR_DONE,          curses.COLOR_GREEN,   -1)

        self._build_layout()
        self._last_thinking_controller = None

    def _build_layout(self):
        self.board_win = self.stdscr.derwin(BOARD_WIN_HEIGHT, BOARD_WIN_WIDTH, 0, 0)
        right_x = BOARD_WIN_WIDTH + 1
        self.panel_black_win = self.stdscr.derwin(PANEL_HEIGHT, PANEL_WIDTH, 0, right_x)
        self.panel_white_win = self.stdscr.derwin(PANEL_HEIGHT, PANEL_WIDTH, PANEL_HEIGHT + PANEL_GAP, right_x)
        right_height = PANEL_HEIGHT * 2 + PANEL_GAP
        bottom_y = max(BOARD_WIN_HEIGHT, right_height) + 1
        _, max_x = self.stdscr.getmaxyx()
        bottom_width = max(10, max_x - 1)
        self.announce_win = self.stdscr.derwin(ANNOUNCE_HEIGHT, bottom_width, bottom_y, 0)
        moves_y = bottom_y + ANNOUNCE_HEIGHT
        self.moves_win = self.stdscr.derwin(MOVES_HEIGHT, bottom_width, moves_y, 0)
        gameover_y = moves_y + MOVES_HEIGHT
        self.gameover_win = self.stdscr.derwin(GAMEOVER_HEIGHT, bottom_width, gameover_y, 0)
        help_y = gameover_y + GAMEOVER_HEIGHT
        self.help_win = self.stdscr.derwin(HELP_HEIGHT, bottom_width, help_y, 0)

    def is_quit_requested(self):
        ch = self.stdscr.getch()
        return ch == 27 or ch == ord("q") or ch == ord("Q")

    def render(self, board, current_controller, all_controllers, available_moves):
        self._draw_board(board, current_controller.color)
        self._draw_panels(board, current_controller, all_controllers)
        self._draw_moves(current_controller, available_moves)
        self._draw_help()
        curses.doupdate()

    def _draw_board(self, board, current_color):
        win = self.board_win
        win.erase()

        header = "   " + "".join(" {}  ".format(chr(ord("a") + c)) for c in range(BOARD_SIZE))
        try:
            win.addstr(0, 0, header)
        except curses.error:
            pass

        board.mark_legal_moves_as_hints(current_color)
        for row in range(BOARD_SIZE):
            try:
                win.addstr(row + 1, 0, "{} ".format(row + 1))
            except curses.error:
                pass
            for col in range(BOARD_SIZE):
                state = board.cell_at(row, col).state
                glyph, pair_id = self._cell_glyph_and_pair(state)
                try:
                    win.addstr(row + 1, 3 + col * CELL_WIDTH, glyph, curses.color_pair(pair_id))
                except curses.error:
                    pass
            try:
                win.addstr(row + 1, 3 + BOARD_SIZE * CELL_WIDTH, " {}".format(row + 1))
            except curses.error:
                pass
        board.clear_move_hints()

        try:
            win.addstr(BOARD_SIZE + 1, 0, header)
        except curses.error:
            pass
        win.noutrefresh()

    def _cell_glyph_and_pair(self, state):
        if state == BLACK:
            return " BB ", PAIR_BLACK_DISC
        if state == WHITE:
            return " WW ", PAIR_WHITE_DISC
        if state == HINT:
            return " ** ", PAIR_HINT
        return "    ", PAIR_EMPTY_CELL

    def _draw_panels(self, board, current_controller, all_controllers):
        black_count, white_count = board.count_pieces()
        by_color = {ctrl.color: ctrl for ctrl in all_controllers}
        black_ctrl = by_color.get(BLACK)
        white_ctrl = by_color.get(WHITE)
        self._draw_panel(self.panel_black_win, "Player 1", black_ctrl, BLACK, black_count, current_controller)
        self._draw_panel(self.panel_white_win, "Player 2", white_ctrl, WHITE, white_count, current_controller)

    def _draw_panel(self, win, label, controller, color, piece_count, current_controller):
        win.erase()
        is_active = controller is not None and controller is current_controller
        pair = curses.color_pair(PAIR_PANEL_ACTIVE if is_active else PAIR_PANEL_DEFAULT)
        attr = pair | (curses.A_BOLD if is_active else 0)

        name = controller.name if controller is not None else "(empty seat)"
        side = "Black" if color == BLACK else "White"
        try:
            win.addstr(0, 0, " {label} ".format(label=label).ljust(PANEL_WIDTH - 1), attr)
            win.addstr(1, 0, " {side}: {name}".format(side=side, name=name).ljust(PANEL_WIDTH - 1), attr)
            win.addstr(2, 0, " Pieces: {}".format(piece_count).ljust(PANEL_WIDTH - 1), attr)
        except curses.error:
            pass
        win.noutrefresh()

    def _draw_moves(self, current_controller, available_moves):
        win = self.moves_win
        win.erase()
        if available_moves:
            algebraic = [coord_to_alg(r, c) for r, c in available_moves]
            text = "Available moves for {}: {}".format(current_controller.name, algebraic)
            _, max_x = win.getmaxyx()
            try:
                win.addstr(0, 0, text[: max_x - 1], curses.A_BOLD)
            except curses.error:
                pass
        win.noutrefresh()

    def _draw_help(self):
        win = self.help_win
        win.erase()
        max_y, max_x = win.getmaxyx()
        try:
            win.addstr(0, 0, "ESC or Q to quit"[: max_x - 1], curses.A_DIM)
        except curses.error:
            pass
        win.noutrefresh()

    def show_thinking_animation(self, controller, frame):
        self._last_thinking_controller = controller
        win = self.announce_win
        win.erase()
        prefix = "{} is Thinking".format(controller.name)
        dot_pairs = [PAIR_THINK_A, PAIR_THINK_B, PAIR_THINK_C]
        try:
            win.addstr(0, 0, prefix, curses.A_BOLD)
            for i in range(4):
                pair = curses.color_pair(dot_pairs[(frame + i) % 3])
                win.addstr(0, len(prefix) + i, ".", pair | curses.A_BOLD)
        except curses.error:
            pass
        win.noutrefresh()
        curses.doupdate()

    def show_done(self, controller):
        win = self.announce_win
        win.erase()
        try:
            win.addstr(0, 0, "{} is Thinking.... ".format(controller.name), curses.A_DIM)
            win.addstr(0, len(controller.name) + 18, "Done!", curses.color_pair(PAIR_DONE) | curses.A_BOLD)
        except curses.error:
            pass
        win.noutrefresh()
        curses.doupdate()

    def announce_move(self, controller, row, col):
        win = self.announce_win
        win.erase()
        try:
            win.addstr(0, 0, "{} played ".format(controller.name), curses.A_BOLD)
            win.addstr(0, len(controller.name) + 8, coord_to_alg(row, col),
                       curses.color_pair(PAIR_DONE) | curses.A_BOLD)
        except curses.error:
            pass
        win.noutrefresh()
        curses.doupdate()

    def flash_status(self, message):
        win = self.announce_win
        win.erase()
        try:
            win.addstr(0, 0, message, curses.A_BOLD)
        except curses.error:
            pass
        win.noutrefresh()
        curses.doupdate()

    def show_game_over(self, board, winner_color, controllers):
        black_count, white_count = board.count_pieces()
        win = self.gameover_win
        win.erase()
        if winner_color is None:
            outcome = "Tie game!"
        else:
            winner_ctrl = next((c for c in controllers if c.color == winner_color), None)
            winner_name = winner_ctrl.name if winner_ctrl else winner_color
            outcome = "{} wins!".format(winner_name)
        try:
            line1 = "GAME OVER  -  Black: {}  White: {}".format(black_count, white_count)
            win.addstr(0, 0, line1, curses.A_BOLD)
            win.addstr(1, 0, outcome, curses.color_pair(PAIR_DONE) | curses.A_BOLD)
        except curses.error:
            pass
        win.noutrefresh()

        help = self.help_win
        help.erase()
        try:
            help.addstr(0, 0, "Press any key to exit.", curses.A_DIM)
        except curses.error:
            pass
        help.noutrefresh()
        curses.doupdate()
