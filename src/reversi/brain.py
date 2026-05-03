import threading


class Brain(threading.Thread):
    def __init__(self, pruner, board, color, result_queue):
        super().__init__(daemon=True)
        self.pruner = pruner
        self.board = board
        self.color = color
        self.result_queue = result_queue

    def run(self):
        move = self.pruner.find_best_move(self.board, self.color)
        self.result_queue.put(move)
