import math
import random

import pygame

from game_classes.vector2 import Vector2
from game_classes.brain import Brain
from game_classes.food_src import FoodSource
from game_classes.water_src import WaterSource
from game_classes.rock import Rock


class TrainingRabbit:
    def __init__(self, x, y, brain: Brain, game):
        self.location = Vector2(x, y)
        self.direction = Vector2(x, y)
        self.brain = brain
        self.game = game

        self.speed = 1
        self.size = 15
        self.hydration = 100
        self.hunger = 100

        # Event Timers
        self.move_timer = 61
        self.hunger_timer = 0
        self.thirst_timer = 0
        self.currently_hiding_timer = 0

        # Event Trackers
        self.hiding = False

        # Training Metrics
        self.fitness = 0

    def draw(self, screen):
        if not self.hiding:
            pygame.draw.circle(screen, self.game.rab, self.location.return_tuple(), self.size)

    # Outline: Movement function focused on training the Action Chooser
    def action_chooser_trainer(self):
        if self.move_timer > self.speed:
            # Decrement the rabbit's hydration
            if self.thirst_timer > 15:
                self.hydration -= 1
                self.thirst_timer = 0

            # Decrement the rabbit's hunger
            if self.hunger_timer > 20:
                self.hunger -= 1
                self.hunger_timer = 0

            # Rabbit dies if it's hunger or hydration runs out
            if self.hydration < 0:
                self.die()
            elif self.hunger < 0:
                self.die()

            # Increment all the rabbit's event timer
            self.thirst_timer += 1
            self.hunger_timer += 1
            self.move_timer = 0

            # Calculate Action
            max_d = math.sqrt(self.game.screen_width ** 2 + self.game.screen_height ** 2)
            f = self.find_nearest(self.game.foxes)
            if f:
                f_dist = self.location.find_distance(f.location)
            else:
                f_dist = max_d

            action = self.brain.predict_action([self.hunger / 100, self.hydration / 100, f_dist / max_d])

            # Calculate New Direction
            go_to_object = None
            if action == "eat":
                # Calculate Fitness
                if self.hunger > 90:
                    self.fitness += 1
                elif self.hunger > 60:
                    self.fitness += 5
                elif self.hunger > 40:
                    self.fitness += 8
                else:
                    self.fitness += 10

                # Calculate New Direction
                f = self.find_nearest(self.game.food)
                if f:
                    go_to_object = f
                    self.direction.set_new_direction(f.location, self.location)
            elif action == "drink":
                # Calculate Fitness
                if self.hydration > 90:
                    self.fitness += 1
                elif self.hydration > 60:
                    self.fitness += 5
                elif self.hydration > 40:
                    self.fitness += 8
                else:
                    self.fitness += 10

                # Calculate New Direction
                w = self.find_nearest(self.game.water)
                if w:
                    go_to_object = w
                    self.direction.set_new_direction(w.location, self.location)
            elif action == "hide":
                # Calculate Fitness
                fox = self.find_nearest(self.game.foxes)
                if not fox:
                    self.fitness -= 5
                else:
                    f_dist = self.location.find_distance(fox.location)
                    if f_dist > max_d / 2:
                        self.fitness += 1
                    elif f_dist > max_d / 4:
                        self.fitness += 4
                    elif f_dist > max_d / 8:
                        self.fitness += 6
                    else:
                        self.fitness += 10

                # Calculate New Direction
                r = self.find_nearest(self.game.rocks)
                if r:
                    go_to_object = r
                    if not self.hiding:
                        self.direction.set_new_direction(r.location, self.location)
                    else:
                        self.direction.set_new_direction(self.location, self.location)
            elif action == "explore":
                # Calculate Fitness
                fox = self.find_nearest(self.game.foxes)
                if self.hunger > 80 and self.hydration > 80 and (not fox or self.location.find_distance(fox.location) >
                                                                 max_d / 2):
                    self.fitness += 10
                elif self.hunger < 50 or self.hydration < 50 or (fox and self.location.find_distance(fox.location) <
                                                                 max_d / 4):
                    self.fitness -= 5
                else:
                    self.fitness += 5

                # Calculate New Direction
                rand_x = random.randint(0, self.game.screen_width)
                rand_y = random.randint(0, self.game.screen_height)
                self.direction.set_new_direction(Vector2(rand_x, rand_y), self.location)

            # Increment Movement
            self.direction.find_unit_vector()
            self.location.add(self.direction)

            # If rabbit goes into the water or off the map, turn it around
            if self.check_location():
                self.direction.x *= -2
                self.direction.y *= -2
                self.location.add(self.direction)

            # Calculate if event should occur
            self.hiding = False
            if go_to_object:
                if self.location.find_distance(go_to_object.location) <= go_to_object.radius:
                    if go_to_object is FoodSource:
                        print('ate')
                        # Reset Hunger
                        self.hunger = 100
                    elif go_to_object is WaterSource:
                        print('drink')
                        # Reset Hydration
                        self.hydration = 100
                    elif go_to_object is Rock:
                        print('hid')
                        # Set Hiding
                        self.hiding = True
        else:
            self.move_timer += 1

    # Find Nearest ____
    def find_nearest(self, li: []):
        nearest = None
        nearest_d = 0
        for x in li:
            d = self.location.find_distance(x.location)
            if not nearest:
                nearest = x
                nearest_d = d
            else:
                if d < nearest_d:
                    nearest = x
                    nearest_d = d

        return nearest

    # Returns true if rabbit goes off the map or into water
    def check_location(self):
        w = self.find_nearest(self.game.water)
        if self.location.find_distance(w.location) < w.radius:
            return True
        if self.location.x > self.game.screen_width or self.location.x < 0:
            return True
        if self.location.y > self.game.screen_height or self.location.y < 0:
            return True

    # Event Methods
    def hide(self):
        # The rabbit will hide behind the rock for the equivalent of 15 moves
        self.hiding = True
        self.direction.x = 0
        self.direction.y = 0

    def die(self):
        if self in self.game.rabbits:
            self.game.rabbits.remove(self)