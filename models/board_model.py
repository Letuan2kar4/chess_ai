import chess

class ChessBoard:
    def __init__(self):
        """
        Khởi tạo bàn cờ:
        - Dùng python-chess để xử lý luật và nước đi.
        - Dùng positions để vẽ GUI (key = (row, col), value = (color, piece)).
        """
        self.board = chess.Board()
        self.positions = {}
        self.setup_board()

    def get_board(self):
        """
        Trả về đối tượng bàn cờ python-chess cho AI và xử lý luật.
        """
        return self.board

    def setup_board(self):
        """
        Khởi tạo self.positions theo logic bàn cờ:
        - Hàng 0 → quân trắng (hàng 1 thực tế)
        - Hàng 7 → quân đen (hàng 8 thực tế)
        """
        white_order = ['rook', 'knight', 'bishop', 'queen', 'king', 'bishop', 'knight', 'rook']
        black_order = ['rook', 'knight', 'bishop', 'queen', 'king', 'bishop', 'knight', 'rook']

        # Trắng ở hàng 0–1
        for col, piece in enumerate(white_order):
            self.positions[(0, col)] = ('white', piece)
        for col in range(8):
            self.positions[(1, col)] = ('white', 'pawn')

        # Đen ở hàng 6–7
        for col, piece in enumerate(black_order):
            self.positions[(7, col)] = ('black', piece)
        for col in range(8):
            self.positions[(6, col)] = ('black', 'pawn')

    def make_move(self, move):
        """
        Di chuyển quân cờ trên bàn cờ thực tế và cập nhật lại self.positions cho GUI.
        """
        self.board.push(move)
        self.update_positions()

    def update_positions(self):
        """
        Cập nhật lại trạng thái self.positions từ python-chess board.
        Đảm bảo khớp với logic row = 0 là hàng 1 (a1–h1).
        """
        self.positions = {}
        board_array = str(self.board).split('\n')  # 8 dòng tương ứng hàng 8 → 1

        for row_idx, row in enumerate(board_array):  # row_idx = 0 (hàng 8), ..., 7 (hàng 1)
            actual_row = 7 - row_idx  # Chuyển về: row 0 = hàng 1
            for col_idx, char in enumerate(row.split()):
                if char == '.':
                    continue
                color = 'white' if char.isupper() else 'black'
                piece_map = {
                    'p': 'pawn', 'r': 'rook', 'n': 'knight',
                    'b': 'bishop', 'q': 'queen', 'k': 'king'
                }
                piece_type = piece_map[char.lower()]
                self.positions[(actual_row, col_idx)] = (color, piece_type)

    def is_player_turn(self):
        """
        Kiểm tra xem có phải lượt trắng (người chơi) không.
        """
        return self.board.turn == chess.WHITE

    def legal_moves(self):
        """
        Trả về danh sách nước đi hợp lệ hiện tại.
        """
        return list(self.board.legal_moves)
