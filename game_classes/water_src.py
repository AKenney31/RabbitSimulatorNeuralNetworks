import pygame
from game_classes.vector2 import Vector2


class WaterSource:
    def __init__(self, x, y, rad, game):
        self.game = game
        self.location = Vector2(x, y)
        self.radius = rad

    def draw(self, screen):
        pygame.draw.circle(screen, self.game.water_blue, self.location.return_tuple(), self.radius)
