import pygame
import random
from pygame.locals import *
from globals import Button, large_tile_images, base_path

# Images
title = pygame.image.load(base_path / 'resources' / "title.png")

single_player_image = pygame.image.load(base_path / 'resources' / "single_player.png").convert_alpha()
single_player_clicked = pygame.image.load(base_path / 'resources' / "single_player_clicked.png").convert_alpha()
local_multiplayer_image = pygame.image.load(base_path / 'resources' / "local_multiplayer.png").convert_alpha()
local_multiplayer_clicked = pygame.image.load(base_path / 'resources' / "local_multiplayer_clicked.png").convert_alpha()
settings_image = pygame.image.load(base_path / 'resources' / "settings.png").convert_alpha()
settings_clicked = pygame.image.load(base_path / 'resources' / "settings_clicked.png").convert_alpha()


# Menu functions
def to_single_player(game_state):
    game_state.new_single_player=True
    game_state.menu_running=False
def to_local_multiplayer(game_state):
    game_state.new_local_multiplayer=True
    game_state.menu_running=False
def to_settings(game_state):
    game_state.new_settings=True
    game_state.menu_running=False


def create_menu(game_state):
    screen_width = game_state.screen_width
    screen_height = game_state.screen_height
    button_height = screen_height*0.25

    single_player_button = Button(button_height, (screen_width*0.5,screen_height*0.6),
                                        single_player_image, single_player_clicked,
                                        action=to_single_player)
    local_multiplayer_button = Button(button_height, (screen_width*0.7,screen_height*0.58),
                                        local_multiplayer_image, local_multiplayer_clicked,
                                        action=to_local_multiplayer)
    settings_button = Button(button_height, (screen_width*0.3,screen_height*0.58),
                                        settings_image, settings_clicked,
                                        action=to_settings)

    tile_1 = Button(button_height,  (screen_width*0.97,screen_height*0.45),     random.choice(list(large_tile_images.values())))
    tile_2 = Button(button_height,  (screen_width*0.85,screen_height*0.83),     random.choice(list(large_tile_images.values())))
    tile_3 = Button(button_height,  (screen_width*0.03,screen_height*0.15),     random.choice(list(large_tile_images.values())))
    tile_4 = Button(button_height,  (screen_width*0.42,screen_height*0.95),     random.choice(list(large_tile_images.values())))
    tile_5 = Button(button_height,  (screen_width*0.1,screen_height*0.7),       random.choice(list(large_tile_images.values())))
    tile_6 = Button(button_height,  (screen_width*0.98,screen_height*0.02),     random.choice(list(large_tile_images.values())))
    tile_7 = Button(button_height,  (screen_width*0.2,screen_height*0.18),     random.choice(list(large_tile_images.values())))
    tile_8 = Button(button_height,  (screen_width*0.8,screen_height*0.18),     random.choice(list(large_tile_images.values())))

    buttons = [single_player_button, local_multiplayer_button, settings_button,
               tile_1, tile_2, tile_3, tile_4, tile_5, tile_6, tile_7, tile_8]

    title_dimensions = title.get_rect()[2:4]
    title_desired_width = screen_width*0.35
    size_multiplier =  title_desired_width / title_dimensions[0]
    title_size = tuple(dimension*size_multiplier for dimension in title_dimensions)
    resized_title = pygame.transform.smoothscale(title, title_size)

    return buttons, resized_title


###################
#### Game Loop ####
###################

def run_menu(game_state, event, buttons, title):
    update_rect = None
    if event.type == pygame.FINGERDOWN or event.type == pygame.MOUSEBUTTONDOWN:
        if event.type == pygame.FINGERDOWN:
            event.pos = (int(event.x * game_state.screen_width), int(event.y * game_state.screen_height))
        for button in buttons:
            if button.rect.collidepoint(event.pos):
                button.shown_image = button.clicked_image
                update_rect = button.rect
                
    if event.type == pygame.FINGERUP or event.type == pygame.MOUSEBUTTONUP:
        if event.type == pygame.FINGERUP:
            event.pos = (int(event.x * game_state.screen_width), int(event.y * game_state.screen_height))
        for button in buttons:
            if button.rect.collidepoint(event.pos):
                try:
                    button.action(game_state)
                except:
                    pass
            if button.shown_image == button.clicked_image:
                button.shown_image = button.image
                update_rect = button.rect

    return buttons, title, update_rect



def draw_menu(screen, buttons, title):
    screen.fill((0, 0, 0, 0))
    screen.blit(title, (screen.get_width()/2-title.get_rect()[2]/2,screen.get_height()*0.125))
    for button in buttons:
        button.draw(screen)
