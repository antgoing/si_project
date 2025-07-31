import pygame
import subprocess
import os
import sys
import json

WIDTH = 800
HEIGHT = 600
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Menu")

font = pygame.font.SysFont("Arial", 32)

selected_track = None
selected_car = None 
selected_config = None

#ladowanie tras
def load_available_tracks():
    return sorted([f for f in os.listdir("maps") if f.startswith("trasa") and f.endswith(".png")])

def save_selection():
    with open("selected.json", "w") as f:
        json.dump({
            "track": selected_track,
            "car": selected_car,
            "config": selected_config
        }, f)

def draw_main_menu(mouse_pos):
    screen.fill((30, 30, 30))
    options = [
        "Rozpocznij symulację",
        "Wybierz Trasę",
        "Wybierz model samochodu",
        "Wyjście"
    ]

    info_lines = [
        f"Wybrana trasa: {selected_track if selected_track else 'brak'}",
        f"Wybrany samochód: {selected_car if selected_car else 'brak'}",
    ]

    for i, info in enumerate(info_lines):
        info_text = pygame.font.SysFont("Arial", 24).render(info, True, (180, 180, 180))
        screen.blit(info_text, (20, 20 + i * 30))

    option_rects = []
    for i, option in enumerate(options):
        rect = pygame.Rect(WIDTH // 2 - 200, 200 + i * 60, 400, 50)
        hovered = rect.collidepoint(mouse_pos)
        color = (0, 255, 0) if hovered else (200, 200, 200)
        text = font.render(option, True, color)
        text_rect = text.get_rect(center=rect.center)
        screen.blit(text, text_rect)
        option_rects.append((rect, i))

    pygame.display.flip()
    return option_rects

def run_main_menu():
    global selected_track
    clock = pygame.time.Clock()
    running = True

    while running:
        mouse_pos = pygame.mouse.get_pos()
        option_rects = draw_main_menu(mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for rect, index in option_rects:
                    if rect.collidepoint(mouse_pos):
                        if index == 0:
                            run_simulation()
                        elif index == 1:
                            run_track_menu()
                        elif index == 2:
                            run_car_menu()
                        elif index == 3:
                            pygame.quit()
                            sys.exit()

        clock.tick(30)

    pygame.quit()

def run_simulation():
    if not selected_track or not selected_car or not selected_config:
        print("Błąd przy wybieraniu")
        return

    save_selection()
    subprocess.run([sys.executable, "simulation.py"])

#menu tras
def run_track_menu():
    global selected_track
    running = True
    clock = pygame.time.Clock()

    while running:
        mouse_pos = pygame.mouse.get_pos()
        screen.fill((20, 20, 20))
        tracks = load_available_tracks()

        draw_text("Kliknij na nazwę, aby wybrać trasę", 20, 20, (180, 180, 0))

        # Przycisk powrotu
        back_rect = draw_text("Powrót", WIDTH - 150, 20, (100, 200, 255))

        track_rects = []
        delete_rects = []

        y_offset = 100
        for track in tracks:
            track_rect = draw_text(track, 50, y_offset, (0, 255, 0) if track == selected_track else (200, 200, 200))
            del_rect = draw_text("Usuń", 600, y_offset, (255, 50, 50))
            track_rects.append((track_rect, track))
            delete_rects.append((del_rect, track))
            y_offset += 50

        create_rect = draw_text("+ Stwórz nową trasę", 50, y_offset + 30, (100, 200, 255))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back_rect.collidepoint(mouse_pos):
                    return
                for rect, track in track_rects:
                    if rect.collidepoint(mouse_pos):
                        selected_track = track
                        save_selection()
                        print(f"Wybrano trasę: {track}")
                        break
                for rect, track in delete_rects:
                    if rect.collidepoint(mouse_pos):
                        os.remove(f"maps/{track}")
                        print(f"Usunięto trasę: {track}")
                        break
                if create_rect.collidepoint(mouse_pos):
                    subprocess.run([sys.executable, "editor.py", "--menu"])
                    break

        pygame.display.flip()
        clock.tick(30)

#menu samochodow 
def run_car_menu():
    global selected_car, selected_config
    running = True
    clock = pygame.time.Clock()

    car_options = [
        ("car1.png", "configs/car1_config.json"),
        ("car2.png", "configs/car2_config.json")
    ]

    while running:
        mouse_pos = pygame.mouse.get_pos()
        screen.fill((20, 20, 20))
        draw_text("Wybierz samochód", 20, 20, (180, 180, 0))

        back_rect = draw_text("Powrót", WIDTH - 150, 20, (100, 200, 255))
        option_rects = []

        y_offset = 100
        for car_file, config_path in car_options:
            label = f"{car_file}"
            rect = draw_text(label, 50, y_offset, (0, 255, 0) if selected_car == car_file else (200, 200, 200))
            option_rects.append((rect, car_file, config_path))
            y_offset += 50

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back_rect.collidepoint(mouse_pos):
                    return
                for rect, car_file, config_path in option_rects:
                    if rect.collidepoint(mouse_pos):
                        selected_car = car_file
                        selected_config = config_path
                        save_selection()
                        print(f"Wybrano auto: {car_file}, konfig: {config_path}")

        pygame.display.flip()
        clock.tick(30)

#rysowanie 
def draw_text(text, x, y, color):
    surf = font.render(text, True, color)
    rect = surf.get_rect(topleft=(x, y))
    screen.blit(surf, rect)
    return rect

if __name__ == "__main__":
    run_main_menu()
