"""
ansi.e -  A simple ANSI art editor.
Copyright (C) 2024 Dominik Behrens

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
import tkinter
import pygame

from tkinter.simpledialog import Dialog


class CharacterMap:
    def __init__(self, w, font: pygame.font.Font):
        self.w = w
        self.surface = None
        self.font = font
        self.cols = int(w / font.size(" ")[1])
        self.sq = round(w / self.cols)
        # Ugly hardcoded characters right now, load these externally later
        self.chars = " ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
        self.chars += "1234567890!§$%&/()=?`´+#-.,;:_'*²³{[]}\\~@<>|^°"
        self.chars += "─━│┃┄┅┆┇┈┉┊┋┌┍┎┏┐┑┒┓└┕┖┗┘┙┚┛├┝┞┟┠┡┢┣┤┥┦┧┨┩┪┫┬┭┮┯┰┱┲┳┴┵" \
                      "┶┷┸┹┺┻┼┽┾┿╀╁╂╃╄╅╆╇╈╉╊╋╌╍╎╏═║╒╓╔╕╖╗╘╙╚╛╜╝╞╟╠╡╢╣╤╥╦╧╨╩╪╫╬" \
                      "╭╮╯╰╱╲╳╴╵╶╷╸╹╺╻╼╽╾╿▀▁▂▃▄▅▆▇█▉▊▋▌▍▎▐░▒▓▔▕▖▗▘▙▚▛▜▝▞▟"
        self.h = int(len(self.chars) / self.cols) * self.sq + 5
        if len(self.chars) % self.cols > 0:
            self.h += self.sq
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
            self.surface.blit(srf, (x + .25 * self.sq, y))
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


class HistoryPalette:
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.history = list()
        self.surface = None
        self.sq = int(self.w / 6)
        self.redraw()

    def select(self, x, y):
        try:
            return self.history[6 * y + x]
        except IndexError:
            return None

    def redraw(self):
        self.surface = pygame.Surface((6 * self.sq, self.h))
        self.surface.fill((30, 35, 40))
        row, col = 0, 0
        for color in self.history:
            if col == 6:
                col = 0
                row += 1
            r, g, b = color
            pygame.draw.rect(self.surface, (r, g, b), (col * self.sq, row * self.sq, self.sq, self.sq))
            col += 1

    def remember(self, color):
        if color not in self.history:
            self.history.insert(0, color)
            if len(self.history) >= 12:
                self.history = self.history[:12]
            self.redraw()


class SettingsDialog(Dialog):
    def __init__(self, w, h):
        self.entry1, self.entry2 = None, None
        self.w, self.h = w, h
        super().__init__(None)

    def body(self, master):
        tkinter.Label(master, text="Canvas Width:").grid(row=0)
        self.entry1 = tkinter.Entry(master)
        self.entry1.insert(0, str(self.w))
        self.entry1.grid(row=0, column=1)

        tkinter.Label(master, text="Canvas Height:").grid(row=1)
        self.entry2 = tkinter.Entry(master)
        self.entry2.insert(0, str(self.h))
        self.entry2.grid(row=1, column=1)
        return self.entry1

    def apply(self):
        try:
            self.w = int(self.entry1.get())
            self.h = int(self.entry2.get())
        except ValueError:
            print("Invalid W/H")
        super().apply()

    def cancel(self, event: None = ...):
        self.withdraw()
        self.destroy()


def open_settings_dialog(w, h):
    d = SettingsDialog(w, h)
    return d.w, d.h
