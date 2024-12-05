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
import pygame
import numpy as np


class Image:
    def __init__(self, w, h, font: pygame.font.Font):
        self.draw_border = False
        fs = font.size(" ")
        self.px = fs[0]
        self.aspect = fs[1] / fs[0]
        self.w, self.h = w, h
        self.bg_r = np.zeros(w * h, dtype="u4")
        self.bg_g = np.zeros(w * h, dtype="u4")
        self.bg_b = np.zeros(w * h, dtype="u4")
        self.fg_r = np.zeros(w * h, dtype="u4")
        self.fg_g = np.zeros(w * h, dtype="u4")
        self.fg_b = np.zeros(w * h, dtype="u4")
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
        if self.px * 0.8 < self.font.size(" ")[0] < self.px * 1.2:
            self.px = self.font.size(" ")[0]
        self.redraw()

    def save_to_file(self, path):
        with open(path, "w", encoding="utf-8") as ofile:
            last_fg = ""
            last_bg = ""
            for n in range(self.w * self.h):
                s = " " if str(self.s[n]) == "" else str(self.s[n])
                fg = f"\x1b[38;2;{self.fg_r[n]};{self.fg_g[n]};{self.fg_b[n]}m"
                bg = f"\x1b[48;2;{self.bg_r[n]};{self.bg_g[n]};{self.bg_b[n]}m"
                if fg != last_fg:
                    s = fg + s
                if bg != last_bg:
                    s = bg + s
                if n % self.w == 0:
                    s += "\x1b[0m\n" + bg + fg
                ofile.write(s)
                last_fg = fg
                last_bg = bg


def load_image_from_file(path, font) -> Image:
    with open(path, "r", encoding="utf-8") as ifile:
        data = dict()
        index = 0
        row = 0
        char = ifile.read(1)
        last_bg = (0, 0, 0)
        last_fg = (0, 0, 0)
        while char != "":
            if char == "\n":
                row += 1
                char = ifile.read(1)
                continue
            # FG r g b, BG r g b, s
            if index not in data:
                bgr, bgg, bgb = last_bg
                fgr, fgg, fgb = last_fg
                data[index] = [fgr, fgg, fgb, bgr, bgg, bgb, ""]
            if char == "\x1b":
                tag = ""
                while char != "m":
                    tag += char
                    char = ifile.read(1)
                spl = list(map(int, tag[2:].split(";")))
                if spl[0] == 38:
                    data[index][0] = spl[2]
                    data[index][1] = spl[3]
                    data[index][2] = spl[4]
                    last_fg = (spl[2], spl[3], spl[4])
                elif spl[0] == 48:
                    data[index][3] = spl[2]
                    data[index][4] = spl[3]
                    data[index][5] = spl[4]
                    last_bg = (spl[2], spl[3], spl[4])
            else:
                data[index][6] = char
                index += 1
            char = ifile.read(1)
        img = Image(int(index/row), row, font)
        for n, key in enumerate(data):
            entry = data[key]
            img.fg_r[n] = entry[0]
            img.fg_g[n] = entry[1]
            img.fg_b[n] = entry[2]
            img.bg_r[n] = entry[3]
            img.bg_g[n] = entry[4]
            img.bg_b[n] = entry[5]
            img.s[n] = entry[6]
        img.redraw()
        return img
