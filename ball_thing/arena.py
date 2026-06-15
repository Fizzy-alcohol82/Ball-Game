"""The arena is just the framed white box and its watermark."""
import pygame

from . import config as cfg


class Arena:
    def __init__(self):
        self.rect = pygame.Rect(*cfg.ARENA)

    def draw(self, surface, font):
        pygame.draw.rect(surface, cfg.ARENA_FILL, self.rect)
        pygame.draw.rect(surface, cfg.ARENA_LINE, self.rect, cfg.ARENA_BORDER)
        mark = font.render("@ballthingsim", True, cfg.WATERMARK)
        surface.blit(mark, mark.get_rect(center=self.rect.center))
