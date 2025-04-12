import pygame
import random
import math
import time
import json

# Constants
WIDTH, HEIGHT = 800, 600
NUM_CITIES = 5
CITIES_FILE = "cities.json"
ARROW_SIZE = 15
CITY_RADIUS = 8
START_RADIUS = 12

def draw_arrow(surface, start, end, color):
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    angle = math.atan2(dy, dx)
    
    pygame.draw.line(surface, color, start, end, 2)
    arrow_points = [
        (end[0] - ARROW_SIZE * math.cos(angle - math.pi/6),
        end[1] - ARROW_SIZE * math.sin(angle - math.pi/6)),
        (end[0] - ARROW_SIZE * math.cos(angle + math.pi/6),
        end[1] - ARROW_SIZE * math.sin(angle + math.pi/6)),
        end
    ]
    pygame.draw.polygon(surface, color, arrow_points)

def calculate_path_length(path):
    return sum(math.dist(path[i], path[(i+1)%len(path)]) for i in range(len(path)))

def main():
    try:
        with open(CITIES_FILE, 'r') as f:
            cities = json.load(f)
            print("Loaded cities from file")
    except FileNotFoundError:
        random.seed(42)
        cities = [(random.randint(50, WIDTH-50), random.randint(50, HEIGHT-50)) 
                for _ in range(NUM_CITIES)]
        with open(CITIES_FILE, 'w') as f:
            json.dump(cities, f)
        print("Created new cities file")

    best_length = float('inf')
    best_path = []
    calculations = 0
    start_time = time.time()
    found_time = 0

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    font = pygame.font.SysFont("Arial", 24)
    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        current_path = random.sample(cities, len(cities))
        current_length = calculate_path_length(current_path)
        calculations += 1

        if current_length < best_length:
            best_length = current_length
            best_path = current_path
            found_time = time.time() - start_time

        screen.fill((255, 255, 255))
        for x, y in cities:
            pygame.draw.circle(screen, (0, 0, 255), (x, y), CITY_RADIUS)
        
        if len(best_path) > 1:
            start_x, start_y = best_path[0]
            pygame.draw.circle(screen, (255, 215, 0), (start_x, start_y), START_RADIUS)
            
            for i in range(len(best_path)):
                start = best_path[i]
                end = best_path[(i+1)%len(best_path)]
                draw_arrow(screen, start, end, (255, 0, 0))

        current_time = time.time() - start_time
        texts = [
            f"Total Time: {current_time:.2f}s",
            f"Best Found At: {found_time:.2f}s",
            f"Best Length: {best_length:.2f}",
            f"Calculations: {calculations}",
            "Mode: Single-Threaded"
        ]
        for i, text in enumerate(texts):
            surf = font.render(text, True, (0, 0, 0))
            screen.blit(surf, (10, 10 + i*30))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()