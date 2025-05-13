import chess

## Bảng pst
from engine.evaluation.evaluation_tables import (
    PAWN_PST_MG,
    KNIGHT_PST_MG,
    BISHOP_PST_MG,
    ROOK_PST_MG,
    QUEEN_PST_MG,
    KING_PST_MG,
    PAWN_PST_EG,
    KNIGHT_PST_EG,
    BISHOP_PST_EG,
    ROOK_PST_EG,
    QUEEN_PST_EG,
    KING_PST_EG,
)

PST_MG = {
    chess.PAWN: PAWN_PST_MG,
    chess.KNIGHT: KNIGHT_PST_MG,
    chess.BISHOP: BISHOP_PST_MG,
    chess.ROOK: ROOK_PST_MG,
    chess.QUEEN: QUEEN_PST_MG,
    chess.KING: KING_PST_MG,
}

PST_EG = {
    chess.PAWN: PAWN_PST_EG,
    chess.KNIGHT: KNIGHT_PST_EG,
    chess.BISHOP: BISHOP_PST_EG,
    chess.ROOK: ROOK_PST_EG,
    chess.QUEEN: QUEEN_PST_EG,
    chess.KING: KING_PST_EG,
}


def eval_psqt(board, phase):
    """
    Đánh giá Piece-Square Table (PSQT) cho bàn cờ hiện tại, theo phase middle game (mg) hoặc end game (eg).
    """
    score = 0
    pst_table = PST_MG if phase == "mg" else PST_EG

    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece is None:
            continue

        piece_type = piece.piece_type
        color = piece.color

        # Lật ô nếu quân đen
        flip_square = square if color == chess.WHITE else chess.square_mirror(square)

        bonus = pst_table[piece_type][flip_square]

        # Cộng điểm cho trắng, trừ điểm cho đen
        if color == chess.WHITE:
            score += bonus
        else:
            score -= bonus

    return score
