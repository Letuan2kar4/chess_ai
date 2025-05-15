import chess

# === 1. Bảng bonus mobility (Middle Game & Endgame) ===
MOBILITY_BONUS = {
    "MG": {
        chess.KNIGHT: [-62, -53, -12, -4, 3, 13, 22, 28, 33],
        chess.BISHOP: [-48, -20, 16, 26, 38, 51, 55, 63, 63, 68, 81, 81, 91, 98],
        chess.ROOK: [-60, -20, 2, 3, 3, 11, 22, 31, 40, 40, 41, 48, 57, 57, 62],
        chess.QUEEN: [
            -30,
            -12,
            -8,
            -9,
            20,
            23,
            23,
            35,
            38,
            53,
            64,
            65,
            65,
            66,
            67,
            67,
            72,
            72,
            77,
            79,
            93,
            108,
            108,
            108,
            110,
            114,
            114,
            116,
        ],
    },
    "EG": {
        chess.KNIGHT: [-81, -56, -31, -16, 5, 11, 17, 20, 25],
        chess.BISHOP: [-59, -23, -3, 13, 24, 42, 54, 57, 65, 73, 78, 86, 88, 97],
        chess.ROOK: [
            -78,
            -17,
            23,
            39,
            70,
            99,
            103,
            121,
            134,
            139,
            158,
            164,
            168,
            169,
            172,
        ],
        chess.QUEEN: [
            -48,
            -30,
            -7,
            19,
            40,
            55,
            59,
            75,
            78,
            96,
            96,
            100,
            121,
            127,
            131,
            133,
            136,
            141,
            147,
            150,
            151,
            168,
            168,
            171,
            182,
            182,
            192,
            219,
        ],
    },
}


def _mobility_count(board: chess.Board, square: chess.Square) -> int:
    pseudo = board.copy()
    piece = board.piece_at(square)
    pseudo.turn = piece.color
    cnt = 0
    for mv in pseudo.legal_moves:
        if mv.from_square != square:
            continue
        dest = board.piece_at(mv.to_square)
        # Skip ăn hậu đối phương
        if dest and dest.piece_type == chess.QUEEN and dest.color != piece.color:
            continue
        cnt += 1
    return cnt

def _mobility_bonus(count: int, table: list[int]) -> int:
    idx = min(count, len(table) - 1)
    return int(table[idx] / 1.24)

# === Core evaluation function ===
def _eval_mobility(
    board: chess.Board, bonus_table: dict[chess.PieceType, list[int]]
) -> int:
    total = 0
    for color in (chess.WHITE, chess.BLACK):
        sign = 1 if color == chess.WHITE else -1
        for piece_type, table in bonus_table.items():
            for sq in board.pieces(piece_type, color):
                cnt = _mobility_count(board, sq)
                bonus = _mobility_bonus(cnt, table)
                total += sign * bonus
    return total

# === Phase-specific wrappers ===
def eval_mobility_mg(board: chess.Board) -> int:
    return _eval_mobility(board, MOBILITY_BONUS["MG"])

def eval_mobility_eg(board: chess.Board) -> int:
    return _eval_mobility(board, MOBILITY_BONUS["EG"])

def eval_mobility(board, phase):
    """
    Hàm đánh giá mobility cho bàn cờ.
    Trả về điểm số, dương có lợi cho trắng, âm có lợi cho đen.
    """
    if phase == "mg":
        return eval_mobility_mg(board)
    else:
        return eval_mobility_eg(board)