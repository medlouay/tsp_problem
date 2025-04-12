import pygame
import math
import time
import json
import multiprocessing
import random
from multiprocessing import Process, Array, Value, Lock

# Constants
WIDTH, HEIGHT = 800, 600
NUM_CITIES = 5
CITIES_FILE = "cities.json"
NUM_WORKERS = 10
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

def worker_process(cities, best_path, best_length, best_time, calculations, lock, running):
    city_list = [(cities[2*i], cities[2*i+1]) for i in range(NUM_CITIES)]
    
    while running.value:
        temp_path = random.sample(city_list, len(city_list))
        length = sum(math.dist(temp_path[i], temp_path[(i+1)%NUM_CITIES]) 
                   for i in range(NUM_CITIES))
        
        with lock:
            calculations.value += 1
            
        if length < best_length.value:
            with lock:
                if length < best_length.value:
                    best_length.value = length
                    best_time.value = time.time()
                    for i, (x, y) in enumerate(temp_path):
                        best_path[2*i] = x
                        best_path[2*i+1] = y

def main():
    try:
        multiprocessing.set_start_method('spawn')
    except RuntimeError:
        pass

    with open(CITIES_FILE, 'r') as f:
        city_coords = json.load(f)
    
    cities = Array('i', [coord for pair in city_coords for coord in pair])
    best_path = Array('i', [-1]*(2*NUM_CITIES))
    best_length = Value('d', math.inf)
    best_time = Value('d', 0.0)
    calculations = Value('i', 0)
    lock = Lock()
    running = Value('i', 1)

    workers = [Process(target=worker_process, 
                     args=(cities, best_path, best_length, best_time, calculations, lock, running))
             for _ in range(NUM_WORKERS)]
    for w in workers:
        w.start()

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    font = pygame.font.SysFont("Arial", 24)
    clock = pygame.time.Clock()
    program_start = time.time()

    while running.value:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running.value = 0

        with lock:
            current_path = [(best_path[2*i], best_path[2*i+1]) 
                          for i in range(NUM_CITIES)]
            display_length = best_length.value
            found_at = best_time.value - program_start if best_time.value > 0 else 0
            current_calcs = calculations.value

        screen.fill((255, 255, 255))
        for x, y in current_path:
            pygame.draw.circle(screen, (0, 0, 255), (x, y), CITY_RADIUS)
        
        if len(current_path) > 1:
            start_x, start_y = current_path[0]
            pygame.draw.circle(screen, (255, 215, 0), (start_x, start_y), START_RADIUS)
            
            for i in range(len(current_path)):
                start = current_path[i]
                end = current_path[(i+1)%len(current_path)]
                draw_arrow(screen, start, end, (255, 0, 0))

        current_time = time.time() - program_start
        metrics = [
            f"Total Time: {current_time:.2f}s",
            f"Best Found At: {found_at:.2f}s",
            f"Best Length: {display_length:.2f}",
            f"Calculations: {current_calcs}",
            f"Workers: {NUM_WORKERS}",
            "Mode: Multi-Process"
        ]
        for i, text in enumerate(metrics):
            surf = font.render(text, True, (0, 0, 0))
            screen.blit(surf, (10, 10 + i*30))

        pygame.display.flip()
        clock.tick(60)

    for w in workers:
        w.join()
    pygame.quit()

if __name__ == "__main__":
    main()