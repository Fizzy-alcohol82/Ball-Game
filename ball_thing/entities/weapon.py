"""The knife each fighter swings.

The blade orbits its owner. Damage is dealt when the blade tip enters the
enemy's body and the owner's attack cooldown has elapsed. Drawing is a simple
rotated polygon so it reads as a knife without needing image assets.
"""
import math
import pygame
from pygame import Vector2

from .. import config as cfg


class Weapon:
    def __init__(self, owner):
        self.owner = owner
        self.angle = 0.0          # current orbit angle (radians)
        self.cooldown = 0.0       # seconds until the next hit may land

    @property
    def tip(self):
        """World-space position of the blade tip."""
        reach = self.owner.radius + cfg.WEAPON_LENGTH
        return self.owner.pos + Vector2(math.cos(self.angle), math.sin(self.angle)) * reach

    def update(self, dt):
        self.angle = (self.angle + cfg.WEAPON_ORBIT_SPEED * dt) % math.tau
        if self.cooldown > 0:
            self.cooldown = max(0.0, self.cooldown - dt)

    def try_hit(self, enemy):
        """Return damage dealt this frame (0 if blocked by cooldown / no contact)."""
        if self.cooldown > 0:
            return 0.0
        if self.tip.distance_to(enemy.pos) <= enemy.radius:
            self.cooldown = 1.0 / self.owner.attack_speed
            return self.owner.damage
        return 0.0

    def draw(self, surface):
        base = self.owner.pos + Vector2(math.cos(self.angle), math.sin(self.angle)) * self.owner.radius
        tip = self.tip
        direction = (tip - base)
        if direction.length_squared() == 0:
            return
        direction = direction.normalize()
        perp = Vector2(-direction.y, direction.x)

        # handle + guard + blade as one tapered polygon
        w = 5
        guard = base + perp * (w + 2)
        guard2 = base - perp * (w + 2)
        body1 = base + perp * w + direction * 6
        body2 = base - perp * w + direction * 6
        blade1 = tip - perp * 1
        blade2 = tip + perp * 1

        pygame.draw.polygon(surface, (60, 70, 90), [guard, guard2, body2, body1])
        pygame.draw.polygon(surface, (225, 232, 245), [body1, body2, blade2, blade1])
        pygame.draw.line(surface, (140, 160, 200), base + direction * 6, tip, 2)
