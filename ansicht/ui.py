import pygame


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
        a = round(n ** (1 / 3))
        remainder = n - a * a * a
        if index < remainder:
            # Fill the rest with b/w (even if it is redundant)
            v = index / remainder * 255
            return v, v, v
        elif remainder <= index < remainder + a * a * a:
            index -= remainder
            g = index % a
            b = (index // a) % a
            r = (index // a) // a % a
            return r / a * 255, g / a * 255, b / a * 255
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
