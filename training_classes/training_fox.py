import math
import random

import pygame

from game_classes.vector2 import Vector2


class TrainingFox:
    def __init__(self, x, y, game):
        self.game = game

        self.location = Vector2(x, y)
        self.radius = 20
        self.direction = Vector2(x, y)
        self.rabbit_vision = 300

        self.speed = 2
        self.move_timer = 0

        self.hunting = False
        self.rab = None

    def draw(self, screen):
        pygame.draw.circle(screen, self.game.fox_orange, self.location.return_tuple(), self.radius)

    def hunt_rabbit(self):
        dist = self.location.find_distance(self.rab.location)
        if dist > self.rabbit_vision:
            self.hunting = False
            self.rab = None
            return False
        elif self.rab.hiding:
            self.hunting = False
            self.rab = None
            return False
        elif dist - self.radius < self.rab.size:
            self.eat()
            return True
        else:
            self.direction.set_new_direction(self.rab.location, self.location)
            return True

    def check_for_rabbits(self):
        for r in self.game.rabbits:
            if not r.hiding:
                dist = self.location.find_distance(r.location)
                if dist < r.size:
                    self.rab = r
                    self.eat()
                    return False

                if dist < self.rabbit_vision:
                    self.rab = r
                    self.hunting = True
                    return True
        return False

    def set_direction(self):
        if not self.hunting:
            if self.check_for_rabbits():
                if self.hunt_rabbit():
                    return
        elif self.hunt_rabbit():
            return

        # The random number will determine whether the fox keeps moving in the same direction or changes course
        rand = random.randint(0, 500)
        if rand < 20:
            rand_x = random.randint(0, self.game.screen_width)
            rand_y = random.randint(0, self.game.screen_height)
            self.direction.x = rand_x
            self.direction.y = rand_y
            self.direction.set_new_direction(Vector2(rand_x, rand_y), self.location)

    def eat(self):
        self.hunting = False
        self.rab.fitness -= 20
        self.rab.die()
        self.rab = None

    def move(self):
        if self.move_timer > self.speed:
            # Set new direction of travel
            self.set_direction()

            # Make direction a unit vector
            self.direction.find_unit_vector()

            # Increment location based on new direction
            self.location.add(self.direction)

            # Increment event timers
            self.move_timer = 0
        else:
            self.move_timer += 1

