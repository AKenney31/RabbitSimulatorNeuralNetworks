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
        self.decision_timer = 0

        # Event Trackers
        self.hiding = False

        # Training Metrics
        self.fitness = 0

    def draw(self, screen):
        # Water health bar
        pygame.draw.rect(screen, "red", (self.location.x - 20, self.location.y - self.size - 12, 40, 4))
        pygame.draw.rect(screen, self.game.water_blue, (self.location.x - 20, self.location.y - self.size - 12,
                                                        40 * (self.hydration / 100), 4))

        # Food health bar
        pygame.draw.rect(screen, "red", (self.location.x - 20, self.location.y - self.size - 6, 40, 4))
        pygame.draw.rect(screen, self.game.food_green, (self.location.x - 20, self.location.y - self.size - 6,
                                                        40 * (self.hunger / 100), 4))
        if not self.hiding:
            pygame.draw.circle(screen, self.game.rab, self.location.return_tuple(), self.size)

    # Outline: Movement function focused on training the Action Performer
    def action_performer_trainer(self):
        # The object being sought out is a rock on the screen
        objective = self.game.rocks[0]

        # The hunger is used as a time limit for the rabbit to reach objective
        if self.hunger_timer > 20:
            self.hunger -= 1
            self.hunger_timer = 0

        self.hunger_timer += 1
        self.decision_timer += 1

        if self.hunger < 0:
            self.fitness -= 100
            self.die()

        if self.decision_timer > 5:
            dist = self.location.find_distance(objective.location)
            self.decision_timer = 0
            new_dir = self.brain.predict_new_direction([objective.location.x, objective.location.y],
                                                       self.game.screen_width, self.game.screen_height)
            self.direction.x = new_dir[0]
            self.direction.y = new_dir[1]
            self.direction.find_unit_vector()
            self.location.add(self.direction)
            print(self.direction.x, self.direction.y)
            new_dist = self.location.find_distance(objective.location)

            if new_dist < dist:
                self.fitness += 10
            else:
                self.fitness -= 20
        else:
            self.location.add(self.direction)

        # If rabbit goes off the map, turn it around
        if self.check_location():
            self.direction.x *= -2
            self.direction.y *= -2
            self.location.add(self.direction)

        # If rabbit reaches objective, die and reward
        if self.location.find_distance(objective.location) - self.size <= objective.radius:
            self.fitness += 100 * len(self.game.rabbits)
            self.die()

    # Outline: Movement function focused on training the Action Chooser
    def action_chooser_trainer(self):
        if self.move_timer > self.speed:
            # Decrement the rabbit's hydration
            if self.thirst_timer > 8:
                self.hydration -= 1
                self.thirst_timer = 0

            # Decrement the rabbit's hunger
            if self.hunger_timer > 12:
                self.hunger -= 1
                self.hunger_timer = 0

            # Rabbit dies if it's hunger or hydration runs out
            if self.hydration < 0:
                self.fitness -= 50
                self.die()
            elif self.hunger < 0:
                self.fitness -= 100
                self.die()

            # Increment all the rabbit's event timer
            self.thirst_timer += 1
            self.hunger_timer += 1
            self.move_timer = 0
            self.decision_timer += 1

            # Calculate Action
            go_to_object = None
            if self.hiding:
                self.hide()
            elif self.decision_timer > 7:
                self.decision_timer = 0
                max_d = math.sqrt(self.game.screen_width ** 2 + self.game.screen_height ** 2)
                f = self.find_nearest(self.game.foxes)
                if f:
                    f_dist = self.location.find_distance(f.location)
                else:
                    f_dist = max_d

                action = self.brain.predict_action([self.hunger / 100, self.hydration / 100, f_dist / max_d])

                # Calculate New Direction
                if action == "eat":
                    # Calculate Fitness
                    if self.hunger > 90:
                        self.fitness -= 3
                    elif self.hunger > 60:
                        self.fitness += 3
                    elif self.hunger > 30:
                        self.fitness += 6
                    else:
                        self.fitness += 20

                    # Calculate New Direction
                    f = self.find_nearest(self.game.food)
                    if f:
                        go_to_object = f
                        self.direction.set_new_direction(f.location, self.location)
                elif action == "drink":
                    # Calculate Fitness
                    if self.hydration > 90:
                        self.fitness -= 5
                    elif self.hydration > 60:
                        self.fitness -= 2
                    elif self.hydration > 40:
                        self.fitness += 1
                    else:
                        self.fitness += 10

                    # Calculate New Direction
                    w = self.find_nearest(self.game.water)
                    if w:
                        go_to_object = w
                        self.direction.set_new_direction(w.location, self.location)
                elif action == "hide":
                    # Needs to decide whether to stay hiding or leave on
                    self.decision_timer = 5
                    # Calculate Fitness
                    fox = self.find_nearest(self.game.foxes)
                    if not fox:
                        self.fitness -= 5
                    else:
                        f_dist = self.location.find_distance(fox.location)
                        if f_dist > 150:
                            self.fitness -= 5
                        elif f_dist > 90:
                            self.fitness -= 2
                        elif f_dist > 60:
                            self.fitness -= 1
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
                    # It will explore for a longer time to try and cover more of the map
                    self.decision_timer -= 3

                    # Calculate Fitness
                    fox = self.find_nearest(self.game.foxes)
                    if self.hunger < 40 or self.hydration < 40 or (fox and self.location.find_distance(fox.location) <
                                                                   max_d / 4):
                        self.fitness -= 50
                    elif self.hunger > 90 and self.hydration > 90 and (fox and self.location.find_distance(fox.location)
                                                                       > max_d / 2):
                        self.fitness += 5
                    else:
                        self.fitness += 3

                    # Calculate New Direction
                    rand_x = random.randint(0, self.game.screen_width)
                    rand_y = random.randint(0, self.game.screen_height)
                    self.direction.set_new_direction(Vector2(rand_x, rand_y), self.location)

            # Increment Movement
            self.direction.find_unit_vector()
            self.location.add(self.direction)

            # If rabbit goes off the map, turn it around
            if self.check_location():
                self.direction.x *= -2
                self.direction.y *= -2
                self.location.add(self.direction)

            # Calculate if event should occur
            if go_to_object:
                if self.location.find_distance(go_to_object.location) - self.size <= go_to_object.radius:
                    if isinstance(go_to_object, FoodSource):
                        # Reset Hunger
                        self.hunger = 100
                    elif isinstance(go_to_object, WaterSource):
                        # Reset Hydration
                        self.hydration = 100
                    elif isinstance(go_to_object, Rock):
                        # Set Hiding
                        self.hide()
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
        self.currently_hiding_timer += 1
        if self.currently_hiding_timer > 15:
            # Finish hiding
            self.hiding = False
            self.currently_hiding_timer = 0

    def die(self):
        if self in self.game.rabbits:
            self.game.rabbits.remove(self)
