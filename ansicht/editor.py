import sys
import pygame

import numpy as np


class Image:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.r = np.zeros(w * h, dtype="int32")
        self.g = np.zeros(w * h, dtype="int32")
        self.b = np.zeros(w * h, dtype="int32")
        self.s = np.zeros(w * h, dtype=("str", 1))


class Editor:
    def __init__(self):
        pygame.init()

        # Initial window size
        window_sizes = pygame.display.get_desktop_sizes()
        pixels = [tup[0] * tup[1] for tup in window_sizes]
        biggest = pixels.index(max(pixels))
        self.w, self.h = window_sizes[biggest]

        # Setup display and clock
        self.screen = pygame.display.set_mode((.8 * self.w, .8 * self.h), pygame.RESIZABLE)
        pygame.display.set_caption("ANSIcht")

        # Clock
        self.clock = pygame.time.Clock()

        # Default image
        self.image = Image(120, 40)
        self.cursor = None

        # Font
        # Try some of these before giving up
        self.font = pygame.font.SysFont(pygame.font.get_default_font(), 21)
        monospace_fonts = ["Hack", "Consolas", "Lucida Console", "Courier New"]
        for font in monospace_fonts:
            path = pygame.font.match_font(font)
            if path is not None:
                self.font = pygame.font.Font(path, 16)
                break

    def resize(self):
        pass

    def redraw(self):
        w, h = self.screen.get_width(), self.screen.get_height()

        # Interface
        self.screen.fill((0, 0, 0))
        self.screen.fill((60, 65, 70), (w - 320, 0, w, h))
        self.screen.fill((80, 85, 90), (0, h - 32, w, h))

        # Grid
        mx, my = (w - 320) / 2, (h - 32) / 2
        sx, sy = mx - self.image.w / 2 * 10, my - self.image.h / 2 * 20
        for row in range(self.image.h):
            for column in range(self.image.w):
                r, g, b = (int(self.image.r[row * self.image.w + column]),
                           int(self.image.g[row * self.image.w + column]),
                           int(self.image.b[row * self.image.w + column]))
                pygame.draw.rect(self.screen, (r, g, b),
                                 (sx + column * 10, sy + row * 20, 11, 21))
                pygame.draw.rect(self.screen, (80, 80, 80),
                                 (sx + column * 10, sy + row * 20, 11, 21),
                                 width=1)

        # Selection
        x, y = pygame.mouse.get_pos()
        if sx < x < sx + self.image.w * 10 and sy < y < sy + self.image.h * 20:
            self.cursor = mapped_x, mapped_y = int((x - sx) / 10), int((y - sy) / 20)
            pygame.draw.rect(self.screen, (200, 200, 200), (sx + mapped_x * 10, sy + mapped_y * 20, 10, 20), width=1)
            self.screen.blit(self.font.render(f"({mapped_x: 6d},{mapped_y: 6d})", 1, (200, 200, 200)), (16, h - 24))
            # Are we drawing?
            if pygame.mouse.get_pressed(3)[0]:
                self.image.r[self.image.w * mapped_y + mapped_x] = 255
            elif pygame.mouse.get_pressed(3)[2]:
                self.image.r[self.image.w * mapped_y + mapped_x] = 0

        # Flip display with the finished surface
        pygame.display.flip()

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.WINDOWRESIZED:
                    self.resize()
            self.redraw()
            self.clock.tick(60)
