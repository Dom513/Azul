import pygame
from pygame.locals import *
from globals import Button, get_background, main_menu, main_menu_clicked, to_menu, base_path
import math

# Images
settings_title = pygame.image.load(base_path / 'resources' / "settings_title.png").convert_alpha()
light_mode = pygame.image.load(base_path / 'resources' / "light_mode.png").convert_alpha()
light_mode_clicked = pygame.image.load(base_path / 'resources' / "light_mode_clicked.png").convert_alpha()
dark_mode = pygame.image.load(base_path / 'resources' / "dark_mode.png").convert_alpha()
dark_mode_clicked = pygame.image.load(base_path / 'resources' / "dark_mode_clicked.png").convert_alpha()
difficulty_hard = pygame.image.load(base_path / 'resources' / "difficulty_hard.png").convert_alpha()
difficulty_hard_clicked = pygame.image.load(base_path / 'resources' / "difficulty_hard_clicked.png").convert_alpha()
difficulty_easy = pygame.image.load(base_path / 'resources' / "difficulty_easy.png").convert_alpha()
difficulty_easy_clicked = pygame.image.load(base_path / 'resources' / "difficulty_easy_clicked.png").convert_alpha()

# Menu functions
def make_light_mode(game_state):
    game_state.mode="light"
    get_background()
def make_dark_mode(game_state):
    game_state.mode="dark"
    get_background()
def make_difficulty_hard(game_state):
    game_state.difficulty="hard"
def make_difficulty_easy(game_state):
    game_state.difficulty="easy"


def create_settings(game_state):
    screen_width = game_state.screen_width
    screen_height = game_state.screen_height
    button_height = screen_height*0.2
    # return to main menu
    menu_button = Button(button_height, (screen_width*0.075,screen_width*0.075), main_menu, main_menu_clicked, action=to_menu)
    # light/dark mode
    mode_text="Light/Dark Mode"
    mode_pos=(screen_width*0.25, screen_height*0.5)
    light_mode_button = Button(button_height, (screen_width*0.18,screen_height*0.7), light_mode, light_mode_clicked, action=make_light_mode)
    dark_mode_button = Button(button_height, (screen_width*0.32,screen_height*0.7), dark_mode, dark_mode_clicked, action=make_dark_mode)
    # difficulty
    diff_text="AI Difficulty"
    diff_pos=(screen_width*0.75, screen_height*0.5)
    diff_easy_button = Button(button_height, (screen_width*0.68,screen_height*0.7), difficulty_easy, difficulty_easy_clicked, action=make_difficulty_easy)
    diff_hard_button = Button(button_height, (screen_width*0.82,screen_height*0.7), difficulty_hard, difficulty_hard_clicked, action=make_difficulty_hard)

    buttons = [menu_button, light_mode_button, dark_mode_button, diff_easy_button, diff_hard_button]
    texts = [(mode_text, mode_pos), (diff_text, diff_pos)]

    title_dimensions = settings_title.get_rect()[2:4]
    title_desired_width = screen_width*0.5
    size_multiplier =  title_desired_width / title_dimensions[0]
    title_size = tuple(dimension*size_multiplier for dimension in title_dimensions)
    resized_title = pygame.transform.smoothscale(settings_title, title_size)

    return buttons, texts, resized_title


###################
#### Game Loop ####
###################

def run_settings(game_state, event, buttons, texts, title):
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

    return buttons, texts, title, update_rect


def draw_settings(game_state, screen, buttons, texts, title):
    screen.fill((0, 0, 0, 0))
    screen.blit(title, (screen.get_width()/2-title.get_rect()[2]/2,screen.get_height()*0.125))
    font = pygame.font.Font(base_path / 'resources' / "boucherie.ttf", int(game_state.screen_height/12))
    for message, pos in texts:
        text = font.render(message, True, game_state.text_col)
        text_pos = text.get_rect(center=pos)
        screen.blit(text, text_pos)
    buttons_pressed = []
    if game_state.mode == "dark":
        buttons_pressed.append(buttons[2])
    else:
        buttons_pressed.append(buttons[1])
    if game_state.difficulty == "hard":
        buttons_pressed.append(buttons[4])
    else:
        buttons_pressed.append(buttons[3])
    for button in buttons:
        show_shadow=True
        if button in buttons_pressed:


            left = button.center[0]-button.rect[2]/2
            top = button.center[1]-button.rect[3]/2
            screen.blit(button.rotated_glow, (left-button.size*0.05-math.sin(math.radians(abs(button.angle))), top-button.size*0.05-math.cos(math.radians(abs(button.angle)))))
            #screen.blit(button.rotated_glow, (left-(button.size+abs(button.angle)*0.7)*0.05, top-(button.size+abs(button.angle)*0.5)*0.05))
            show_shadow=False
        button.draw(screen, show_shadow)
