import pygame
import sys
import os
import time

WIDTH, HEIGHT = 1920, 1080
BRUSH_SIZE = 50
BG_COLOR = (255, 255, 255)     
LINE_COLOR = (0, 0, 0)          
START_COLOR = (0, 255, 0)      
START_LINE_WIDTH = BRUSH_SIZE
START_POS = (700, 800)
START_ORIENTATION = 'vertical'

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Track Editor")

canvas = pygame.Surface((WIDTH, HEIGHT))
canvas.fill(BG_COLOR)

font = pygame.font.SysFont("Arial", 24)
message = ""
message_time = 0

def draw_text_button(text, x, y, color=(0, 0, 0)):
    surf = font.render(text, True, color)
    rect = surf.get_rect(topleft=(x, y))
    screen.blit(surf, rect)
    return rect

def draw_start_line(surface):
    if START_ORIENTATION == 'vertical':
        pygame.draw.line(surface, START_COLOR,
                         (START_POS[0], START_POS[1] - BRUSH_SIZE),
                         (START_POS[0], START_POS[1] + BRUSH_SIZE),
                         START_LINE_WIDTH)
    else:
        pygame.draw.line(surface, START_COLOR,
                         (START_POS[0] - BRUSH_SIZE, START_POS[1]),
                         (START_POS[0] + BRUSH_SIZE, START_POS[1]),
                         START_LINE_WIDTH)

def show_message(text):
    global message, message_time
    message = text
    message_time = time.time()

def save_track():
    os.makedirs("maps", exist_ok=True)
    idx = 1
    while os.path.exists(f"maps/trasa{idx}.png"):
        idx += 1
    pygame.image.save(canvas, f"maps/trasa{idx}.png")
    show_message(f"Zapisano jako trasa{idx}.png")

def main():
    global BRUSH_SIZE
    drawing = False
    running = True

    BRUSH_SIZES = [20, 30, 40, 50, 60]
    brush_buttons = []

    while running:
        screen.blit(canvas, (0, 0))
        draw_start_line(screen)

        save_btn = draw_text_button("Zapisz trasę", 20, 20)
        reset_btn = draw_text_button("Nowa trasa", 20, 60)
        exit_btn = draw_text_button("Wyjdź z edytora", 20, 100)

        #pedzel
        brush_buttons.clear()
        x_offset = WIDTH - 350
        screen.blit(font.render("Rozmiar pędzla:", True, (0, 0, 0)), (x_offset, 20))
        for i, size in enumerate(BRUSH_SIZES):
            btn = draw_text_button(str(size), x_offset + i * 60, 50)
            brush_buttons.append((btn, size))

        # komunikaty
        if message and time.time() - message_time < 2.5:
            msg_surf = font.render(message, True, (0, 120, 255))
            screen.blit(msg_surf, (20, HEIGHT - 40))

        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if save_btn.collidepoint(mouse_pos):
                        save_track()
                    elif reset_btn.collidepoint(mouse_pos):
                        canvas.fill(BG_COLOR)
                        show_message("Wyczyszczono i rozpoczęto nową trasę")
                    elif exit_btn.collidepoint(mouse_pos):
                        show_message("Powrót do menu")
                        running = False
                    else:
                        for btn, size in brush_buttons:
                            if btn.collidepoint(mouse_pos):
                                BRUSH_SIZE = size
                                show_message(f"Rozmiar pędzla: {size}")
                                break
                        else:
                            drawing = True

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    drawing = False

        if drawing:
            mx, my = pygame.mouse.get_pos()
            pygame.draw.circle(canvas, LINE_COLOR, (mx, my), BRUSH_SIZE)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    if "--menu" not in sys.argv:
        print("Nie można uruchomić edytora bez menu.")
        sys.exit()
    main()
