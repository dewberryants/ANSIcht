import sys
import pygame

import numpy as np


class Image:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.r = np.zeros(w * h, dtype="ushort")
        self.g = np.zeros(w * h, dtype="ushort")
        self.b = np.zeros(w * h, dtype="ushort")
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
        self.image = Image(160, 80)

    def resize(self):
        pass

    def redraw(self):
        self.screen.fill((0, 0, 0))  # Fill the screen with black

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
