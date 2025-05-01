import chess
import sys
import os


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from engine.evaluation_engine import eval_psqt

# Tạo board từ FEN khai cuộc
board = chess.Board("8/8/8/4k3/8/8/8/8 w - - 0 1")

# Tính điểm PSQT middle game
mg_score = eval_psqt(board, phase="mg")
print("Middle Game PSQT Score:", mg_score)

# Tính điểm PSQT end game
eg_score = eval_psqt(board, phase="eg")
print("End Game PSQT Score:", eg_score)
