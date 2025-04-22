import chess
from engine.minimax import get_best_move_alpha_beta

class GameController:
    def __init__(self, board, gui, player_is_white=True):
        self.board = board
        self.gui = gui
        self.selected_square = None
        self.highlighted_square = []
        self.promotion_pending = None
        self.awaiting_promotion_choice = False
        
        self.player_color = 'white' if player_is_white else 'black'
        self.player_is_white = player_is_white
        self.is_flipped = not player_is_white

    def handle_click(self, mouse_pos):
        # 👑 Nếu đang chờ người chơi chọn quân để phong
        if self.awaiting_promotion_choice:
            self.handle_promotion_click(mouse_pos)
            return

        # 👉 Dịch toạ độ GUI → ô cờ (row, col)
        row = mouse_pos[1] // 75 if self.is_flipped else 7 - (mouse_pos[1] // 75)
        col = mouse_pos[0] // 75
        clicked_square = (row, col)
        print(f"✅ Clicked at pixel {mouse_pos} → square {clicked_square}")

        # 👆 Click lại cùng 1 ô → bỏ chọn
        if self.selected_square == clicked_square:
            self.selected_square = None
            self.highlighted_square = []
            return

        # 🧠 Nếu chưa chọn quân
        if self.selected_square is None:
            piece = self.board.positions.get(clicked_square)
            if piece and piece[0] == self.player_color:
                legal_targets = self.get_legal_targets(clicked_square)
                self.selected_square = clicked_square
                self.highlighted_square = legal_targets
                print(f"✴ Có thể đi: {legal_targets}")

                # 🐞 DEBUG THÊM TOÀN BỘ CÁC NƯỚC ĐI HỢP LỆ
                print("📋 Tất cả nước đi hợp lệ tại thời điểm hiện tại:")
                for move in self.board.get_board().legal_moves:
                    print("♟️", move.uci(), f"(from {move.from_square} to {move.to_square})")

            else:
                print("🚫 Không phải quân bạn hoặc không có quân")


        # 🏹 Nếu đã chọn quân → thử đi đến clicked_square
        else:
            move_uci = self.convert_to_uci(self.selected_square, clicked_square)
            move = chess.Move.from_uci(move_uci)

            if self.is_promotion_move(self.selected_square, clicked_square):
                print("👑 Phát hiện nước đi cần phong tốt → bật menu chọn quân...")
                self.promotion_pending = (self.selected_square, clicked_square)
                self.awaiting_promotion_choice = True
                return
            
            if move in self.board.get_board().legal_moves:
                    self.board.make_move(move)
                    self.selected_square = None
                    self.highlighted_square = []
            else:
                print("🚫 Nước đi không hợp lệ:", move)
                self.selected_square = None
                self.highlighted_square = []

    def handle_promotion_click(self, mouse_pos):
        """Xử lý khi đang chờ chọn quân phong"""
        choice = self.gui.handle_promotion_menu(mouse_pos)
        if choice:
            start, end = self.promotion_pending
            move_uci = self.convert_to_uci(start, end) + choice
            print(f"✅ Đang phong tốt → tạo move {move_uci}")
            try:
                move = chess.Move.from_uci(move_uci)
                if move in self.board.get_board().legal_moves:
                    self.board.make_move(move)
                    print("✅ Phong tốt thành công:", move)
                else:
                    print("❌ Move phong tốt không hợp lệ:", move)
            except Exception as e:
                print("❌ Lỗi khi tạo move phong:", move_uci, e)
        else:
            print("🛑 Click ngoài menu phong tốt → huỷ chọn")

        # Reset sau phong
        self.promotion_pending = None
        self.awaiting_promotion_choice = False
        self.selected_square = None
        self.highlighted_square = []

    def is_promotion_move(self, start, end):
        """Kiểm tra nếu là tốt đi đến hàng cuối"""
        row, _ = end
        piece = self.board.positions.get(start)
        return piece and piece[1] == 'pawn' and (row == 0 or row == 7)

    def get_legal_targets(self, square):
        row, col = square
        from_sq = chess.square(col, row)
        all_moves = list(self.board.get_board().legal_moves)
        return [
            (chess.square_rank(m.to_square), chess.square_file(m.to_square))
            for m in all_moves if m.from_square == from_sq
        ]

    def convert_to_uci(self, start, end):
        def to_chess(sq):
            return chr(ord('a') + sq[1]) + str(sq[0] + 1)
        return to_chess(start) + to_chess(end)

    def ai_move_if_needed(self):
        opponent_turn = chess.BLACK if self.player_color == 'white' else chess.WHITE
        if self.board.get_board().turn == opponent_turn:
            move = get_best_move_alpha_beta(self.board.get_board(), depth=3)
            self.board.make_move(move)
