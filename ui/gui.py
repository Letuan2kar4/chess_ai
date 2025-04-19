import pygame
import os

class GUI:
    def __init__(self, screen, board):
        self.screen = screen
        self.board = board
        self.tile_size = 75  # Kích thước mỗi ô cờ
        self.piece_images = {}
        self.load_images()

    def load_images(self):
        """
        Tải ảnh các quân cờ từ thư mục 'assets'.
        Đặt tên theo dạng: whitepawn.png, blackqueen.png,...
        """
        pieces = ['pawn', 'rook', 'knight', 'bishop', 'queen', 'king']
        colors = ['white', 'black']
        for color in colors:
            for piece in pieces:
                path = os.path.join("assets", f"{color}{piece}.png")
                try:
                    image = pygame.image.load(path).convert_alpha()
                    image = pygame.transform.scale(image, (self.tile_size, self.tile_size))
                    self.piece_images[f"{color}{piece}"] = image
                except Exception as e:
                    print(f"Error loading {path}: {e}")

    def draw_board(self):
        """
        Vẽ bàn cờ 8x8, trắng và đen xen kẽ.
        Đảo chiều để quân trắng ở dưới.
        """
        colors = [(240, 217, 181), (181, 136, 99)]  # Màu sáng và tối
        for row in range(8):
            for col in range(8):
                draw_row = 7 - row  # ✅ Đảo hàng để vẽ từ dưới lên
                color = colors[(row + col) % 2]
                rect = pygame.Rect(col * self.tile_size, draw_row * self.tile_size, self.tile_size, self.tile_size)
                pygame.draw.rect(self.screen, color, rect)

    def draw_pieces(self):
        """
        Dựa trên board.positions để vẽ quân cờ đúng vị trí.
        """
        for position, piece_info in self.board.positions.items():
            color, piece = piece_info
            image = self.piece_images.get(f"{color}{piece}")
            if image:
                row, col = position
                draw_row = 7 - row  # ✅ Đảo hàng để vẽ đúng chiều
                self.screen.blit(image, (col * self.tile_size, draw_row * self.tile_size))

    def draw_highlights(self, squares):
        """
        Vẽ các ô nước đi hợp lệ:
        - Chấm tròn nhỏ nếu là ô trống
        - Vòng tròn nếu là ô có quân địch
        """
        for row, col in squares:
            draw_row = 7 - row  # ✅ Đảo hàng
            center_x = col * self.tile_size + self.tile_size // 2
            center_y = draw_row * self.tile_size + self.tile_size // 2

            target_piece = self.board.positions.get((row, col))

            if target_piece is None:
                # Nước đi bình thường → chấm nhỏ
                pygame.draw.circle(
                    self.screen,
                    (160, 160, 160),
                    (center_x, center_y),
                    self.tile_size // 8
                )
            else:
                # Có quân địch → vòng tròn
                pygame.draw.circle(
                    self.screen,
                    (160, 160, 160),
                    (center_x, center_y),
                    self.tile_size // 2 - 5,
                    4  # độ dày đường viền
                )

    def render(self, highlighted_square=None):
        """
        Gọi hàm vẽ tổng: bàn cờ + quân cờ + highlight
        """
        self.draw_board()
        self.draw_pieces()
        if highlighted_square:
            self.draw_highlights(highlighted_square)
        pygame.display.flip()
