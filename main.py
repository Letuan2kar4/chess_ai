# main.py
import pygame
from models.board_model import ChessBoard
from ui.gui import GUI
from src.chess_controller import GameController

def main():
    pygame.init()
    # Khởi tạo cửa sổ game (ví dụ 600x600 pixel)
    screen = pygame.display.set_mode((600, 600))
    pygame.display.set_caption("Tuấn Lê 2kar4 và Cờ vua")
    
    # Khởi tạo object bàn cờ; bạn cần định nghĩa lớp ChessBoard trong models/board_model.py
    board = ChessBoard()  
    # Ví dụ: board.positions là một dict chứa thông tin vị trí quân cờ, dạng {(row, col): (color, piece)}
    # VD: {(0, 0): ("white", "rook"), (0, 1): ("white", "knight"), ...}
    controller = GameController(board)
    # Khởi tạo giao diện GUI, truyền cả screen và board vào (để vẽ dựa trên trạng thái bàn cờ)
    gui = GUI(screen, board)
    
    clock = pygame.time.Clock()
    running = True
    while running:
        # Xử lý sự kiện
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # Bạn có thể thêm xử lý sự kiện chuột hoặc bàn phím ở đây (ví dụ chọn quân, di chuyển, …)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    controller.handle_click(mouse_pos)
        # Cập nhật logic game (nếu có) ở đây
        controller.ai_move_if_needed()
        # Vẽ giao diện
        gui.render(controller.highlighted_square)
        pygame.display.flip()  # Cập nhật màn hình
        
        clock.tick(60)  # Giới hạn 60 FPS
    
    pygame.quit()
     

if __name__ == '__main__':
    main()
