import pygame
from globals2 import *


# -----------------------------
# LOCAL MULTIPLAYER MANAGER
# -----------------------------

class MultiPlayer(GamePage):
    def __init__(self):
        super().__init__()

    def start_next_turn(self):
        self.start_rotating_game_boards()
