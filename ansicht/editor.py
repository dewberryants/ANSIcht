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
import os.path
import sys
import pygame

from ansicht.image import Image, load_image_from_file
from ansicht.ui import Palette, CharacterMap, open_settings_dialog
from tkinter import Tk, filedialog

from ansicht.resources import icon_open, icon_save, icon_settings


class Editor:
    def __init__(self):
        pygame.init()

        # Initial window size
        window_sizes = pygame.display.get_desktop_sizes()
        pixels = [tup[0] * tup[1] for tup in window_sizes]
        biggest = pixels.index(max(pixels))
        self.w, self.h = window_sizes[biggest]

        # Setup display and clock
        pygame.display.set_icon(pygame.Surface((32, 32), flags=pygame.SRCALPHA))
        self.screen = pygame.display.set_mode((.8 * self.w, .8 * self.h), pygame.RESIZABLE)
        pygame.display.set_caption("ANSIcht")

        # Clock
        self.clock = pygame.time.Clock()

        # Font
        # Try some of these before giving up
        self.font_size = 16
        self.font_name = pygame.font.get_default_font()
        monospace_fonts = ["Hack", "Consolas", "Lucida Console", "Courier New"]
        for font in monospace_fonts:
            path = pygame.font.match_font(font)
            if os.path.exists(path):
                self.font_name = path
            break
        self.font = pygame.font.Font(self.font_name, self.font_size)

        # Hidden TKInter Root node for file dialogs
        Tk().withdraw()

        # Icon Square sizes
        self.w_icons = 48

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

    def brush_preview(self):
        srf = pygame.Surface((self.w_icons, self.w_icons))
        txt = self.font.render(self.char_map.selected, 1, self.palette.selected_fg)
        srf.fill(self.palette.selected_bg)
        sx = round((self.w_icons - txt.get_width()) / 2)
        sy = round((self.w_icons - txt.get_height()) / 2)
        srf.blit(txt, (sx, sy))
        return srf

    def draw_sidebar(self, x, width, height):
        def w(frac):
            return int(width * frac)

        # Basic Background Fill
        self.screen.fill((60, 65, 70), (x, 0, width, height))

        # Open, Save, Options, etc.
        self.screen.blit(icon_open, (x + w(.05) + .2 * self.w_icons, w(.05) + .2 * self.w_icons))
        self.screen.blit(icon_save, (x + w(.1) + (.2 + 1) * self.w_icons, w(.05) + .2 * self.w_icons))
        self.screen.blit(icon_settings, (x + w(.15) + (.2 + 2) * self.w_icons, w(.05) + .2 * self.w_icons))

        # FG/BG palette and symbol table
        self.screen.blit(self.palette.surface, (x + w(0.05), w(0.1) + self.w_icons))
        self.screen.blit(self.char_map.surface, (x + w(0.05), w(0.15) + self.w_icons + self.palette.h))

        # Drawing Preview
        self.screen.blit(self.brush_preview(), (x + w(.2) + 4 * self.w_icons, w(.05)))

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

            # Open Button
            sy = .05 * 320
            if sx < x < sx + self.w_icons and sy < y < sy + self.w_icons:
                f = filedialog.askopenfilename(filetypes=[("ANSI File", "*.ans")],
                                               title="Open...")
                try:
                    if type(f) is str:
                        self.image = load_image_from_file(str(f), self.font)
                        print(f"Opened file '{f}'!")
                    else:
                        raise IOError
                except IOError:
                    print(f"Could not load from file '{f}'!")
                except UnicodeDecodeError:
                    print(f"Could not decode character. This should not happen :(")

            # Save Button
            sx = (w - 320) + .1 * 320 + self.w_icons
            if sx < x < sx + self.w_icons and sy < y < sy + self.w_icons:
                f = filedialog.asksaveasfilename(confirmoverwrite=True,
                                                 filetypes=[("ANSI File", "*.ans")],
                                                 title="Save As...",
                                                 defaultextension=".ans")
                try:
                    if type(f) is str:
                        self.image.save_to_file(f)
                        print(f"Saved to file '{f}'!")
                    else:
                        raise IOError()
                except IOError:
                    print(f"Could not save to file '{f}'!")
                except UnicodeEncodeError:
                    print(f"Could not encode character. This should not happen :(")

            # Settings Button
            sx = (w - 320) + .15 * 320 + 2 * self.w_icons
            if sx < x < sx + self.w_icons and sy < y < sy + self.w_icons:
                new_w, new_h = open_settings_dialog(self.image.w, self.image.h)
                if new_w != self.image.w or new_h != self.image.h:
                    self.image = Image(new_w, new_h, self.font)

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
        if sx < x < sx + self.image.w * psx and sy < y < sy + self.image.h * psy and x < w - 320:
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
                # Pick color and symbol from image
                i = mapped_y * self.image.w + mapped_x
                self.palette.selected_fg = (self.image.fg_r[i], self.image.fg_g[i], self.image.fg_b[i])
                self.palette.selected_bg = (self.image.bg_r[i], self.image.bg_g[i], self.image.bg_b[i])
                self.char_map.selected = self.image.s[i]
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
