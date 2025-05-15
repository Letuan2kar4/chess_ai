import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import chess
from engine.evaluation.mobility import evaluate_mobility

board = chess.Board(
    "r1bqk2r/pppp1ppp/2n2n2/2b1p3/4P3/2N2N2/PPPP1PPP/R1BQKB1R w KQkq - 2 4"
)

print("White MG mobility:", evaluate_mobility(board, chess.WHITE, "MG"))
print("Black MG mobility:", evaluate_mobility(board, chess.BLACK, "MG"))
