import pygame
import random
from globals2 import *

class Menu(Page):
    def __init__(self):
        super().__init__()

    def build(self):
        (sw, sh) = game_state.screen_dimensions
        self.create_title(sw, sh)
        self.create_buttons(sw, sh)
        super().build()

    def create_title(self, sw, sh):
        self.titles.empty()
        title_size = 0.2 if sw >= sh else 0.25
        title = UIImage("title.png", (0.5, 0.18), title_size)
        self.titles.add(title)

    def create_buttons(self, sw, sh):
        self.buttons.empty()
        size_ratio = 0.26
        start_y = 0.55

        labels_callbacks = [
            ("settings.png", "settings_clicked.png", lambda: switch_scene("settings")),
            ("single_player.png", "single_player_clicked.png", lambda: switch_scene("single_player_continue_game")),
            ("local_multiplayer.png", "local_multiplayer_clicked.png", lambda: switch_scene("multiplayer_continue_game"))
        ]
        if sw >= sh:
            pos_ratios = [(0.5 + (i-1) * (size_ratio*0.8), start_y) for i in range(3)]
        else:
            pos_ratios = [(0.5, 0.425), (0.3, 0.65), (0.7, 0.65)]

        for i, (image_path, clicked_image_path, callback) in enumerate(labels_callbacks):
            pos_ratio = pos_ratios[i]
            angle = random.randint(-20, 20)
            button = UIButton(pos_ratio, size_ratio, image_path, clicked_image_path, angle, callback)
            self.buttons.add(button)

        # Decorative blank buttons (use ratios instead of absolute px)
        if sw >= sh:
            blank_coords = [
                (0.01, 0.2),
                (0.2, 0.18),
                (0.8, 0.18),
                (0.98, 0.02),
                (0.1, 0.7),
                (0.42, 0.95),
                (0.85, 0.83),
                (0.97, 0.45)]
        else:
            blank_coords = [
                (0.05, 0.01),
                (0.1, 0.4),
                (0.2, 0.9),
                (0.52, 0.99),
                (0.92, 0.83),
                (0.98, 0.02),
                (0.97, 0.45)]

        tile_images = ["red_tile.png", "blue_tile.png", "green_tile.png", "yellow_tile.png", "purple_tile.png"]

        for pos_ratio in blank_coords:
            angle = random.randint(-20, 20)
            image_path = random.choice(tile_images)
            button = UIButton(pos_ratio, size_ratio, image_path, angle=angle)
            self.buttons.add(button)