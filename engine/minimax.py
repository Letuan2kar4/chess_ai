from engine.evaluation_engine import evaluate_board

def alphabeta(board, depth, alpha, beta, is_maximizing):
    # Điểm dừng đệ quy: tìm kiếm hết độ sâu hoặc kết thúc ván
    if depth == 0 or board.is_game_over():
        return evaluate_board(board)

    if is_maximizing:  # AI (đen) muốn điểm càng cao càng tốt
        max_eval = -float("inf")
        for move in board.legal_moves:
            board.push(move)
            eval = alphabeta(board, depth - 1, alpha, beta, False)
            board.pop()
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:  # cắt tỉa nhánh không cần thiết
                break
        return max_eval
    else:  # Người chơi (trắng) muốn điểm càng thấp càng tốt
        min_eval = float("inf")
        for move in board.legal_moves:
            board.push(move)
            eval = alphabeta(board, depth - 1, alpha, beta, True)
            board.pop()
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:  # cắt tỉa nhánh không cần thiết
                break
        return min_eval

def get_best_move_alpha_beta(board, depth):
    best_move = None
    best_eval = -float("inf")
    alpha = -float("inf")
    beta = float("inf")

    for move in board.legal_moves:
        board.push(move)
        eval = alphabeta(board, depth - 1, alpha, beta, False)
        board.pop()

        if eval > best_eval:
            best_eval = eval
            best_move = move
            alpha = max(alpha, eval)

    return best_move
