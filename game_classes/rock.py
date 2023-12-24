import math
import pygame
from game_classes.vector2 import Vector2


class Rock:
    def __init__(self, x, y, rad, game):
        self.game = game
        self.location = Vector2(x, y)
        self.radius = rad
        capacity = (math.pi * math.pow(rad, 2)) / 2
        self.capacity = int(capacity)
        self.occupants = 0

    def draw(self, screen):
        pygame.draw.circle(screen, self.game.rock_gray, self.location.return_tuple(), self.radius)
