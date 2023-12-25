import math

import pygame
import globals as g
from game_classes.food_src import FoodSource
from game_classes.rock import Rock
from game_classes.water_src import WaterSource
from vector2 import Vector2
from brain import Brain
import random


class Rabbit:
    def __init__(self, x, y, speed, size, brain: Brain, game):
        self.location = Vector2(x, y)
        self.direction = Vector2(x, y)
        self.brain = brain
        self.game = game

        self.speed = speed
        self.size = size
        self.hydration = 100
        self.hunger = 100
        self.life = 0

        # Event Timers
        self.move_timer = 51
        self.hunger_timer = 0
        self.thirst_timer = 0
        self.currently_drinking_timer = 0
        self.currently_eating_timer = 0
        self.currently_hiding_timer = 0
        self.decision_timer = 0

        # Event Trackers
        self.hiding = False
        self.currently_drinking = False
        self.currently_eating = False
        self.being_eaten = False
        self.food = None
        self.rock = None
        self.times_eaten = 0
        self.times_drink = 0
        self.times_hide = 0

    def draw(self, screen):
        if not self.hiding:
            pygame.draw.circle(screen, g.r_light, self.location.return_tuple(), self.size)

    # Outline: Main Movement Driver Methods, Go To Methods, Check For Methods, Event Methods, Quadrant Methods
    # Main Movement Driver Methods
    def move(self):
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

            # Perform current actions
            if self.currently_eating:
                self.eat()
            elif self.currently_drinking:
                self.drink()
            elif self.hiding:
                self.hide()
            elif self.being_eaten:
                self.be_eaten()
            else:
                # Increment decision timer
                self.decision_timer += 1
                go_to_object = None

                # The decision timer is designed to allow the rabbit to maintain the same direction and decision for
                # a few moves to speed up computation and allow for more events to occur
                if self.decision_timer > 7:
                    self.decision_timer = 0
                    # Calculate Action
                    max_d = math.sqrt(self.game.screen_width ** 2 + self.game.screen_height ** 2)
                    f = self.find_nearest(self.game.foxes)
                    if f:
                        f_dist = self.location.find_distance(f.location)
                    else:
                        f_dist = max_d

                    action = self.brain.predict_action([self.hunger / 100, self.hydration / 100, f_dist / max_d])

                    # Calculate New Direction
                    if action == "eat":
                        # Calculate New Direction
                        go_to_object = self.find_nearest(self.game.food)
                        if go_to_object:
                            performance = self.brain.predict_new_direction([go_to_object.location.x, go_to_object.location.y])
                            self.direction.x = performance[0]
                            self.direction.y = performance[1]
                    elif action == "drink":
                        # Calculate New Direction
                        go_to_object = self.find_nearest(self.game.water)
                        if go_to_object:
                            performance = self.brain.predict_new_direction([go_to_object.location.x, go_to_object.location.y])
                            self.direction.x = performance[0]
                            self.direction.y = performance[1]
                    elif action == "hide":
                        # Calculate New Direction
                        go_to_object = self.find_nearest(self.game.rocks)
                        if go_to_object:
                            performance = self.brain.predict_new_direction([go_to_object.location.x, go_to_object.location.y])
                            self.direction.x = performance[0]
                            self.direction.y = performance[1]
                    elif action == "explore":
                        self.decision_timer -= 3
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

                if go_to_object:
                    if self.location.find_distance(go_to_object.location) - self.size <= go_to_object.radius:
                        if isinstance(go_to_object, FoodSource):
                            self.eat()
                        elif isinstance(go_to_object, WaterSource):
                            self.drink()
                        elif isinstance(go_to_object, Rock):
                            self.hide()
        else:
            self.move_timer += 1

    # Find Nearest ____
    def find_nearest(self, li):
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
    def eat(self):
        # The rabbit will eat the source for the equivalent of 15 moves
        self.currently_eating = True
        self.direction.x = 0
        self.direction.y = 0
        self.currently_eating_timer += 1
        if self.currently_eating_timer > 15:
            # Finish eating
            self.food.eat()
            self.times_eaten += 1
            if self.times_eaten > 2:
                self.reproduce()
                self.times_eaten = 0
            self.food = None
            self.currently_eating = False
            self.hunger = 100
            self.currently_eating_timer = 0

    def drink(self):
        # The rabbit will stand still at the edge of the water source for the equivalent of 15 moves
        self.currently_drinking = True
        self.direction.x = 0
        self.direction.y = 0
        self.currently_drinking_timer += 1
        if self.currently_drinking_timer > 15:
            # Finish drinking
            if self.times_drink > 2:
                self.reproduce()
                self.times_drink = 0
            self.currently_drinking = False
            self.hydration = 100
            self.currently_drinking_timer = 0

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

    def reproduce(self):
        self.game.rabbits.append(Rabbit(self.location.x, self.location.y, self.speed, self.size,
                                        Brain(brain=self.brain), self.game))

    def be_eaten(self):
        self.being_eaten = True
        self.direction.x = 0
        self.direction.y = 0

    def die(self):
        if self in g.rabbits:
            g.rabbits.remove(self)
