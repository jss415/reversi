# Reversi — AI vs AI

<video src="https://raw.githubusercontent.com/jss415/reversi/main/demo.mp4" controls muted loop playsinline width="800"></video>

Terminal Othello where two alpha-beta minimax agents play each other live. Built from scratch in Python — no third-party dependencies.

## Run

```
git clone https://github.com/<you>/reversi
cd reversi
python play.py
```

Requires Python 3.9+. No `pip install` step — the game uses only the standard library. Press `ESC` or `Q` at any point to quit.

## How the AI works

Each turn an `AiController` spawns a `Brain` thread that runs `AlphaBetaPruner.find_best_move`. The pruner does iterative deepening from depth 1 upward, returning the best move from the deepest _fully completed_ iteration before time expires. Evaluation weights piece count, corner control, and edge presence; corners dominate because they can never be flipped.

## Project layout

```
reversi/
├── README.md
├── requirements.txt
├── play.py                    # entry point
├── demo.mp4
└── src/
    └── reversi/
        ├── settings.py        # constants, direction vectors, helpers
        ├── piece.py           # Piece (single cell)
        ├── board.py           # Board (8×8 state, rules, captures)
        ├── ai.py              # AlphaBetaPruner
        ├── brain.py           # threading.Thread wrapper for the search
        ├── controllers.py     # AiController
        ├── game.py            # turn loop
        └── ui.py              # curses UI
```
