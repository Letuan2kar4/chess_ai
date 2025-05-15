import chess


def eval_pieces(board, phase):
    return eval_pieces_mg(board) if phase == "mg" else eval_pieces_eg(board)


def eval_pieces_mg(board):
    """
    Đánh giá đặc trưng của quân NBRQ trong giai đoạn middle game.
    Trả về tổng điểm cho cả hai bên: trắng dương, đen âm.
    """
    total = 0
    for square, piece in board.piece_map().items():
        if piece.piece_type not in (
            chess.KNIGHT,
            chess.BISHOP,
            chess.ROOK,
            chess.QUEEN,
        ):
            continue
        rank = chess.square_rank(square)
        file = chess.square_file(square)
        color = piece.color
        sign = 1 if color == chess.WHITE else -1

        v = 0
        v += (
            sign
            * [0, 25, -5, 24, 45][outpost_total(board, piece, color, sign, rank, file)]
        )
        v += sign * 14 * minor_behind_pawn(board, piece, color, sign, rank, file)
        v -= sign * 2 * bishop_pawns(board, piece, color, sign, rank, file)
        v -= sign * 3 * bishop_xray_pawns(board, piece, color, rank, file)
        v += sign * 4 * rook_on_queen_file(board, piece, file)
        v += sign * 12 * rook_on_king_ring(board, piece, color, rank, file)
        v += sign * 19 * bishop_on_king_ring(board, piece, color, rank, file)
        v += sign * [0, 15, 38][rook_on_file(board, piece, color, file)]
        v -= (
            sign
            * trapped_rook(board, piece, color, rank, file)
            * 44
            * (
                1
                if (
                    board.has_castling_rights(chess.WHITE)
                    or board.has_castling_rights(chess.BLACK)
                )
                else 2
            )
        )
        v -= sign * 45 * weak_queen(board, piece, color, rank, file)
        v -= sign * 1 * queen_infiltration(board, piece, color, sign, rank, file)

        if piece.piece_type == chess.KNIGHT:
            v -= sign * 6 * king_protector(board, piece, color, rank, file)
        else:
            v -= sign * 4 * king_protector(board, piece, color, rank, file)

        v += sign * 36 * long_diagonal_bishop(board, piece, rank, file)

        total += v

    return total


def eval_pieces_eg(board):
    """
    Đánh giá đặc trưng của quân NBRQ trong giai đoạn endgame.
    Trả về tổng điểm cho cả hai bên: trắng dương, đen âm.
    """
    total = 0
    for square, piece in board.piece_map().items():
        if piece.piece_type not in (
            chess.KNIGHT,
            chess.BISHOP,
            chess.ROOK,
            chess.QUEEN,
        ):
            continue

        rank = chess.square_rank(square)
        file = chess.square_file(square)
        color = piece.color
        sign = 1 if color == chess.WHITE else -1

        v = 0
        # Outpost (EG)
        v += (
            sign
            * [0, 17, 29, 18, 29][outpost_total(board, piece, color, sign, rank, file)]
        )
        # Minor behind pawn
        v += sign * 2 * minor_behind_pawn(board, piece, color, sign, rank, file)
        # Bishop pawns
        v -= sign * 5 * bishop_pawns(board, piece, color, sign, rank, file)
        # Bishop xray pawns
        v -= sign * 4 * bishop_xray_pawns(board, piece, color, rank, file)
        # Rook on queen file
        v += sign * 8 * rook_on_queen_file(board, piece, file)
        # Rook on file (EG)
        v += sign * [0, 5, 23][rook_on_file(board, piece, color, file)]
        # Trapped rook
        v -= (
            sign
            * trapped_rook(board, piece, color, rank, file)
            * 10
            * (
                1
                if (
                    board.has_castling_rights(chess.WHITE)
                    or board.has_castling_rights(chess.BLACK)
                )
                else 2
            )
        )
        # Weak queen
        v -= sign * 12 * weak_queen(board, piece, color, rank, file)
        # Queen infiltration
        v += sign * 11 * queen_infiltration(board, piece, color, sign, rank, file)
        # King protector
        v -= sign * 7 * king_protector(board, piece, color, rank, file)

        total += v

    return total


def outpost_total(board, piece, color, sign, rank, file):
    """
    Điểm thưởng trong giai đoạn trung cuộc và tàn cuộc cho các vị trí outpost của mã và tượng,
    đặc biệt cao hơn nếu quân outpost được tốt đồng minh bảo vệ.

    Trả về:
    0: Không phải mã hoặc tượng, hoặc không phải outpost, hoặc không đạt điều kiện đánh giá
    1: Mã có thể nhảy đến một ô outpost hợp lệ
    2: Mã đang ở outpost nằm ở các cột biên, không bị đe dọa, và ít quân địch gần
    3: Tượng ở vị trí outpost hợp lệ
    4: Mã ở outpost thuộc các cột trung tâm (c đến f)
    """
    if piece.piece_type not in (chess.KNIGHT, chess.BISHOP):
        return 0

    is_knight = piece.piece_type == chess.KNIGHT

    if not outpost(board, piece, color, sign, rank, file):
        if not is_knight:
            return 0
        return reachable_outpost(board, piece, color, sign, rank, file)

    if is_knight and (file < 2 or file > 5):
        enemy_threatens = False
        enemy_count = 0

        for x in range(8):
            for y in range(8):
                sq = chess.square(x, y)
                enemy_piece = board.piece_at(sq)
                if enemy_piece and enemy_piece.color != color:
                    # Check if enemy piece can attack knight's position
                    if (abs(file - x) == 2 and abs(rank - y) == 1) or (
                        abs(file - x) == 1 and abs(rank - y) == 2
                    ):
                        enemy_threatens = True
                    # Count enemies in the same half of the board
                    if (x < 4 and file < 4) or (x >= 4 and file >= 4):
                        enemy_count += 1

        if not enemy_threatens and enemy_count <= 1:
            return 2

    return 4 if is_knight else 3


def reachable_outpost(board, piece, color, sign, rank, file):
    """
    Kiểm tra xem quân mã có thể nhảy đến một ô outpost hợp lệ hay không.
    Không xét bảo vệ, chỉ quan tâm có nước nhảy đến ô được tính là outpost.

    Trả về:
    0: Không thể đến outpost nào
    1: Có thể đến ít nhất một ô outpost
    """
    if piece.piece_type != chess.KNIGHT:
        return 0

    knight_moves = [
        (2, 1),
        (1, 2),
        (-1, 2),
        (-2, 1),
        (-2, -1),
        (-1, -2),
        (1, -2),
        (2, -1),
    ]

    for dx, dy in knight_moves:
        tx, ty = file + dx, rank + dy
        if 0 <= tx <= 7 and 0 <= ty <= 7:
            target_square = chess.square(tx, ty)

            # Chỉ cần trống và là ô outpost hợp lệ
            target_piece = board.piece_at(target_square)
            if target_piece and target_piece.color == color:
                continue  # quân mình cản
            if outpost_square(board, color, sign, tx, ty):
                return 1

    return 0


def outpost(board, piece, color, sign, rank, file):
    """
    Đánh giá tổng số quân cờ có thể tạo thành outpost tại ô square.
    """
    if piece.piece_type not in (chess.KNIGHT, chess.BISHOP):
        return 0
    if not outpost_square(board, color, sign, file, rank):
        return 0
    return 1


def outpost_square(board, color, sign, file, rank):
    """
    Kiển tra 2 ô chéo liền sau có tốt đồng minh bảo kê không
    và 2 cột 2 bên có tốt địch không.
    Nếu có bảo kê và cột nào không có tốt địch thì trả về True.
    """
    if color == chess.WHITE:
        if rank < 3 or rank > 5:
            return 0
    else:
        if rank < 2 or rank > 4:
            return 0
    enemy_color = not color
    for r in range(rank + sign, 3 + sign * 3, sign):
        if file > 0:
            left_square = chess.square(file - 1, r)
            if (
                board.piece_at(left_square)
                and (board.piece_at(left_square).piece_type == chess.PAWN)
                and (board.piece_at(left_square).color == enemy_color)
            ):
                return 0
        if file < 7:
            right_square = chess.square(file + 1, r)
            if (
                board.piece_at(right_square)
                and board.piece_at(right_square).piece_type == chess.PAWN
                and board.piece_at(right_square).color == enemy_color
            ):
                return 0

    # kiểm tra có tốt đồng minh ở ô chéo liền sau bảo kê không

    if file > 0:
        left_square = chess.square(file - 1, rank - sign)
        if (
            board.piece_at(left_square)
            and (board.piece_at(left_square).piece_type == chess.PAWN)
            and (board.piece_at(left_square).color == color)
        ):
            return 1
    if file < 7:
        right_square = chess.square(file + 1, rank - sign)
        if (
            board.piece_at(right_square)
            and board.piece_at(right_square).piece_type == chess.PAWN
            and board.piece_at(right_square).color == color
        ):
            return 1
    return 0


def minor_behind_pawn(board, piece, color, sign, rank, file):
    """
    Đánh giá quân mã hoặc tượng nằm sau tốt đồng minh.
    Trả về 1 nếu quân cờ nằm sau tốt đồng minh, 0 nếu không.
    """
    if piece.piece_type not in (chess.KNIGHT, chess.BISHOP):
        return 0
    # Prevent out-of-bounds access
    new_rank = rank + sign
    if 0 <= file <= 7 and 0 <= new_rank <= 7:
        pawn_square = chess.square(file, new_rank)
        pawn_piece = board.piece_at(pawn_square)
        if pawn_piece and pawn_piece.piece_type == chess.PAWN and pawn_piece.color == color:
            return 1
    return 0


def bishop_pawns(board, piece, color, sign, rank, file):
    """
    Đánh giá số lượng tốt ảnh hưởng đến hoạt động của tượng,
    đồng thời debug in ra nội dung:
    - v       = số pawn cùng phe cùng màu ô
    - blocked = số pawn cùng phe ở cột c–f bị chặn
    - support = True/False (có pawn bảo kê chéo sau không)
    """
    if not piece or piece.piece_type != chess.BISHOP:
        return 0

    # tính v và blocked
    c = (file + rank) % 2
    v = 0
    blocked = 0
    for x in range(8):
        for y in range(8):
            sq = chess.square(x, y)
            p = board.piece_at(sq)
            if not p or p.piece_type != chess.PAWN or p.color != color:
                continue

            if (x + y) % 2 == c:
                v += 1

            if 1 <= x <= 6:
                ahead_rank = y + sign
                if 0 <= ahead_rank <= 7:
                    ahead_sq = chess.square(x, ahead_rank)
                    if board.piece_at(ahead_sq):
                        blocked += 1

    # kiểm tra support
    support = False
    back_rank = rank - sign
    for df in (-1, +1):
        f = file + df
        if 0 <= f < 8 and 0 <= back_rank < 8:
            sq = chess.square(f, back_rank)
            p = board.piece_at(sq)
            if p and p.piece_type == chess.PAWN and p.color == color:
                support = True
                break

    return v * (blocked + (0 if support else 1))


def rook_on_file(board, piece, color, file):
    """
    Đánh giá cột xe đang đứng:
    - 2: cột hoàn toàn mở (không có pawn nào ở cột đó)
    - 1: cột nửa mở (chỉ có pawn địch, không có pawn đồng minh)
    - 0: cột bị chặn (có pawn đồng minh)
    """
    # Chỉ tính khi đó là Xe của phe đang xét
    if not piece or piece.piece_type != chess.ROOK or piece.color != color:
        return 0

    open_file = 1
    for y in range(8):
        sq = chess.square(file, y)
        p = board.piece_at(sq)
        if p and p.piece_type == chess.PAWN:
            if p.color == color:
                # Có pawn đồng minh trên file → cột bị chặn
                return 0
            else:
                # Pawn địch → cột chỉ còn là semi-open
                open_file = 0

    return open_file + 1


def trapped_rook(board, piece, color, rank, file):
    """
    Trả về 1 nếu Rook của bên `color` trên ô (file, rank) đang bị giam:
    - Không đứng trên cột semi-open/open (rook_on_file == 0)
    - Có ≤ 3 nước đi hợp lệ (mobility ≤ 3)
    - Nằm cùng nửa bàn với vua (không còn đường chạy về hộ tống)
    Ngược lại trả về 0.
    """
    # 1) Chỉ xét Rook cùng màu
    if not piece or piece.piece_type != chess.ROOK or piece.color != color:
        return 0

    # 2) Nếu đang trên cột semi-open/open → không trapped
    if rook_on_file(board, piece, color, file) > 0:
        return 0

    # 3) Đếm số nước đi hợp lệ của xe
    mobility_count = 0
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]  # up, down, right, left

    for dx, dy in directions:
        next_file, next_rank = file, rank
        while True:
            next_file += dx
            next_rank += dy
            if not (0 <= next_file <= 7 and 0 <= next_rank <= 7):
                break

            next_square = chess.square(next_file, next_rank)
            piece_at = board.piece_at(next_square)

            if piece_at is None:
                mobility_count += 1
            else:
                if piece_at.color != color:
                    mobility_count += 1
                break

    if mobility_count > 3:
        return 0

    # 4) Lấy file của vua cùng màu
    king_sq = board.king(color)
    if king_sq is None:
        return 0
    king_file = chess.square_file(king_sq)

    # 5) Nếu Rook và Vua ở hai nửa bàn khác nhau → không trapped
    #    (cột 0–3 là nửa trái, 4–7 là nửa phải)
    if (king_file < 4) != (file < king_file):
        return 0

    # 6) Thỏa các điều kiện → Rook bị giam
    return 1


def weak_queen(board, piece, color, rank, file):
    if not piece or piece.piece_type != chess.QUEEN:
        return 0

    enemy_color = not color

    directions = [
        (-1, -1),
        (0, -1),
        (1, -1),
        (-1, 0),
        (1, 0),
        (-1, 1),
        (0, 1),
        (1, 1),
    ]

    for dx, dy in directions:
        count = 0
        for dist in range(1, 8):
            x = file + dx * dist
            y = rank + dy * dist
            if not (0 <= x <= 7 and 0 <= y <= 7):
                break

            sq = chess.square(x, y)
            piece_at_sq = board.piece_at(sq)

            if piece_at_sq:
                if piece_at_sq.color == enemy_color:
                    if (
                        piece_at_sq.piece_type == chess.ROOK
                        and (dx == 0 or dy == 0)
                        and count == 1
                    ):
                        return 1
                    if (
                        piece_at_sq.piece_type == chess.BISHOP
                        and (dx != 0 and dy != 0)
                        and count == 1
                    ):
                        return 1
                count += 1
    return 0


def long_diagonal_bishop(board, piece, rank, file):
    if not piece or piece.piece_type != chess.BISHOP:
        return 0

    # Phải nằm trên 1 trong 2 đường chéo chính
    if file != rank and file + rank != 7:
        return 0
    x1 = file
    if min(x1, 7 - x1) > 2:
        return 0
    # Xác định điểm trung tâm cần thấy dựa vào đường chéo
    if file == rank:
        target = (4, 4) if file < 4 else (3, 3)
    else:
        target = (3, 4) if file > 4 else (4, 3)

    dx = 1 if file < target[0] else -1
    dy = 1 if rank < target[1] else -1

    x, y = file + dx, rank + dy
    while (x, y) != target:
        if not (0 <= x <= 7 and 0 <= y <= 7):
            return 0
        sq = chess.square(x, y)
        piece_at = board.piece_at(sq)
        if piece_at and piece_at.piece_type == chess.PAWN:
            return 0
        x += dx
        y += dy

    # Nếu tới target và không bị chặn
    return 1


def rook_on_queen_file(board, piece, file):
    """
    Trả về 1 nếu quân Xe (Rook) đứng cùng cột với bất kỳ quân Hậu (Queen) nào.
    Ngược lại trả về 0.
    """
    if not piece or piece.piece_type != chess.ROOK:
        return 0

    for r in range(8):
        sq = chess.square(file, r)
        p = board.piece_at(sq)
        if p and p.piece_type == chess.QUEEN:
            return 1

    return 0


def bishop_xray_pawns(board, piece, color, rank, file):
    if not piece or piece.piece_type != chess.BISHOP:
        return 0

    enemy_color = not color
    count = 0

    directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

    for dx, dy in directions:
        x, y = file + dx, rank + dy
        while 0 <= x <= 7 and 0 <= y <= 7:
            sq = chess.square(x, y)
            p = board.piece_at(sq)
            if p:
                if p.piece_type == chess.PAWN and p.color == enemy_color:
                    count += 1
            x += dx
            y += dy

    return count


def rook_on_king_ring(board, piece, color, rank, file):
    """
    Trả về 1 nếu quân xe đang đứng cùng cột với một ô thuộc King Ring của vua địch,
    không chiếu vua, và có một quân cản (không phải R, Q, K) nằm giữa xe và vua,
    trong phạm vi các rank nhất định.
    Ngược lại trả về 0.
    """
    if not piece or piece.piece_type != chess.ROOK or piece.color != color:
        return 0

    enemy_color = not color

    # 1) Nếu xe đang chiếu vua địch → không tính điểm
    if board.is_check():
        return 0

    # 2) Lấy vị trí vua địch
    king_square = board.king(enemy_color)
    if king_square is None:
        return 0

    king_rank = chess.square_rank(king_square)
    king_file = chess.square_file(king_square)

    # 3) Nếu không cùng cột hoặc cột lệch >1 (không thuộc ring) → loại
    if abs(king_file - file) > 1:
        return 0

    # 4) Duyệt từ rook đến king, tính hướng đi và vùng hợp lệ
    step = 1 if rank < king_rank else -1

    # Quân cản chỉ tính nếu nó nằm trong các rank này:
    valid_ranks = set(range(0, 5)) if step == 1 else set(range(3, 8))

    for r in range(rank + step, king_rank, step):
        sq = chess.square(file, r)
        if r not in valid_ranks:
            continue
        blocker = board.piece_at(sq)
        if blocker:
            if blocker.piece_type not in (chess.ROOK, chess.QUEEN, chess.KING):
                return 1
            else:
                break  # nếu cản bởi R/Q/K thì loại
    return 0


def bishop_on_king_ring(board, piece, color, rank, file):
    if not piece or piece.piece_type != chess.BISHOP or piece.color != color:
        return 0

    enemy_color = not color
    king_sq = board.king(enemy_color)
    if king_sq is None:
        return 0

    king_file = chess.square_file(king_sq)
    king_rank = chess.square_rank(king_sq)

    directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
    for dx, dy in directions:
        x, y = file + dx, rank + dy
        blocker_found = False

        while 0 <= x <= 7 and 0 <= y <= 7:
            sq = chess.square(x, y)

            if abs(x - king_file) <= 1 and abs(y - king_rank) <= 1:
                if blocker_found:
                    return 1
                else:
                    break

            piece_at = board.piece_at(sq)
            if piece_at:
                if blocker_found:
                    break

                if piece_at.piece_type in (chess.QUEEN, chess.PAWN):
                    break

                if board.is_attacked_by(enemy_color, sq):
                    break

                blocker_found = True

            x += dx
            y += dy

    return 0


def queen_infiltration(board, piece, color, sign, rank, file):
    if not piece or piece.piece_type != chess.QUEEN or piece.color != color:
        return 0

    if (color == chess.WHITE and rank < 4) or (color == chess.BLACK and rank > 3):
        return 0

    enemy_color = not color

    for df in [-1, 1]:
        f = file + df
        r = rank + sign
        while 0 <= f < 8 and 0 <= r < 8:
            sq = chess.square(f, r)
            p = board.piece_at(sq)
            if p and p.piece_type == chess.PAWN and p.color == enemy_color:
                return 0
            r += sign

    return 1


def king_protector(board, piece, color, rank, file):
    """
    Trả về khoảng cách Chebyshev từ mã (N) hoặc tượng (B) đến vua cùng màu.
    Các quân khác sẽ trả về 0.
    """
    if not piece or piece.piece_type not in (chess.KNIGHT, chess.BISHOP):
        return 0

    king_sq = board.king(color)
    if king_sq is None:
        return 0

    king_rank = chess.square_rank(king_sq)
    king_file = chess.square_file(king_sq)

    return max(abs(rank - king_rank), abs(file - king_file))
