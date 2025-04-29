import chess

# ===== Bảng Cân bằng cặp quân ======
IMBALANCE_BISHOP_PAIR = 30
IMBALANCE_KNIGHT_PAIR = 20
IMBALANCE_KNIGHT_VS_BISHOP = 10
IMBALANCE_ROOK_VS_MINOR = 15
IMBALANCE_QUEEN_VS_ROOK_PAIR = 20


def eval_imbalance(board):
    """
    Đánh giá sự mất cân bằng giữa các loại quân trên bàn cờ.
    """
    score = 0

    white = {
        chess.PAWN: len(board.pieces(chess.PAWN, chess.WHITE)),
        chess.KNIGHT: len(board.pieces(chess.KNIGHT, chess.WHITE)),
        chess.BISHOP: len(board.pieces(chess.BISHOP, chess.WHITE)),
        chess.ROOK: len(board.pieces(chess.ROOK, chess.WHITE)),
        chess.QUEEN: len(board.pieces(chess.QUEEN, chess.WHITE)),
    }

    black = {
        chess.PAWN: len(board.pieces(chess.PAWN, chess.BLACK)),
        chess.KNIGHT: len(board.pieces(chess.KNIGHT, chess.BLACK)),
        chess.BISHOP: len(board.pieces(chess.BISHOP, chess.BLACK)),
        chess.ROOK: len(board.pieces(chess.ROOK, chess.BLACK)),
        chess.QUEEN: len(board.pieces(chess.QUEEN, chess.BLACK)),
    }

    ### 1. Bishop pair bonus
    if white[chess.BISHOP] >= 2:
        score += IMBALANCE_BISHOP_PAIR
    if black[chess.BISHOP] >= 2:
        score -= IMBALANCE_BISHOP_PAIR

    ### 2. Knight pair bonus
    if white[chess.KNIGHT] >= 2:
        score += IMBALANCE_KNIGHT_PAIR
    if black[chess.KNIGHT] >= 2:
        score -= IMBALANCE_KNIGHT_PAIR

    ### 3. Knight vs Bishop imbalance
    if (
        white[chess.KNIGHT] > black[chess.KNIGHT]
        and black[chess.BISHOP] > white[chess.BISHOP]
    ):
        score += IMBALANCE_KNIGHT_VS_BISHOP
    if (
        black[chess.KNIGHT] > white[chess.KNIGHT]
        and white[chess.BISHOP] > black[chess.BISHOP]
    ):
        score -= IMBALANCE_KNIGHT_VS_BISHOP

    ### 4. Rook vs Minor pieces
    white_minor = white[chess.KNIGHT] + white[chess.BISHOP]
    black_minor = black[chess.KNIGHT] + black[chess.BISHOP]

    if white[chess.ROOK] > black[chess.ROOK] and black_minor > white_minor:
        score += IMBALANCE_ROOK_VS_MINOR
    if black[chess.ROOK] > white[chess.ROOK] and white_minor > black_minor:
        score -= IMBALANCE_ROOK_VS_MINOR

    ### 5. Queen vs Rook pair
    if white[chess.QUEEN] > black[chess.QUEEN] and black[chess.ROOK] >= 2:
        score += IMBALANCE_QUEEN_VS_ROOK_PAIR
    if black[chess.QUEEN] > white[chess.QUEEN] and white[chess.ROOK] >= 2:
        score -= IMBALANCE_QUEEN_VS_ROOK_PAIR

    return score
