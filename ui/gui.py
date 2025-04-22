import pygame
import os

class GUI:
    def __init__(self, screen, board, player_is_white):
        self.screen = screen
        self.board = board
        self.tile_size = 75  # Kích thước mỗi ô cờ
        self.piece_images = {}
        self.player_is_white = player_is_white  # is_flipped: True nếu người chơi đang ở phía trên (cầm quân đen), để lật bàn cờ xuống dướ
        self.load_images()
        self.last_move = None

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
    
    def gui_coords(self, row):
        """
        Chuyển row bàn cờ (0–7) thành vị trí để vẽ GUI.
        Nếu is_flipped=True (người chơi cầm đen) → đảo chiều vẽ
        """
        return (7 - row) if self.player_is_white else row

    def draw_board(self):
        """
        Vẽ bàn cờ 8x8, trắng và đen xen kẽ.
        Sau khi vẽ từng ô → vẽ thêm viền đen mỏng.
        """
        colors = [(240, 217, 181), (181, 136, 99)]  # Màu sáng và tối
        for row in range(8):
            for col in range(8):
                draw_row = 7 - row  # ✅ Đảo hàng để vẽ từ dưới lên
                color = colors[(row + col) % 2]
                rect = pygame.Rect(col * self.tile_size, draw_row * self.tile_size, self.tile_size, self.tile_size)

                # Vẽ ô nền
                pygame.draw.rect(self.screen, color, rect)

    def highlight_last_move(self):
        if not self.last_move:
            return

        from_row, from_col, to_row, to_col = self.last_move
        highlight_color = (255, 255, 153)

        for row, col in [(from_row, from_col), (to_row, to_col)]:
            draw_row = self.gui_coords(row)
            x = col * self.tile_size
            y = draw_row * self.tile_size

            # Tạo 1 surface trong suốt để vẽ highlight mờ
            highlight_surface = pygame.Surface((self.tile_size, self.tile_size))
            highlight_surface.set_alpha(100)  # Độ mờ (0 là trong suốt, 255 là đậm)
            highlight_surface.fill(highlight_color)

            self.screen.blit(highlight_surface, (x, y))

    def draw_pieces(self):
        """
        Dựa trên board.positions để vẽ quân cờ đúng vị trí.
        """
        for position, piece_info in self.board.positions.items():
            color, piece = piece_info
            image = self.piece_images.get(f"{color}{piece}")
            if image:
                row, col = position
                draw_row = self.gui_coords(row)  # ✅ Đảo hàng để vẽ đúng chiều
                x = col * self.tile_size + (self.tile_size - image.get_width()) // 2
                y = draw_row * self.tile_size + (self.tile_size - image.get_height()) // 2
                self.screen.blit(image, (x, y))

    def draw_highlights(self, squares):
        """
        Vẽ các ô nước đi hợp lệ:
        - Chấm tròn nhỏ nếu là ô trống
        - Vòng tròn nếu là ô có quân địch
        """
        for row, col in squares:
            draw_row = self.gui_coords(row) # ✅ Đảo hàng
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
        self.highlight_last_move()
        self.draw_pieces()
        if highlighted_square:
            self.draw_highlights(highlighted_square)
        pygame.display.flip()
    
    def handle_promotion_menu(self, mouse_pos):
        """
        Hiển thị menu chọn quân khi phong tốt (và xử lý chọn).
        """
        print("👑 Hiển thị menu phong tốt...")
        menu_rects = []
        choices = ['q', 'r', 'b', 'n']
        base_x, base_y = 250, 150

        for i, code in enumerate(choices):
            rect = pygame.Rect(base_x, base_y + i * 80, 75, 75)
            print(f"🟦 Vẽ ô {code.upper()} tại {rect}")
            pygame.draw.rect(self.screen, (220, 220, 220), rect)
            pygame.draw.rect(self.screen, (0, 0, 0), rect, 2)
            piece_name = {'q': 'queen', 'r': 'rook', 'b': 'bishop', 'n': 'knight'}[code]
            image = self.piece_images.get(f"white{piece_name}")
            if image:
                self.screen.blit(image, (base_x, base_y + i * 80))
            menu_rects.append((rect, code))

        pygame.display.flip()

        for rect, code in menu_rects:
            if rect.collidepoint(mouse_pos):
                print(f"✅ Click trúng {code.upper()} → chọn phong")
                return code

        print("❌ Click ngoài menu phong tốt")
        return None


    def draw_promotion_overlay(self):
        """
        Vẽ lại popup phong tốt (dùng khi đang chờ chọn quân).
        """
        choices = ['q', 'r', 'b', 'n']
        base_x, base_y = 250, 150

        for i, code in enumerate(choices):
            rect = pygame.Rect(base_x, base_y + i * 80, 75, 75)
            pygame.draw.rect(self.screen, (220, 220, 220), rect)
            pygame.draw.rect(self.screen, (0, 0, 0), rect, 2)
            piece_name = {'q': 'queen', 'r': 'rook', 'b': 'bishop', 'n': 'knight'}[code]
            image = self.piece_images.get(f"white{piece_name}")
            if image:
                self.screen.blit(image, (base_x, base_y + i * 80))

