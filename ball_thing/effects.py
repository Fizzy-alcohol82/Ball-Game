"""Lightweight eye-candy: motion trails and hit sparks.

Kept deliberately dependency-free (just pygame draw calls) so the engine stays
portable. Nothing here affects gameplay state.
"""
import pygame
from pygame import Vector2


class Trail:
    """A fading streak of past positions, used for the Full Throttle blur."""

    def __init__(self, length=14):
        self.length = length
        self.points = []

    def push(self, pos):
        self.points.append(Vector2(pos))
        if len(self.points) > self.length:
            self.points.pop(0)

    def clear(self):
        self.points.clear()

    def draw(self, surface, color, radius):
        n = len(self.points)
        for i, p in enumerate(self.points):
            frac = (i + 1) / n
            alpha = int(70 * frac)
            r = max(2, int(radius * frac))
            ghost = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(ghost, (*color, alpha), (r, r), r)
            surface.blit(ghost, (p.x - r, p.y - r))


class Particle:
    def __init__(self, pos, vel, life, color, size):
        self.pos = Vector2(pos)
        self.vel = Vector2(vel)
        self.life = life
        self.max_life = life
        self.color = color
        self.size = size

    def update(self, dt):
        self.pos += self.vel * dt
        self.vel *= 0.90
        self.life -= dt
        return self.life > 0

    def draw(self, surface):
        frac = max(0.0, self.life / self.max_life)
        alpha = int(255 * frac)
        r = max(1, int(self.size * frac))
        chip = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(chip, (*self.color, alpha), (r, r), r)
        surface.blit(chip, (self.pos.x - r, self.pos.y - r))


class ParticleSystem:
    def __init__(self):
        self.particles = []

    def burst(self, pos, color, count=10):
        import random
        import math
        for _ in range(count):
            ang = random.uniform(0, math.tau)
            spd = random.uniform(60, 220)
            vel = (math.cos(ang) * spd, math.sin(ang) * spd)
            self.particles.append(
                Particle(pos, vel, random.uniform(0.25, 0.55), color, random.uniform(2, 5))
            )

    def update(self, dt):
        self.particles = [p for p in self.particles if p.update(dt)]

    def draw(self, surface):
        for p in self.particles:
            p.draw(surface)
