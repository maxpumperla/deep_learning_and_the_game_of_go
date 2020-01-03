Chess
-----

This directory provides a chess `dlgo`-compliant `GameState`, so that
some parts of the book can be tried with chess, in addition to Go and
TicTacToe.

At the moment, the code supports `../minimax/alphabeta.py`,
see the example `../../alpha_beta_chess.py`,
which can be run from its directory with `python alpha_beta_chess.py`.

Eventually, it would be interesting to support more of the book with
chess in addition to go.

## Dependencies

The code is a shallow wrapping of the `python-chess` library, which is
usually imported with `import chess`.

Here, we use `import chess as _chess` and reserve the name `chess` for
the `dlgo.chess` code.

To install [`python-chess`](https://python-chess.readthedocs.io/en/latest/),
run `pip install python-chess`.
