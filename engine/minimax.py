import chess
from engine.evaluation_engine import evaluate_board
from engine.evaluation_engine import PIECE_VALUES


def move_score_nangcao(board, move):
    """
    Chấm điểm từng nước đi để sắp xếp:
    - Ăn quân giá trị cao bằng quân thấp (MVV-LVA)
    - Nước chiếu
    - Nước phong tốt
    - Ưu tiên trung tâm
    """
    score = 0

    # 🥷 MVV-LVA: Most Valuable Victim - Least Valuable Attacker
    if board.is_capture(move):
        victim = board.piece_at(move.to_square)
        attacker = board.piece_at(move.from_square)
        if victim and attacker:
            score += (
                10 * PIECE_VALUES[victim.piece_type] - PIECE_VALUES[attacker.piece_type]
            )

    # 👑 Nước phong tốt
    if move.promotion:
        score += 900 if move.promotion == chess.QUEEN else 500

    # 👊 Nước chiếu
    board.push(move)
    if board.is_check():
        score += 300
    board.pop()

    # 🔄 Ưu tiên kiểm soát trung tâm
    center_bonus = [chess.D4, chess.E4, chess.D5, chess.E5]
    if move.to_square in center_bonus:
        score += 50

    return score


def order_moves(board):
    """
    Trả về danh sách nước đi được sắp xếp theo độ "tốt"
    """
    moves = list(board.legal_moves)
    moves.sort(key=lambda m: move_score_nangcao(board, m), reverse=True)
    return moves


def quiescence_search(board, alpha, beta, ai_color):
    """
    Mở rộng tìm kiếm tại trạng thái không "yên tĩnh" (ví dụ: có thể ăn quân).
    Tránh đánh giá sai vì dừng ngay ở nước có bắt quân.
    """
    stand_pat = evaluate_board(board)
    if board.turn != ai_color:
        stand_pat = -stand_pat

    if stand_pat >= beta:
        return beta
    if stand_pat > alpha:
        alpha = stand_pat

    for move in board.legal_moves:
        if board.is_capture(move):  # ❗ Chỉ mở rộng nếu là nước ăn
            board.push(move)
            score = -quiescence_search(board, -beta, -alpha, ai_color)
            board.pop()

            if score >= beta:
                return beta
            if score > alpha:
                alpha = score

    return alpha


# 🧠 Bảng băm lưu điểm các trạng thái đã đánh giá
transposition_table = {}


def fen_key(board):
    """
    Trích xuất phần cần thiết từ FEN để làm khóa:
    - Bỏ lượt đi (w/b), số nước đi kể từ lần bắt tốt, số lượt đã đi
    - Chỉ giữ vị trí quân và quyền nhập thành (có thể ảnh hưởng luật)
    """
    parts = board.fen().split(" ")
    return f"{parts[0]} {parts[2]}"


def alphabeta(board, depth, alpha, beta, is_maximizing, ai_color):
    """
    Hàm đệ quy Alpha-Beta Pruning với Transposition Table
    - board: trạng thái bàn cờ hiện tại
    - depth: độ sâu tìm kiếm còn lại
    - alpha: điểm tốt nhất của Max đã tìm được
    - beta: điểm tốt nhất của Min đã tìm được
    - is_maximizing: True nếu là lượt AI (Max)
    - ai_color: màu quân của AI (chess.WHITE hoặc chess.BLACK)
    """

    # ✋ Nếu đạt độ sâu cuối hoặc game kết thúc → đánh giá luôn
    if depth == 0:
        return quiescence_search(board, alpha, beta, ai_color)

    if board.is_game_over():
        score = evaluate_board(board)
        return score if board.turn == ai_color else -score

    # 🔑 Dùng FEN (chuỗi duy nhất đại diện bàn cờ) làm key
    board_hash = hash(fen_key(board))

    if board_hash in transposition_table:
        return transposition_table[board_hash]  # ✅ Trả về điểm đã tính

    if is_maximizing:
        max_eval = -float("inf")
        for move in order_moves(board):
            board.push(move)
            eval = alphabeta(board, depth - 1, alpha, beta, False, ai_color)
            board.pop()
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break  # ✂️ Cắt nhánh
        transposition_table[board_hash] = max_eval  # 💾 Lưu vào bảng băm
        return max_eval
    else:
        min_eval = float("inf")
        for move in order_moves(board):
            board.push(move)
            eval = alphabeta(board, depth - 1, alpha, beta, True, ai_color)
            board.pop()
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break  # ✂️ Cắt nhánh
        transposition_table[board_hash] = min_eval  # 💾 Lưu vào bảng băm
        return min_eval


def get_best_move_alpha_beta(board, depth):
    """
    Hàm gọi ban đầu để tìm nước đi tốt nhất cho AI
    """
    ai_color = board.turn  # ✅ Ghi nhận màu quân AI tại thời điểm gọi
    best_move = None
    best_eval = -float("inf")
    alpha = -float("inf")
    beta = float("inf")

    for move in order_moves(board):
        board.push(move)
        eval = alphabeta(board, depth - 1, alpha, beta, False, ai_color)
        board.pop()

        if eval > best_eval:
            best_eval = eval
            best_move = move
            alpha = max(alpha, eval)

    return best_move
