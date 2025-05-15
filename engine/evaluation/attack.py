import chess

def eval_attack(board):
    """
    Đánh giá tấn công cơ bản dựa trên số quân phòng thủ & bị đe dọa gần vua.
    Dương cho trắng, âm cho đen.
    """
    total = 0
    for color in (chess.WHITE, chess.BLACK):
        king_sq = board.king(color)
        if king_sq is None:
            continue  # Vua bị bắt (đã chiếu bí), bỏ qua

        # Vùng quanh vua: 3x3
        danger_squares = []
        rank = chess.square_rank(king_sq)
        file = chess.square_file(king_sq)
        for dr in [-1, 0, 1]:
            for df in [-1, 0, 1]:
                r, f = rank + dr, file + df
                if 0 <= r < 8 and 0 <= f < 8:
                    sq = chess.square(f, r)
                    danger_squares.append(sq)

        attacked_value = 0
        for sq in danger_squares:
            # Nếu ô này bị tấn công bởi đối phương
            attackers = board.attackers(not color, sq)
            if attackers:
                # Ưu tiên nếu quân mạnh bị tấn
                target = board.piece_at(sq)
                if target:
                    attacked_value += piece_value(target.piece_type)
                else:
                    attacked_value += 30  # Vị trí trống nhưng gần vua

        # Trừ điểm nếu bên mình bị đe dọa
        score = attacked_value
        total += score if color == chess.WHITE else -score
    return total


def piece_value(piece_type):
    values = {
        chess.PAWN: 100,
        chess.KNIGHT: 300,
        chess.BISHOP: 300,
        chess.ROOK: 500,
        chess.QUEEN: 900,
        chess.KING: 0  # không tính
    }
    return values.get(piece_type, 0)
