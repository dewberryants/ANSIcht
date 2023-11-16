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

        # Mouse speed
        self.last_x, self.last_y = None, None

        # Default image
        self.image = Image(120, 40)
        self.cursor = None
        self.mx, self.my = (self.screen.get_width() - 320) / 2, (self.screen.get_height() - 32) / 2
        self.ps = (10, 20)

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

    def zoom(self, event):
        neg = event.precise_y < 0
        factor = 0.5 if neg else 1.5
        # Smallest zoom distance is 1x2, so we don't lose the actual pixel ratio
        newx = round(self.ps[0] * factor) if round(self.ps[0] * factor) >= 1 else 1
        self.ps = (newx, 2 * newx)

    def redraw(self):
        w, h = self.screen.get_width(), self.screen.get_height()

        self.screen.fill((0, 0, 0))

        # Image Grid
        psx, psy = self.ps
        sx, sy = self.mx - self.image.w / 2 * psx, self.my - self.image.h / 2 * psy
        for row in range(self.image.h):
            for column in range(self.image.w):
                r, g, b = (int(self.image.r[row * self.image.w + column]),
                           int(self.image.g[row * self.image.w + column]),
                           int(self.image.b[row * self.image.w + column]))
                pygame.draw.rect(self.screen, (r, g, b),
                                 (sx + column * psx, sy + row * psy, psx + 1, psy + 1))
                pygame.draw.rect(self.screen, (80, 80, 80),
                                 (sx + column * psx, sy + row * psy, psx + 1, psy + 1),
                                 width=1)

        # Interface
        self.screen.fill((60, 65, 70), (w - 320, 0, w, h))
        self.screen.fill((80, 85, 90), (0, h - 32, w, h))

        # Selection
        x, y = pygame.mouse.get_pos()
        if self.last_x and self.last_y:
            dx, dy = x - self.last_x, y - self.last_y
        else:
            dx, dy = 0, 0
        if sx < x < sx + self.image.w * psx and sy < y < sy + self.image.h * psy:
            self.cursor = mapped_x, mapped_y = int((x - sx) / psx), int((y - sy) / psy)
            pygame.draw.rect(self.screen, (200, 200, 200), (sx + mapped_x * psx, sy + mapped_y * psy, psx, psy),
                             width=1)
            self.screen.blit(self.font.render(f"({mapped_x: 6d},{mapped_y: 6d})", 1, (200, 200, 200)), (16, h - 24))
            # Are we drawing?
            if pygame.mouse.get_pressed(3)[0]:
                self.image.r[self.image.w * mapped_y + mapped_x] = 255
            elif pygame.mouse.get_pressed(3)[2]:
                self.image.r[self.image.w * mapped_y + mapped_x] = 0
            # Are we moving the image around?
            elif pygame.mouse.get_pressed(3)[1]:
                self.mx += 0.5 * dx
                self.my += 0.5 * dy

        # Update last mouse position
        self.last_x, self.last_y = x, y

        # Flip display with the finished surface
        pygame.display.flip()

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.WINDOWRESIZED:
                    self.resize()
                elif event.type == pygame.MOUSEWHEEL:
                    self.zoom(event)
            self.redraw()
            self.clock.tick(60)
