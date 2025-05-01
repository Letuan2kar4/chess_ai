import chess


def pawns_mg(board):
    """
    Đánh giá đặc trưng pawn trong giai đoạn middle game cho 1 ô.
    Trả về điểm số dựa trên các tiêu chí:
        - doubled_isolated
        - isolated
        - backward
        - doubled
        - connected
        - weak_unopposed
        - blocked
    """
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if not piece or piece.piece_type != chess.PAWN:
            return 0

        color = piece.color
        sign = 1 if color == chess.WHITE else -1
        score = 0

        # Doubled Isolated
        if doubled_isolated(board, square):
            score -= sign * 8
        # Isolated
        elif isolated(board, square):
            score -= sign * 4
        # Backward
        elif backward(board, square):
            score -= sign * 7

        # Doubled
        score -= sign * 8 * doubled(board, square)

        # Connected
        if connected(board, square):
            score += sign * connected_bonus(board, square)

        # Weak Unopposed
        score -= sign * 10 * weak_unopposed_pawn(board, square)

        # Blocked
        blocked_level = blocked(board, square)  # 0, 1 hoặc 2
        penalties = [0, 8, 2]
        score -= sign * penalties[blocked_level]

    return score


def pawns_eg(board):
    """
    Đánh giá đặc trưng pawn trong giai đoạn endgame cho 1 ô.
    Bao gồm các tiêu chí:
        - doubled_isolated
        - isolated
        - backward
        - doubled
        - connected (scaled theo rank)
        - weak_unopposed
        - weak_lever
        - blocked
    """
    score = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if not piece or piece.piece_type != chess.PAWN:
            return 0

        color = piece.color
        sign = 1 if color == chess.WHITE else -1
        rank = (
            chess.square_rank(square)
            if color == chess.WHITE
            else 7 - chess.square_rank(square)
        )

        # Doubled Isolated
        if doubled_isolated(board, square):
            score -= sign * 45
        # Isolated
        elif isolated(board, square):
            score -= sign * 12
        # Backward
        elif backward(board, square):
            score -= sign * 19

        # Doubled
        score -= sign * 45 * doubled(board, square)

        # Connected (bonus nhân thêm hệ số tùy rank)
        if connected(board, square):
            connected_bonus_score = connected_bonus(board, square)
            score += sign * (connected_bonus_score * (rank - 3) // 4)

        # Weak Unopposed
        score -= sign * 22 * weak_unopposed_pawn(board, square)

        # Weak Lever
        score -= sign * 45 * weak_lever(board, square)

        # Blocked
        blocked_level = blocked(board, square)  # 0, 1 hoặc 2
        penalties = [0, -3, 3]
        score += sign * penalties[blocked_level]

    return score


# ====== Các hàm thành phần ======


def doubled(board, square):
    """
    Kiểm tra xem Tốt ở ô square có bị doubled (chồng) không.
    """
    piece = board.piece_at(square)
    color = piece.color
    sign = 1 if color == chess.WHITE else -1

    if not piece or piece.piece_type != chess.PAWN:
        return 0

    file = chess.square_file(square)
    rank = chess.square_rank(square)

    # Kiểm tra ngay trên rank cao hơn
    under_square = chess.square(file, rank - sign)
    if (
        board.piece_at(under_square)
        and board.piece_at(under_square).piece_type == chess.PAWN
        and board.piece_at(under_square).color == color
    ):
        left_under = chess.square(file - 1, rank - sign) if file > 0 else None
        right_under = chess.square(file + 1, rank - sign) if file < 7 else None

        if (
            left_under
            and board.piece_at(left_under)
            and board.piece_at(left_under).piece_type == chess.PAWN
            and board.piece_at(left_under).color == color
        ):
            return 0
        if (
            right_under
            and board.piece_at(right_under)
            and board.piece_at(right_under).piece_type == chess.PAWN
            and board.piece_at(right_under).color == color
        ):
            return 0

        return 1
    return 0


def isolated(board, square):
    """
    Kiểm tra xem Tốt ở ô square có bị isolated (cô lập) không.
    """
    piece = board.piece_at(square)
    color = piece.color
    if not piece or piece.piece_type != chess.PAWN:
        return 0

    file = chess.square_file(square)

    # Kiểm tra toàn bộ file bên trái và bên phải
    for rank in range(8):
        if file > 0:
            left_square = chess.square(file - 1, rank)
            if (
                board.piece_at(left_square)
                and (board.piece_at(left_square).piece_type == chess.PAWN)
                and (board.piece_at(left_square).color == color)
            ):
                return 0
        if file < 7:
            right_square = chess.square(file + 1, rank)
            if (
                board.piece_at(right_square)
                and board.piece_at(right_square).piece_type == chess.PAWN
                and board.piece_at(right_square).color == color
            ):
                return 0

    return 1


def backward(board, square):
    """
    Kiểm tra xem Tốt ở ô square có bị backward (tụt hậu) không.
    """
    piece = board.piece_at(square)
    color = piece.color
    sign = 1 if color == chess.WHITE else -1
    if not piece or piece.piece_type != chess.PAWN:
        return 0

    file = chess.square_file(square)
    rank = chess.square_rank(square)

    # Kiểm tra từ rank hiện tại trở lên, xem có Tốt bạn hỗ trợ không
    for y in range(1, rank):
        if file > 0:
            left = chess.square(file - 1, y)
            if (
                board.piece_at(left)
                and board.piece_at(left).piece_type == chess.PAWN
                and board.piece_at(left).color == color
            ):
                return 0
        if file < 7:
            right = chess.square(file + 1, y)
            if (
                board.piece_at(right)
                and board.piece_at(right).piece_type == chess.PAWN
                and board.piece_at(right).color == color
            ):
                return 0
    # Kiểm tra nếu đường tiến bị quân địch cản
    enemy_color = not piece.color
    front_left = (
        chess.square(file - 1, rank + 2 * sign) if file > 0 and rank + 2 < 7 else None
    )
    front_right = (
        chess.square(file + 1, rank + 2 * sign) if file < 7 and rank + 2 < 7 else None
    )
    front = chess.square(file, rank + sign) if rank + 1 < 7 else None

    for sq in [front_left, front_right, front]:
        if sq is not None:
            enemy = board.piece_at(sq)
            if enemy and enemy.color == enemy_color:
                return 1

    return 0


def doubled_isolated(board, square):
    """
    Kiểm tra quân tốt ở ô square có phải là doubled isolated pawn không.
    1. Nếu có tốt đồng minh ở file bên trái/phải → Không phải isolated → return 0
    2. Nếu không có: kiểm tra từ vị trí tốt lên phía trước (theo hướng phong cấp):
        - Nếu không có quân địch ➔ return 0
    3. Nếu có quân địch ở phía trước: kiểm tra từ vị trí tốt xuống phía sau:
        - Nếu có quân đồng minh ở phía sau ➔ return 1
    """
    piece = board.piece_at(square)
    if not piece or piece.piece_type != chess.PAWN:
        return 0

    color = piece.color
    file = chess.square_file(square)
    rank = chess.square_rank(square)
    sign = 1 if color == chess.WHITE else -1
    enemy_color = not color

    # 1. Kiểm tra isolated
    for rank in range(8):
        if file > 0:
            left_square = chess.square(file - 1, rank)
            if (
                board.piece_at(left_square)
                and board.piece_at(left_square).piece_type == chess.PAWN
            ):
                return 0
        if file < 7:
            right_square = chess.square(file + 1, rank)
            if (
                board.piece_at(right_square)
                and board.piece_at(right_square).piece_type == chess.PAWN
            ):
                return 0

    # 2. Kiểm tra có quân địch phía trước không
    has_enemy_in_front = False
    start_rank = rank + sign
    end_rank = 8 if color == chess.WHITE else -1

    for r in range(start_rank, end_rank, sign):
        front_sq = chess.square(file, r)
        front_piece = board.piece_at(front_sq)
        if (
            front_piece
            and front_piece.color == enemy_color
            and front_piece.piece_type == chess.PAWN
        ):
            has_enemy_in_front = True
            break

    if not has_enemy_in_front:
        return 0

    # 3. Kiểm tra có quân đồng minh phía sau không
    start_rank = rank - sign
    end_rank = -1 if color == chess.WHITE else 8

    for r in range(start_rank, end_rank, -sign):
        back_sq = chess.square(file, r)
        back_piece = board.piece_at(back_sq)
        if (
            back_piece
            and back_piece.color == color
            and back_piece.piece_type == chess.PAWN
        ):
            return 1  # Có quân đồng minh phía sau

    return 0


def phalanx(board, square):
    """
    Kiểm tra xem Tốt ở ô `square` có tạo thành Phalanx (hàng ngang) không.
    Phalanx xảy ra khi một Tốt có đồng đội ngay bên trái hoặc bên phải cùng rank.
    """
    piece = board.piece_at(square)
    if not piece or piece.piece_type != chess.PAWN:
        return 0

    file = chess.square_file(square)
    rank = chess.square_rank(square)
    color = piece.color

    # Kiểm tra ô bên trái cùng rank
    if file > 0:
        left_square = chess.square(file - 1, rank)
        left_piece = board.piece_at(left_square)
        if (
            left_piece
            and left_piece.piece_type == chess.PAWN
            and left_piece.color == color
        ):
            return 1

    # Kiểm tra ô bên phải cùng rank
    if file < 7:
        right_square = chess.square(file + 1, rank)
        right_piece = board.piece_at(right_square)
        if (
            right_piece
            and right_piece.piece_type == chess.PAWN
            and right_piece.color == color
        ):
            return 1

    return 0


def supported(board, square):
    """
    Kiểm tra xem Tốt ở ô `square` có được hỗ trợ bởi Tốt khác không.
    Một Tốt được coi là hỗ trợ nếu có đồng minh ở phía sau chéo trái hoặc phải.
    Trả về 0 (không được hỗ trợ), 1 (hỗ trợ một bên), hoặc 2 (hỗ trợ cả hai bên).
    """
    piece = board.piece_at(square)
    if not piece or piece.piece_type != chess.PAWN:
        return 0

    file = chess.square_file(square)
    rank = chess.square_rank(square)
    color = piece.color
    sign = 1 if color == chess.WHITE else -1

    count = 0
    if rank < 2 or rank > 6:
        return 0

    # Kiểm tra chéo trái
    if file > 0:
        left_under = chess.square(file - 1, rank - sign)
        p = board.piece_at(left_under)
        if p and p.piece_type == chess.PAWN and p.color == color:
            count += 1

    # Kiểm tra chéo phải
    if file < 7:
        right_under = chess.square(file + 1, rank - sign)
        p = board.piece_at(right_under)
        if p and p.piece_type == chess.PAWN and p.color == color:
            count += 1

    return count


def connected(board, square):
    """
    Kiểm tra xem Tốt ở ô `square` có được kết nối (connected) không.
    Một Tốt được coi là connected nếu:
    - Có đồng minh hỗ trợ từ chéo sau (supported) hoặc
    - Đứng ngang hàng cùng với một đồng minh khác (phalanx).
    """
    if not board.piece_at(square):
        return 0

    if supported(board, square) or phalanx(board, square):
        return 1

    return 0


def opposed(board, square):
    """
    Kiểm tra xem Tốt ở ô square có bị opposed (bị đối đầu trực tiếp bởi Tốt đối phương) hay không.
    """
    piece = board.piece_at(square)
    if not piece or piece.piece_type != chess.PAWN:
        return 0

    file = chess.square_file(square)
    rank = chess.square_rank(square)

    color = piece.color
    enemy_color = not color
    sign = 1 if color == chess.WHITE else -1
    start = rank + sign
    end = 8 if sign == 1 else -1

    # Trắng tiến lên => kiểm tra các ô phía trước
    # Đen tiến xuống => kiểm tra các ô phía sau
    for r in range(start, end, sign):
        front_sq = chess.square(file, r)
        enemy = board.piece_at(front_sq)
        if enemy and enemy.piece_type == chess.PAWN and enemy.color == enemy_color:
            return 1

    return 0


def connected_bonus(board, square):
    """
    Tính điểm thưởng cho Tốt được kết nối (connected).
    Dựa vào:
    - Rank hiện tại.
    - Các yếu tố: supported, phalanx, opposed.
    - Nếu không connected thì trả 0.
    """
    if not board.piece_at(square):
        return 0

    if not connected(board, square):
        return 0

    piece = board.piece_at(square)
    color = piece.color
    rank = chess.square_rank(square)

    # Seed bảng theo rank (bắt đầu từ rank 1)
    seed = [0, 7, 8, 12, 29, 48, 86]

    # Phân biệt hướng
    if color == chess.BLACK:
        rank = 7 - rank  # Lật rank lại cho đen (do bên stockfish là từ trên xuống)

    op = opposed(board, square)
    ph = phalanx(board, square)
    su = supported(board, square)

    bonus = seed[rank] * (2 + ph - op) + 21 * su

    return bonus


def weak_unopposed_pawn(board, square):
    """
    Kiểm tra xem Tốt ở ô square có là weak unopposed pawn không:
    - Không bị đối đầu (opposed == 0)
    - Và bị cô lập (isolated) hoặc tụt hậu (backward)
    """
    piece = board.piece_at(square)
    if not piece or piece.piece_type != chess.PAWN:
        return 0

    if opposed(board, square):
        return 0

    if isolated(board, square):
        return 1
    elif backward(board, square):
        return 1

    return 0


def blocked(board, square):
    """
    Trả về:
        2 nếu tốt ở hàng 6 (WHITE) hoặc hàng 3 (BLACK) bị chặn bởi tốt địch ngay phía trước
        1 nếu tốt ở hàng 5 (WHITE) hoặc hàng 4 (BLACK) bị chặn tương tự
        0 nếu không bị chặn hoặc không thuộc các hàng trên
    """
    piece = board.piece_at(square)
    if not piece or piece.piece_type != chess.PAWN:
        return 0

    file = chess.square_file(square)
    rank = chess.square_rank(square)
    color = piece.color
    sign = 1 if color == chess.WHITE else -1
    if rank in [3 + sign, 4 + sign]:  # hàng 5 và 6
        front_square = chess.square(file, rank + sign)
        blocker = board.piece_at(front_square)
        if (
            blocker
            and blocker.color == (not color)
            and blocker.piece_type == chess.PAWN
        ):
            return rank - 3 if color == chess.WHITE else 4 - rank

    return 0


def weak_lever(board, square):
    """
    Trả về 1 nếu tốt ở 'square' bị 'weak lever':
    - Bị tấn công bởi 2 tốt địch từ phía TRƯỚC (chéo)
    - Không có tốt đồng minh ở phía SAU (chéo)
    """
    piece = board.piece_at(square)
    if not piece or piece.piece_type != chess.PAWN:
        return 0

    color = piece.color
    enemy_color = not color
    file = chess.square_file(square)
    rank = chess.square_rank(square)
    sign = 1 if color == chess.WHITE else -1

    # Tốt địch tấn công từ phía trước
    enemies = []
    for df in [-1, 1]:
        f, r = file + df, rank + sign
        if 0 <= f <= 7 and 0 <= r <= 7:
            p = board.piece_at(chess.square(f, r))
            enemies.append(p and p.piece_type == chess.PAWN and p.color == enemy_color)
    if not all(enemies):
        return 0

    # Tốt đồng minh ở phía sau (có thì thoát)
    for df in [-1, 1]:
        f, r = file + df, rank - sign
        if 0 <= f <= 7 and 0 <= r <= 7:
            p = board.piece_at(chess.square(f, r))
            if p and p.piece_type == chess.PAWN and p.color == color:
                return 0

    return 1
