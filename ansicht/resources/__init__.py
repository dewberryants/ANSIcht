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

from importlib.resources import files

icon_open = pygame.image.frombytes(
    files('ansicht.resources').joinpath('open.bin').read_bytes(), (32, 32), 'RGBA'
)
icon_settings = pygame.image.frombytes(
    files('ansicht.resources').joinpath('settings.bin').read_bytes(), (32, 32), 'RGBA'
)
icon_save = pygame.image.frombytes(
    files('ansicht.resources').joinpath('save.bin').read_bytes(), (32, 32), 'RGBA'
)

__all__ = [icon_open, icon_settings, icon_save]
