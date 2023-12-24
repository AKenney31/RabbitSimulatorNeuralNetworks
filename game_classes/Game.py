import random

import pygame

from game_classes.brain import Brain
from game_classes.food_src import FoodSource
from game_classes.vector2 import Vector2
from game_classes.water_src import WaterSource
from game_classes.rock import Rock
from game_classes.rabbit import Rabbit
from game_classes.fox import Fox


class Game:
    def __init__(self):
        # Define Simulation Objects
        self.rabbits: [Rabbit] = []
        self.foxes: [Fox] = []
        self.water: [WaterSource] = []
        self.rocks: [Rock] = []
        self.food: [FoodSource] = []

        # Define Simulation Variables
        self.food_generator = 0
        self.fox_spawn_numbers = [20, 50, 100, 300]
        self.ind = 0

        # Define Pygame Screen Variables
        self.screen_width = 700
        self.screen_height = 700

        # Define Colors
        self.rab = (166, 111, 111)
        self.grass_green = (27, 207, 84)
        self.food_green = (7, 112, 40)
        self.water_blue = (14, 90, 204)
        self.fox_orange = (247, 144, 0)
        self.rock_gray = (96, 88, 97)

    def draw_window(self, screen: pygame.surface):
        screen.fill(self.grass_green)
        for w in self.water:
            w.draw(screen)
        for f in self.food:
            f.draw(screen)
        for r in self.rocks:
            r.draw(screen)
        for rab in self.rabbits:
            rab.draw(screen)
        for fox in self.foxes:
            fox.draw(screen)
        pygame.display.flip()

    def generate_food(self):
        while 1:
            x = random.randint(0, self.screen_width)
            y = random.randint(0, self.screen_height)
            valid = True

            for w in self.water:
                if w.location.find_distance(Vector2(x, y)) <= w.radius:
                    valid = False

            if valid:
                self.food.append(FoodSource(x, y, self))
                return

    def game_loop(self):
        # Reset Simulation Objects
        self.rabbits = []
        self.foxes = []
        self.water = []
        self.rocks = []
        self.food = []
        pygame.init()
        size = self.screen_width, self.screen_height
        screen = pygame.display.set_mode(size)

        # Add Water
        self.water.append(WaterSource(550, 200, 100, self))
        self.water.append(WaterSource(50, 600, 50, self))
        # Add Rabbits
        self.rabbits.append(Rabbit(200, 40, 60, 10, Brain(), self))
        self.rabbits.append(Rabbit(400, 140, 65, 15, Brain(), self))
        self.rabbits.append(Rabbit(600, 350, 70, 16, Brain(), self))
        self.rabbits.append(Rabbit(350, 600, 65, 15, Brain(), self))
        self.rabbits.append(Rabbit(200, 40, 75, 17, Brain(), self))
        self.rabbits.append(Rabbit(400, 140, 80, 20, Brain(), self))
        # Add Rocks
        self.rocks.append(Rock(200, 400, 20, self))
        self.rocks.append(Rock(70, 70, 30, self))
        self.rocks.append(Rock(600, 500, 50, self))
        self.rocks.append(Rock(400, 600, 15, self))
        self.rocks.append(Rock(150, 200, 30, self))

        while 1:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit(0)

            if len(self.rabbits) == 0:
                print("No More Rabbits")
                pygame.quit()
                exit(0)
            elif len(self.rabbits) > 400:
                print("Rabbits win")
                pygame.quit()
                exit(0)

            for rab in self.rabbits:
                rab.move()

            for fox in self.foxes:
                fox.move()

            if self.food_generator > 5000 and len(self.food) < 10:
                self.generate_food()
                self.food_generator = 0
            elif len(self.food) < 10:
                self.food_generator += 1

            if self.fox_spawn_numbers[self.ind] == len(self.rabbits):
                x = random.randint(0, self.screen_width)
                y = random.randint(0, self.screen_height)
                self.foxes.append(Fox(x, y))
                self.ind += 1

            self.draw_window(screen)


def main():
    g = Game()
    g.game_loop()


if __name__ == "__main__":
    main()
