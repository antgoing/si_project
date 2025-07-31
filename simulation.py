import pygame
import neat
import math
import os
import json
import tempfile
import sys

WIDTH = 1920
HEIGHT = 1080
CAR_SIZE_X = 50
CAR_SIZE_Y = 50
START_POS = (700, 800) 
START_ORIENTATION = 'vertical'
START_LINE_WIDTH = 50
START_LINE_COLOR = (0, 255, 0)
BORDER_COLOR = (255, 255, 255, 255)
LAP_ZONE_RADIUS = 60
current_generation = 0

#load config
with open("selected.json") as f:
    data = json.load(f)
    selected_track = data.get("track")
    selected_car = data.get("car")
    selected_config = data.get("config")

if not selected_track or not selected_car or not selected_config:
    print("Error: Nie wybrano trasy, samochodu lub konfiguracji")
    sys.exit(1)

def load_neat_config(json_path):
    with open(json_path) as f:
        data = json.load(f)

    temp = tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.ini')
    for section, items in data.items():
        temp.write(f"[{section}]\n")
        for key, val in items.items():
            temp.write(f"{key} = {val}\n")
        temp.write("\n")
    temp.close()
    return temp.name

#klasa samochodu
class Car:
    def __init__(self, sprite_file):
        self.sprite = pygame.image.load(f"assets/{sprite_file}").convert()
        self.sprite = pygame.transform.scale(self.sprite, (CAR_SIZE_X, CAR_SIZE_Y))
        self.rotated_sprite = self.sprite
        self.position = [700, 800]
        self.angle = 0
        self.speed = 0
        self.speed_set = False
        self.center = [self.position[0] + CAR_SIZE_X / 2, self.position[1] + CAR_SIZE_Y / 2]
        self.radars = []
        self.alive = True
        self.distance = 0
        self.time = 0
        self.lap_times = []
        self.last_lap_time = None
        self.lap_completed = False
        
     
    def draw(self, screen):
        screen.blit(self.rotated_sprite, self.position)
        for radar in self.radars:
            pos = radar[0]
            pygame.draw.line(screen, (0, 0, 255), self.center, pos, 1)
            pygame.draw.circle(screen, (0, 0, 255), pos, 5)
    #kolizje
    def check_collision(self, game_map):
        self.alive = True
        for point in self.corners:
            if game_map.get_at((int(point[0]), int(point[1]))) == BORDER_COLOR:
                self.alive = False
                break

    def check_radar(self, degree, game_map):
        length = 0
        x = int(self.center[0])
        y = int(self.center[1])
        while not game_map.get_at((x, y)) == BORDER_COLOR and length < 300:
            length += 1
            x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * length)
            y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * length)
        dist = int(math.hypot(x - self.center[0], y - self.center[1]))
        self.radars.append([(x, y), dist])

    def update(self, game_map):
        if not self.speed_set:
            self.speed = 20
            self.speed_set = True

        self.rotated_sprite = self.rotate_center(self.sprite, self.angle)
        self.position[0] += math.cos(math.radians(360 - self.angle)) * self.speed
        self.position[1] += math.sin(math.radians(360 - self.angle)) * self.speed

        self.position[0] = max(self.position[0], 20)
        self.position[0] = min(self.position[0], WIDTH - 120)
        self.position[1] = max(self.position[1], 20)
        self.position[1] = min(self.position[1], HEIGHT - 120)

        self.distance += self.speed
        self.time += 1
        self.center = [self.position[0] + CAR_SIZE_X / 2, self.position[1] + CAR_SIZE_Y / 2]
        
        l = 0.5 * CAR_SIZE_X
        self.corners = [
            [self.center[0] + math.cos(math.radians(360 - (self.angle + a))) * l,
             self.center[1] + math.sin(math.radians(360 - (self.angle + a))) * l]
            for a in [30, 150, 210, 330]
        ]
        
        dx = self.center[0] - START_POS[0]
        dy = self.center[1] - START_POS[1]
        dist = math.hypot(dx, dy)

        if dist < LAP_ZONE_RADIUS:
            if not self.lap_completed:
                now = pygame.time.get_ticks()
                if self.last_lap_time is not None:
                    lap_time = (now - self.last_lap_time) / 1000.0  # sekundy
                    self.lap_times.append(lap_time)
                self.last_lap_time = now
                self.lap_completed = True
        else:
            self.lap_completed = False

        self.check_collision(game_map)
        self.radars.clear()
        for d in [-120, -90, -60, -30, 0, 30, 60, 90, 120]:
            self.check_radar(d, game_map)

    def get_data(self):
        radars = self.radars
        return_values = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        for i, radar in enumerate(radars):
            return_values[i] = int(radar[1] / 30)

        return return_values

    def get_reward(self):
        return self.distance / (CAR_SIZE_X / 2)

    def rotate_center(self, image, angle):
        rect = image.get_rect()
        rotated_image = pygame.transform.rotate(image, angle)
        rot_rect = rect.copy()
        rot_rect.center = rotated_image.get_rect().center
        return rotated_image.subsurface(rot_rect).copy()

def run_simulation(genomes, config):
    global current_generation
    current_generation += 1

    nets = []
    cars = []

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 30)
    button_font = pygame.font.SysFont("Arial", 24)
    exit_button = pygame.Rect(WIDTH - 160, 20, 140, 40)
    game_map = pygame.image.load(os.path.join("maps", selected_track)).convert()

    for genome_id, genome in genomes:
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        genome.fitness = 0
        cars.append(Car(selected_car))

    counter = 0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if exit_button.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        for i, car in enumerate(cars):
            if car.alive:
                output = nets[i].activate(car.get_data())
                choice = output.index(max(output))
                if choice == 0:
                    car.angle += 10
                elif choice == 1:
                    car.angle -= 10
                elif choice == 2:
                    if car.speed - 2 >= 12:
                        car.speed -= 2
                else:
                    car.speed += 2

        still_alive = 0
        for i, car in enumerate(cars):
            if car.alive:
                still_alive += 1
                car.update(game_map)
                genomes[i][1].fitness += car.get_reward()

        if still_alive == 0 or counter > 60 * 30:
            pygame.display.flip()
            pygame.time.delay(1000)
            break

        screen.blit(game_map, (0, 0))
        for car in cars:
            if car.alive:
                car.draw(screen)

        avg_fitness = sum(g.fitness for _, g in genomes) / len(genomes)
        best_fitness = max(g.fitness for _, g in genomes)
        top_speed = max([car.speed for car in cars if car.alive], default=0)
        
        if START_ORIENTATION == 'vertical':
            pygame.draw.line(screen, START_LINE_COLOR,
                            (START_POS[0], START_POS[1] - START_LINE_WIDTH),
                            (START_POS[0], START_POS[1] + START_LINE_WIDTH), 6)
        else:
            pygame.draw.line(screen, START_LINE_COLOR,
                            (START_POS[0] - START_LINE_WIDTH, START_POS[1]),
                            (START_POS[0] + START_LINE_WIDTH, START_POS[1]), 6)
            
        fastest_lap = min((min(car.lap_times) for car in cars if car.lap_times), default=None)

        extra_stats = [
            f"Generacja: {current_generation}",
            f"Liczba aut: {still_alive}",
            f"Średni Fitness: {avg_fitness:.2f}",
            f"Najlepszy Fitness: {best_fitness:.2f}",
            f"Największa predkość: {top_speed:.1f}",
            f"Naj. Okrążenie: {fastest_lap:.2f}s" if fastest_lap is not None else "Naj. Okrążenie: N/A"
        ]

        for i, stat in enumerate(extra_stats):
            stat_surface = font.render(stat, True, (0, 0, 0))
            screen.blit(stat_surface, (20, 0 + i * 30))

        pygame.draw.rect(screen, (200, 0, 0), exit_button)
        exit_text = button_font.render("Zakończ", True, (255, 255, 255))
        screen.blit(exit_text, (WIDTH - 150, 30))

        pygame.display.flip()
        clock.tick(120)
        counter += 1
    
    

if __name__ == "__main__":
    ini_config = load_neat_config(selected_config)
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        ini_config
    )

    pop = neat.Population(config)
    pop.add_reporter(neat.StdOutReporter(True))
    pop.add_reporter(neat.StatisticsReporter())
    pop.run(run_simulation, 100)
    os.remove(ini_config)
