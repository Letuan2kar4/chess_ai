from evaluation.material import eval_material
from evaluation.psqt import eval_psqt
from evaluation.imbalance import eval_imbalance
from evaluation.pawns import eval_pawns
# === HÀM CHÍNH ===


def evaluate_board(board):
    """
    Hàm đánh giá tổng cho bàn cờ.
    Trả về điểm số, dương có lợi cho trắng, âm có lợi cho đen.
    """
    # 1. Tính phase (giai đoạn cờ)
    phase_score = phase(board)  # 0.0 (endgame) -> 1.0 (middle game)

    # 2. Tính điểm middle game và end game riêng
    mg_score = (
        eval_material(board, phase="mg")
        + eval_psqt(board, phase="mg")
        + eval_imbalance(board)
        + eval_pawns(board, phase="mg")
        + eval_pieces(board, phase="mg")
        + eval_mobility(board, phase="mg")
        + eval_threats(board, phase="mg")
        + eval_passed_pawns(board, phase="mg")
        + eval_king(board, phase="mg")
        + eval_space(board)
    )  # chỉ MG mới có

    eg_score = (
        eval_material(board, phase="eg")
        + eval_psqt(board, phase="eg")
        + eval_imbalance(board)
        + eval_pawns(board, phase="eg")
        + eval_pieces(board, phase="eg")
        + eval_mobility(board, phase="eg")
        + eval_threats(board, phase="eg")
        + eval_passed_pawns(board, phase="eg")
        + eval_king(board, phase="eg")
    )
    # Endgame không có Space

    # 3. Blend middle game và end game theo phase
    blended_score = int(mg_score * phase_score + eg_score * (1 - phase_score))

    # 4. Thêm bonus tempo (nước đi)
    blended_score += eval_tempo(board)

    # 5. Điều chỉnh theo rule50 (50-move rule)
    blended_score = int(blended_score * (100 - rule50(board)) / 100)

    return blended_score


# ====== HÀM STUB (chưa viết) ======


def eval_pieces(board, phase="mg"):
    return 0


def eval_mobility(board, phase="mg"):
    return 0


def eval_threats(board, phase="mg"):
    return 0


def eval_passed_pawns(board, phase="mg"):
    return 0


def eval_king(board, phase="mg"):
    return 0


def eval_space(board):
    return 0


def eval_tempo(board):
    return 0


def rule50(board):
    return 0


def phase(board):
    return 1.0  # Tạm return 1.0 (full middle game) – viết sau
