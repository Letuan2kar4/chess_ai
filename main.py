# main.py
import random
import pygame
from models.board_model import ChessBoard
from ui.gui import GUI
from src.chess_controller import GameController
from ui.menu import show_main_menu

def main():
    while True:
        choice = show_main_menu()
        if choice == "QUIT":
            break
        elif choice == "PLAY":
            start_game()

def start_game():
    pygame.init()
    # Khởi tạo cửa sổ game (ví dụ 600x600 pixel)
    screen = pygame.display.set_mode((600, 600))
    pygame.display.set_caption("Tuấn Lê 2kar4 và Cờ vua")
    
    # Khởi tạo object bàn cờ; bạn cần định nghĩa lớp ChessBoard trong models/board_model.py
    board = ChessBoard()  
    # Ví dụ: board.positions là một dict chứa thông tin vị trí quân cờ, dạng {(row, col): (color, piece)}
    # VD: {(0, 0): ("white", "rook"), (0, 1): ("white", "knight"), ...}
     # 🎮 Random vai trò: True = người cầm trắng, False = người cầm đen
    player_is_white = random.choice([True, False])
    print("Người chơi cầm", "trắng" if player_is_white else "đen")
    
    gui = GUI(screen, board, player_is_white)
    controller = GameController(board, gui, player_is_white)
    
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
        if controller.awaiting_promotion_choice:
            gui.draw_promotion_overlay()

        pygame.display.flip()  # Cập nhật màn hình
        
        clock.tick(60)  # Giới hạn 60 FPS
    
    pygame.quit()
     

if __name__ == '__main__':
    main()
