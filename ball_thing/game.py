"""The Game ties the components together and owns the loop.

Each frame: reset multipliers -> let active abilities stamp their multipliers
-> move + collide -> resolve weapon hits -> update meters/effects -> render.
The fight is a simulation (auto-battler), matching the source videos; the only
input is pause / restart / quit.
"""
import sys
import pygame

from . import config as cfg
from . import physics
from .arena import Arena
from .entities import Fighter
from .abilities import FullThrottle, WorldStasis
from .effects import ParticleSystem
from .ui import HUD


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((cfg.WIDTH, cfg.HEIGHT))
        pygame.display.set_caption("Ball Thing")
        self.clock = pygame.time.Clock()
        self.fonts = self._load_fonts()
        self.hud = HUD(self.fonts)
        self.arena = Arena()
        self.paused = False
        self.winner = None
        self.reset()

    def _load_fonts(self):
        def f(size, bold=True):
            return pygame.font.SysFont("dejavusans,arial", size, bold=bold)
        return {
            "name": f(40), "label": f(13), "stat": f(20),
            "big": f(48), "ball": f(20), "mark": f(16),
        }

    def reset(self):
        ax, ay, aw, ah = cfg.ARENA
        self.mach = Fighter(cfg.MACH, (ax + aw * 0.25, ay + ah * 0.5))
        self.stasis = Fighter(cfg.STASIS, (ax + aw * 0.75, ay + ah * 0.5))
        self.mach.ability = FullThrottle(self.mach)
        self.stasis.ability = WorldStasis(self.stasis)
        self.fighters = [self.mach, self.stasis]
        self.particles = ParticleSystem()
        self.winner = None
        self.paused = False

    # ---- simulation step ---------------------------------------------------
    def update(self, dt):
        if self.winner or self.paused:
            return

        for fr in self.fighters:
            fr.reset_mults()

        # abilities tick first, then stamp their multipliers for this frame
        self.mach.ability.update(dt)
        self.stasis.ability.update(dt)
        if self.mach.ability.active:
            self.mach.ability.apply(self.stasis)
        if self.stasis.ability.active:
            self.stasis.ability.apply(self.mach)

        self.mach.steer_toward(self.stasis.pos, dt, cfg.STEER_STRENGTH)
        self.stasis.steer_toward(self.mach.pos, dt, cfg.STEER_STRENGTH)
        for fr in self.fighters:
            fr.integrate(dt)
            physics.confine_to_arena(fr)
            fr.weapon.update(dt)
        physics.collide_pair(self.mach, self.stasis)

        self._resolve_hit(self.mach, self.stasis)
        self._resolve_hit(self.stasis, self.mach)

        self.particles.update(dt)

        for fr in self.fighters:
            if not fr.alive:
                self.winner = self.stasis if fr is self.mach else self.mach

    def _resolve_hit(self, attacker, defender):
        dmg = attacker.weapon.try_hit(defender)
        if dmg > 0:
            defender.take_damage(dmg)
            self.particles.burst(attacker.weapon.tip, cfg.HIT_SPARK, count=12)
            attacker.ability.add_charge(cfg.CHARGE_ON_DEAL)
            defender.ability.add_charge(cfg.CHARGE_ON_TAKE)

    # ---- render ------------------------------------------------------------
    def draw(self):
        self.screen.fill(cfg.BG)
        self.arena.draw(self.screen, self.fonts["mark"])
        prev = self.screen.get_clip()
        self.screen.set_clip(self.arena.rect)
        for fr in self.fighters:
            fr.weapon.draw(self.screen)
        for fr in self.fighters:
            fr.draw(self.screen, self.fonts["ball"])
        self.particles.draw(self.screen)
        self.screen.set_clip(prev)

        self.hud.draw_names(self.screen, self.mach, self.stasis)
        self.hud.draw_meters(self.screen, self.mach, self.stasis)
        self.hud.draw_stats(self.screen, self.mach)
        if self.winner:
            self.hud.draw_banner(self.screen, self.winner)
        pygame.display.flip()

    # ---- input + loop ------------------------------------------------------
    def handle_events(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return False
            if e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_ESCAPE, pygame.K_q):
                    return False
                if e.key == pygame.K_r:
                    self.reset()
                if e.key == pygame.K_SPACE:
                    self.paused = not self.paused
        return True

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(cfg.FPS) / 1000.0
            dt = min(dt, 1 / 30)   # clamp big hitches so physics stays sane
            running = self.handle_events()
            self.update(dt)
            self.draw()
        pygame.quit()
        sys.exit()
