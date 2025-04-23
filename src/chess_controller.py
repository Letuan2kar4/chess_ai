import chess
import pygame.mixer
from engine.minimax import get_best_move_alpha_beta

class GameController:
    def __init__(self, board, gui, player_is_white):
        self.board = board
        self.gui = gui
        self.selected_square = None
        self.highlighted_square = []
        self.promotion_pending = None
        self.awaiting_promotion_choice = False
        
        self.player_color = 'white' if player_is_white else 'black'
        self.player_is_white = player_is_white
        self.is_flipped = not player_is_white

        self.last_move_time = 0
        self.ai_move_delay = 1000
        self.ai_move_pending = False if self.player_is_white else True

        pygame.mixer.init()
        self.move_sound = pygame.mixer.Sound("assets/sounds/move-self.mp3")
        self.capture_sound = pygame.mixer.Sound("assets/sounds/capture.mp3")

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
                # Kiểm tra nếu có quân ở ô đích → là nước ăn quân
                is_capture = self.board.get_board().is_capture(move)

                self.board.make_move(move)

                from_row = chess.square_rank(move.from_square)
                from_col = chess.square_file(move.from_square)
                to_row = chess.square_rank(move.to_square)
                to_col = chess.square_file(move.to_square)
                self.gui.last_move = (from_row, from_col, to_row, to_col)

                self.last_move_time = pygame.time.get_ticks()
                self.ai_move_pending = True

                # Phát âm thanh
                if is_capture:
                    self.capture_sound.play()
                else:
                    self.move_sound.play()

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
                    is_capture = self.board.get_board().is_capture(move)
                    self.board.make_move(move)
                    if is_capture:
                        self.capture_sound.play()
                    else:
                        self.move_sound.play()
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
        """Kiểm tra nếu là nước phong tốt CHÍNH XÁC theo màu quân (đen hoặc trắng)"""
        to_row, _ = end
        piece = self.board.positions.get(start)

        if not piece or piece[1] != 'pawn':
            return False

        color = piece[0]

        # Trắng phong ở hàng 7, đen phong ở hàng 0
        if (color == 'white' and to_row != 7) or (color == 'black' and to_row != 0):
            return False

        # Check xem có move hợp lệ dạng phong cấp không
        move_uci = self.convert_to_uci(start, end)
        for suffix in ['q', 'r', 'b', 'n']:
            move = chess.Move.from_uci(move_uci + suffix)
            if move in self.board.get_board().legal_moves:
                return True

        return False



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
        current_time = pygame.time.get_ticks()

        if self.ai_move_pending and self.board.get_board().turn == opponent_turn:
            if current_time - self.last_move_time >= self.ai_move_delay:
                move = get_best_move_alpha_beta(self.board.get_board(), depth = 6)

                self.board.make_move(move)

                from_row = chess.square_rank(move.from_square)
                from_col = chess.square_file(move.from_square)
                to_row = chess.square_rank(move.to_square)
                to_col = chess.square_file(move.to_square)
                self.gui.last_move = (from_row, from_col, to_row, to_col)

                self.last_move_time = current_time
                self.ai_move_pending = False
