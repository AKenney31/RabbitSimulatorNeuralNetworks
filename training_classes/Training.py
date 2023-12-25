import random

import pygame
import tensorflow as tf

from game_classes.brain import Brain
from game_classes.food_src import FoodSource
from game_classes.water_src import WaterSource
from game_classes.rock import Rock
from training_classes.training_rabbit import TrainingRabbit
from training_classes.training_fox import TrainingFox


def modify_brain(brain: Brain, chooser: bool):
    new_brain = Brain(brain)
    model = new_brain.action_chooser if chooser else new_brain.action_performer

    # Mutate weights
    for layer in model.layers:
        layer.set_weights([w + tf.random.normal(w.shape, stddev=.05) for w in layer.get_weights()])
    return new_brain


class Training:
    def __init__(self):
        # Define Simulation Objects
        self.rabbits: [TrainingRabbit] = []
        self.foxes: [TrainingFox] = []
        self.water: [WaterSource] = []
        self.rocks: [Rock] = []
        self.food: [FoodSource] = []

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

        # Training Variables
        self.pop: [TrainingRabbit] = []

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

    def game_loop_chooser(self, i: int, brain: Brain = None):
        # Reset Simulation Objects
        self.rabbits = []
        self.foxes = []
        self.water = []
        self.rocks = []
        self.food = []
        pygame.init()
        size = self.screen_width, self.screen_height
        screen = pygame.display.set_mode(size)
        pygame.display.set_caption(f'Training Window: {i + 1}')
        # Add Fox
        self.foxes.append(TrainingFox(self.screen_width / 2, self.screen_height / 1.5, self))
        self.foxes.append(TrainingFox(self.screen_width / 2, self.screen_height / 2, self))
        self.foxes.append(TrainingFox(self.screen_width / 2, self.screen_height / 2.5, self))
        # Add Water
        self.water.append(WaterSource(550, 200, 100, self))
        self.water.append(WaterSource(50, 600, 50, self))
        # Add Rabbits
        self.rabbits.append(TrainingRabbit(random.randint(0, self.screen_width),
                                           random.randint(0, self.screen_height),
                                           modify_brain(brain, True) if brain else Brain(), self))
        self.rabbits.append(TrainingRabbit(random.randint(0, self.screen_width),
                                           random.randint(0, self.screen_height),
                                           modify_brain(brain, True) if brain else Brain(), self))
        self.rabbits.append(TrainingRabbit(random.randint(0, self.screen_width),
                                           random.randint(0, self.screen_height),
                                           modify_brain(brain, True) if brain else Brain(), self))
        self.rabbits.append(TrainingRabbit(random.randint(0, self.screen_width),
                                           random.randint(0, self.screen_height),
                                           modify_brain(brain, True) if brain else Brain(), self))
        self.rabbits.append(TrainingRabbit(random.randint(0, self.screen_width),
                                           random.randint(0, self.screen_height),
                                           modify_brain(brain, True) if brain else Brain(), self))
        self.rabbits.append(TrainingRabbit(random.randint(0, self.screen_width),
                                           random.randint(0, self.screen_height),
                                           modify_brain(brain, True) if brain else Brain(), self))
        self.pop = self.rabbits.copy()
        # Add Rocks
        self.rocks.append(Rock(200, 400, 20, self))
        self.rocks.append(Rock(70, 70, 30, self))
        self.rocks.append(Rock(600, 500, 50, self))
        self.rocks.append(Rock(300, 600, 15, self))
        self.rocks.append(Rock(150, 200, 30, self))
        # Add Food
        self.food.append(FoodSource(350, 400, self))
        self.food.append(FoodSource(200, 47, self))
        self.food.append(FoodSource(30, 60, self))
        self.food.append(FoodSource(400, 600, self))
        self.food.append(FoodSource(600, 600, self))

        while 1:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit(0)

            if len(self.rabbits) == 0:
                pygame.quit()
                return

            for rab in self.rabbits:
                rab.action_chooser_trainer()

            for fox in self.foxes:
                fox.move()

            self.draw_window(screen)

    def game_loop_performer(self, i: int, brain: Brain = None):
        # Reset Simulation Objects
        self.rabbits = []
        self.foxes = []
        self.water = []
        self.rocks = []
        self.food = []
        pygame.init()
        size = self.screen_width, self.screen_height
        screen = pygame.display.set_mode(size)
        pygame.display.set_caption(f'Training Window: {i + 1}')

        # Add Rabbits
        self.rabbits.append(TrainingRabbit(random.randint(0, self.screen_width),
                                           random.randint(0, self.screen_height),
                                           modify_brain(brain, False) if brain else Brain(), self))
        self.rabbits.append(TrainingRabbit(random.randint(0, self.screen_width),
                                           random.randint(0, self.screen_height),
                                           modify_brain(brain, False) if brain else Brain(), self))
        self.rabbits.append(TrainingRabbit(random.randint(0, self.screen_width),
                                           random.randint(0, self.screen_height),
                                           modify_brain(brain, False) if brain else Brain(), self))
        self.pop = self.rabbits.copy()

        # Add Rock
        self.rocks.append(Rock(random.randint(0, self.screen_width), random.randint(0, self.screen_height),
                               20, self))

        while 1:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit(0)

            if len(self.rabbits) == 0:
                pygame.quit()
                return

            for rab in self.rabbits:
                rab.action_performer_trainer()

            self.draw_window(screen)

    def train_model(self, performer: bool):
        for i in range(250):
            best_brain = None
            if len(self.pop) > 0:
                best_brain = self.pop[0].brain
                best_fitness = self.pop[0].fitness
                for rab in self.pop:
                    if rab.fitness > best_fitness:
                        best_brain = rab.brain
                        best_fitness = rab.fitness
            self.game_loop_performer(i, brain=best_brain) if performer else self.game_loop_chooser(i, brain=best_brain)

        if len(self.pop) > 0:
            best_brain = self.pop[0].brain
            best_fitness = self.pop[0].fitness
            for rab in self.pop:
                if rab.fitness > best_fitness:
                    best_brain = rab.brain
                    best_fitness = rab.fitness

            best_brain.save_action_performer() if performer else best_brain.save_action_chooser()


def main():
    t = Training()
    print('Type:\n"1" to train the action chooser\n"2" to train the action performer\n"3" to train both')
    i = int(input('Then press enter: '))
    if i == 1:
        t.train_model(performer=False)
    elif i == 2:
        t.train_model(performer=True)
    else:
        t.train_model(performer=False)
        t.train_model(performer=True)


if __name__ == "__main__":
    main()
