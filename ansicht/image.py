import pygame
import numpy as np


class Image:
    def __init__(self, w, h, font: pygame.font.Font):
        self.draw_border = False
        fs = font.size(" ")
        self.px = fs[0]
        self.aspect = fs[1] / fs[0]
        self.w, self.h = w, h
        self.bg_r = np.zeros(w * h, dtype="int32")
        self.bg_g = np.zeros(w * h, dtype="int32")
        self.bg_b = np.zeros(w * h, dtype="int32")
        self.fg_r = np.zeros(w * h, dtype="int32")
        self.fg_g = np.zeros(w * h, dtype="int32")
        self.fg_b = np.zeros(w * h, dtype="int32")
        self.s = np.zeros(w * h, dtype=("str", 1))
        self.font = font
        self.surface = None
        self.redraw()

    def redraw(self):
        py = round(self.aspect * self.px)
        self.surface = pygame.Surface((self.w * self.px, self.h * py))
        for row in range(self.h):
            for column in range(self.w):
                r, g, b, s = (int(self.bg_r[row * self.w + column]),
                              int(self.bg_g[row * self.w + column]),
                              int(self.bg_b[row * self.w + column]),
                              str(self.s[row * self.w + column]))
                pygame.draw.rect(self.surface, (r, g, b),
                                 (column * self.px, row * py, self.px, py))
                if s != " ":
                    r, g, b = (int(self.fg_r[row * self.w + column]),
                               int(self.fg_g[row * self.w + column]),
                               int(self.fg_b[row * self.w + column]))
                    srf = self.font.render(s, 1, (r, g, b))
                    srf = pygame.transform.scale(srf, (self.px, py))
                    self.surface.blit(srf, (column * self.px, row * py, self.px + 1, py + 1))
                if self.draw_border:
                    pygame.draw.rect(self.surface, (80, 80, 80),
                                     (column * self.px, row * py, self.px, py),
                                     width=1)

    def set_pixel(self, x, y, fg, bg, s):
        r, g, b = bg
        self.bg_r[y * self.w + x] = r
        self.bg_g[y * self.w + x] = g
        self.bg_b[y * self.w + x] = b
        self.s[y * self.w + x] = s
        py = round(self.px * self.aspect)
        pygame.draw.rect(self.surface, (r, g, b), (x * self.px, y * py, self.px + 1, py + 1))
        if s != " ":
            r, g, b, = fg
            self.fg_r[y * self.w + x] = r
            self.fg_g[y * self.w + x] = g
            self.fg_b[y * self.w + x] = b
            srf = self.font.render(s, 1, (r, g, b))
            srf = pygame.transform.scale(srf, (self.px, py))
            self.surface.blit(srf, (x * self.px, y * py, self.px + 1, py + 1))
        if self.draw_border:
            pygame.draw.rect(self.surface, (80, 80, 80), (x * self.px, y * py, self.px + 1, py + 1), width=1)

    def resize(self, factor):
        # Smallest zoom distance is 1x2, so we don't lose the actual pixel ratio
        self.px = round(self.px * factor) if round(self.px * factor) >= 1 else 1
        self.redraw()