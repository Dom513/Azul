# settings.py
import pygame
import random
from globals2 import *

class Settings(Page):
    def __init__(self):
        super().__init__()

    def build(self, change_angles=True):
        (sw, sh) = game_state.screen_dimensions
        self.create_title(sw, sh)
        self.create_text(sw, sh)
        self.create_buttons(sw, sh, change_angles)
        super().build()

    def create_title(self, sw, sh):
        self.titles.empty()
        title_coord = (0.5, 0.18) if sw >= sh else (0.5, 0.2)
        title = UIImage("settings_title.png", title_coord, 0.15)
        self.titles.add(title)

    def create_text(self, sw, sh):
        self.texts.empty()
        text_size = 0.07 if sw >= sh else 0.09
        mode_text_coord = (0.27, 0.5) if sw >= sh else (0.5, 0.35)
        mode_text = UIText("Light/Dark Mode", mode_text_coord, text_size)
        difficulty_text_coord = (0.73, 0.5) if sw >= sh else (0.5, 0.65)
        difficulty_text = UIText("CPU Difficulty", difficulty_text_coord, text_size)
        self.texts.add(mode_text, difficulty_text)

    def create_buttons(self, sw, sh, change_angles):
        angles = [button.angle for button in self.buttons] if not change_angles else None
        self.buttons.empty()

        button_size_ratio = 0.2

        ratio_from_top = 0.15 if sw >= sh else 0.15*sw/sh
        top_left_pos_ratio = GetEqualTopLeftRatio("top", ratio_from_top)

        labels_callbacks = [
            ("light", self.toggle_mode_light, (0.2, 0.7) if sw >= sh else (0.35, 0.45), button_size_ratio),
            ("dark", self.toggle_mode_dark, (0.34, 0.7) if sw >= sh else (0.65, 0.45), button_size_ratio),
            ("easy", self.toggle_difficulty_easy, (0.66, 0.7) if sw >= sh else (0.35, 0.75), button_size_ratio),
            ("hard", self.toggle_difficulty_hard, (0.8, 0.7) if sw >= sh else (0.65, 0.75), button_size_ratio),
            ("menu", lambda: switch_scene("menu"), top_left_pos_ratio, button_size_ratio * 0.75)
        ]

        possible_images = {
            "light": ("light_mode.png", "light_mode_clicked.png"),
            "dark": ("dark_mode.png", "dark_mode_clicked.png"),
            "easy": ("difficulty_easy.png", "difficulty_easy_clicked.png"),
            "hard": ("difficulty_hard.png", "difficulty_hard_clicked.png"),
            "menu": ("main_menu.png", "main_menu_clicked.png")
        }

        for i, (button_key, callback, pos_ratio, size_ratio) in enumerate(labels_callbacks):
            image_path, clicked_image_path = possible_images[button_key]
            angle = angles[i] if angles else random.randint(-20, 20)
            button = UIButton(pos_ratio, size_ratio, image_path, clicked_image_path, angle, callback)
            self.buttons.add(button)
            if game_state.mode == button_key:
                button.always_show_glow=True
            if game_state.difficulty == button_key:
                button.always_show_glow = True

    def toggle_mode_dark(self):
        game_state.mode = "dark"
        game_state.get_background()
        self.build(change_angles=False)

    def toggle_mode_light(self):
        game_state.mode = "light"
        game_state.get_background()
        self.build(change_angles=False)

    def toggle_difficulty_easy(self):
        game_state.difficulty ="easy"
        self.build(change_angles=False)

    def toggle_difficulty_hard(self):
        game_state.difficulty = "hard"
        self.build(change_angles=False)
