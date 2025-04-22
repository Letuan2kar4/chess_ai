import pygame

def show_main_menu():
    pygame.init()
    screen = pygame.display.set_mode((600, 600))
    pygame.display.set_caption("Chess Game Menu")

    # Colors
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (128, 128, 128)

    # Button dimensions
    button_width = 200
    button_height = 50
    button_spacing = 20

    # Calculate positions for centered buttons
    screen_center_x = screen.get_width() // 2
    screen_center_y = screen.get_height() // 2

    play_button = pygame.Rect(
        screen_center_x - button_width // 2,
        screen_center_y - button_height - button_spacing // 2,
        button_width,
        button_height
    )

    quit_button = pygame.Rect(
        screen_center_x - button_width // 2,
        screen_center_y + button_spacing // 2,
        button_width,
        button_height
    )

    # Font
    font = pygame.font.Font(None, 36)
    title_font = pygame.font.Font(None, 64)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if play_button.collidepoint(mouse_pos):
                    return "PLAY"
                if quit_button.collidepoint(mouse_pos):
                    return "QUIT"

        # Draw
        screen.fill(WHITE)

        # Draw title
        title_text = title_font.render("Chess Game", True, BLACK)
        title_rect = title_text.get_rect(center=(screen_center_x, 120))
        screen.blit(title_text, title_rect)

        # Draw play button
        pygame.draw.rect(screen, BLACK, play_button)
        play_text = font.render("Play", True, WHITE)
        play_text_rect = play_text.get_rect(center=play_button.center)
        screen.blit(play_text, play_text_rect)

        # Draw quit button
        pygame.draw.rect(screen, BLACK, quit_button)
        quit_text = font.render("Quit", True, WHITE)
        quit_text_rect = quit_text.get_rect(center=quit_button.center)
        screen.blit(quit_text, quit_text_rect)

        pygame.display.flip()
