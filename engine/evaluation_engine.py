import chess
from engine.evaluation.material import eval_material
from engine.evaluation.psqt import eval_psqt
from engine.evaluation.imbalance import eval_imbalance
from engine.evaluation.pawns import eval_pawns
from engine.evaluation.mobility import eval_mobility
from engine.evaluation.king import eval_king_safety_mg, eval_king_safety_eg
from engine.evaluation.pieces import eval_pieces

# === HÀM CHÍNH ===


def evaluate_board(board):
    if board.is_checkmate():
        return -9999 if board.turn else 9999
    if board.is_stalemate() or board.is_insufficient_material():
        return 0  # Hòa cờ
    """
    Hàm đánh giá tổng cho bàn cờ.
    Trả về điểm số, dương có lợi cho trắng, âm có lợi cho đen.
    """
    # 1. Tính phase (giai đoạn cờ)
    phase = find_phase(board)  # 0.0 (endgame) -> 1.0 (middle game)

    # 2. Tính điểm middle game và end game riêng
    mg_score = (
        eval_material(board, phase="mg")
        + eval_psqt(board, phase="mg")
        + eval_imbalance(board)
        + eval_pawns(board, phase="mg")
        + eval_pieces(board, phase="mg")
        + eval_mobility(board, phase="mg")
        ##+ eval_threats(board, phase="mg")
        + eval_king_safety_mg(board)
    )  # chỉ MG mới có

    eg_score = (
        eval_material(board, phase="eg")
        + eval_psqt(board, phase="eg")
        + eval_imbalance(board)
        + eval_pawns(board, phase="eg")
        + eval_pieces(board, phase="eg")
        + eval_mobility(board, phase="eg")
        ##+ eval_threats(board, phase="eg")
        + eval_king_safety_eg(board)
    )
    # Endgame không có Space

    # 3. Blend middle game và end game theo phase
    blended_score = int(mg_score * phase + eg_score * (1 - phase))

    return blended_score


def non_pawn_material(board) -> int:
    piece_values = {
        chess.KNIGHT: 325,
        chess.BISHOP: 325,
        chess.ROOK: 550,
        chess.QUEEN: 1000,
    }
    total = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece and piece.piece_type in piece_values:
            total += piece_values[piece.piece_type]
    return total


def find_phase(board) -> int:
    MG_LIMIT = 15258
    EG_LIMIT = 3915

    npm = non_pawn_material(board) + non_pawn_material(board.mirror())  # cả hai bên
    npm = max(EG_LIMIT, min(npm, MG_LIMIT))

    phase128 = ((npm - EG_LIMIT) * 128) // (MG_LIMIT - EG_LIMIT)
    return phase128  # hoặc phase256 nếu bạn muốn: * 2
