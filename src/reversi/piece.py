from .settings import EMPTY, BLACK, WHITE, HINT


class Piece:
    def __init__(self, state=EMPTY):
        self.state = state

    def is_empty(self):
        return self.state == EMPTY or self.state == HINT

    def flip(self):
        if self.state == BLACK:
            self.state = WHITE
        elif self.state == WHITE:
            self.state = BLACK
        else:
            raise ValueError("cannot flip non-disc cell")

    def __repr__(self):
        return "Piece({!r})".format(self.state)
