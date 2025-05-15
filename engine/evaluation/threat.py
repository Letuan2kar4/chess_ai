import chess


def eval_threats_mg(board):
    """
    Tổng hợp đánh giá các loại đe dọa (threats) trong giai đoạn trung cuộc (middle game).
    Đã scale theo hệ số Stockfish và chia 1.24.
    """
    v = 0
    v += 56 * hanging(board)  # 69 / 1.24 ≈ 56
    v += 19 if king_threat(board) > 0 else 0  # 24 / 1.24 ≈ 19
    """v += 39 * pawn_push_threat(board)  # 48 / 1.24 ≈ 39
    v += 139 * threat_safe_pawn(board)  # 173 / 1.24 ≈ 139
    v += 48 * slider_on_queen(board)  # 60 / 1.24 ≈ 48
    v += 12 * knight_on_queen(board)  # 16 / 1.24 ≈ 12
    v += 6 * restricted(board)  # 7 / 1.24 ≈ 6
    v += 11 * weak_queen_protection(board)  # 14 / 1.24 ≈ 11
    for square in chess.SQUARES:
        v += [0, 4, 46, 62, 71, 63, 0][
            minor_threat(board, square)
        ]  # scaled từ [0,5,57,77,88,79,0]
        v += [0, 2, 29, 33, 0, 46, 0][
            rook_threat(board, square)
        ]  # scaled từ [0,3,37,42,0,58,0]"""
    return v


def weak_enemies(board, piece, color, rank, file):
    # 1) Phải là quân đối phương
    if not piece or piece.color == color:
        return 0

    enemy = piece.color
    # 2) Kiểm tra pawn địch bảo vệ (ô chéo liền dưới)
    down = rank - 1 if enemy == chess.WHITE else rank + 1
    for df in (-1, 1):
        f2 = file + df
        if 0 <= f2 < 8 and 0 <= down < 8:
            p = board.piece_at(chess.square(f2, down))
            if p and p.piece_type == chess.PAWN and p.color == enemy:
                return 0

    # 3) Ta tấn công nó?
    sq = chess.square(file, rank)
    our = len(board.attackers(color, sq))
    if our == 0:
        return 0

    # 4) Nếu ta chỉ tấn công 1 lần thì địch không tấn công lại >1
    opp = len(board.attackers(enemy, sq))
    if our <= 1 and opp > 1:
        return 0

    return 1


def hanging(board, piece, color, rank, file):
    # 1) Phải là weak enemy
    if not weak_enemies(board, piece, color, rank, file):
        return 0

    sq = chess.square(file, rank)
    enemy = piece.color
    # 2) Ta tấn công >1 lần và không phải pawn
    our = len(board.attackers(color, sq))
    if piece.piece_type != chess.PAWN and our > 1:
        return 1
    # 3) Hoặc địch không tấn công lại
    opp = len(board.attackers(enemy, sq))
    if opp == 0:
        return 1
    return 0


def king_attack(board, piece, color, rank, file):
    """
    1 nếu vua bên 'color' nằm sát cạnh ô (file,rank) (8 ô xung quanh), ngược lại 0.
    """
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            x = file + dx
            y = rank + dy
            if 0 <= x < 8 and 0 <= y < 8:
                p = board.piece_at(chess.square(x, y))
                if p and p.piece_type == chess.KING and p.color == color:
                    return 1
    return 0


def king_threat(board, piece, color, rank, file):
    """
    1 nếu quân địch ở (file,rank):
    - Là pawn/knight/bishop/rook/queen
    - weak_enemies == 1
    - và king_attack == 1
    Ngược lại 0.
    """
    # 1) Chỉ xét đối phương và lọc loại
    if (
        not piece
        or piece.color == color
        or piece.piece_type
        not in (chess.PAWN, chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN)
    ):
        return 0

    # 2) Phải weak_enemies
    if not weak_enemies(board, piece, color, rank, file):
        return 0

    # 3) Phải có king_attack
    if not king_attack(board, piece, color, rank, file):
        return 0

    return 1
