import queue
import time

from .ai import AlphaBetaPruner
from .brain import Brain


class GameAborted(Exception):
    pass


class AiController:
    def __init__(self, name, color, timeout_seconds=2.0):
        self.name = name
        self.color = color
        self.pruner = AlphaBetaPruner(timeout_seconds=timeout_seconds)

    def choose_move(self, board, ui):
        result_queue = queue.Queue()
        brain = Brain(self.pruner, board, self.color, result_queue)
        brain.start()

        animation_frame = 0
        while result_queue.empty():
            if ui is not None and ui.is_quit_requested():
                raise GameAborted()
            if ui is not None:
                ui.show_thinking_animation(self, animation_frame)
            animation_frame = (animation_frame + 1) % 3
            time.sleep(0.15)

        brain.join()
        if ui is not None:
            ui.show_done(self)
            time.sleep(0.25)
        return result_queue.get()
