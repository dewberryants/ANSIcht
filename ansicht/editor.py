import sys
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


class CharacterMap:
    def __init__(self, w, h, font: pygame.font.Font):
        self.w, self.h = w, h
        self.surface = None
        self.font = font
        self.cols = 12
        self.sq = int(w / self.cols)
        # Ugly hardcoded characters right now, load these externally later
        self.chars = " ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
        self.chars += "1234567890!§$%&/()=?`´+#-.,;:_'*²³{[]}\\~@<>|^°"
        self.chars += "─━│┃┄┅┆┇┈┉┊┋┌┍┎┏┐┑┒┓└┕┖┗┘┙┚┛├┝┞┟┠┡┢┣┤┥┦┧┨┩┪┫┬┭┮┯┰┱┲┳┴┵" \
                      "┶┷┸┹┺┻┼┽┾┿╀╁╂╃╄╅╆╇╈╉╊╋╌╍╎╏═║╒╓╔╕╖╗╘╙╚╛╜╝╞╟╠╡╢╣╤╥╦╧╨╩╪╫╬" \
                      "╭╮╯╰╱╲╳╴╵╶╷╸╹╺╻╼╽╾╿▀▁▂▃▄▅▆▇█▉▊▋▌▍▎▐░▒▓▔▕▖▗▘▙▚▛▜▝▞▟"
        self.marker = (0, 0)
        self.selected = " "
        self.redraw()

    def redraw(self):
        self.surface = pygame.Surface((self.w, self.h))
        self.surface.fill((30, 35, 40))
        x = 0
        y = 0
        for char in self.chars:
            srf = self.font.render(f"{char} ", 1, (180, 180, 180))
            if int(x) / self.sq == self.cols:
                x = 0
                y += self.sq
            self.surface.blit(srf, (x + .25 * self.sq, y + .25 * self.sq))
            if (x / self.sq, y / self.sq) == self.marker:
                pygame.draw.rect(self.surface, (0, 255, 0), (x, y, self.sq, self.sq), width=1)
            x += self.sq

    def select(self, x, y):
        try:
            self.marker = (x, y)
            self.selected = self.chars[y * self.cols + x]
            self.redraw()
        except IndexError:
            pass


class Palette:
    def __init__(self, w, h):
        self.marker_bg = (0, 0)
        self.marker_fg = (0, 0)
        self.selected_bg = (0, 0, 0)
        self.selected_fg = (0, 0, 0)
        self.cols = 12
        self.sq = int(w / self.cols)
        self.h = h
        self.surface = None
        self.redraw()

    def value(self, index):
        n = self.cols * int(self.h / self.sq)
        if index < self.cols:
            # First row is b&w
            v = round(index * 255 / self.cols)
            return v, v, v
        elif index < n:
            index -= self.cols
            n -= self.cols
            # Rest of the rows are distributed rgb
            sec = 3 * index / n
            if 0 <= sec < 1:
                g = 255 * 3 * index / n
                r = 255 - g
                return r, g, 0
            elif 1 <= sec < 2:
                b = 255 * 3 * (index - n / 3) / n
                g = 255 - b
                return 0, g, b
            elif 2 <= sec < 3:
                r = 255 * 3 * (index - 2 * n / 3) / n
                b = 255 - r
                return r, 0, b
            else:
                return 255, 255, 255
        else:
            # Something went wrong
            return 0, 0, 0

    def select(self, x, y, fg=False):
        r, g, b = self.value(self.cols * y + x)
        if fg:
            self.selected_fg = (r, g, b)
            self.marker_fg = (x, y)
        else:
            self.selected_bg = (r, g, b)
            self.marker_bg = (x, y)
        self.redraw()

    def redraw(self):
        rows = round(self.h / self.sq)
        self.surface = pygame.Surface((self.cols * self.sq, self.h))
        self.surface.fill((30, 35, 40))
        for row in range(rows):
            for column in range(self.cols):
                r, g, b = self.value(row * self.cols + column)
                pygame.draw.rect(self.surface, (r, g, b), (column * self.sq, row * self.sq, self.sq, self.sq))
                if (column, row) == self.marker_bg:
                    pygame.draw.rect(self.surface, (0, 255, 0),
                                     (column * self.sq, row * self.sq, self.sq, self.sq),
                                     width=1)
                elif (column, row) == self.marker_fg:
                    pygame.draw.rect(self.surface, (0, 0, 255),
                                     (column * self.sq, row * self.sq, self.sq, self.sq),
                                     width=1)


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

        # Default image
        self.image = Image(120, 40, self.font)
        self.cursor = None
        self.mx, self.my = (self.screen.get_width() - 320) / 2, (self.screen.get_height() - 32) / 2

        # Default Palette
        self.palette = Palette(320 * 0.9, (self.screen.get_height() - 32) / 2 - 0.1 * 320)

        # Default Character Map
        self.char_map = CharacterMap(320 * 0.9, (self.screen.get_height() - 32) / 2 - (0.8 / 3 + 0.1) * 320, self.font)

    def resize(self):
        w, h = 320 * 0.9, (self.screen.get_height() - 32) / 2 - (0.8 / 3 + 0.1) * 320
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

        def h(frac):
            return int(height * frac)

        # Basic Background Fill
        self.screen.fill((60, 65, 70), (x, 0, width, height))

        # Three squares at the top for the drawing tools:
        # Dot, Line, Square
        pygame.draw.rect(self.screen, (30, 35, 40),
                         (x + w(.05), w(.05), w(.8 / 3), w(.8 / 3)))
        pygame.draw.rect(self.screen, (30, 35, 40),
                         (x + 2 * w(.05) + w(.8 / 3), w(.05), w(.8 / 3), w(.8 / 3)))
        pygame.draw.rect(self.screen, (30, 35, 40),
                         (x + 3 * w(.05) + 2 * w(.8 / 3), w(.05), w(.8 / 3), w(.8 / 3)))

        # FG/BG palette and symbol table
        self.screen.blit(self.palette.surface, (x + w(0.05), w(0.1) + w(.8 / 3)))
        self.screen.blit(self.char_map.surface, (x + w(0.05), w(0.15) + w(.8 / 3) + self.palette.h))

    def mouse(self, event):
        if event.button == 1 or event.button == 3:
            w, h = self.screen.get_width(), self.screen.get_height()
            x, y = event.pos

            # Palette
            sx = (w - 320) + .05 * 320
            sy = (0.8 / 3 + .1) * 320
            if sx < x < w - .05 * 320 and sy < y < sy + self.palette.h:
                mapped_x, mapped_y = int((x - sx) / self.palette.sq), int((y - sy) / self.palette.sq)
                self.palette.select(mapped_x, mapped_y, event.button == 3)

            # Character Map
            sy = (0.8 / 3 + .15) * 320 + self.palette.h
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
