from engine.evaluation_engine import evaluate_board


def alphabeta(board, depth, alpha, beta, maximizing_player, ai_color):
    """
    Thuần Alpha-Beta Pruning:
    - board: trạng thái bàn cờ hiện tại
    - depth: độ sâu tìm kiếm còn lại
    - alpha: điểm lớn nhất Max đã tìm thấy
    - beta: điểm nhỏ nhất Min đã tìm thấy
    - maximizing_player: True nếu lượt AI (Max), False nếu đối thủ (Min)
    - ai_color: màu quân AI (chess.WHITE hoặc chess.BLACK)
    """
    # Nếu đạt độ sâu cuối hoặc game kết thúc
    if depth == 0 or board.is_game_over():
        score = evaluate_board(board)
        return score if board.turn == ai_color else -score

    if maximizing_player:
        max_eval = -float("inf")
        for move in board.legal_moves:
            board.push(move)
            eval = alphabeta(board, depth - 1, alpha, beta, False, ai_color)
            board.pop()
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break  # Cắt tỉa
        return max_eval
    else:
        min_eval = float("inf")
        for move in board.legal_moves:
            board.push(move)
            eval = alphabeta(board, depth - 1, alpha, beta, True, ai_color)
            board.pop()
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break  # Cắt tỉa
        return min_eval


def get_best_move(board, depth):
    """
    Tìm nước đi tốt nhất cho AI tại trạng thái hiện tại
    """
    ai_color = board.turn
    best_move = None
    best_eval = -float("inf")
    alpha = -float("inf")
    beta = float("inf")

    for move in board.legal_moves:
        board.push(move)
        eval = alphabeta(board, depth - 1, alpha, beta, False, ai_color)
        board.pop()

        if eval > best_eval:
            best_eval = eval
            best_move = move
            alpha = max(alpha, eval)

    return best_move
