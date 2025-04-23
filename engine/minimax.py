from engine.evaluation_engine import evaluate_board

def order_moves(board):
    moves = list(board.legal_moves)

    def move_score(move):
        if board.is_capture(move):
            return 10  # ăn quân
        if move.promotion:
            return 9   # phong tốt
        return 0       # nước thường

    moves.sort(key=move_score, reverse=True)
    return moves

def alphabeta(board, depth, alpha, beta, is_maximizing, ai_color):
    """
    Hàm đệ quy alpha-beta pruning
    - board: bàn cờ hiện tại (python-chess)
    - depth: độ sâu tìm kiếm
    - alpha, beta: giá trị cắt tỉa
    - is_maximizing: True nếu đang xét lượt của AI
    - ai_color: màu quân của AI (chess.WHITE hoặc chess.BLACK)
    """

    # ⛔ Khi đạt đến độ sâu cuối hoặc hết ván thì đánh giá bàn cờ
    if depth == 0 or board.is_game_over():
        # 🧠 Nếu là lượt AI thì giữ nguyên điểm, nếu là lượt người chơi thì đảo chiều
        return evaluate_board(board) * (1 if ai_color == board.turn else -1)

    if is_maximizing:
        max_eval = -float("inf")
        for move in order_moves(board):
            board.push(move)
            eval = alphabeta(board, depth - 1, alpha, beta, False, ai_color)
            board.pop()
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break  # ✂️ Cắt tỉa beta
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
                break  # ✂️ Cắt tỉa alpha
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
