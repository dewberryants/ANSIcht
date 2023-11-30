"""
ANSIcht -  A simple ANSI art editor.
Copyright (C) 2023 Dominik Behrens

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the Lesser GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import sys
import pygame

from image import Image
from ui import Palette, CharacterMap


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

        # Font
        # Try some of these before giving up
        self.font = pygame.font.SysFont(pygame.font.get_default_font(), 21)
        monospace_fonts = ["Hack", "Consolas", "Lucida Console", "Courier New"]
        for font in monospace_fonts:
            path = pygame.font.match_font(font)
            if path is not None:
                self.font = pygame.font.Font(path, 16)
                break

        # Icon Square sizes
        self.w_icons = 0.4 / 3 * 320

        # Default image
        self.image = Image(120, 40, self.font)
        self.cursor = None
        self.mx, self.my = (self.screen.get_width() - 320) / 2, (self.screen.get_height() - 32) / 2

        # Default Palette
        self.palette = Palette(320 * 0.9, (self.screen.get_height() - 32) / 2 - .1 * 320)

        # Default Character Map
        self.char_map = CharacterMap(320 * .9,
                                     (self.screen.get_height() - 32) / 2 - .1 * 320 - self.w_icons, self.font)

    def resize(self):
        w, h = 320 * 0.9, (self.screen.get_height() - 32) / 2 - .1 * 320 - self.w_icons
        self.palette.sq = int(w / self.palette.cols)
        self.palette.h = h
        self.palette.redraw()
        self.char_map.w, self.char_map.h = w, h
        self.char_map.redraw()
        pass

    def zoom(self, event):
        neg = event.precise_y < 0
        factor = 0.5 if neg else 1.5
        self.image.resize(factor)

    def draw_sidebar(self, x, width, height):
        def w(frac):
            return int(width * frac)

        # Basic Background Fill
        self.screen.fill((60, 65, 70), (x, 0, width, height))

        # Three squares at the top for the drawing tools:
        # Dot, Line, Square
        pygame.draw.rect(self.screen, (30, 35, 40),
                         (x + w(.05), w(.05), self.w_icons, self.w_icons))
        pygame.draw.rect(self.screen, (30, 35, 40),
                         (x + 2 * w(.05) + self.w_icons, w(.05), self.w_icons, self.w_icons))

        # FG/BG palette and symbol table
        self.screen.blit(self.palette.surface, (x + w(0.05), w(0.1) + self.w_icons))
        self.screen.blit(self.char_map.surface, (x + w(0.05), w(0.15) + self.w_icons + self.palette.h))

    def mouse(self, event):
        if event.button == 1 or event.button == 3:
            w, h = self.screen.get_width(), self.screen.get_height()
            x, y = event.pos

            # Palette
            sx = (w - 320) + .05 * 320
            sy = .1 * 320 + self.w_icons
            if sx < x < w - .05 * 320 and sy < y < sy + self.palette.h:
                mapped_x, mapped_y = int((x - sx) / self.palette.sq), int((y - sy) / self.palette.sq)
                self.palette.select(mapped_x, mapped_y, event.button == 3)

            # Character Map
            sy = .15 * 320 + self.w_icons + self.palette.h
            if sx < x < w - .05 * 320 and sy < y < sy + self.char_map.h:
                mapped_x, mapped_y = int((x - sx) / self.char_map.sq), int((y - sy) / self.char_map.sq)
                self.char_map.select(mapped_x, mapped_y)

    def redraw(self):
        w, h = self.screen.get_width(), self.screen.get_height()

        self.screen.fill((30, 33, 35))

        # Image Grid
        psx, psy = self.image.px, round(self.image.aspect * self.image.px)
        sx, sy = self.mx - self.image.w / 2 * psx, self.my - self.image.h / 2 * psy
        self.screen.blit(self.image.surface, (sx, sy))

        # Sidebar
        self.draw_sidebar(w - 320, 320, h - 32)

        # Status Bar
        self.screen.fill((80, 85, 90), (0, h - 32, w, h))

        # Selection
        x, y = pygame.mouse.get_pos()
        dx, dy = pygame.mouse.get_rel()
        if sx < x < sx + self.image.w * psx and sy < y < sy + self.image.h * psy:
            self.cursor = mapped_x, mapped_y = int((x - sx) / psx), int((y - sy) / psy)
            pygame.draw.rect(self.screen, (200, 200, 200), (sx + mapped_x * psx, sy + mapped_y * psy, psx, psy),
                             width=1)
            self.screen.blit(self.font.render(f"({mapped_x + 1: 6d},{mapped_y + 1: 6d}) ",
                                              1, (200, 200, 200)), (16, h - 24))
            # Are we drawing?
            if pygame.mouse.get_pressed(3)[0]:
                self.image.set_pixel(mapped_x, mapped_y,
                                     self.palette.selected_fg, self.palette.selected_bg, self.char_map.selected)
            elif pygame.mouse.get_pressed(3)[2]:
                self.image.set_pixel(mapped_x, mapped_y, (0, 0, 0), (0, 0, 0), " ")
            # Are we moving the image around?
            elif pygame.mouse.get_pressed(3)[1]:
                self.mx += 0.5 * dx
                self.my += 0.5 * dy

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
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.mouse(event)
            self.redraw()
            self.clock.tick(60)
