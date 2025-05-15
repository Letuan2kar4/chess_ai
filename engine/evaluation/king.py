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
    total = 0
    for color in (chess.WHITE, chess.BLACK):
        sign = 1 if color == chess.WHITE else -1
        king_sq = board.king(color)
        if king_sq is None:
            continue

        rank = chess.square_rank(king_sq)
        file = chess.square_file(king_sq)

        # Điểm cộng nếu có tốt gần vua
        shield_bonus = 0
        direction = 1 if color == chess.WHITE else -1
        for df in [-1, 0, 1]:
            f = file + df
            r = rank + direction
            if 0 <= f <= 7 and 0 <= r <= 7:
                sq = chess.square(f, r)
                piece = board.piece_at(sq)
                if piece and piece.piece_type == chess.PAWN and piece.color == color:
                    shield_bonus += 15  # Có tốt che

        # Điểm trừ nếu bị tấn công gần vua
        attackers_penalty = len(board.attackers(not color, king_sq)) * 20

        # Có tốt ở cánh vua không?
        pawnless = 1
        for df in [-1, 0, 1]:
            f = file + df
            if 0 <= f <= 7:
                for r in range(1, 7):
                    sq = chess.square(f, r)
                    p = board.piece_at(sq)
                    if p and p.piece_type == chess.PAWN and p.color == color:
                        pawnless = 0
                        break

        total += sign * (shield_bonus - attackers_penalty + pawnless * 20)
    return total



def eval_king_safety_eg(board):
    total = 0
    for color in (chess.WHITE, chess.BLACK):
        sign = 1 if color == chess.WHITE else -1
        king_sq = board.king(color)
        opp_king_sq = board.king(not color)
        if king_sq is None or opp_king_sq is None:
            continue

        # Khoảng cách giữa 2 vua → càng gần càng tốt
        dist = chess.square_distance(king_sq, opp_king_sq)

        # Điểm trừ nếu vua cách xa đối thủ
        dist_penalty = dist * 8  # hệ số nhẹ để tránh mất tempo

        # Điểm trừ nếu bị tấn công
        danger_penalty = len(board.attackers(not color, king_sq)) * 10

        # Phạt nếu thiếu tốt ở cánh quanh vua
        file = chess.square_file(king_sq)
        pawnless = 1
        for df in [-1, 0, 1]:
            f = file + df
            if 0 <= f <= 7:
                for r in range(1, 7):
                    sq = chess.square(f, r)
                    p = board.piece_at(sq)
                    if p and p.piece_type == chess.PAWN and p.color == color:
                        pawnless = 0
                        break

        total += sign * (-dist_penalty - danger_penalty + pawnless * 30)
    return total


