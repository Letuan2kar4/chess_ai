import chess
import unittest


def long_diagonal_bishop(board, piece, color, rank, file):
    if not piece or piece.piece_type != chess.BISHOP:
        return 0

    # Phải nằm trên 1 trong 2 đường chéo chính
    if file != rank and file + rank != 7:
        return 0
    x1 = file
    if min(x1, 7 - x1) > 2:
        return 0
    # Xác định điểm trung tâm cần thấy dựa vào đường chéo
    if file == rank:
        target = (4, 4) if file < 4 else (3, 3)
    else:
        target = (3, 4) if file > 4 else (4, 3)

    dx = 1 if file < target[0] else -1
    dy = 1 if rank < target[1] else -1

    x, y = file + dx, rank + dy
    while (x, y) != target:
        if not (0 <= x <= 7 and 0 <= y <= 7):
            return 0
        sq = chess.square(x, y)
        piece_at = board.piece_at(sq)
        if piece_at and piece_at.piece_type == chess.PAWN:
            return 0
        x += dx
        y += dy

    # Nếu tới target và không bị chặn
    return 1


def long_diagonal_from_fen(fen, square, expected):
    board = chess.Board(fen)
    piece = board.piece_at(square)
    color = piece.color if piece else chess.WHITE
    rank = chess.square_rank(square)
    file = chess.square_file(square)
    result = long_diagonal_bishop(board, piece, color, rank, file)
    status = "✅" if result == expected else "❌"
    return f"[{status}] {chess.square_name(square)} | {piece.symbol() if piece else '?'} | result = {result} | expected = {expected} | FEN = {fen}"


class TestLongDiagonalBishop(unittest.TestCase):
    def test_cases(self):
        tests = [
            ("8/2r5/8/8/4P3/8/6B1/8 b - - 1 1", chess.G2, 0),  # a1, empty long diag
        ]
        for i, (fen, square, expected) in enumerate(tests, 1):
            print(f"Test #{i}:", long_diagonal_from_fen(fen, square, expected))


if __name__ == "__main__":
    unittest.main()
