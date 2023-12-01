import pygame

from importlib.resources import files

icon_open = pygame.image.frombytes(
    files('resources').joinpath('open.bin').read_bytes(), (32, 32), 'RGBA'
)
icon_settings = pygame.image.frombytes(
    files('resources').joinpath('settings.bin').read_bytes(), (32, 32), 'RGBA'
)
icon_save = pygame.image.frombytes(
    files('resources').joinpath('save.bin').read_bytes(), (32, 32), 'RGBA'
)

__all__ = [icon_open, icon_settings, icon_save]
