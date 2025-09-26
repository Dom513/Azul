import pygame
import math
import random
from pygame.sprite import Sprite, Group, LayeredUpdates
from pygame.locals import *
from pathlib import Path
import sys


#########################
# PATHS & CONSTANTS
#########################
# Determine if the app is running as a packaged executable or as a script
if getattr(sys, 'frozen', False):  # If running as an executable
    base_path = Path(sys._MEIPASS)  # Path to the extracted resources folder
else:
    base_path = Path(__file__).parent  # Path to the current script
resources_path = base_path / "resources"

FPS = 30

# Colours
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

#########################
# RESOURCE LOADER
#########################
class ResourceManager:
    def __init__(self):
        self.cache = {}
        pygame.font.init()

    def load_image(self, filename, size=None, angle=None):
        """Load image and optionally scale."""
        key = (filename, size, angle)
        if key in self.cache:
            img = self.cache[key]
        else:
            path = resources_path / filename
            if "background" in filename:
                img = pygame.image.load(path).convert()
            else:
                img = pygame.image.load(path).convert_alpha()
            if angle:
                img = pygame.transform.rotate(img, angle)
                angle_rad = math.radians(abs(angle))
                w, h = size     
                new_w = abs(w * math.cos(angle_rad)) + abs(h * math.sin(angle_rad))
                new_h = abs(h * math.cos(angle_rad)) + abs(w * math.sin(angle_rad))
                size = (int(new_w), int(new_h))
            if size:
                img = pygame.transform.smoothscale(img, size)
            self.cache[key] = img
        
        
        return img

    def load_font(self, filename, size):
        path = resources_path / filename
        return pygame.font.Font(path, size)

resources = ResourceManager()

#########################
# GAME STATE CONTAINER
#########################
class GameState:
    """Global game state: mode, difficulty, theme, etc."""
    def __init__(self):
        self.running = True
        self.scenes = {}
        if sys.platform in ("win32", "cygwin"):
            self.screen_width = 600
            self.screen_height = 300
            self.fullscreen = pygame.display.set_mode((self.screen_width, self.screen_height), RESIZABLE)
            self.screen_dimensions = (self.screen_width, self.screen_height)
        elif sys.platform.startswith("linux"):
            info = pygame.display.Info()
            self.screen_width = info.current_w
            self.screen_height = info.current_h
            self.dummy_fullscreen = pygame.display.set_mode((self.screen_width, self.screen_height), RESIZABLE)
            self.screen_width, self.screen_height = self.dummy_fullscreen.get_size()
            self.fullscreen = pygame.display.set_mode((self.screen_width, self.screen_height))
            self.screen_dimensions = (self.screen_width, self.screen_height)
        self.tile_size_ratio = 0.065  # change???
        self.mode = "light"
        self.difficulty = "easy"
        self.text_col = "#300000"
        self.get_background()
        self.current_scene = "menu"
        self.font = base_path / 'resources' / "boucherie.ttf"
        self.player_names = [f"Player {i+1}" for i in range(4)]
        self.rects_to_draw = []

    def get_background(self):
        if self.mode == "light":
            self.bg_image = resources.load_image("background_light.jpg", self.fullscreen.get_size())
            self.popup_image = pygame.transform.smoothscale(self.bg_image, self.screen_dimensions)
            darken = pygame.Surface(self.popup_image.get_size(), pygame.SRCALPHA)
            darken.fill((130, 60, 0, 100))
            self.popup_image.blit(darken, (0, 0))
            self.text_col = "#300000"
            self.border_col = "#110049"
            self.player_cols = ["#1C0074", "#920000", "#006600", "#740077"]
        else:
            self.bg_image = resources.load_image("background_dark.jpg", self.fullscreen.get_size())
            self.popup_image = pygame.transform.smoothscale(self.bg_image, self.screen_dimensions)
            darken = pygame.Surface(self.popup_image.get_size(), pygame.SRCALPHA)
            darken.fill((130, 60, 0, 80))
            self.popup_image.blit(darken, (0, 0))
            self.text_col = "#FFE4B3"
            self.border_col = "#007CCF"
            self.player_cols = ["#0096F0", "red", "#00A43E", "#AF4CF2"]
        self.rects_to_draw = [self.fullscreen.get_rect()]

game_state = GameState()


#############################
# Page Classes
#############################

class Page():
    def __init__(self):
        self.buttons = Group()
        self.text_inputs = Group()
        self.titles = Group()
        self.texts = Group()
        self.sprites = Group()
        self.popups = Group()
        self.build()
    
    def handle_event(self, event):
        pygame.mouse.set_visible(True)
        event.scaled_pos = get_event_pos(event)
        if not (event.type==pygame.FINGERUP and sys.platform in ("win32", "cygwin")):
            for button in self.buttons:
                button.handle_event(event)
            for input_box in self.text_inputs:
                input_box.handle_event(event)
            for sprite in self.sprites:
                sprite.handle_event(event)
            for popup in self.popups:
                popup.handle_event(event)
        if event.type==pygame.FINGERUP:
            pygame.mouse.set_visible(False)

    def build(self):
        self.screen = pygame.Surface(game_state.screen_dimensions, pygame.SRCALPHA)
        game_state.get_background()
        for button in self.buttons:
            button.build()
        for input_box in self.text_inputs:
            input_box.build()
        for title in self.titles:
            title.build()
        for text in self.texts:
            text.build()
        for sprite in self.sprites:
            sprite.build()
        for popup in self.popups:
            popup.build()
        game_state.rects_to_draw = [game_state.fullscreen.get_rect()]

    def update(self, dt):
        self.buttons.update()
        self.text_inputs.update()
        self.titles.update()
        self.texts.update()
        self.sprites.update(dt)
        self.popups.update()

    def draw(self, surface):
        surface.fill((0, 0, 0, 0))
        for sprite in self.sprites:
            sprite.draw(surface)
        for sprite in [sprite for sprite in self.sprites if hasattr(sprite, "tiles")]:
            for tile in sprite.tiles:
                if tile.dragging:
                    dragging_tiles = [t for t in tile.parent.tiles if t.colour == tile.colour]
                    for tile in dragging_tiles:
                        tile.draw(surface)
                    break
        for popup in self.popups:
            popup.draw(surface)
        for button in self.buttons:
            button.draw(surface)
        for input_box in self.text_inputs:
            input_box.draw(surface)
        for title in self.titles:
            title.draw(surface)
        for text in self.texts:
            text.draw(surface)
        


class GamePage(Page):
    def __init__(self):
        super().__init__()
        self.player_names = game_state.player_names if not hasattr(self, "player_names") else self.player_names
        self.round_number = 0
        self.build()
        #self.populate(new_game=True)
        self.game_boards_rotating = False
        self.scoring = False
        self.scoring_end_game = False
        self.start_new_round()

    def start_new_round(self):
        self.round_number += 1
        self.populate(new_game=self.round_number==1)
        self.animating = True
        self.animation_timer = 0
        show(self.new_round_popup)

    def create_buttons(self, sw, sh):
        visible = [b.visible for b in self.buttons][0] if len(self.buttons)>0 else True
        self.buttons.empty()
        ratio_from_top = 0.12 if sw >= sh else 0.125*sw/sh
        top_left_pos_ratio = GetEqualTopLeftRatio("top", ratio_from_top)
        size_ratio = 0.12 if sw >= sh else 0.15
        button = UIButton(top_left_pos_ratio, size_ratio, "main_menu.png", "main_menu_clicked.png", callback=lambda: switch_scene("menu"), visible=visible)
        self.buttons.add(button)

    def build(self):
        (sw, sh) = game_state.screen_dimensions
        self.tile_size = int(min(min(sh,sw), max(sh,sw)//2) * game_state.tile_size_ratio)
        self.create_buttons(sw, sh)
        self.generate_factories(sw, sh)
        self.generate_game_boards(sw, sh)
        self.generate_popups(sw, sh)
        super().build()

    def generate_popups(self, sw, sh):
        if sw >= sh:
            self.popup_coords = [(0.72*sw, 0.5*sh), (0.25*sw, 0.5*sh)]
        else:
            self.popup_coords = [(0.5*sw, 0.5*sh), (0.5*sw, 0.25*sh)]

    def generate_factories(self, sw, sh):
        if sw >= sh:
            ratio_from_top = 0.5
            (equal_ratio_from_left,_) = GetEqualTopLeftRatio("top", ratio_from_top)
            ratio_from_left = min(0.25, equal_ratio_from_left)
        else:
            ratio_from_left = 0.5
            (_,equal_ratio_from_top) = GetEqualTopLeftRatio("left", ratio_from_left)
            ratio_from_top = 0.25 if equal_ratio_from_top > 0.275 else 0.275
        center = (sw*ratio_from_left, sh*ratio_from_top)
        radius = min(sh*ratio_from_top, sw*ratio_from_left)*game_state.tile_size_ratio*10
        self.factory_coords = [center]
        self.num_of_factories = 2*game_state.number_of_players+1
        angle_step = 2 * math.pi / self.num_of_factories  # Angle between vertices
        for i in range(self.num_of_factories):
            angle = (i) * angle_step - math.pi/2
            px = ratio_from_left*sw + radius * math.cos(angle)
            py = ratio_from_top*sh + radius * math.sin(angle)
            pos = (px,py)
            self.factory_coords.append(pos)
            
    def generate_game_boards(self, sw, sh):
        if sw >= sh:
            poses_and_sizes = [((0.73,0.25), 0.925),
                            ((0.6,0.6), 0.45),
                            ((0.73,0.825), 0.45),
                            ((0.86,0.6), 0.45),] if game_state.number_of_players == 4 else\
                            [((0.73,0.3), 0.925),
                            ((0.595,0.725), 0.45),
                            ((0.855,0.725), 0.45),] if game_state.number_of_players == 3 else\
                            [((0.73,0.275), 0.925),
                            ((0.73,0.725), 0.625)]
        else:
            poses_and_sizes = [((0.525, 0.6), 0.875),
                               ((0.275, 0.775), 0.4125),
                               ((0.5125, 0.885), 0.4125),
                               ((0.75, 0.775), 0.4125)] if game_state.number_of_players == 4 else\
                              [((0.525, 0.6), 0.875),
                               ((0.275, 0.8), 0.4125),
                               ((0.75, 0.8), 0.4125)] if game_state.number_of_players == 3 else\
                              [((0.525, 0.6), 0.875),
                               ((0.5125, 0.825), 0.725)]
        self.game_board_coords = []
        self.game_board_sizes = []
        for i in range(game_state.number_of_players):
            pos_ratio = poses_and_sizes[i][0]
            pos = (sw*pos_ratio[0], sh*pos_ratio[1])
            self.game_board_coords.append(pos)
            self.game_board_sizes.append(poses_and_sizes[i][1])

    def refill_bag_of_tiles(self):
        print("refilling")
        all_used_tiles = self.removed_tiles
        tiles_in_play = [t.colour for factory in self.factories for t in factory.tiles] + \
                        [t.colour for game_board in self.game_boards for t in game_board.tiles] + \
                        [t.colour for game_board in self.game_boards for tower in game_board.towers for t in tower.tiles]
        counts = {"red":0, "blue":0, "yellow":0, "green":0, "purple":0}
        for tile in all_used_tiles:
            counts[tile] = counts.get(tile, 0) + 1
        print("before all used tiles", counts)
        counts = {"red":0, "blue":0, "yellow":0, "green":0, "purple":0}
        for tile in tiles_in_play:
            counts[tile] = counts.get(tile, 0) + 1
        print("before tiles in play", counts)
        for colour in tiles_in_play:
            if colour in all_used_tiles:
                all_used_tiles.remove(colour)

        self.bag_of_tiles = all_used_tiles
        self.removed_tiles = tiles_in_play
        counts = {"red":0, "blue":0, "yellow":0, "green":0, "purple":0}
        for tile in self.removed_tiles:
            counts[tile] = counts.get(tile, 0) + 1
        print("after all used tiles", counts)
        tiles_in_play = [t.colour for factory in self.factories for t in factory.tiles] + \
                        [t.colour for game_board in self.game_boards for t in game_board.tiles] + \
                        [t.colour for game_board in self.game_boards for tower in game_board.towers for t in tower.tiles]
        counts = {"red":0, "blue":0, "yellow":0, "green":0, "purple":0}
        for tile in tiles_in_play:
            counts[tile] = counts.get(tile, 0) + 1
        print("after tiles in play", counts)
        counts = {"red":0, "blue":0, "yellow":0, "green":0, "purple":0}
        for tile in self.bag_of_tiles:
            counts[tile] = counts.get(tile, 0) + 1
        print("after bag_of_tiles immediately", counts)


        
    def populate(self, new_game=False):
        if new_game:
            self.bag_of_tiles = ["red"]*20 + ["blue"]*20 + ["yellow"]*20 + ["green"]*20 + ["purple"]*20
            self.removed_tiles = []
            self.game_boards = [GameBoard(self, i+1) for i in range(game_state.number_of_players)]
            self.sprites.add(*self.game_boards)
        else:
            self.sprites.remove(*self.factories)
            self.sprites.remove(self.pot)
        #print("before rem", [c[0] for c in self.removed_tiles])
        counts = {}
        for tile in self.removed_tiles:
            counts[tile] = counts.get(tile, 0) + 1
        #print("before rem", counts)
        #print("before bag", [c[0] for c in self.bag_of_tiles])
        counts = {}
        for tile in self.bag_of_tiles:
            counts[tile] = counts.get(tile, 0) + 1
        #print("before bag", counts)
        self.popups.empty()
        self.new_round_popup = NewRoundPopup(self, 1)
        self.end_game_popup = EndGamePopup(self, 2)
        self.popups.add(*[self.new_round_popup, self.end_game_popup])
        self.pot = Pot(self, 0)
        self.factories = [Factory(self, i+1) for i in range(self.num_of_factories)]
        self.sprites.add(*self.factories)
        self.sprites.add(self.pot)
        #print("after rem", [c[0] for c in self.removed_tiles])
        counts = {"red":0, "blue":0, "yellow":0, "green":0, "purple":0}
        for tile in self.removed_tiles:
            counts[tile] = counts.get(tile, 0) + 1
        #print("after rem", counts)
        #print("after bag", [c[0] for c in self.bag_of_tiles])
        counts = {"red":0, "blue":0, "yellow":0, "green":0, "purple":0}
        for tile in self.bag_of_tiles:
            counts[tile] = counts.get(tile, 0) + 1
        #print("after bag", counts)

    def start_rotating_game_boards(self):
        self.game_boards_rotating = True
        self.delay_before_rotating = 0

    def animate_game_boards(self, dt):
        if self.game_boards_rotating:
            self.delay_before_rotating += dt
            if self.delay_before_rotating > 1:
                base = list(range(1, game_state.number_of_players + 1))
                current_game_board = [g for g in self.game_boards if g.player_pos==1][0]
                idx = (current_game_board.idx) % game_state.number_of_players
                new_player_poses = base[-idx:] + base[:-idx] if idx else base
                for game_board in self.game_boards:
                    game_board.player_pos = new_player_poses[game_board.idx-1]
                    next_coords = self.game_board_coords[game_board.player_pos-1]
                    new_tile_size = self.game_board_sizes[game_board.player_pos-1] * self.tile_size
                    height = new_tile_size * 92/14
                    width = game_board.original_image.get_width() * (height/game_board.original_image.get_height())
                    next_size = width
                    move(game_board, next_coords, next_size)
                self.game_boards_rotating=False
        
        elif self.scoring:
            self.scoring_timer += dt
            if self.scoring_phase == 0:  # wait between round end and scoring
                if self.scoring_timer >= 0.8:
                    self.next_round_starting_game_board = [g for g in self.game_boards if "one" in [t.colour for t in list(g.towers)[0].tiles]][0]
                    self.game_boards_scored = 0
                    self.scoring_timer = 0
                    self.scoring_phase = 1

            elif self.scoring_phase == 1:   # wait before scoring first tower
                if self.scoring_timer >= 0.2:
                    self.game_boards_scored += 1
                    self.game_boards_rotated = False
                    self.scoring_timer = 0
                    self.scoring_phase = 2
                    self.current_tower_idx = 1

            elif self.scoring_phase == 2:   # wait between each tower
                game_board = [g for g in self.game_boards if g.player_pos==1][0]
                tile_score_text = [text for text in game_board.texts if text.idx==3][0]
                if self.current_tower_idx < len(game_board.towers):
                    tower = [t for t in game_board.towers if t.idx==self.current_tower_idx][0]
                    if len(tower.tiles)==tower.idx or hasattr(tower, "last_tile"):
                        if self.scoring_timer >= 0.4:
                            hide(tile_score_text)
                            first_tile_pos = tower.tile_coords[0]
                            tower.last_tile = list(tower.tiles)[-1]
                            if not getattr(tower, "scored", False):
                                tower.scored = True
                                for tile in list(tower.tiles)[:-1]:
                                    if not tile.animating:
                                        move(tile, first_tile_pos, tile.size, speed=600*game_board.tile_size/game_board.parent.tile_size)
                                if not tower.last_tile.animating:
                                    game_board_row_colours = game_board.tile_colours[tower.idx-1:] + game_board.tile_colours[:tower.idx-1]
                                    game_board_colour_index = game_board_row_colours.index(tower.last_tile.colour)
                                    game_board_tile_index = (tower.idx-1)*5+game_board_colour_index+1
                                    game_board_tile_pos = game_board.tile_coords[game_board_tile_index-1]
                                    move(tower.last_tile, game_board_tile_pos, tower.last_tile.size, speed=600*game_board.tile_size/game_board.parent.tile_size)
                                    
                            elif tower.last_tile.pos[0] >= first_tile_pos[0]:
                                for tile in list(tower.tiles)[:-1]:
                                    tower.tiles.remove(tile)
                            if not tower.last_tile.animating:  # tile getting added to gameboard
                                game_board_row_colours = game_board.tile_colours[tower.idx-1:] + game_board.tile_colours[:tower.idx-1]
                                game_board_colour_index = game_board_row_colours.index(tower.last_tile.colour)
                                game_board_tile_index = (tower.idx-1)*5+game_board_colour_index+1
                                game_board_tile_pos = game_board.tile_coords[game_board_tile_index-1]
                                game_board.add_tile(tower.last_tile, game_board_tile_index)
                                game_board.score_tile(game_board_tile_pos)
                                del tower.last_tile
                                del tower.scored
                    else:
                        self.scoring_timer = 0
                        self.current_tower_idx += 1
                
                elif self.current_tower_idx == len(game_board.towers): # idx = 6, but is minus tower
                    minus_tower = [t for t in game_board.towers if t.idx==0][0]
                    if self.scoring_timer > 0.4:
                        hide(tile_score_text)
                        self.scoring_timer = 0
                        self.scoring_phase = 3 if len(minus_tower.tiles) > 0 else 4

            elif self.scoring_phase == 3:   # minus tower
                game_board = [g for g in self.game_boards if g.player_pos==1][0]
                tower = [t for t in game_board.towers if t.idx==0][0]
                tile_score_text = [text for text in game_board.texts if text.idx==3][0]
                if len(tower.tiles) > 0 or tile_score_text.visible==True:
                    if 0.3 <= self.scoring_timer < 0.5:
                        hide(tile_score_text)
                    if len(tower.tiles)>0 and self.scoring_timer >= 0.5:
                        tile_to_remove = list(tower.tiles)[0]
                        game_board.score_tile(tile_to_remove.idx, minus_tower=True)
                        tower.tiles.remove(tile_to_remove)
                        self.scoring_timer = 0
                else:
                    self.scoring_timer = 0
                    self.scoring_phase = 4
                            
            elif self.scoring_phase == 4: # wait before rotating or starting new round
                if self.game_boards_scored < game_state.number_of_players:
                    if not getattr(self, "game_boards_rotated", False):
                        self.game_boards_rotated = True
                        self.start_rotating_game_boards()
                    elif self.game_boards_rotated and not self.game_boards_rotating:
                        self.scoring_phase = 1
                        self.scoring_timer = 0
                else:
                    if self.scoring_timer > 1:
                        self.scoring = False
                        self.scoring_timer = 0
                        self.scoring_phase = 0
                        self.game_boards_scored = 0

                        for game_board in self.game_boards:
                            nice_game_board = [next((tile for tile in game_board.tiles if tile.pos == coord), "-") for coord in game_board.tile_coords]
                            game_board.nice_game_board = [nice_game_board[i*5:i*5+5] for i in range(5)]
                            if any([all([tile!="-" for tile in row]) for row in game_board.nice_game_board]):
                                self.scoring_end_game = True
                                self.scoring_timer += 0.5
                        if not self.scoring_end_game:
                            base = list(range(1, game_state.number_of_players + 1))
                            idx = base.index(self.next_round_starting_game_board.idx)
                            new_player_poses = base[-idx:] + base[:-idx] if idx else base
                            for game_board in self.game_boards:
                                game_board.player_pos = new_player_poses[game_board.idx-1]
                                next_coords = self.game_board_coords[game_board.player_pos-1]
                                new_tile_size = self.game_board_sizes[game_board.player_pos-1] * self.tile_size
                                height = new_tile_size * 92/14
                                width = game_board.rect.width * (height/game_board.rect.height)
                                next_size = width
                                snap(game_board, next_coords, next_size)
                            self.new_round_popup.build()
                            show(self.new_round_popup)
                            self.start_new_round()

        elif self.scoring_end_game:
            self.scoring_timer += dt
            if self.scoring_phase == 0:  # scoring rows, cols, diags
                game_board = [g for g in self.game_boards if g.player_pos==1][0]
                if self.scoring_timer >= 0.2:
                    self.scoring_timer = 0
                    self.game_boards_scored +=1
                    self.game_boards_rotated = False
                    self.scoring_phase = 1
                    self.block_idx = 0
                    rows = game_board.nice_game_board
                    cols = [[row[i] for row in game_board.nice_game_board] for i in range(5)]
                    diags = []
                    for i in range(5):
                        diag = []
                        for j in range(5):
                            if i+5-j > 4:
                                i -= 5
                            diag.append(game_board.nice_game_board[i+5-j][j])
                        diags.append(diag)
                    self.blocks = rows+cols+diags

            elif self.scoring_phase == 1:   # score each block
                game_board = [g for g in self.game_boards if g.player_pos==1][0]
                tile_score_text = [t for t in game_board.texts if t.idx==3][0]
                if self.block_idx < 15:
                    block = self.blocks[self.block_idx]
                    if all([t!="-" for t in block]):
                        for t, tile in enumerate(block):
                            if self.scoring_timer >= 0.05*t:
                                tile.show_glow = True
                        if 0.05*4 <= self.scoring_timer < 0.9 and not tile_score_text.visible:
                            game_board.tile_score = 2 if self.block_idx < 5 else 7 if self.block_idx < 10 else 10
                            game_board.score = max(0, game_board.score+game_board.tile_score)
                            game_board.text_messages[1] = str(game_board.score)
                            game_board.text_messages[2] = f"+{game_board.tile_score}"
                            show(tile_score_text)
                        if self.scoring_timer >=0.9:
                            for tile in block:
                                tile.show_glow = False
                                hide(tile_score_text)
                        if self.scoring_timer >= 1:
                            self.block_idx += 1
                            self.scoring_timer = 0
                    else:
                        self.block_idx += 1
                        self.scoring_timer = 0
                else:  # all blocks done
                    if self.scoring_timer >= 0.1:
                        self.scoring_phase = 2
                        self.scoring_timer = 0


            elif self.scoring_phase == 2:   # wait before rotating
                if self.game_boards_scored < game_state.number_of_players:
                    if not getattr(self, "game_boards_rotated", False):
                        self.game_boards_rotated = True
                        self.start_rotating_game_boards()
                    elif self.game_boards_rotated and not self.game_boards_rotating:
                        self.scoring_phase = 0
                        self.scoring_timer = -0.5
                else:
                    if self.scoring_timer > 1:
                        self.scoring_end_game = False
                        for factory in self.factories:
                            hide(factory)
                        self.end_game_popup.build()
                        show(self.end_game_popup)
                        for button in self.end_game_popup.buttons:
                            show(button)
                        for button in self.buttons:
                            hide(button)
                    

    def animate_factories(self, dt):
        """Animate factories and their tiles appearing one by one."""
        self.animation_timer += dt
        if self.animating:
            if not self.pot.animating:
                self.pot.start_animation()
            self.latest_factory = int(self.animation_timer//0.25)
            for factory in self.factories[:self.latest_factory]:
                if not factory.animating:
                    factory.start_animation()
            if self.latest_factory == len(self.factories):
                self.animating = False
                self.animation_timer = 0
        elif self.new_round_popup.visible:
            if self.animation_timer > 1:
                hide(self.new_round_popup)

    def start_scoring(self):
        self.scoring = True
        self.scoring_timer = 0
        self.scoring_phase = 0

    def update(self, dt, single_player=False):
        scoring_so_include_rect = self.scoring or self.scoring_end_game
        if scoring_so_include_rect:
            if not single_player:
                game_board = [g for g in self.game_boards if g.player_pos==1][0]
            else:
                game_board = [g for g in self.game_boards if g.player_pos==self.current_player_idx][0]
            game_state.rects_to_draw.append(game_board.extended_rect)
        self.animate_factories(dt)
        self.animate_game_boards(dt)
        super().update(dt)
        if scoring_so_include_rect:
            game_state.rects_to_draw.append(game_board.extended_rect)


class NumOfPlayers(Page):
    def __init__(self, next_page):
        self.next_page = next_page
        super().__init__()

    def build(self):
        (sw, sh) = game_state.screen_dimensions
        self.create_texts(sw, sh)
        self.create_buttons(sw, sh)
        super().build()

    def create_buttons(self, sw, sh):
        self.buttons.empty()
        size_ratio = 0.26
        start_y = 0.6

        if self.next_page == "single_player":
            labels_callbacks = [("two_players_com.png", "two_players_com_clicked.png", lambda: self.choose_number_of_players(2)),
                                ("three_players_com.png", "three_players_com_clicked.png", lambda: self.choose_number_of_players(3)),
                                ("four_players_com.png", "four_players_com_clicked.png", lambda: self.choose_number_of_players(4)),]
        else:
            labels_callbacks = [
                ("two_players.png", "two_players_clicked.png", lambda: self.choose_number_of_players(2)),
                ("three_players.png", "three_players_clicked.png", lambda: self.choose_number_of_players(3)),
                ("four_players.png", "four_players_clicked.png", lambda: self.choose_number_of_players(4))
            ]
        
        if sw >= sh:
            pos_ratios = [(0.5 + (i-1) * (size_ratio*0.8), start_y) for i in range(3)]
        else:
            pos_ratios = [(0.5, 0.35), (0.5, 0.55), (0.5, 0.75)]
        
        for i, (image_path, clicked_image_path, callback) in enumerate(labels_callbacks):
            pos_ratio = pos_ratios[i]
            angle = random.randint(-20, 20)
            button = UIButton(pos_ratio, size_ratio, image_path, clicked_image_path, angle, callback)
            self.buttons.add(button)

        # Main Menu button
        ratio_from_top = 0.15 if sw >= sh else 0.15*sw/sh
        top_left_pos_ratio = GetEqualTopLeftRatio("top", ratio_from_top)
        size_ratio = 0.15
        button = UIButton(top_left_pos_ratio, size_ratio, "main_menu.png", "main_menu_clicked.png", callback=lambda: switch_scene("menu"))
        self.buttons.add(button)

    def create_texts(self, sw, sh):
        self.texts.empty()
        title_coord = (0.5, 0.25) if sw >= sh else (0.5, 0.2)
        text_size = 0.12 if sw >= sh else 0.1
        text = UIText("How Many Players?", title_coord, text_size)
        self.texts.add(text)

    def choose_number_of_players(self, number):
        game_state.number_of_players = number
        #multipliers = {2: (1/27, 0.75), 3: (1/28, 0.58), 4: (1/30, 0.5)}
        if self.next_page == "single_player":
            game_state.single_player_number_of_players = number
            switch_scene("single_player")
        else:
            game_state.multiplayer_number_of_players = number
            switch_scene("input_players")


class ContinueGame(Page):
    def __init__(self, next_page):
        self.next_page = next_page
        super().__init__()

    def build(self):
        (sw, sh) = game_state.screen_dimensions
        self.create_texts(sw, sh)
        self.create_buttons(sw, sh)
        super().build()

    def create_buttons(self, sw, sh):
        self.buttons.empty()
        size_ratio = 0.26
        start_y = 0.6

        labels_callbacks = [("continue.png", "continue_clicked.png", lambda: self.choose_new_game(False)),
                            ("new_game.png", "new_game_clicked.png", lambda: self.choose_new_game(True)),]
        
        if sw >= sh:
            pos_ratios = [(0.5 + (i-0.5) * (size_ratio*0.8), start_y) for i in range(2)]
        else:
            pos_ratios = [(0.5, 0.5), (0.5, 0.7)]
        
        for i, (image_path, clicked_image_path, callback) in enumerate(labels_callbacks):
            pos_ratio = pos_ratios[i]
            angle = random.randint(-20, 20)
            button = UIButton(pos_ratio, size_ratio, image_path, clicked_image_path, angle, callback)
            self.buttons.add(button)

        # Main Menu button
        ratio_from_top = 0.15 if sw >= sh else 0.15*sw/sh
        top_left_pos_ratio = GetEqualTopLeftRatio("top", ratio_from_top)
        size_ratio = 0.15
        button = UIButton(top_left_pos_ratio, size_ratio, "main_menu.png", "main_menu_clicked.png", callback=lambda: switch_scene("menu"))
        self.buttons.add(button)

    def create_texts(self, sw, sh):
        self.texts.empty()
        if sw >= sh:
            title_coords = [(0.5, 0.2), (0.5, 0.3)]
            text_size = 0.12
            texts = [UIText("You have an existing", title_coords[0], text_size),
                     UIText(f"{len(game_state.scenes[self.next_page].game_board_coords)} player game. Continue?", title_coords[1], text_size)]
        else:
            title_coords = [(0.5, 0.23), (0.5, 0.28), (0.5, 0.35)]
            text_size = 0.1
            texts = [UIText("You have an existing", title_coords[0], text_size),
                     UIText(f"{len(game_state.scenes[self.next_page].game_board_coords)} player game.", title_coords[1], text_size),
                     UIText("Continue?", title_coords[2], text_size)]
        self.texts.add(*texts)

    def choose_new_game(self, new_game):
        if new_game:
            if self.next_page == "single_player":
                game_state.scenes.pop("single_player", None)
                switch_scene("single_player_num_players")
            elif self.next_page == "multiplayer":
                game_state.scenes.pop("multiplayer", None)
                switch_scene("multiplayer_num_players")
        else:
            switch_scene(self.next_page)


class PlayerNames(Page):
    def __init__(self):
        self.player_cols = ["#0096F0", "red", "#00A43E", "#AF4CF2"] if game_state.mode=="dark" else ["#1C0074", "#920000", "#006600", "#740077"]
        super().__init__()

    def build(self):
        (sw, sh) = game_state.screen_dimensions
        self.create_inputs(sw, sh)
        self.create_buttons(sw, sh)
        self.create_texts(sw, sh)
        super().build()

    def create_inputs(self, sw, sh):
        self.text_inputs.empty()
        if sw >= sh:
            if game_state.number_of_players == 2:
                coords = [(0.31, 0.5), (0.69, 0.5)]
            elif game_state.number_of_players == 3:
                coords = [(0.31, 0.45), (0.69, 0.45), (0.5, 0.65)]
            else:
                coords = [(0.31, 0.4), (0.69, 0.4), (0.31, 0.6), (0.69, 0.6)]
            text_input_width_ratio = 0.35
            text_input_height_ratio = 0.15
        else:
            coords = [(0.5, 0.3), (0.5, 0.41), (0.5, 0.52), (0.5, 0.63)][:game_state.number_of_players]
            text_input_width_ratio = 0.675
            text_input_height_ratio = 0.0825

        text_input_rects = []
        for (cx, cy) in coords:
            rect = (
                cx - text_input_width_ratio / 2,   # shift left from center
                cy - text_input_height_ratio / 2,  # shift up from center
                text_input_width_ratio,
                text_input_height_ratio
            )
            text_input_rects.append(rect)

        self.inputs = [
            UITextInput(i, text_input_rect, self.player_cols[i], game_state.player_names[i])
            for i, text_input_rect in enumerate(text_input_rects)
        ]
        self.text_inputs.add(*self.inputs)

    def create_buttons(self, sw, sh):
        self.buttons.empty()
        # Main Menu button
        ratio_from_top = 0.15 if sw >= sh else 0.15*sw/sh
        top_left_pos_ratio = GetEqualTopLeftRatio("top", ratio_from_top)
        size_ratio = 0.15
        button = UIButton(top_left_pos_ratio, size_ratio, "main_menu.png", "main_menu_clicked.png", callback=lambda: switch_scene("menu"))
        self.buttons.add(button)
        # Continue button
        ratio_from_top = 0.15
        top_left_pos_ratio = GetEqualTopLeftRatio("top", ratio_from_top)
        new_pos_ratio = (1-top_left_pos_ratio[0], 1-top_left_pos_ratio[1])
        size_ratio = 0.2
        button = UIButton(new_pos_ratio, size_ratio, "play.png", "play_clicked.png", callback=lambda: switch_scene("multiplayer"))
        self.buttons.add(button)

    def create_texts(self, sw, sh):
        self.texts.empty()
        text_size = 0.12 if sw >= sh else 0.1
        text = UIText("Enter Player Names", (0.5, 0.2), text_size)
        self.texts.add(text)


#############################
# UI SPRITES
#############################

class UIButton(Sprite):
    def __init__(self, pos_ratio, height_ratio, image, clicked_image=None, angle=None, callback=lambda: None, visible=True):
        super().__init__()
        self.pos_ratio = pos_ratio
        self.height_ratio = height_ratio
        self.callback = callback
        self.base_image = image
        self.base_clicked = clicked_image if clicked_image else image
        self.angle = angle if angle is not None else random.randint(-20, 20)
        self.visible = visible
        self.disabled = clicked_image is None
        self.show_glow = False
        self.always_show_glow = False
        self.pressed = False
        self.build()

    def build(self):
        """Rebuild button images/rects when screen is buildd."""
        (sw, sh) = game_state.screen_dimensions
        # Determine size + position
        height = int(min(min(sh,sw), max(sh,sw)//2) * self.height_ratio)
        cx, cy = int(sw * self.pos_ratio[0]), int(sh * self.pos_ratio[1])
        # Load images
        self.image = resources.load_image(self.base_image, (height, height), self.angle)
        self.clicked_image = resources.load_image(self.base_clicked, (height, height), self.angle)
        self.shown_image = self.image
        self.rect = self.image.get_rect(center=(cx, cy))

        # Shadow
        shadow = pygame.Surface((height, height), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (0, 0, 0, 150), shadow.get_rect(), border_radius=height//8)
        self.rotated_shadow = pygame.transform.rotate(shadow, self.angle)
        self.shadow_offset = (self.rect.x + self.rect.width*0.05,
                              self.rect.y + self.rect.height*0.05)

        # Glow
        glow_size = int(height + math.sqrt(height))
        glow = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
        pygame.draw.rect(glow, (255, 255, 0, 255), glow.get_rect(), border_radius=glow_size // 7)
        self.rotated_glow = pygame.transform.rotate(glow, self.angle)
        self.glow_offset = (
            self.rect.centerx - self.rotated_glow.get_width() // 2,
            self.rect.centery - self.rotated_glow.get_height() // 2
        )

    def handle_event(self, event):
        if self.visible:
            if self.rect is None:
                return
            if event.type in (pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN) and self.rect.collidepoint(event.scaled_pos):
                self.shown_image = self.clicked_image
                self.pressed = True
            elif event.type in (pygame.MOUSEBUTTONUP, pygame.FINGERUP):
                self.shown_image = self.image
                self.show_glow = False
                if self.pressed and self.rect.collidepoint(event.scaled_pos):
                    self.callback()
                self.pressed = False
            if event.type in (pygame.MOUSEMOTION, pygame.FINGERMOTION):
                game_state.rects_to_draw.append(self.rotated_glow.get_rect(topleft = self.glow_offset))
                    
    def draw(self, surface):
        if self.visible:
            if self.rotated_shadow:
                surface.blit(self.rotated_shadow, self.shadow_offset)
            # Get mouse position in fullscreen coordinates
            x_full, y_full = pygame.mouse.get_pos()
            # Convert to render_surface coordinates
            x = x_full * game_state.screen_dimensions[0] / game_state.fullscreen.get_width()
            y = y_full * game_state.screen_dimensions[1] / game_state.fullscreen.get_height()
            self.show_glow = self.rect.collidepoint((x,y)) and not self.disabled and pygame.mouse.get_visible()
            if (self.show_glow and self.rotated_glow) or self.always_show_glow:
                surface.blit(self.rotated_glow, self.glow_offset)
            if self.shown_image:
                surface.blit(self.shown_image, self.rect.topleft)


class UITextInput(Sprite):
    def __init__(self, player, rect, colour, initial_text):
        super().__init__()
        self.player = player
        self.ratio_rect = rect
        self.initial_text = initial_text
        self.text = initial_text
        self.colour = colour
        self.active = False
        self.cached_octagon = {}
        self.build()
        
    def build(self):
        (sw, sh) = game_state.screen_dimensions
        # Determine size + position
        self.rect = pygame.Rect(
            int(self.ratio_rect[0]*sw), 
            int(self.ratio_rect[1]*sh), 
            int(self.ratio_rect[2]*sw),
            int(self.ratio_rect[3]*sh)
        )
        self.font = pygame.font.Font(game_state.font, int(self.rect.height * 0.7))
        while self.font.size(self.text)[0] >= self.rect.width*0.95:
            self.text = self.text[:-1]
        self.rendered_text = self.font.render(self.text, True, game_state.text_col)
        cut_size = int(min(min(sh,sw), max(sh,sw)//2) * 0.025)
        border_radius = int(min(min(sh,sw), max(sh,sw)//2) * 0.015)      
        region = game_state.popup_image
        self.cached_octagon[False] = crop_image_to_octagon(
            region, self.rect, cut_size, self.colour, border_radius, colour=False)
        self.cached_octagon[True] = crop_image_to_octagon(
            region, self.rect, cut_size, self.colour, border_radius, colour=True)
        self.border_radius = border_radius

    def handle_event(self, event):
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN):
            self.active = self.rect.collidepoint(event.scaled_pos)
            if self.text == "":
                self.text = self.initial_text
            if self.active:
                pygame.key.start_text_input()
                self.text = ""
            self.rendered_text = self.font.render(self.text, True, game_state.text_col)
            game_state.player_names[self.player] = self.text
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                self.active = False
                pygame.key.stop_text_input()
                if self.text == "":
                    self.text = self.initial_text
            else:
                self.text += event.unicode
                while self.font.size(self.text)[0] >= self.rect.width*0.9:
                    self.text = self.text[:-1]
            self.rendered_text = self.font.render(self.text, True, game_state.text_col)
            game_state.player_names[self.player] = self.text
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.FINGERDOWN, pygame.FINGERUP) or event.type == pygame.KEYDOWN and self.active:
            game_state.rects_to_draw.append(self.rect)

    def draw(self, surface):
        surface.blit(self.cached_octagon[self.active], (self.rect.x - self.border_radius, self.rect.y - self.border_radius))
        text_rect = self.rendered_text.get_rect(center=self.rect.center)
        surface.blit(self.rendered_text, text_rect)


class UIImage(Sprite):
    def __init__(self, image_path, pos_ratio, height_ratio):
        super().__init__()
        self.original_image = resources.load_image(image_path)
        self.height_ratio = height_ratio
        self.pos_ratio = pos_ratio
        self.build()

    def build(self):
        (sw, sh) = game_state.screen_dimensions
        height = min(int(min(sh,sw) * self.height_ratio), int(max(sh,sw) * self.height_ratio)//2)
        width = int(self.original_image.get_width() * (height / self.original_image.get_height()))
        cx = int(sw * self.pos_ratio[0])
        cy = int(sh * self.pos_ratio[1])
        self.image = pygame.transform.smoothscale(self.original_image, (width, height))
        self.rect = self.image.get_rect(center=(cx, cy))

    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)


class UIText(Sprite):
    def __init__(self, message, pos_ratio, size_ratio, color=None):
        super().__init__()
        self.message = message
        self.pos_ratio = pos_ratio
        self.size_ratio = size_ratio
        self.colour = color if color else game_state.text_col
        self.build()

    def build(self):
        (sw, sh) = game_state.screen_dimensions
        self.font_size = int(min(min(sh,sw), max(sh,sw)//2)*self.size_ratio)
        self.font = pygame.font.Font(game_state.font, self.font_size)
        self.rendered_text = self.font.render(self.message, True, self.colour)
        self.rect = self.rendered_text.get_rect(center=(sw*self.pos_ratio[0], sh*self.pos_ratio[1]))

    def draw(self, surface):
        surface.blit(self.rendered_text, self.rect.topleft)


class Popup(Sprite):
    def __init__(self, parent, idx):
        super().__init__()
        self.parent = parent
        self.idx = idx
        self.visible = False
        self.texts = Group()
        self.buttons = Group()

    def build(self):
        (sw, sh) = game_state.screen_dimensions
        cut_size = int(min(min(sh,sw), max(sh,sw)//2) * 0.03)
        self.border_radius = int(min(min(sh,sw), max(sh,sw)//2) * 0.02)
        popup_area = game_state.popup_image
        self.octagon_image = crop_image_to_octagon(
            popup_area,
            self.original_rect,  # relative rect
            cut_size,
            game_state.border_col,
            self.border_radius)
        self.rect = pygame.Rect(self.original_rect.x-self.border_radius, self.original_rect.y-self.border_radius,
                            self.original_rect.width+self.border_radius*2, self.original_rect.height+self.border_radius*2)

    def handle_event(self, event):
        for button in self.buttons:
            button.handle_event(event)
        # if self.visible and event.type in (pygame.MOUSEMOTION, pygame.FINGERMOTION) and self.rect.collidepoint(event.scaled_pos):
        #     game_state.rects_to_draw.append(self.rect)

    def update(self):
        self.buttons.update()

    def draw(self, surface):
        if self.visible:
            surface.blit(self.octagon_image, (self.rect.x, self.rect.y))
            for text in self.texts:
                text.draw(surface)
            for button in self.buttons:
                button.draw(surface)


class NewRoundPopup(Popup):
    def __init__(self, parent, idx):
        super().__init__(parent, idx)
        self.build()
    
    def build(self):
        (sw, sh) = game_state.screen_dimensions
        self.next_player = self.parent.next_round_starting_game_board if hasattr(self.parent, "next_round_starting_game_board") else [g for g in self.parent.game_boards if g.player_pos==1][0]
        self.next_player_col = game_state.player_cols[self.next_player.idx-1]
        self.next_player_name = self.next_player.text_messages[0]
        self.round_number = self.parent.round_number
        self.pos = self.parent.popup_coords[self.idx - 1]
        self.messages = [f"Round {self.round_number}", f"{self.next_player_name} goes first"]
        self.colours = [None, self.next_player_col]
        if self.next_player_name == "You":
            self.messages[1] = "You go first"
        self.size_ratios = [0.12, 0.075]
        text_dimensions = [pygame.font.Font(game_state.font, int(min(min(sh,sw), max(sh,sw)//2)*self.size_ratios[i])).size(self.messages[i]) for i in range(len(self.messages))]
        self.width = min(max([width for (width,height) in text_dimensions]+[max(sh,sw)*0.3])*1.2, max(sh,sw)*0.45)
        self.height = sum([height for (width,height) in text_dimensions]) +10  # 20px padding top/bottom
        self.original_rect = pygame.Rect(self.pos[0] - self.width // 2, self.pos[1] - self.height // 2, self.width, self.height)
        super().build()
        self.generate_texts()

    def generate_texts(self):
        (sw, sh) = game_state.screen_dimensions
        self.texts.empty()
        h = self.original_rect.height
        # place messages stacked inside popup rect
        for i, (msg, size_ratio, colour) in enumerate(zip(self.messages, self.size_ratios, self.colours)):
            y = self.original_rect.y + h/3.2 + i*(h/2.3)
            x = self.original_rect.centerx
            text = UIText(msg, (x/sw, y/sh), size_ratio, colour) 
            self.texts.add(text)

class EndGamePopup(Popup):
    def __init__(self, parent, idx):
        super().__init__(parent, idx)
        self.build()
    
    def build(self):
        (sw, sh) = game_state.screen_dimensions
        self.pos = self.parent.popup_coords[self.idx-1]
        self.messages = [f"{g.text_messages[0]}: {g.text_messages[1]}" for g in self.parent.game_boards]
        self.colours = game_state.player_cols
        self.size_ratios = [0.075]*4 if sw >= sh else [0.1]*4
        self.width = sw*0.35 if sw >= sh else sw*0.8
        self.height = sh*0.8 if sw >= sh else sh*0.425
        self.original_rect = pygame.Rect(self.pos[0] - self.width // 2, self.pos[1] - self.height // 2, self.width, self.height)
        super().build()
        self.generate_texts()
        self.create_buttons(sw, sh)

    def generate_texts(self):
        (sw, sh) = game_state.screen_dimensions
        h = self.original_rect.height
        self.texts.empty()
        players_scores = [(g.text_messages[0], g.text_messages[1]) for g in self.parent.game_boards]
        max_score = max(score for _, score in players_scores)
        winners = [(name, score) for name, score in players_scores if score == max_score]
        if len(winners) > 1:
            results_msg = "It's a tie!"
            results_msg_size = 0.1
        elif winners[0][0] == "You":
            results_msg = "You Win"
            results_msg_size = 0.1
        else:
            results_msg = f"{winners[0][0]} Wins"
            font_size = int(min(min(sh,sw), max(sh,sw)//2)*0.1)
            font = pygame.font.Font(game_state.font, font_size)
            results_msg_size = min(0.1, 0.1*(self.original_rect.width*0.95)/font.size(results_msg)[0])
        title_text = UIText(results_msg, (self.original_rect.centerx/sw, (self.original_rect.y+h/9)/sh), results_msg_size)
        self.texts.add(title_text)
        text_rects = []
        self.text_coords = []
        # place messages stacked inside popup rect
        for i, (msg, size_ratio, colour) in enumerate(zip(self.messages, self.size_ratios, self.colours)):
            x = self.original_rect.centerx
            y = self.original_rect.centery + (i-game_state.number_of_players*0.5+0.2)*(h/(2*game_state.number_of_players**1.1))
            tw, th = pygame.font.Font(game_state.font, int(min(sh,sw*0.8)*size_ratio)).size(msg)
            text_rect = pygame.Rect(0,0,tw,th)
            text_rect.center = (x, y)
            text_rects.append(text_rect)
        furthest_right = max([rect.right for rect in text_rects]) - sw*0.01
        for rect in text_rects:
            rect.right = furthest_right
            self.text_coords.append(rect.center)
        for i, (msg, (x,y), size_ratio, colour) in enumerate(zip(self.messages, self.text_coords, self.size_ratios, self.colours)):
            text = UIText(msg, (x/sw,y/sh), size_ratio, colour) 
            self.texts.add(text)

    def create_buttons(self, sw, sh):
        self.buttons.empty()
        # Main Menu button
        pos_ratio = (0.16, 0.775) if sw >= sh else (0.3, 0.395)
        size_ratio = 0.15 if sw >= sh else 0.175
        button = UIButton(pos_ratio, size_ratio, "main_menu.png", "main_menu_clicked.png", callback=lambda: end_game_menu())
        show(button) if self.visible else hide(button)
        self.buttons.add(button)
        # Restart button
        pos_ratio = (0.34, 0.775) if sw >= sh else (0.7, 0.395)
        size_ratio = 0.15 if sw >= sh else 0.175
        button = UIButton(pos_ratio, size_ratio, "play_again.png", "play_again_clicked.png", callback=lambda: switch_scene("single_player_num_players"))
        show(button) if self.visible else hide(button)
        self.buttons.add(button)

def end_game_menu():
    game_state.scenes.pop(game_state.current_scene)
    switch_scene("menu")

##################
# SPRITE CLASSES #
##################

class Tile(Sprite):
    def __init__(self, parent, idx, colour):
        super().__init__()
        self.parent = parent
        self.idx = idx
        self.colour = colour
        self.original_image = resources.load_image(f"{self.colour}_tile.png")
        self.build()
        self.dragging = False
        self.visible = False
        self.show_glow=False
        self.animating=False

    def build(self, new_pos=None, new_tile_size=None):
        self.tile_size = int(new_tile_size if new_tile_size else self.parent.tile_size)
        self.size = self.tile_size
        self.pos = new_pos if new_pos else self.parent.tile_coords[self.idx-1]
        self.image = pygame.transform.smoothscale(self.original_image, (self.size, self.size))
        self.rect = self.image.get_rect(center=self.pos)
        # glow
        self.glow_size = int(self.size * 1.4)
        self.glow = pygame.Surface((self.glow_size, self.glow_size), pygame.SRCALPHA)
        self.glow_rect = self.glow.get_rect()
        pygame.draw.rect(self.glow, (255, 255, 0, 255), self.glow_rect)
        self.glow_offset = (
            self.rect.centerx - self.glow.get_width() // 2,
            self.rect.centery - self.glow.get_height() // 2
        )

    def draw(self, surface):
        if self.visible:
            if self.show_glow:
                surface.blit(self.glow, self.glow_offset)
            surface.blit(self.image, self.rect.topleft)

    # NEXT
    def handle_event(self, event):
        if not self.visible or self.parent.__class__.__name__ == "GameBoard":
            return
        game = self.parent.parent if self.parent.__class__.__name__ in ["Factory","Pot"] else self.parent.parent.parent
        pot = game.pot
        if self.parent.__class__.__name__ in ["Factory", "Pot"]:
            if self.dragging:
                over_board = None
                over_tower = None
                current_game_board = [board for board in game.game_boards if board.player_pos == 1][0]
                minus_tower = [tower for tower in current_game_board.towers if tower.idx == 0][0]
                if current_game_board.rect.collidepoint(event.scaled_pos):
                    over_board = current_game_board
                    for tower in current_game_board.towers:
                        if tower.rect.collidepoint(event.scaled_pos):
                            over_tower = tower
                            break

            if event.type in (pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN):  # Left click
                if self.rect.collidepoint(event.scaled_pos):
                    self.dragging = True
                    dragging_tiles = [tile for tile in self.parent.tiles if tile.colour == self.colour]
                    for i, tile in enumerate(dragging_tiles):
                        tile.drag_offset = (-tile.rect.width*1.04*(i), 0)
                        new_tile_pos = (event.scaled_pos[0]+tile.drag_offset[0], event.scaled_pos[1]+tile.drag_offset[1])
                        snap(tile, new_tile_pos, tile.rect.width)

            elif event.type in (pygame.MOUSEBUTTONUP, pygame.FINGERUP):
                if self.dragging:
                    tiles_to_move = [tile for tile in self.parent.tiles if tile.colour == self.colour]
                    tiles_to_pot = [tile for tile in self.parent.tiles if tile.colour != self.colour]
                    tiles_in_pot = [tile for tile in pot.tiles if tile not in tiles_to_move + tiles_to_pot]
                    tiles_to_pot = tiles_in_pot + tiles_to_pot

                    if self.parent == pot:
                        one_tile = [tile for tile in pot.tiles if tile.colour == "one"]
                        tiles_to_move = [tile for tile in tiles_to_move if tile.colour != "one"]
                        tiles_to_move = one_tile + tiles_to_move
                        tiles_to_pot = [tile for tile in tiles_to_pot if tile.colour != "one"]

                    if over_tower and over_tower.can_place(tiles_to_move[-1]):
                        sizes = [over_tower.tile_size]*len(tiles_to_move)
                        new_pot_sizes = [tile.size for tile in tiles_to_pot]
                        parent_factory = self.parent
                        poses = transfer_tiles(tiles_to_move, parent_factory, over_tower, minus_tower, self.parent==pot)
                        new_pot_poses = transfer_tiles(tiles_to_pot, parent_factory, pot, minus_tower)
                        all_tiles_to_move_and_remove = tiles_to_move + tiles_to_pot
                        tiles_to_move = tiles_to_move[:len(poses)]
                        sizes = sizes[:len(poses)]
                        tiles_to_pot = tiles_to_pot[:len(new_pot_poses)]
                        new_pot_sizes = new_pot_sizes[:len(new_pot_poses)]
                        poses = poses + new_pot_poses
                        sizes = sizes + new_pot_sizes
                        all_tiles_to_move = tiles_to_move + tiles_to_pot
                        all_tiles_to_remove = [tile for tile in all_tiles_to_move_and_remove if tile not in all_tiles_to_move]
                        for i, tile in enumerate(all_tiles_to_move):
                            move(tile, poses[i], sizes[i])
                        for i, tile in enumerate(all_tiles_to_remove):
                            hide(tile)
                            snap(tile, (0,0), 0)
                        over_board.move_made = True
                    else:
                        poses = [tile.parent.tile_coords[tile.idx-1] for tile in tiles_to_move]
                        sizes = [tile.parent.tile_size for tile in tiles_to_move]
                        for i, tile in enumerate([tile for tile in tiles_to_move]):
                            snap(tile, poses[i], sizes[i])
                    self.dragging = False

            elif event.type in (pygame.MOUSEMOTION, pygame.FINGERMOTION):
                if self.dragging:
                    if over_board:
                        new_tile_size = over_board.tile_size
                    else:
                        new_tile_size = self.parent.tile_size

                    dragging_tiles = [tile for tile in self.parent.tiles if tile.colour == self.colour]
                    for i, tile in enumerate(dragging_tiles):
                        self.drag_offset = (-self.rect.width*1.04*(i), 0)
                        new_tile_pos = (event.scaled_pos[0]+self.drag_offset[0], event.scaled_pos[1]+self.drag_offset[1])
                        snap(tile, new_tile_pos, new_tile_size)
    
    def update(self, dt):
        if self.animating:
            self.anim_time += dt
            t = min(self.anim_time / self.anim_duration, 1.0)  # Clamp [0,1]
            # Linear interpolation (can replace with easing later)
            new_x = self.start_pos[0] + (self.end_pos[0] - self.start_pos[0]) * t
            new_y = self.start_pos[1] + (self.end_pos[1] - self.start_pos[1]) * t
            new_width = int(self.start_size + (self.end_size - self.start_size) * t)
            snap(self, (new_x, new_y), new_width)
            if t >= 1.0:
                self.animating = False


# FACTORY CLASS
class Factory(Sprite):
    def __init__(self, parent, idx):
        super().__init__()
        self.parent = parent
        self.idx = idx
        self.original_image = resources.load_image("factory.png")
        self.tiles = Group()
        self.build()
        self.populate()
        self.visible = True
        self.animating = False
        
    def build(self, new_pos=None, new_tile_size=None):
        self.tile_size = int(new_tile_size if new_tile_size else self.parent.tile_size)
        self.size = self.tile_size * 2.9
        self.pos = new_pos if new_pos else self.parent.factory_coords[self.idx]
        self.image = pygame.transform.smoothscale(self.original_image, (self.size, self.size))
        self.rect = self.image.get_rect(center=self.pos)

        self.generate_tile_coords()

        for i, tile in enumerate(self.tiles):
            tile.build()

    def draw(self, surface):
        if self.visible:
            surface.blit(self.image, self.rect.topleft)
            for tile in self.tiles:
                tile.draw(surface)

    def generate_tile_coords(self):
        offset = self.tile_size*0.525
        x = self.pos[0]
        y = self.pos[1]
        self.tile_coords = [(x-offset, y-offset), (x+offset, y-offset),
                       (x-offset, y+offset), (x+offset, y+offset)]

    def populate(self):
        for i in range(4):
            try:
                colour = self.parent.bag_of_tiles.pop(random.randrange(len(self.parent.bag_of_tiles)))
            except:
                self.parent.refill_bag_of_tiles()
                try:  # only if objectively not enough tiles
                    colour = self.parent.bag_of_tiles.pop(random.randrange(len(self.parent.bag_of_tiles)))
                except:
                    continue
            self.parent.removed_tiles.append(colour)
            tile = Tile(self, i, colour)
            self.tiles.add(tile)

    def start_animation(self):
        self.animating = True
        self.tiles_timer = 0

    def handle_event(self, event):
        if self.visible:
            for tile in self.tiles:
                tile.handle_event(event)

    def update(self, dt):
        if self.animating:
            self.tiles_timer += dt
            self.latest_tile = int(self.tiles_timer//0.05)
            for tile in list(self.tiles)[:self.latest_tile]:
                show(tile)
            if self.latest_tile >= len(self.tiles):
                self.animating = False
        for tile in self.tiles:
            tile.update(dt)

    def remove_tile(self, tile):
        if tile in self.tiles:
            self.tiles.remove(tile)


# POT CLASS
class Pot(Factory):
    def __init__(self, parent, idx=0):
        super().__init__(parent, idx)
        self.image=None
        # self.build()
        # self.populate()
        self.visible = True

    def build(self, new_pos=None, new_tile_size=None):
        self.tile_size = int(new_tile_size if new_tile_size else self.parent.tile_size)
        self.pos = new_pos if new_pos else self.parent.factory_coords[self.idx]

        self.generate_tile_coords()
        for i, tile in enumerate(self.tiles):
            tile.build()

    def draw(self, surface):
        if self.visible == True:
            for tile in self.tiles:
                tile.draw(surface)

    def populate(self):
        tile = Tile(self, 1, "one")
        self.tiles.add(tile)

    def generate_tile_coords(self):
        tile_size = self.parent.tile_size
        gap = tile_size/14
        center_x = self.pos[0]
        center_y = self.pos[1]
        coords = [(center_x + x*(gap+tile_size), 
                        center_y + y*(gap+tile_size))
                        for x in range(-2,3) for y in range(-2,3)]
        # now add bonus 3 tile spaces for worst case scenario
        coords += [(center_x + 3*(gap+tile_size), center_y),
                      (center_x - 3*(gap+tile_size), center_y),
                      (center_x, center_y + 3*(gap+tile_size))]

        # Order coords
        self.tile_coords = sorted(coords, key=lambda c: math.sqrt((c[0]-center_x)**2 + (c[1]-center_y)**2))
    


# TOWER CLASS
class Tower(Sprite):
    def __init__(self, parent, idx):
        super().__init__()
        self.parent = parent
        self.tiles = Group()
        self.idx = idx  # 0 = minus tower
        self.build()
        self.scoring = False

    def build(self, new_pos=None, new_tile_size=None):
        self.tile_size = int(new_tile_size if new_tile_size else self.parent.tile_size)
        self.pos = new_pos if new_pos else self.parent.tower_coords[self.idx]

        tile_size = self.tile_size
        tile_gap = self.tile_size/14
        tower_height = tile_size if self.idx != 0 else tile_size*4 + tile_gap*12
        tower_width = tile_size*(self.idx) + tile_gap*self.idx if self.idx != 0 else tile_size*2 + tile_gap*4
        self.rect = pygame.rect.Rect(self.pos[0], self.pos[1], tower_width, tower_height)

        self.generate_tile_coords()
        for i, tile in enumerate(self.tiles):
            tile.build()

    def draw(self, surface):
        #pygame.draw.rect(surface, (255, 100, 0), self.rect)  # dark orange square
        for tile in self.tiles:
            tile.draw(surface)

    def update(self, dt):
        for tile in self.tiles:
            tile.update(dt)

    def generate_tile_coords(self):
        tile_size = self.tile_size
        tile_gap = self.tile_size/14
        left = self.rect.topleft[0]
        top = self.rect.topleft[1]
        if self.idx != 0:  # normal tower
            length = int(self.idx)
            left_coords = [left + (tile_size+tile_gap)*i for i in range(length)]
            top_coords = [top]*length
            top_left_coords = list(zip(left_coords, top_coords))[::-1]
        else:  # minus tower
            lc1 = left
            lc2 = left + tile_gap*4 + tile_size
            left_coords = [lc1, lc2, lc1, lc2, lc1, lc2, lc1]
            top_coords = [top + (tile_size+tile_gap*4)/2*i for i in range(7)]
            top_left_coords = list(zip(left_coords, top_coords))
        self.tile_coords = [(coord[0]+tile_size/2, coord[1]+tile_size/2) for coord in top_left_coords]

    def can_place(self, tile):
        if self.idx == 0:  # if minus tower, yes
            return True  
        if self.idx <= len(self.tiles):   # if tower full, no
            return False
        existing_tiles_in_gameboard = [t.colour for t in self.parent.tiles if t.pos[1]==self.parent.tile_coords[(self.idx-1)*5][1]]
        if tile.colour in existing_tiles_in_gameboard:  # if tile in gameboard, no
            return False
        if not self.tiles:  # if tower empty, yes
            return True
        return self.tiles.sprites()[0].colour == tile.colour

    def start_scoring(self):
        self.scoring = True
        self.scoring_timer = 0
    

class Text(Sprite):
    def __init__(self, parent, idx):
        super().__init__()
        self.parent = parent
        self.idx = idx+1  # 1 = name, 2 = score, 3 = add_score
        self.build()
        self.visible = True if self.idx in [1,2] else False

    def build(self, new_pos=None, new_tile_size=None):
        self.tile_size = int(new_tile_size if new_tile_size else self.parent.tile_size)
        self.pos = new_pos if new_pos else self.parent.text_coords[self.idx-1]

    def update(self, dt):
        message = self.parent.text_messages[self.idx-1]
        self.size = int(self.parent.text_sizes[self.idx-1])
        self.font = pygame.font.Font(game_state.font, self.size)
        self.rendered_text = self.font.render(message, True, game_state.player_cols[self.parent.idx-1])
        self.rect = self.rendered_text.get_rect(topright = self.pos)
        self.rendered_text = self.font.render(message, True, game_state.player_cols[self.parent.idx-1])
        if self.idx in [1,2]:
            if self.rect.topleft[0] > self.parent.rect.topleft[0]:
                self.rect.topleft = (self.parent.rect.topleft[0], self.rect.topleft[1])
                self.parent.text_coords[self.idx-1] = self.rect.topright
        elif self.idx == 3:
            score_text = list(self.parent.texts)[1]
            self.rect.topleft = (score_text.rect.topright[0]+self.tile_size*0.3, self.rect.topleft[1])
            self.parent.text_coords[self.idx-1] = self.rect.topright

    def draw(self, surface):
        if self.visible:
            surface.blit(self.rendered_text, self.rect.topleft)
        


# GAMEBOARD CLASS
class GameBoard(Sprite):
    def __init__(self, parent, idx):
        super().__init__()
        self.parent = parent
        self.idx = idx
        self.player_pos = idx
        self.original_image = resources.load_image(f"game_board_{self.idx}.png")
        self.score = 0
        self.tile_score = "+0"
        self.towers = Group()
        self.tiles = Group()
        self.texts = Group()
        self.build()
        self.populate()
        self.visible = True
        self.animating = False
        self.move_made = False
        self.scoring = False

    def build(self, new_pos=None, new_tile_size=None):
        self.tile_size = int(new_tile_size if new_tile_size else self.parent.tile_size*self.parent.game_board_sizes[self.player_pos-1])
        self.pos = new_pos if new_pos else self.parent.game_board_coords[self.player_pos-1]
        height = self.tile_size * 92/14
        width = self.original_image.get_width() * (height/self.original_image.get_height())
        self.size = (width, height)
        self.image = pygame.transform.smoothscale(self.original_image, self.size)
        self.rect = self.image.get_rect(center=self.pos)

        self.generate_towers()
        for tower in self.towers:
            tower.build()

        self.generate_tile_coords()
        for i, tile in enumerate(self.tiles):
            tile.build()

        self.generate_texts()
        for text in self.texts:
            text.build()
        
        self.extended_rect = self.rect.unionall([text.rect for text in self.texts])

    def handle_event(self, event):
        if self.visible:
            for tile in self.tiles:
                tile.handle_event(event)

    def draw(self, surface):
        if self.visible:
            surface.blit(self.image, self.rect.topleft)
            for tower in self.towers:
                tower.draw(surface)
            for tile in self.tiles:
                tile.draw(surface)
            for text in self.texts:
                text.draw(surface)

    def update(self, dt):
        if self.move_made:
            self.move_made = False
            if hasattr(self.parent, "current_player_idx"):
                self.parent.current_player_idx = (self.parent.current_player_idx)%len(self.parent.game_boards) +1
            if any([len(factory.tiles) != 0 for factory in list(self.parent.factories)+[self.parent.pot]]):
                self.parent.start_next_turn()
            else:
                self.parent.start_scoring()

        if self.animating:
            self.anim_time += dt
            t = min(self.anim_time / self.anim_duration, 1.0)  # Clamp [0,1]
            # Linear interpolation (can replace with easing later)
            new_x = self.start_pos[0] + (self.end_pos[0] - self.start_pos[0]) * t
            new_y = self.start_pos[1] + (self.end_pos[1] - self.start_pos[1]) * t
            new_width = int(self.start_size + (self.end_size - self.start_size) * t)
            snap(self, (new_x, new_y), new_width)
            if t >= 1.0:
                self.animating = False

        for tower in self.towers:
            tower.update(dt)
        for tile in self.tiles:
            tile.update(dt)
        for text in self.texts:
            text.update(dt)

        self.extended_rect = self.rect.unionall([text.rect for text in self.texts])

    def populate(self):
        towers = [Tower(self, i) for i in range(6)]
        self.towers.add(*towers)
        texts = [Text(self, i) for i in range(3)]
        self.texts.add(*texts)

    def generate_towers(self):
        tile_size = self.tile_size
        tile_gap = tile_size/14
        left_anchor = self.rect.left+tile_gap*3
        top_anchor = self.rect.top+tile_gap*3
        tower_coords = [(left_anchor+(tile_size+tile_gap)*4, top_anchor),
                             (left_anchor+(tile_size+tile_gap)*3,top_anchor+(tile_size+tile_gap*4)),
                             (left_anchor+(tile_size+tile_gap)*2, top_anchor+(tile_size+tile_gap*4)*2),
                             (left_anchor+(tile_size+tile_gap), top_anchor+(tile_size+tile_gap*4)*3),
                             (left_anchor, top_anchor+(tile_size+tile_gap*4)*4)]

        left_anchor = self.rect.left+tile_size*10+tile_gap*51
        top_anchor = self.rect.top+tile_gap*12
        minus_tower_coords = (left_anchor, top_anchor)

        self.tower_coords = [minus_tower_coords] + tower_coords

    def generate_tile_coords(self):
        tile_size = self.tile_size
        tile_gap = tile_size/14
        left_anchor = self.rect.left+tile_size*5.5+tile_gap*21
        top_anchor = self.rect.top+tile_size*0.5+tile_gap*3
        self.tile_coords = [(left_anchor+i*(tile_size+tile_gap*4), top_anchor+j*(tile_size+tile_gap*4)) for j in range(5) for i in range(5)]
        self.tile_colours = ["purple", "green", "red", "yellow", "blue"]

    def generate_texts(self):
        tile_size = self.tile_size
        tile_gap = tile_size/14
        right_anchor = self.rect.left + tile_size*4
        top_anchor = self.rect.top - tile_gap*3
        self.text_coords = [(right_anchor, top_anchor), (right_anchor-tile_size*2.5, top_anchor+tile_size-tile_gap*0.7), (right_anchor-tile_size*1.1, top_anchor+tile_size+tile_gap*3)]
        self.text_messages = [self.parent.player_names[self.idx-1], str(self.score), f"{self.tile_score}"]
        self.text_sizes = [self.tile_size*1.2, self.tile_size*2, self.tile_size*1.25]

    def start_scoring(self):
        self.scoring = True
        self.scoring_timer = 0

    def add_tile(self, tile, idx):
        tile.parent.tiles.remove(tile)
        self.tiles.add(tile)
        tile.parent = self
        tile.idx = idx
        
    def score_tile(self, tile_location, minus_tower=False):
        if minus_tower:
            minus_list = [-1,-1,-2,-2,-2,-3,-3]
            self.tile_score = minus_list[tile_location-1]
            operation = ""
        else:
            x,y = tile_location
            coords_in_use = [coord for coord in self.tile_coords if any([tile.pos==coord for tile in self.tiles])]
            row_coords = [coord for coord in self.tile_coords if coord[1]==y]
            col_coords = [coord for coord in self.tile_coords if coord[0]==x]

            horizontal_count = 0
            this_group_contains_new_tile = False
            for coord in row_coords:
                if coord == (x,y):
                    this_group_contains_new_tile = True

                if coord in coords_in_use:
                    horizontal_count += 1
                elif this_group_contains_new_tile:
                    break
                else:
                    horizontal_count = 0

            vertical_count = 0 
            this_group_contains_new_tile = False
            for coord in col_coords:
                if coord == (x,y):
                    this_group_contains_new_tile = True
                
                if coord in coords_in_use:
                    vertical_count += 1
                elif this_group_contains_new_tile:
                    break
                else:
                    vertical_count = 0

            if horizontal_count == 1 or vertical_count == 1:
                self.tile_score = horizontal_count + vertical_count - 1
            else:
                self.tile_score = horizontal_count + vertical_count
            operation = "+"
        
        self.score = max(0, self.score+self.tile_score)
        self.text_messages[1] = str(self.score)
        self.text_messages[2] = f"{operation}{self.tile_score}"
        tile_score_text = [t for t in self.texts if t.idx==3][0]
        show(tile_score_text)
        
            
        

#########################
# BACKGROUND MANAGEMENT
#########################

def build(event, scenes):
    if sys.platform in ("win32", "cygwin"):
        game_state.screen_height = event.h
        game_state.screen_width = event.w
        game_state.fullscreen = pygame.display.set_mode((game_state.screen_width, game_state.screen_height), RESIZABLE)
        game_state.screen_dimensions = (game_state.screen_width, game_state.screen_height)
    elif sys.platform.startswith("linux"):
        info = pygame.display.Info()
        game_state.screen_width = info.current_w
        game_state.screen_height = info.current_h
        game_state.dummy_fullscreen = pygame.display.set_mode((game_state.screen_width, game_state.screen_height), RESIZABLE)
        game_state.screen_width, game_state.screen_height = game_state.dummy_fullscreen.get_size()
        game_state.fullscreen = pygame.display.set_mode((game_state.screen_width, game_state.screen_height))
        game_state.screen_dimensions = (game_state.screen_width, game_state.screen_height)
    for scene in scenes.values():
        if hasattr(scene, 'build'):
            scene.build()      
   

#########################
# Functions
#########################

def snap(self, final_pos, final_size=None):
    game_state.rects_to_draw.append(self.rect)
    final_width = final_size
    final_tile_size = self.tile_size * (final_width/self.rect.width) if final_size else None
    self.build(final_pos, final_tile_size)
    # self.image = pygame.transform.smoothscale(self.original_image, (final_width, final_height))
    # self.rect = self.image.get_rect(center = final_pos)
    # self.pos = final_pos
    game_state.rects_to_draw.append(self.rect)
    if hasattr(self, "texts"):
        for text in self.texts:
            game_state.rects_to_draw.append(text.rect)

def move(self, final_pos, final_size, speed=None):
    (sw, sh) = game_state.screen_dimensions
    self.start_pos = self.rect.center
    self.start_size = self.rect.width
    self.end_pos = final_pos
    self.end_size = final_size

    xdist = self.end_pos[0]-self.start_pos[0]
    ydist = self.end_pos[1]-self.start_pos[1]
    dist = (math.sqrt(xdist**2 + ydist**2)/max(sw,sh)) * 600

    if dist > 0:
        self.animating = True
        self.anim_time = 0
        self.anim_duration = dist/speed if speed else (dist**0.25)/7
    else:
        self.animating = False

def switch_scene(scene_name):
    if scene_name == "single_player_continue_game":
        if hasattr(game_state, "number_of_players") and "single_player" in game_state.scenes.keys() and game_state.single_player_number_of_players == len(game_state.scenes["single_player"].game_board_coords):
            game_state.scenes[scene_name] = ContinueGame("single_player")
        else:
            scene_name = "single_player_num_players"
    elif scene_name == "multiplayer_continue_game":
        if hasattr(game_state, "number_of_players") and "multiplayer" in game_state.scenes.keys() and game_state.multiplayer_number_of_players == len(game_state.scenes["multiplayer"].game_board_coords):
            game_state.scenes[scene_name] = ContinueGame("multiplayer")
        else:
            scene_name = "multiplayer_num_players"
    if scene_name == "single_player_num_players":
        game_state.scenes[scene_name] = NumOfPlayers("single_player")
        game_state.scenes.pop("single_player", None)
    elif scene_name == "single_player":
        if scene_name not in game_state.scenes:
            from single_player2 import SinglePlayer
            game_state.scenes["single_player"] = SinglePlayer()
    elif scene_name == "multiplayer_num_players":
        game_state.scenes[scene_name] = NumOfPlayers("multiplayer")
        game_state.scenes.pop("multiplayer", None)
    elif scene_name == "input_players":
        game_state.scenes[scene_name] = PlayerNames()
    elif scene_name == "multiplayer":
        if scene_name not in game_state.scenes:
            from multiplayer2 import MultiPlayer
            game_state.scenes["multiplayer"] = MultiPlayer()
    elif scene_name == "menu":
        from menu2 import Menu
        game_state.scenes[scene_name] = Menu()
      
    game_state.current_scene = scene_name
    #game_state.fullscreen.blit(game_state.bg_image, (0, 0))
    game_state.rects_to_draw = [game_state.fullscreen.get_rect()]
    pygame.key.stop_text_input()
    

def show(self):
    self.visible = True
    game_state.rects_to_draw.append(self.rect)
def hide(self):
    self.visible = False
    game_state.rects_to_draw.append(self.rect)


def transfer_tiles(tiles_to_move, source, target, minus_tower, source_is_pot=False):
    poses = []
    tiles_left_to_move = tiles_to_move.copy()

    for i, tile in enumerate(tiles_to_move):
        try:
            if source_is_pot and tile.colour == "one":
                current_target = minus_tower
            else:
                current_target = target
            tile_coord_idx = len(current_target.tiles) if target.__class__.__name__ != "Pot" else i
            target_pos = current_target.tile_coords[tile_coord_idx]
            poses.append(target_pos)
            source.tiles.remove(tile)
            current_target.tiles.add(tile)
            tile.parent = current_target
            tile.idx = tile_coord_idx+1
            tiles_left_to_move.remove(tile)

        except:
            if current_target.idx == 0:
                for tile in tiles_left_to_move:
                    source.tiles.remove(tile)
            else:
                minus_poses = transfer_tiles(tiles_left_to_move, source, minus_tower, minus_tower)
                poses += minus_poses
            break

    return poses


#########################
# UI HELPERS
#########################
def center_image(img, screen):
    """Return rect for centering an image on screen."""
    return img.get_rect(center=(screen.get_width() / 2, screen.get_height() / 2))

def GetEqualTopLeftRatio(side, ratio_from_known_side):
    (sw, sh) = game_state.screen_dimensions
    if side == "top":
        ratio_from_top = ratio_from_known_side
        distance_from_top = ratio_from_top * sh
        ratio_from_left = distance_from_top / sw
    else:
        ratio_from_left = ratio_from_known_side
        distance_from_left = ratio_from_left * sw
        ratio_from_top = distance_from_left / sh

    return (ratio_from_left, ratio_from_top)

def create_octagon_mask(rect, cut_size):
    x, y, width, height = rect
    cut_size = min(cut_size, width/2, height/2)
    points = [
        (x + cut_size, y),                  # Top-left corner
        (x + width - cut_size, y),         # Top-right corner
        (x + width, y + cut_size),         # Right-top corner
        (x + width, y + height - cut_size),# Right-bottom corner
        (x + width - cut_size, y + height),# Bottom-right corner
        (x + cut_size, y + height),        # Bottom-left corner
        (x, y + height - cut_size),        # Left-bottom corner
        (x, y + cut_size)                  # Left-top corner
    ]
    return points

def crop_image_to_octagon(image, rect, cut_size, border_colour=None, border_thickness=0, colour=None):
    # Create a mask surface
    mask_surface = pygame.Surface((rect[2], rect[3]), pygame.SRCALPHA)
    mask_surface.fill((0, 0, 0, 0))  # Transparent background

    # Draw the octagon shape on the mask
    octagon_points = create_octagon_mask((0, 0, rect[2], rect[3]), cut_size)
    if colour:
        pygame.draw.polygon(mask_surface, (255, 255, 255, 200), octagon_points)  # semi-transparent
    else:
        pygame.draw.polygon(mask_surface, (255, 255, 255, 255), octagon_points)

    # Crop the given region from the original image (⚡ no flip, no scale)
    cropped_image = pygame.Surface((rect[2], rect[3]), pygame.SRCALPHA)
    cropped_image.blit(image, (0, 0), rect)

    # Apply mask
    cropped_image.blit(mask_surface, (0, 0), None, pygame.BLEND_RGBA_MULT)

    # Draw a border
    border_surface = pygame.Surface((rect[2] + border_thickness * 2, rect[3] + border_thickness * 2), pygame.SRCALPHA)
    border_surface.fill((0, 0, 0, 0))

    octagon_points = create_octagon_mask(
        (0, 0, rect[2] + border_thickness * 2, rect[3] + border_thickness * 2),
        cut_size + border_thickness // 2,
    )
    pygame.draw.polygon(border_surface, border_colour, octagon_points)
    border_surface.blit(cropped_image, (border_thickness, border_thickness))

    return border_surface



################
# Game Setup
################

def generate_x_agon(game_state):
    x = 2*game_state.number_of_players+1

    ratio_from_top = 0.5
    (cx, cy) = GetEqualTopLeftRatio("top", ratio_from_top)
    radius_ratio = 0.3
    (rx, ry) = GetEqualTopLeftRatio("top", radius_ratio)

    angle_step = 2 * math.pi / x  # Angle between vertices
    vertices = []
    for i in range(x):
        angle = i * angle_step - math.pi/2
        px = cx + rx * math.cos(angle)
        py = cy + ry * math.sin(angle)
        vertices.append((px, py))
    return (cx, cy), vertices


def get_event_pos(event):
    (sw, sh) = game_state.fullscreen.get_size()
    if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
        pos = event.pos
        try:
            x_full, y_full = pos
            # scale down to render_surface coordinates
            x = x_full * game_state.screen_dimensions[0] / game_state.fullscreen.get_width()
            y = y_full * game_state.screen_dimensions[1] / game_state.fullscreen.get_height()
            return (x,y)
        except:
            pass

    elif event.type in (pygame.FINGERDOWN, pygame.FINGERUP, pygame.FINGERMOTION):
        # Finger events give normalized (0..1) values
        event.pos = (int(event.x * sw), int(event.y * sh))
        pos = event.pos
        try:
            x_full, y_full = pos
            # scale down to render_surface coordinates
            x = x_full * game_state.screen_dimensions[0] / game_state.fullscreen.get_width()
            y = y_full * game_state.screen_dimensions[1] / game_state.fullscreen.get_height()
            return (x,y)
        except:
            pass

    return None