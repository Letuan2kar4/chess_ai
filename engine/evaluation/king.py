import chess

# --- Các hàm thành phần (giữ nguyên style của bạn) ---


def shelter_strength(board, square):
    """
    Độ vững chắc của lá chắn tốt trước vua ở ô `square`.
    Trả về điểm (luôn dương) ứng với số tốt đồng minh che chở.
    """
    color = board.piece_at(square).color
    dir_ = 1 if color == chess.WHITE else -1
    file = chess.square_file(square)
    rank = chess.square_rank(square)
    bonus = 0

    for df in (-1, 0, +1):
        f = file + df
        if 0 <= f <= 7:
            for dr in (1, 2, 3):
                r = rank + dir_ * dr
                if 0 <= r <= 7:
                    sq = chess.square(f, r)
                    p = board.piece_at(sq)
                    if p and p.piece_type == chess.PAWN and p.color == color:
                        bonus += (4 - dr) * 5
                    elif p and p.piece_type == chess.PAWN and p.color != color:
                        bonus -= (4 - dr) * 3
    return bonus


def flank_attack(board, square):
    """
    Số quân (mọi loại) từ đối phương tấn công vào ô `square`.
    """
    color = board.piece_at(square).color
    return len(board.attackers(not color, square))


def pawnless_flank(board, square):
    """
    Trả 1 nếu xung quanh cánh vua (3 file) không có tốt đồng minh, 0 nếu có.
    """
    color = board.piece_at(square).color
    king_file = chess.square_file(square)
    for df in (-1, 0, +1):
        f = king_file + df
        if 0 <= f <= 7:
            for r in range(8):
                p = board.piece_at(chess.square(f, r))
                if p and p.piece_type == chess.PAWN and p.color == color:
                    return 0
    return 1


def king_danger(board, square):
    """
    20 điểm cho mỗi quân đối phương đang chiếu hoặc tấn công king ở `square`.
    """
    color = board.piece_at(square).color
    return len(board.attackers(not color, square)) * 20


# --- King safety midgame & endgame, tự động cho trắng (+) và đen (−) ---


def eval_king_safety_mg(board):
    """
    Tính điểm an toàn vua giai đoạn giữa trận.
    Trả về tổng: trắng dương, đen âm.
    """
    total = 0
    for color in (chess.WHITE, chess.BLACK):
        sign = 1 if color == chess.WHITE else -1
        sq = board.king(color)
        # -shelter + (kd^2)//4096 + flank*8 + pawnless*int(17/1.24)
        mg = (
            -shelter_strength(board, sq)
            + (king_danger(board, sq) ** 2) // 4096
            + flank_attack(board, sq) * 8
            + pawnless_flank(board, sq) * int(17 / 1.24)
        )
        total += sign * mg
    return total


def eval_king_safety_eg(board):
    """
    Tính điểm an toàn vua giai đoạn tàn cuộc.
    Trả về tổng: trắng dương, đen âm.
    """
    total = 0
    for color in (chess.WHITE, chess.BLACK):
        sign = 1 if color == chess.WHITE else -1
        sq = board.king(color)
        # -int(16/1.24)*distance + (kd//16) + pawnless*int(95/1.24)
        dist = chess.square_distance(sq, board.king(not color))
        eg = (
            -int(16 / 1.24) * dist
            + king_danger(board, sq) // 16
            + pawnless_flank(board, sq) * int(95 / 1.24)
        )
        total += sign * eg
    return total
