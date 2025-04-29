import chess

# ====== HỆ SỐ CƠ BẢN ======
PIECE_VALUES_MG = {
    chess.PAWN: 100,
    chess.KNIGHT: 629,
    chess.BISHOP: 665,
    chess.ROOK: 1028,
    chess.QUEEN: 2046,
    chess.KING: 0,
}

PIECE_VALUES_EG = {
    chess.PAWN: 166,
    chess.KNIGHT: 688,
    chess.BISHOP: 737,
    chess.ROOK: 1112,
    chess.QUEEN: 2162,
    chess.KING: 0,
}


def eval_material(board, phase="mg"):
    """
    Tính tổng điểm vật chất trên bàn cờ.
    Phase = 'mg' (middle game) hoặc 'eg' (end game).
    """
    score = 0
    piece_values = PIECE_VALUES_MG if phase == "mg" else PIECE_VALUES_EG

    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            value = piece_values[piece.piece_type]
            if piece.color == chess.WHITE:
                score += value
            else:
                score -= value

    return score
