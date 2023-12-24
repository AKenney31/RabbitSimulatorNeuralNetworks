import pygame
from game_classes.vector2 import Vector2


class FoodSource:
    def __init__(self, x, y, game):
        self.game = game
        self.location = Vector2(x, y)
        self.radius = 15
        self.meals = 0

    def draw(self, screen):
        pygame.draw.circle(screen, self.game.food_green, self.location.return_tuple(), self.radius)

    def eat(self):
        self.meals += 1
        if self.meals > 1 and self in g.food:
            self.game.food.remove(self)
