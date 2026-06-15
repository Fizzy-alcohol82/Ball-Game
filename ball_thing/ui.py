"""Heads-up display: the names, the two charge bars, the stat readout, and
the end-of-fight banner. Pure rendering, no game logic.
"""
import pygame

from . import config as cfg


class HUD:
    def __init__(self, fonts):
        self.f_name = fonts["name"]
        self.f_label = fonts["label"]
        self.f_stat = fonts["stat"]
        self.f_big = fonts["big"]

    def _outlined(self, text, font, color):
        base = font.render(text, True, color)
        out = pygame.Surface((base.get_width() + 4, base.get_height() + 4), pygame.SRCALPHA)
        edge = font.render(text, True, (255, 255, 255))
        for dx, dy in ((0, 0), (2, 0), (0, 2), (2, 2)):
            out.blit(edge, (dx, dy))
        out.blit(base, (1, 1))
        return out

    def draw_names(self, surface, mach, stasis):
        left = self._outlined(mach.name, self.f_name, mach.color)
        surface.blit(left, (cfg.ARENA_MARGIN_X, 28))
        right = self._outlined(stasis.name, self.f_name, cfg.STASIS_GRAY_DK)
        surface.blit(right, right.get_rect(topright=(cfg.WIDTH - cfg.ARENA_MARGIN_X, 28)))

    def _meter(self, surface, x, y, w, ability, align_right=False):
        h = 22
        pygame.draw.rect(surface, cfg.METER_TRACK, (x, y, w, h), border_radius=4)
        fill_w = int(w * ability.charge)
        if fill_w > 0:
            fx = x + w - fill_w if align_right else x
            pygame.draw.rect(surface, ability.fill_color, (fx, y, fill_w, h), border_radius=4)
        pygame.draw.rect(surface, cfg.ARENA_LINE, (x, y, w, h), 2, border_radius=4)
        lbl = self.f_label.render(ability.label, True, cfg.INK)
        if align_right:
            surface.blit(lbl, lbl.get_rect(midright=(x + w - 8, y + h // 2)))
        else:
            surface.blit(lbl, lbl.get_rect(midleft=(x + 8, y + h // 2)))

    def draw_meters(self, surface, mach, stasis):
        y = cfg.ARENA_BOTTOM + 28
        w = (cfg.WIDTH - 2 * cfg.ARENA_MARGIN_X - 16) // 2
        self._meter(surface, cfg.ARENA_MARGIN_X, y, w, mach.ability)
        self._meter(surface, cfg.WIDTH - cfg.ARENA_MARGIN_X - w, y, w, stasis.ability, align_right=True)

    def draw_stats(self, surface, focus):
        """Show the focal fighter's live (effective) stats, like the videos."""
        y = cfg.ARENA_BOTTOM + 64
        dmg = self.f_stat.render(f"Damage: {focus.damage:.2f}", True, focus.color)
        spd = self.f_stat.render(f"Speed: {focus.speed:.2f}", True, focus.color)
        surface.blit(dmg, (cfg.ARENA_MARGIN_X, y))
        surface.blit(spd, (cfg.ARENA_MARGIN_X, y + 26))
        atk = self.f_stat.render(f"Attack Speed: {focus.attack_speed:.2f}", True, cfg.STASIS_GRAY_DK)
        surface.blit(atk, atk.get_rect(topright=(cfg.WIDTH - cfg.ARENA_MARGIN_X, y + 13)))

    def draw_banner(self, surface, winner):
        overlay = pygame.Surface((cfg.WIDTH, cfg.HEIGHT), pygame.SRCALPHA)
        overlay.fill((255, 255, 255, 170))
        surface.blit(overlay, (0, 0))
        title = self.f_big.render(f"{winner.name} wins", True, winner.color)
        surface.blit(title, title.get_rect(center=(cfg.WIDTH // 2, cfg.HEIGHT // 2 - 20)))
        sub = self.f_stat.render("press R to run it back", True, cfg.MUTED)
        surface.blit(sub, sub.get_rect(center=(cfg.WIDTH // 2, cfg.HEIGHT // 2 + 24)))
