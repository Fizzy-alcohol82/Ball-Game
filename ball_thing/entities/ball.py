"""A fighter is the ball itself: health, motion, and its weapon.

Base stats come from config; *effective* stats fold in any active ability
multipliers. The HUD reads the effective values so the numbers visibly jump
when Full Throttle or World Stasis kicks in.
"""
import math
import random
import pygame
from pygame import Vector2

from .. import config as cfg
from .weapon import Weapon
from ..effects import Trail


class Fighter:
    def __init__(self, spec, pos):
        self.name = spec["name"]
        self.color = spec["color"]
        self.color_dk = spec["color_dk"]
        self.text_color = spec["text_color"]

        self.base_damage = spec["damage"]
        self.base_speed = spec["speed"]
        self.base_attack_speed = spec["attack_speed"]

        self.radius = cfg.BALL_RADIUS
        self.pos = Vector2(pos)
        ang = random.uniform(0, 6.28)
        self.vel = Vector2(1, 0).rotate_rad(ang)

        self.health = cfg.START_HEALTH
        self.weapon = Weapon(self)
        self.ability = None        # set by Game
        self.trail = Trail()

        # transient per-frame multipliers, recomputed every tick
        self._mult = dict(speed=1.0, damage=1.0, attack=1.0)

    # ---- effective stats (base * multipliers) ------------------------------
    def reset_mults(self):
        self._mult = dict(speed=1.0, damage=1.0, attack=1.0)

    def apply_mult(self, speed=1.0, damage=1.0, attack=1.0):
        self._mult["speed"] *= speed
        self._mult["damage"] *= damage
        self._mult["attack"] *= attack

    @property
    def speed(self):
        return self.base_speed * self._mult["speed"]

    @property
    def damage(self):
        return self.base_damage * self._mult["damage"]

    @property
    def attack_speed(self):
        return self.base_attack_speed * self._mult["attack"]

    @property
    def alive(self):
        return self.health > 0

    @property
    def boosting(self):
        return self._mult["speed"] > 1.05

    # ---- motion ------------------------------------------------------------
    def steer_toward(self, target, dt, strength):
        """Rotate the current heading slightly toward `target` (capped per frame)."""
        to = target - self.pos
        if to.length_squared() == 0:
            return
        desired = to.normalize()
        cur = self.vel.normalize() if self.vel.length_squared() else desired
        cur_ang = math.atan2(cur.y, cur.x)
        des_ang = math.atan2(desired.y, desired.x)
        diff = (des_ang - cur_ang + math.pi) % (2 * math.pi) - math.pi
        max_turn = strength * dt
        turn = max(-max_turn, min(max_turn, diff))
        new_ang = cur_ang + turn
        self.vel = Vector2(math.cos(new_ang), math.sin(new_ang)) * (self.vel.length() or 1)

    def integrate(self, dt):
        # constant-speed travel: keep direction, set magnitude from speed stat
        target = self.speed * cfg.SPEED_TO_PXPS
        if self.vel.length_squared() == 0:
            self.vel = Vector2(1, 0)
        self.vel = self.vel.normalize() * target
        self.pos += self.vel * dt

        if self.boosting:
            self.trail.push(self.pos)
        else:
            self.trail.clear()

    def take_damage(self, amount):
        self.health = max(0.0, self.health - amount)

    # ---- drawing -----------------------------------------------------------
    def draw(self, surface, font):
        if self.boosting:
            self.trail.draw(surface, self.color, self.radius)
        pygame.draw.circle(surface, self.color_dk, self.pos, self.radius + 2)
        pygame.draw.circle(surface, self.color, self.pos, self.radius)
        label = font.render(str(int(round(self.health))), True, self.text_color)
        surface.blit(label, label.get_rect(center=self.pos))
