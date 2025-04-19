import chess
from engine.minimax import get_best_move_alpha_beta

class GameController:
    def __init__(self, board):
        self.board = board 
        self.selected_square = None
        self.highlighted_square = []

    def handle_click(self, mouse_pos):
        row = 7 - (mouse_pos[1] // 75)
        col = mouse_pos[0] // 75
        clicked_square = (row, col)
        print(f"✅ Clicked at pixel {mouse_pos} → square {clicked_square}")

        # Nếu click trùng ô đã chọn → huỷ chọn
        if self.selected_square == clicked_square:
            print("❌ Click trùng ô đã chọn → hủy chọn")
            self.selected_square = None
            self.highlighted_square = []
            return

        # Nếu chưa chọn quân nào
        if self.selected_square is None:
            piece = self.board.positions.get(clicked_square)
            print("📦 Quân tại ô:", piece)

            if piece and piece[0] == 'white':
                legal_targets = self.get_legal_targets(clicked_square)
                if legal_targets:
                    self.selected_square = clicked_square
                    self.highlighted_square = legal_targets
                    print(f" ✴ Có thể đi: {legal_targets}")
                else:
                    print("🚫 Quân trắng này không có nước đi hợp lệ")
            else:
                print("🚫 Không phải quân trắng hoặc không có quân")

        # Nếu đã chọn quân → xử lý đi quân
        else:
            move_uci = self.convert_to_uci(self.selected_square, clicked_square)
            print("📝 Thử thực hiện nước:", move_uci)

            try:
                move = chess.Move.from_uci(move_uci)
            except Exception as e:
                print("❌ Lỗi khi tạo move từ uci:", move_uci, e)
                self.selected_square = None
                self.highlighted_square = []
                return

            if move in self.board.get_board().legal_moves:
                print("🔄 Di chuyển:", move.uci())
                self.board.make_move(move)
                self.selected_square = None
                self.highlighted_square = []
            else:
                print("🚫 Nước đi không hợp lệ:", move.uci())

                new_piece = self.board.positions.get(clicked_square)
                if not new_piece or new_piece[0] != 'white':
                    self.selected_square = None
                    self.highlighted_square = []
                else:
                    self.selected_square = clicked_square
                    self.highlighted_square = self.get_legal_targets(clicked_square)

    def get_legal_targets(self, square):
        row, col = square
        from_sq = chess.square(col, row)  # ✅ Không cần đảo nữa vì GUI đã đảo rồi
        print(f"📍 Kiểm tra từ GUI square {square} → internal square index {from_sq}")

        all_moves = list(self.board.get_board().legal_moves)
        print(f"📋 Tổng số nước đi: {len(all_moves)}")
        for move in all_moves:
            print("♟️", move.uci(), f"(from {move.from_square} → to {move.to_square})")

        targets = [
            (chess.square_rank(m.to_square), chess.square_file(m.to_square))  # ✅ Không đảo rank nữa
            for m in all_moves if m.from_square == from_sq
        ]
        print(f"🎯 Các ô đi hợp lệ từ quân ở {square}: {targets}")
        return targets

    def convert_to_uci(self, start, end):
        def to_chess(sq):
            return chr(ord('a') + sq[1]) + str(sq[0] + 1)  # ✅ Không đảo row nữa
        return to_chess(start) + to_chess(end)

    def ai_move_if_needed(self):
        if not self.board.is_player_turn():
            move = get_best_move_alpha_beta(self.board.get_board(), depth=3)
            self.board.make_move(move)
