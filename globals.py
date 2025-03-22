import pygame
import random
import sys
import math
from pygame.locals import *
from pathlib import Path
import os
import platform


# Determine if the app is running as a packaged executable or as a script
if getattr(sys, 'frozen', False):  # If running as an executable
    base_path = Path(sys._MEIPASS)  # Path to the extracted resources folder
else:
    base_path = Path(__file__).parent  # Path to the current script


def detect_os():
    if "ANDROID_STORAGE" in os.environ:
        return "Android"
    elif platform.system() == "Windows":
        return "Windows"
    else:
        return "Unknown OS"


# Setup global game info
class GlobalState:
    def __init__(self):
        self.platform = detect_os()
        self.mode = "light"
        self.difficulty = "easy"
        self.min_screen_ratio = 1.85
        self.max_screen_ratio = 2.25
        self.default_screen_ratio = 2.1
        info = pygame.display.Info()  # Get screen info
        self.screen_height = int(info.current_h*0.6)
        self.screen_width = int(info.current_w*0.7)
        self.large_tile_height_multiplier = 1/25
        if self.platform == "Android":
            self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.FULLSCREEN | pygame.DOUBLEBUF)
        elif self.platform == "Windows":
            self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.RESIZABLE)
        self.font = pygame.font.Font(base_path / 'resources' / "boucherie.ttf", 24)
        self.new_menu=True
        self.new_settings=False
        self.new_single_player=False
        self.single_player_running=False
        self.new_local_multiplayer=False
        self.local_multiplayer_running=False
        

game_state = GlobalState()


# Images
red_tile_large = pygame.image.load(base_path / 'resources' / "red_tile_large.png")
blue_tile_large = pygame.image.load(base_path / 'resources' / "blue_tile_large.png")
yellow_tile_large = pygame.image.load(base_path / 'resources' / "yellow_tile_large.png")
green_tile_large = pygame.image.load(base_path / 'resources' / "green_tile_large.png")
purple_tile_large = pygame.image.load(base_path / 'resources' / "purple_tile_large.png")
red_tile = pygame.image.load(base_path / 'resources' / "red_tile.png")
blue_tile = pygame.image.load(base_path / 'resources' / "blue_tile.png")
yellow_tile = pygame.image.load(base_path / 'resources' / "yellow_tile.png")
green_tile = pygame.image.load(base_path / 'resources' / "green_tile.png")
purple_tile = pygame.image.load(base_path / 'resources' / "purple_tile.png")
one_tile = pygame.image.load(base_path / 'resources' / "one_tile_new.png")
game_board_1_long = pygame.image.load(base_path / 'resources' / "game_board_1.png")
game_board_2_long = pygame.image.load(base_path / 'resources' / "game_board_2.png")
game_board_3_long = pygame.image.load(base_path / 'resources' / "game_board_3.png")
game_board_4_long = pygame.image.load(base_path / 'resources' / "game_board_4.png")
game_board_1_compressed = pygame.image.load(base_path / 'resources' / "game_board_1_compressed.png")
game_board_2_compressed = pygame.image.load(base_path / 'resources' / "game_board_2_compressed.png")
game_board_3_compressed = pygame.image.load(base_path / 'resources' / "game_board_3_compressed.png")
game_board_4_compressed = pygame.image.load(base_path / 'resources' / "game_board_4_compressed.png")
game_board_long = [game_board_1_long, game_board_2_long, game_board_3_long, game_board_4_long]
game_board_compressed = [game_board_1_compressed, game_board_2_compressed, game_board_3_compressed, game_board_4_compressed]
factory_image = pygame.image.load(base_path / 'resources' / "factory.png")
background_light = pygame.image.load(base_path / 'resources' / "background_light.jpg")
background_dark = pygame.image.load(base_path / 'resources' / "background_dark.jpg")
popup_dark = pygame.image.load(base_path / 'resources' / "popup_dark.png")
popup_light = pygame.image.load(base_path / 'resources' / "popup_light.png")

tile_images = {"r":red_tile, "b": blue_tile, "y": yellow_tile, "g": green_tile, "p": purple_tile}
large_tile_images = {"r":red_tile_large, "b": blue_tile_large, "y": yellow_tile_large, "g": green_tile_large, "p": purple_tile_large}

two_players_mul = pygame.image.load(base_path / 'resources' / "two_players.png")
two_players_mul_clicked = pygame.image.load(base_path / 'resources' / "two_players_clicked.png")
three_players_mul = pygame.image.load(base_path / 'resources' / "three_players.png")
three_players_mul_clicked = pygame.image.load(base_path / 'resources' / "three_players_clicked.png")
four_players_mul = pygame.image.load(base_path / 'resources' / "four_players.png")
four_players_mul_clicked = pygame.image.load(base_path / 'resources' / "four_players_clicked.png")
two_players_com = pygame.image.load(base_path / 'resources' / "two_players_com.png")
two_players_com_clicked = pygame.image.load(base_path / 'resources' / "two_players_com_clicked.png")
three_players_com = pygame.image.load(base_path / 'resources' / "three_players_com.png")
three_players_com_clicked = pygame.image.load(base_path / 'resources' / "three_players_com_clicked.png")
four_players_com = pygame.image.load(base_path / 'resources' / "four_players_com.png")
four_players_com_clicked = pygame.image.load(base_path / 'resources' / "four_players_com_clicked.png")

main_menu = pygame.image.load(base_path / 'resources' / "main_menu.png").convert_alpha()
main_menu_clicked = pygame.image.load(base_path / 'resources' / "main_menu_clicked.png").convert_alpha()
play = pygame.image.load(base_path / 'resources' / "play.png").convert_alpha()
play_clicked = pygame.image.load(base_path / 'resources' / "play_clicked.png").convert_alpha()
play_again = pygame.image.load(base_path / 'resources' / "play_again.png").convert_alpha()
play_again_clicked = pygame.image.load(base_path / 'resources' / "play_again_clicked.png").convert_alpha()
light_popup = pygame.image.load(base_path / 'resources' / "light_popup.png").convert_alpha()
dark_popup = pygame.image.load(base_path / 'resources' / "dark_popup.png").convert_alpha()


######################
###### Classes #######
######################

class Tile:
    def __init__(self, col, height, top_left):
        self.col=col
        colour, image = col
        self.colour = colour
        self.original_image = image
        self.height = height
        self.top_left = top_left
        self.image = pygame.transform.smoothscale(self.original_image, (height, height))
        self.rect = self.image.get_rect(topleft = top_left)
        self.larger_rect = pygame.Rect(self.rect[0]-self.rect[2], self.rect[1]-self.rect[3], self.rect[2]*3, self.rect[3]*3)
        self.glow = pygame.Surface((self.height*30/25, self.height*30/25), pygame.SRCALPHA)       

    def draw(self, screen, glow=False):
        if glow:
            pygame.draw.rect(self.glow, "yellow", self.glow.get_rect(), border_radius=int(self.height/10))
            screen.blit(self.glow, (self.top_left[0]-self.height*2.5/25, self.top_left[1]-self.height*2.5/25))
        screen.blit(self.image, self.top_left)

    def snap(self, height, top_left):
        if height != self.height:
            self.height = height
            self.image = pygame.transform.smoothscale(self.original_image, (height, height))
            self.glow = pygame.Surface((self.height*30/25, self.height*30/25), pygame.SRCALPHA)  
        self.top_left = top_left
        self.rect = self.image.get_rect(topleft = top_left)
        self.larger_rect = pygame.Rect(self.rect[0]-self.rect[2], self.rect[1]-self.rect[3], self.rect[2]*3, self.rect[3]*3)

    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)
    

class Factory:
    def __init__(self, center, tiles=None):
        self.original_image = factory_image
        self.center = center
        self.radius = game_state.large_tile_height*2.8
        self.image = pygame.transform.smoothscale(self.original_image, (self.radius, self.radius))
        self.rect = self.image.get_rect(center=self.center)
        self.generate_coords()
        if tiles == None:
            self.tiles = [Tile(random.choice(list(tile_images.items())), game_state.large_tile_height, self.coords[i]) for i in range(4)]
        else:
            self.tiles = [Tile((tile.colour, tile.original_image), game_state.large_tile_height, self.coords[i]) for i,tile in enumerate(tiles)]

    def draw(self, screen):
        left = self.center[0] - self.radius/2
        top = self.center[1] - self.radius/2
        screen.blit(self.image, (left,top))
        for tile in self.tiles:
            tile.draw(screen)

    def generate_coords(self):
        tile_height = game_state.large_tile_height
        half_gap = game_state.large_tile_height/50
        x = self.center[0]
        y = self.center[1]
        self.coords = [(x-tile_height-half_gap, y+half_gap), (x+half_gap, y+half_gap),
                       (x-tile_height-half_gap, y-tile_height-half_gap), (x+half_gap, y-tile_height-half_gap)]


class Pot:
    def __init__(self, center, tiles=None):
        self.center = center
        self.rect = [self.center[0]-game_state.screen_width/6.25, self.center[1]-game_state.screen_width/6.25, game_state.screen_width/3.125, game_state.screen_width/3.125]
        self.generate_coords()
        self.order_coords()
        if tiles == None:
            self.tiles = [Tile(("o",one_tile), game_state.large_tile_height, self.next_coords(1,0)[0])]
        else:
            self.tiles = [Tile((tile.colour, tile.original_image), game_state.large_tile_height, self.next_coords(1,i)[0]) for i,tile in enumerate(tiles)]
        
    def draw(self, screen):
        for tile in self.tiles:
            tile.draw(screen)

    def generate_coords(self):
        spacing = game_state.large_tile_height*27/25
        center_x = self.center[0]
        center_y = self.center[1]
        self.coords = [(center_x + x*spacing - game_state.large_tile_height/2, 
                        center_y + y*spacing - game_state.large_tile_height/2)
                        for x in range(-2,3) for y in range(-2,3)]
        # now add bonus 3 tile spaces for worst case scenario
        self.coords += [(center_x + 3*spacing - game_state.large_tile_height/2, center_y - game_state.large_tile_height/2),
                      (center_x - 3*spacing - game_state.large_tile_height/2, center_y - game_state.large_tile_height/2),
                      (center_x - game_state.large_tile_height/2, center_y + 3*spacing - game_state.large_tile_height/2)]

    def order_coords(self):
        center_x = self.center[0] - game_state.large_tile_height/2
        center_y = self.center[1] - game_state.large_tile_height/2
        distances = [(coord, math.sqrt((coord[0]-center_x)**2 + (coord[1]-center_y)**2)) for coord in self.coords]
        sorted_distances = sorted(distances, key=lambda x: x[1])
        sorted_coords = [coord for coord,_ in sorted_distances]
        self.coords = sorted_coords
    
    def next_coords(self, new_tiles, existing_tiles):
        return self.coords[existing_tiles : existing_tiles+new_tiles]
    

class Gameboard:
    def __init__(self, player, top_left, towers=None, tiles=None, player_pos=None, score=0):
        self.player_pos = player_pos if player_pos else player
        self.player = player
        self.top_left = top_left
        self.score = score
        self.get_dimensions()
        self.generate_tile_coords()
        if tiles == None:
            self.tiles = [[None]*5,[None]*5,[None]*5,[None]*5,[None]*5]
        else:
            self.tiles = [[Tile((tile.colour,tile.original_image), self.tile_height, tile.top_left) if isinstance(tile, Tile) else None for tile in row] for row in tiles]
        self.generate_tower_coords()
        if towers == None:
            self.towers = [Tower(self.player, self.player_pos, i, self.tile_height, self.tower_coords[i]) for i in range(6)]
        else:
            self.towers = [Tower(self.player, self.player_pos, tower.category, self.tile_height, self.tower_coords[i], tower.tiles) for i,tower in enumerate(towers)]
        self.snap(self.tile_height, self.top_left)
        

    def draw(self, screen, add_score=None, glow_tiles=[]):
        screen.blit(self.image, self.top_left)
        #pygame.draw.rect(screen, "blue", (self.top_left[0], self.top_left[1], self.tile_height*2, self.tile_height*2))
        text = "Score"
        score = str(self.score)
        text_pos = (self.top_left[0], self.top_left[1]-self.tile_height*0.1)
        score_left = self.top_left[0]-self.tile_height/2 if self.score >= 100 and self.player_pos == 1 else self.top_left[0]
        score_pos = (score_left, self.top_left[1]+self.tile_height*0.6)
        text_font = pygame.font.Font(base_path / 'resources' / "boucherie.ttf", int(self.tile_height))
        score_font = pygame.font.Font(base_path / 'resources' / "boucherie.ttf", int(self.tile_height*1.75))
        texts =  [(text, text_pos, text_font), (score, score_pos, score_font)]
        score_rect = score_font.render(score, True, game_state.text_col).get_rect(topleft = score_pos)
        if add_score != None:
            if add_score > 0:
                add_score = f"+{add_score}"
                add_score_col = "#00A43E" if game_state.mode == "dark" else "#007400"
            else:
                add_score = str(add_score)
                add_score_col = "red"
            add_score_pos = (score_rect[0]+score_rect[2]+self.tile_height*0.075, self.top_left[1]+self.tile_height*0.825)
            add_score_font = pygame.font.Font(base_path / 'resources' / "boucherie.ttf", int(self.tile_height*1.15))
            text = add_score_font.render(add_score, True, add_score_col)
            text_pos = text.get_rect(topleft = add_score_pos)
            screen.blit(text, text_pos)
        for message, pos, font in texts:  # without add_score
            player_cols = ["#0096F0", "red", "#00A43E", "#AF4CF2"] if game_state.mode=="dark" else ["#1C0074", "#920000", "#006600", "#740077"]
            col = player_cols[self.player-1]
            text = font.render(message, True, col)
            text_pos = text.get_rect(topleft = pos)
            screen.blit(text, text_pos)
        for row in self.tiles:
            for tile in row:
                if isinstance(tile, Tile):
                    if tile in glow_tiles:
                        tile.draw(screen, glow=True)
                    else:
                        tile.draw(screen)
        for tower in self.towers:
            tower.draw(screen)

    def get_dimensions(self, height_limit=None):
        self.tile_height = game_state.large_tile_height if self.player_pos==1 else game_state.small_tile_height
        tile_height = self.tile_height
        tile_gap = tile_height/25
        if self.player_pos == 1 or (self.player_pos == 2 and game_state.number_of_players == 2) or (self.player_pos != 1 and game_state.number_of_players == 4):
            self.original_image = game_board_long[self.player-1]
            if height_limit:
                desired_height = height_limit
                self.tile_height = desired_height/5.88
                if self.player_pos != 1:
                    game_state.small_tile_height = self.tile_height
            else:
                desired_height = 2*tile_gap + 5*(tile_height+tile_gap*4)
        else:
            self.original_image = game_board_compressed[self.player-1]
            if height_limit:
                desired_height = height_limit
                self.tile_height = desired_height/7.44
                game_state.small_tile_height = self.tile_height
            else:
                desired_height = 2*tile_gap + 5*(tile_height+tile_gap*4) + (tile_gap*14+tile_height)

        self.original_dimensions = self.original_image.get_rect()[2:4]
        size_multiplier =  desired_height / self.original_dimensions[1]
        self.dimensions = tuple(dimension*size_multiplier for dimension in self.original_dimensions)
        self.height = self.dimensions[1]
        if self.top_left[0] + self.dimensions[0] > game_state.screen_width*0.98:
            height_to_width_ratio = self.dimensions[1]/self.dimensions[0]
            self.get_dimensions(height_limit = (game_state.screen_width*0.98-self.top_left[0])*height_to_width_ratio)

    def snap(self, tile_height, top_left):
        self.top_left = top_left
        ratio_change = tile_height/self.tile_height
        self.height = self.height * ratio_change
        self.get_dimensions()
        self.image = pygame.transform.smoothscale(self.original_image, self.dimensions)
        self.rect = self.image.get_rect(topleft=self.top_left)
        # if doesn't fit on screen
        if self.rect[0]+self.dimensions[0] > game_state.screen_width-game_state.screen_height-0.04:
            pass

        self.generate_tile_coords()
        for i,row in enumerate(self.tiles):
            for j,tile in enumerate(row):
                try:
                    tile.snap(self.tile_height, self.coords[i][j])
                except:
                    pass
        self.generate_tower_coords()
        for i, tower in enumerate(self.towers):
            tower.player_pos = self.player_pos
            tower.coords = self.tower_coords[i]
            tower.snap(tower.height*ratio_change, self.tower_coords[i])

    def generate_tile_coords(self):
        tile_height = self.tile_height
        tile_gap = tile_height/25
        left = self.top_left[0] + tile_height*5 + tile_gap*21
        top = self.top_left[1] + tile_gap*3
        grid_colours = ["p", "g", "r", "y", "b", "p", "g", "r", "y", "b"]
        coords = [[[(left+(tile_height+tile_gap*4)*i,top+(tile_height+tile_gap*4)*j), grid_colours[i+j]] for i in range(5)] for j in range(5)]
        # transpose
        self.coords = [[coords[col][row][0] for row in range(len(coords))] for col in range(len(coords[0]))]
        self.coord_cols = [[coords[row][col][1] for row in range(len(coords))] for col in range(len(coords[0]))]

    def generate_tower_coords(self):
        tile_height = self.tile_height
        tile_gap = tile_height/25
        left_anchor = self.top_left[0]+tile_gap*2
        top_anchor = self.top_left[1]+tile_gap*2
        self.tower_coords = [(left_anchor+(tile_height+tile_gap)*4, top_anchor),
                             (left_anchor+(tile_height+tile_gap)*3,top_anchor+(tile_height+tile_gap*4)),
                             (left_anchor+(tile_height+tile_gap)*2, top_anchor+(tile_height+tile_gap*4)*2),
                             (left_anchor+(tile_height+tile_gap), top_anchor+(tile_height+tile_gap*4)*3),
                             (left_anchor, top_anchor+(tile_height+tile_gap*4)*4)]
        if self.player_pos == 1 or (self.player_pos == 2 and game_state.number_of_players == 2) or (self.player_pos != 1 and game_state.number_of_players == 4):
            left_anchor = self.top_left[0]+tile_height*12
            top_anchor = self.top_left[1]+tile_height*2/3
            self.tower_coords.append((left_anchor, top_anchor))
        else:
            left_anchor = self.top_left[0]+tile_height*3.5
            top_anchor = self.top_left[1]+tile_height*6.2
            self.tower_coords.append((left_anchor, top_anchor))
        self.tower_coords = [self.tower_coords[-1]] + self.tower_coords[:-1]

    def add_tiles(self, tower):
        if len(tower.tiles) == tower.category:  # if tower full
            row = tower.category-1
            col = self.coord_cols[row].index(tower.tiles[0].colour)
            self.tiles[row][col] = tower.tiles[0]

            tiles_to_collect = list(tower.tiles)[1:]
            collect_coords = [tower.coords[0]]*(len(tower.tiles)-1)
            collect_heights = [self.tile_height]*(len(tower.tiles)-1)
            
            tiles_to_move = [tower.tiles[0]]
            new_coords = [self.coords[row][col]]
            new_heights = [self.tile_height]

            game_board_tiles_after = [[t.colour if isinstance(t, Tile) else "-" for t in row] for row in self.tiles]

            score = calculate_tile_score(game_board_tiles_after, (row,col))
        
        else:
            return 0, [],[],[],[],[],[]

        return score, tiles_to_collect, collect_coords, collect_heights, tiles_to_move, new_coords, new_heights


class Tower:
    def __init__(self, player, player_pos, category, tile_height, top_left, tiles=None):
        self.player_pos = player_pos
        self.player = player
        self.category = category
        self.tile_height = tile_height
        self.top_left = top_left
        self.generate_coords()
        if tiles == None:
            self.tiles = []
        else:
            #if self.category == 0:
             #   self.tiles = []
            #else:
            self.tiles = [Tile((tile.colour,tile.original_image), self.tile_height, self.coords[i]) for i,tile in enumerate(tiles)]
        self.snap(self.height, self.top_left)

    def draw(self, screen):
        colours = [(255,0,0,100), (0,0,255,100), (255,209,125,100), (0,255,255,100)]
        #pygame.draw.rect(screen, colours[self.player-1], self.rect)
        for tile in self.tiles:
            tile.draw(screen)

    def snap(self, height, top_left):
        self.top_left = top_left
        ratio_change = height/self.height
        self.height = height
        self.tile_height = self.tile_height * ratio_change
        self.generate_coords()
        for i,tile in enumerate(self.tiles):
            tile.snap(self.tile_height, self.coords[i])

    def generate_coords(self):
        self.tile_gap = self.tile_height/25
        tile_height = self.tile_height
        tile_gap = self.tile_gap
        left = self.top_left[0]
        top = self.top_left[1]
        if self.category != 0:  # normal tower
            length = int(self.category)
            left_coords = [left+tile_gap + (tile_height+tile_gap)*i for i in range(length)]
            top_coords = [top+tile_gap]*length
            self.coords = list(zip(left_coords, top_coords))[::-1]
            if length == 1:
                top += (tile_gap)
                height = tile_height*4/5
            elif length == 5:
                top += (tile_height*1/5+tile_gap)
                height = tile_height*4/5
            else:
                top += (tile_height*1/5+tile_gap)
                height = tile_height*3/5
            self.rect = pygame.Rect((left, top,  (tile_height+tile_gap)*(length)+tile_gap,  height))
        else:  # minus tower
            if self.player_pos == 1 or (self.player_pos == 2 and game_state.number_of_players == 2) or (self.player_pos != 1 and game_state.number_of_players == 4):  #zig zag
                lc1 = left + tile_gap
                lc2 = left + tile_gap*5 + tile_height
                left_coords = [lc1, lc2, lc1, lc2, lc1, lc2, lc1]
                top_coords = [top + tile_gap + (tile_height+tile_gap*4)/2*i for i in range(7)]
                self.coords = list(zip(left_coords, top_coords))
                self.rect = pygame.Rect((left, top, tile_height*2+tile_gap*6, tile_height*4+tile_gap*14))
            else:  # straight minus
                length = 7
                left_coords = [left+tile_gap*3 + (tile_height+tile_gap*4)*i for i in range(length)]
                top_coords = [top+tile_gap*3]*length
                self.coords = list(zip(left_coords, top_coords))
                left += tile_gap
                top += (tile_height*1/5+tile_gap)
                height = tile_height*4/5
                self.rect = pygame.Rect((left, top,  (tile_height+tile_gap*4)*(length),  height))
        self.height = self.rect[3]

    def add_tiles(self, tiles, current_factory=None, pot=None, spaces=None):
        moving_tiles = []
        moving_coords = []
        moving_sizes = []
        remaining_tiles = []
        for i, tile in enumerate(tiles):
            try:
                moving_coords.append(self.coords[len(self.tiles)+i])
                moving_tiles.append(tile)
                moving_sizes.append(self.tile_height)
            except:
                remaining_tiles.append(tile)
        if current_factory and "o" in [tile.colour for tile in pot.tiles] and isinstance(current_factory, Pot) and spaces<len(tiles)+1:
            one = current_factory.tiles[0]
            remaining_tiles = [moving_tiles[-1]] + remaining_tiles
            moving_tiles = [one] + moving_tiles[:-1]

        for tile in moving_tiles:
            self.tiles.append(tile)

        return moving_tiles, moving_coords, moving_sizes, remaining_tiles


class Button:
    def __init__(self, size, center, image, clicked_image=None, action=None):
        self.size = size
        self.original_image = image
        if clicked_image == None:
            self.original_clicked_image = image
        else:
            self.original_clicked_image = clicked_image
        self.center = center
        self.angle = random.randint(-20,20)
        self.resize()
        self.shown_image = self.image
        self.action = action  # Function to execute when button is clicked
        self.generate_shadow()
        self.generate_glow()

    def draw(self, screen, show_shadow=True):
        left = self.center[0]-self.rect[2]/2
        top = self.center[1]-self.rect[3]/2
        if show_shadow:
            screen.blit(self.rotated_shadow, (left-int(self.size/18), top+int(self.size/18)))
        screen.blit(self.shown_image, (left,top))

    def resize(self):
        #rotate
        self.rotated_image = pygame.transform.rotate(self.original_image, self.angle)
        self.rotated_clicked_image = pygame.transform.rotate(self.original_clicked_image, self.angle)
        self.rotated_rect = self.rotated_image.get_rect(center = self.center)
        #resize
        angle = self.angle*-1 if self.angle<0 else self.angle
        button_desired_size = self.size*(math.cos(math.radians(angle))+math.sin(math.radians(angle)))
        self.button_size = (button_desired_size, button_desired_size)
        self.image = pygame.transform.smoothscale(self.rotated_image, self.button_size)
        self.clicked_image = pygame.transform.smoothscale(self.rotated_clicked_image, self.button_size)
        self.rect = self.image.get_rect(center=self.center)

    def generate_shadow(self):
        self.shadow = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.rect(self.shadow, (0,0,0,170), self.shadow.get_rect(), border_radius=int(self.size/10) )       
        self.rotated_shadow = pygame.transform.rotate(self.shadow, self.angle)

    def generate_glow(self):
        self.glow = pygame.Surface((self.size*1.1, self.size*1.1), pygame.SRCALPHA)
        pygame.draw.rect(self.glow, (255,255,0,250), self.glow.get_rect(), border_radius=int(self.size/8) )
        self.rotated_glow = pygame.transform.rotate(self.glow, self.angle)

        


#####################
##### Functions #####
#####################

def resize(event):
    game_state.screen_width = event.w
    game_state.screen_height = event.h
    game_state.screen = pygame.display.set_mode((game_state.screen_width, game_state.screen_height), pygame.RESIZABLE)
    try:
        game_state.large_tile_height = game_state.screen_width * game_state.large_tile_height_multiplier
        game_state.small_tile_height = game_state.large_tile_height * game_state.small_tile_height_multiplier
    except:
        pass


def get_background():
    if game_state.platform == "Android":
        if game_state.mode == "light":
            game_state.background_col=(255,209,125)
            game_state.text_col = "#300000"
        else:
            game_state.background_col=(90,40,0)
            game_state.text_col = "#FFE4B3"
    elif game_state.platform == "Windows":
        if game_state.mode == "light":
            game_state.background = background_light
            game_state.text_col = "#300000"
        else:
            game_state.background = background_dark
            game_state.text_col = "#FFE4B3"


def blit_background():
    if game_state.platform == "Android":
        game_state.screen.fill(game_state.background_col)
    elif game_state.platform == "Windows":
        game_state.screen.blit(game_state.background, (0,0))


def move(objects_to_move, new_coords, new_heights, game_boards, factories, pot, buttons, game_info, speed=None):
    component_distances = []
    for i, object in enumerate(objects_to_move):
        component_distances.append([new_coords[i][0]-object.top_left[0], new_coords[i][1]-object.top_left[1]])
    distances = [math.sqrt(dist[0]**2 + dist[1]**2) for dist in component_distances]
    start_distances = distances
    start_heights = [object.height for object in objects_to_move]
    speed = [dist/20 if dist <= game_state.screen_height/2 else dist/50 for dist in distances] if speed==None else [speed]*len(distances)
    
    while any(distances[i] > game_state.large_tile_height for i in range(len(distances))):
        for i, object in enumerate(objects_to_move):
            if distances[i] >= new_heights[i]/2:
                left = object.top_left[0] - component_distances[i][0] * speed[i]/distances[i] * 3
                top = object.top_left[1] - component_distances[i][1] * speed[i]/distances[i] * 3
                height = start_heights[i] + (1-distances[i]/start_distances[i])*(new_heights[i]-start_heights[i])
                top_left = (left,top)
                if distances[i] >= new_heights[i]/2:
                    object.snap(height, top_left)

                component_distances = []
                for i, object in enumerate(objects_to_move):
                    component_distances.append([object.top_left[0]-new_coords[i][0], object.top_left[1]-new_coords[i][1]])
                distances = [math.sqrt(dist[0]**2 + dist[1]**2) for dist in component_distances]

            else:
                object.snap(new_heights[i], new_coords[i])

        blit_background()
        draw_game(game_state.screen, game_boards, factories, pot, buttons, game_info)
        pygame.display.flip()
        pygame.time.delay(10)
    
    for i, object in enumerate(objects_to_move):
        object.snap(new_heights[i], new_coords[i])

    blit_background()
    draw_game(game_state.screen, game_boards, factories, pot, buttons, game_info)
    pygame.display.flip()

def calculate_tile_score(after, coord):
    x,y = coord
    # Check horizontal connections
    horizontal_count = 0  # Start with the tile itself
    # Count left
    for col in range(y-1, -1, -1):
        if after[x][col] != "-":  # Non-zero indicates a tile
            horizontal_count = max(2, horizontal_count+1)
        else:
            break
    # Count right
    for col in range(y+1, 5):
        if after[x][col] != "-":  # Non-zero indicates a tile
            horizontal_count = max(2, horizontal_count+1)
        else:
            break

    # Check vertical connections
    vertical_count = 0  # Start with the tile itself, 1 point was included in horizontal
    # Count up
    for row in range(x-1, -1, -1):
        if after[row][y] != "-":  # Non-zero indicates a tile
            vertical_count = max(2, vertical_count+1)
        else:
            break
    # Count down
    for row in range(x+1, 5):
        if after[row][y] != "-":  # Non-zero indicates a tile
            vertical_count = max(2, vertical_count+1)
        else:
            break

    # Calculate the total score
    if horizontal_count + vertical_count == 0:
        return 1
    else:
        return horizontal_count + vertical_count
    

def able_to_be_placed(tower, game_board, dragged_tiles):
    if tower.tiles==[]:
        if not dragged_tiles[0].colour in [t.colour if isinstance(t, Tile) else "-" for t in game_board.tiles[tower.category-1]]:
            return True
    elif len(tower.tiles) != tower.category:
        if tower.tiles[0].original_image==dragged_tiles[0].original_image:
            return True
    return False

def to_menu(game_state):
    game_state.new_menu=True
    game_state.settings_running=False
    game_state.input_running=False
    game_state.write_names=False
    game_state.new_single_player = False
    game_state.single_player_running=False
    game_state.new_local_multiplayer=False
    game_state.local_multiplayer_running=False

def play_names(game_state):
    game_state.write_names=False

def run_game_again(game_state):
    if game_state.local_multiplayer_running:
        game_state.new_local_multiplayer = True
        game_state.local_multiplayer_running = False
    else:
        game_state.new_single_player = True
        game_state.single_player_running = False
        

def draw_popup(game_state, screen, message, error_message, user_input):
    popup_width, popup_height = 400, 200
    popup_x = (game_state.screen_width - popup_width) // 2
    popup_y = (game_state.screen_height - popup_height) // 2
    # Draw pop-up box
    pygame.draw.rect(screen, "grey", (popup_x, popup_y, popup_width, popup_height))  # Background
    pygame.draw.rect(screen, "black", (popup_x, popup_y, popup_width, popup_height), 3)  # Border
    # Render the messages
    text_surface = game_state.font.render(message, True, "black")
    text_rect = text_surface.get_rect(center=(popup_x + popup_width // 2, popup_y + 50))
    screen.blit(text_surface, text_rect)
    error_text_surface = game_state.font.render(error_message, True, "red")
    error_text_rect = text_surface.get_rect(center=(popup_x + popup_width // 2, popup_y + 80))
    screen.blit(error_text_surface, error_text_rect)
    # Render the user's input text
    input_surface = game_state.font.render(user_input, True, "black")
    input_rect = input_surface.get_rect(center=(popup_x + popup_width // 2, popup_y + 120))
    screen.blit(input_surface, input_rect)

#########################
### Number of players ###
#########################

def choose_two_players(game_state):
    game_state.number_of_players = 2
    game_state.large_tile_height_multiplier = 1/27
    game_state.large_tile_height = game_state.screen_width * game_state.large_tile_height_multiplier
    game_state.small_tile_height_multiplier = 0.75
    game_state.small_tile_height = game_state.large_tile_height * game_state.small_tile_height_multiplier
    game_state.input_running = False
def choose_three_players(game_state):
    game_state.number_of_players = 3
    game_state.large_tile_height_multiplier = 1/28
    game_state.large_tile_height = game_state.screen_width * game_state.large_tile_height_multiplier
    game_state.small_tile_height_multiplier = 0.58
    game_state.small_tile_height = game_state.large_tile_height * game_state.small_tile_height_multiplier
    game_state.input_running = False
def choose_four_players(game_state):
    game_state.number_of_players = 4
    game_state.large_tile_height_multiplier = 1/30
    game_state.large_tile_height = game_state.screen_width * game_state.large_tile_height_multiplier
    game_state.small_tile_height_multiplier = 0.5
    game_state.small_tile_height = game_state.large_tile_height * game_state.small_tile_height_multiplier
    game_state.input_running = False

def create_number_of_players(game_state):
    screen_width = game_state.screen_width
    screen_height = game_state.screen_height
    button_height = screen_height*0.25
    if game_state.new_single_player:
        two_players = two_players_com
        two_players_clicked = two_players_com_clicked
        three_players = three_players_com
        three_players_clicked = three_players_com_clicked
        four_players = four_players_com
        four_players_clicked = four_players_com_clicked
    else:
        two_players = two_players_mul
        two_players_clicked = two_players_mul_clicked
        three_players = three_players_mul
        three_players_clicked = three_players_mul_clicked
        four_players = four_players_mul
        four_players_clicked = four_players_mul_clicked

    two_players_button = Button(button_height, (screen_width*0.3,screen_height*0.63),
                                        two_players, two_players_clicked, action=choose_two_players)
    three_players_button = Button(button_height, (screen_width*0.5,screen_height*0.6),
                                        three_players, three_players_clicked, action=choose_three_players)
    four_players_button = Button(button_height, (screen_width*0.7,screen_height*0.63),
                                        four_players, four_players_clicked, action=choose_four_players)
    menu_button = Button(button_height*0.5, (screen_height*0.1,screen_height*0.1), main_menu, main_menu_clicked, action=to_menu)

    buttons = [menu_button, two_players_button, three_players_button, four_players_button]

    return buttons

def run_number_of_players(game_state, event, buttons):
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

    return buttons, update_rect


def draw_number_of_players(game_state, screen, buttons):
    game_state.font = pygame.font.Font(base_path / 'resources' / "boucherie.ttf", int(game_state.screen_height/8))
    text_surface = game_state.font.render("How many players?", True, game_state.text_col)
    game_state.font = pygame.font.Font(base_path / 'resources' / "boucherie.ttf", 24)
    text_rect = text_surface.get_rect(center=(screen.get_width()*0.5, screen.get_height()*0.25))
    screen.blit(text_surface, text_rect)
    for button in buttons:
        button.draw(screen)

########## Write names

def create_write_names(game_state):
    screen_width = game_state.screen_width
    screen_height = game_state.screen_height
    button_height = screen_height*0.25
    try:
        game_state.player_names
    except:
        game_state.player_names = []
        for i in range(game_state.number_of_players):
            game_state.player_names.append(f"Player {i+1}")

    play_button = Button(button_height*0.85, (screen_width*0.91,screen_height-screen_width*0.09),
                                        play, play_clicked, action=play_names)
    
    buttons = play_button
    screen = game_state.screen
    player_cols = ["#0096F0", "red", "#00A43E", "#AF4CF2"] if game_state.mode=="dark" else ["#1C0074", "#CC0000", "#006600", "#740077"]
    game_state.font = pygame.font.Font(base_path / 'resources' / "boucherie.ttf", int(game_state.screen_height/9))
    if game_state.number_of_players == 2:
        name_coords = [(screen.get_width()*0.32, screen.get_height()*0.5),(screen.get_width()*0.68, screen.get_height()*0.5)]
    elif game_state.number_of_players == 3:
        name_coords = [(screen.get_width()*0.32, screen.get_height()*0.45),(screen.get_width()*0.68, screen.get_height()*0.45),(screen.get_width()*0.5, screen.get_height()*0.65)]
    else:
        name_coords = [(screen.get_width()*0.32, screen.get_height()*0.45),(screen.get_width()*0.68, screen.get_height()*0.45),(screen.get_width()*0.32, screen.get_height()*0.65),(screen.get_width()*0.68, screen.get_height()*0.65)]
    text_rects = []
    for i,name in enumerate(game_state.player_names):
        full_name_text = game_state.font.render("MoMoMoMoMo", True, player_cols[i])
        full_name_rect = full_name_text.get_rect(center=name_coords[i])
        text_rect = pygame.Rect((full_name_rect[0], full_name_rect[1], full_name_rect[2], full_name_rect[3]))
        text_rects.append(text_rect)

    return text_rects, buttons

def run_write_names(game_state, event, text_rects, buttons, editing_index):
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
        
        for i, rect in enumerate(text_rects):
            if game_state.player_names[i] == "":
                game_state.player_names[i] = f"Player {i+1}"
        for i, rect in enumerate(text_rects):
            if rect.collidepoint(event.pos):
                pygame.key.start_text_input()
                editing_index = i
                game_state.player_names[i] = ""
                update_rect = text_rects
                break
        
        else:
            pygame.key.stop_text_input()
            if editing_index != None:
                update_rect = text_rects[editing_index]
            editing_index = None

    if event.type == pygame.KEYDOWN and editing_index is not None:
        if event.key == pygame.K_BACKSPACE and game_state.player_names[editing_index] != "":
            game_state.player_names[editing_index] = game_state.player_names[editing_index][:-1]
            update_rect = text_rects[editing_index]
        elif event.key == pygame.K_RETURN:
            pygame.key.stop_text_input()
            update_rect = text_rects[editing_index]
            editing_index = None
        else:
            text_surface = game_state.font.render(game_state.player_names[editing_index], True, game_state.text_col)
            text_rect = text_surface.get_rect(center=text_rects[editing_index].center)
            if text_rect[2] < text_rects[editing_index][2]*0.85:
                game_state.player_names[editing_index] += event.unicode
                update_rect = text_rects[editing_index]
                
    return buttons, editing_index, update_rect


def draw_write_names(game_state, screen, text_rects, buttons, editing_index):
    game_state.font = pygame.font.Font(base_path / 'resources' / "boucherie.ttf", int(game_state.screen_height/8))
    text_surface = game_state.font.render("Enter Player Names", True, game_state.text_col)
    text_rect = text_surface.get_rect(center=(screen.get_width()*0.5, screen.get_height()*0.225))
    screen.blit(text_surface, text_rect)
    for button in buttons:
        button.draw(screen)

    player_cols = ["#0096F0", "red", "#00A43E", "#AF4CF2"] if game_state.mode=="dark" else ["#1C0074", "#CC0000", "#006600", "#740077"]
    game_state.font = pygame.font.Font(base_path / 'resources' / "boucherie.ttf", int(game_state.screen_height/9))
    for i,name in enumerate(game_state.player_names):
        text_surface = game_state.font.render(name, True, game_state.text_col)
        text_rect = text_surface.get_rect(center=text_rects[i].center)
        backing_rect = text_rects[i]
        cut_size = int(backing_rect[3]*0.2)
        border_radius = int(backing_rect[3]*0.1)
        popup = popup_dark if game_state.mode == "dark" else popup_light
        # Crop the image to an octagon and add a border
        if i == editing_index:
            octagon_image = crop_image_to_octagon(popup, backing_rect, cut_size, player_cols[i], border_radius, colour=True)
        else:
            octagon_image = crop_image_to_octagon(popup, backing_rect, cut_size, player_cols[i], border_radius)
        
        screen.blit(octagon_image, (backing_rect[0] - border_radius, backing_rect[1] - border_radius))
        screen.blit(text_surface, text_rect)
        



########################
##### Create Game ######
########################

def rotate_game_boards(game_state, game_boards):
    game_board_coords = [g.top_left for g in game_boards]
    game_board_tile_heights = [g.tile_height for g in game_boards]
    game_board_new_coords = list([game_board_coords[-1]] + game_board_coords[:-1])
    game_board_new_tile_heights = list([game_board_tile_heights[-1]] + game_board_tile_heights[:-1])
    for i,game_board in enumerate(game_boards):
        game_board.player_pos -= 1
        if game_board.player_pos == 0:
            game_board.player_pos = game_state.number_of_players
        game_board.snap(game_board_new_tile_heights[i], game_board_new_coords[i])
    update_rect = [pygame.Rect(gb.rect[0]-gb.rect[2]*0.05, gb.rect[1]-gb.rect[3]*0.1, gb.rect[2]*1.1, gb.rect[3]*1.2) for gb in game_boards]
    return update_rect

def arrange_game_boards(game_boards=None, game_info=None, new_round=None):
    left_anchor = game_state.screen_width*0.475
    top_anchor = game_state.screen_height*0.04
    coords = [(left_anchor, top_anchor)]
    right_anchor = game_state.screen_width - top_anchor
    game_board_area_width = right_anchor - left_anchor

    if game_state.number_of_players == 4:
        coords = [(left_anchor+top_anchor, top_anchor)]
        game_board_top = game_state.screen_height * 0.5
        left_anchor = game_state.screen_width*0.475
        game_board_area_width = right_anchor - left_anchor 
        coords += [(left_anchor, game_board_top), 
                   (left_anchor + game_board_area_width/4, game_board_top + game_board_area_width/4.75), 
                   (left_anchor+game_board_area_width/2, game_board_top)]
    elif game_state.number_of_players == 3:
        game_board_top = game_state.screen_height * 0.575
        left_anchor = game_state.screen_width*0.475
        game_board_area_width = right_anchor - left_anchor   
        step = game_board_area_width / (game_state.number_of_players-1)
        coords += [(left_anchor+step*i, game_board_top) for i in range(game_state.number_of_players-1)]
    else:  # number of players = 2
        game_board_top = game_state.screen_height * 0.55
        left_anchor = game_state.screen_width*0.525
        game_board_area_width = right_anchor - left_anchor   
        step = game_board_area_width / (game_state.number_of_players - 1)
        coords += [(left_anchor+step*i, game_board_top) for i in range(game_state.number_of_players-1)]


    if game_boards == None:
        game_boards = [Gameboard(i+1, coords[i]) for i in range(game_state.number_of_players)]
    else:
        game_boards = [Gameboard(i+1, coords[game_boards[i].player_pos-1], towers=game_boards[i].towers,
                                 tiles=game_boards[i].tiles, player_pos=game_boards[i].player_pos, 
                                 score=game_boards[i].score) for i in range(game_state.number_of_players)]
        if new_round:
            game_info["next_player"] = game_info["next_first_player"]
            if game_state.local_multiplayer_running:
                while game_boards[game_info["next_first_player"]-1].player_pos != 1:
                    update_rect = rotate_game_boards(game_state, game_boards)
        else:
            if game_state.local_multiplayer_running:
                while game_boards[game_info["next_player"]-1].player_pos != 1:
                    update_rect = rotate_game_boards(game_state, game_boards)
            
    return game_boards, game_info

def generate_x_agon(game_state):
    x = 2*game_state.number_of_players+1
    radius = game_state.screen_width/6.25
    cx, cy = game_state.screen_height*0.15 + radius, game_state.screen_height*0.5
    angle_step = 2 * math.pi / x  # Angle between vertices
    vertices = []
    for i in range(x):
        angle = i * angle_step - math.pi/2
        px = cx + radius * math.cos(angle)
        py = cy + radius * math.sin(angle)
        vertices.append((px, py))
    return (cx, cy), vertices

def create_game(game_state, game_boards=None, factories=None, pot=None, game_info=None, new_round=None):
    center, factory_points = generate_x_agon(game_state)
    if game_boards != None:
        game_boards, game_info = arrange_game_boards(game_boards=game_boards, game_info=game_info, new_round=new_round)
    else:
        game_boards, game_info = arrange_game_boards()
    if factories != None:
        for i, factory in enumerate(factories):
            factories[i] = Factory((factory_points[i][0], factory_points[i][1]), factory.tiles)
        pot = Pot(center, pot.tiles)
    else:
        factories = [Factory((x,y)) for (x,y) in factory_points]
        pot = Pot(center)
    round = game_info["round"]+1 if game_info else 0
    next_first_player = game_info["next_first_player"] if game_info else 1
    next_player = game_info["next_first_player"] if game_info else 1
    game_info = {"selected_tile": None,
                 "dragged_tiles": [],
                 "offsets": [],
                 "current_factory": None,
                 "positions_in_factory": [],
                 "moving_objects": [],
                 "moving_new_coords": [],
                 "moving_new_heights": [],
                 "round": round,
                 "next_first_player": next_first_player,
                 "next_player": next_player,
                 "placed": False}
    return game_boards, factories, pot, game_info

def get_dragged_tiles(factory, tile):
    return [t for t in factory.tiles if (t.original_image == tile.original_image and tile.original_image != one_tile)]

def draw_game(screen, game_boards, factories, pot, buttons, game_info, add_score=None, glow_tiles=[]):
    if screen != game_state.screen:
        screen.fill((0, 0, 0, 0))
    for button in buttons:
        button.draw(screen)
    for game_board in game_boards:
        if add_score and game_board.player == add_score[0]:
            game_board.draw(screen, add_score[1], glow_tiles)
        elif glow_tiles != []:
            game_board.draw(screen, None, glow_tiles)
        else:
            game_board.draw(screen)
    for factory in factories:
        factory.draw(screen)
    pot.draw(screen)
    for tile in game_info["dragged_tiles"]:
        tile.draw(screen)


def create_octagon_mask(rect, cut_size):
    x, y, width, height = rect
    cut_size = min(cut_size, width // 2, height // 2)
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
        pygame.draw.polygon(mask_surface, (255, 255, 255, 200), octagon_points)  # White transparent to show colour
    else:
        pygame.draw.polygon(mask_surface, (255, 255, 255, 255), octagon_points)  # White shape
    # Crop the image using the mask
    cropped_image = pygame.Surface((rect[2], rect[3]), pygame.SRCALPHA)
    image = pygame.transform.flip(image, False, True)
    image = pygame.transform.scale(image, (game_state.screen_width*1.05, game_state.screen_height*1.1))
    cropped_image.blit(image, (0, 0), rect)
    cropped_image.blit(mask_surface, (0, 0), None, pygame.BLEND_RGBA_MULT)
    # Draw a border
    border_surface = pygame.Surface((rect[2]+border_thickness*2, rect[3]+border_thickness*2), pygame.SRCALPHA)
    border_surface.fill((0, 0, 0, 0))  # Transparent background
    octagon_points = create_octagon_mask(
        (0, 0, rect[2]+border_thickness*2, rect[3]+border_thickness*2), cut_size+border_thickness//2)
    pygame.draw.polygon(border_surface, border_colour, octagon_points)
    border_surface.blit(cropped_image, (border_thickness, border_thickness))
    return border_surface


def draw_new_round(screen, game_boards, factories, pot, buttons, game_info, new_round, game_mode):
    update_rect = None
    if not new_round["run_once"]:
        for game_board in game_boards:
            game_board.draw(screen)
        for button in buttons:
            button.draw(screen)
        for factory in factories:
            left = factory.center[0] - factory.radius/2
            top = factory.center[1] - factory.radius/2
            screen.blit(factory.image, (left,top))
        pot.draw(screen)
        text_center = game_state.screen_width*0.725
        round_text = f"Round {game_info['round']}"
        round_pos = (text_center, game_state.screen_height*0.4)
        player_cols = ["#0096F0", "red", "#00A43E", "#AF4CF2"] if game_state.mode=="dark" else ["#1C0074", "#CC0000", "#006600", "#740077"]
        if game_mode == "single":
            if game_info["next_first_player"] == 1:
                first_player_text = "You go first"
            else:
                if len(game_boards) == 2:
                    first_player_text = f"CPU goes first"
                else:
                    first_player_text = f"CPU {game_info['next_first_player']-1} goes first"
        else:
            #first_player_text = f"Player {game_info["next_first_player"]} goes first"
            first_player_text = f"{game_state.player_names[game_info['next_first_player']-1]} goes first"
        first_player_pos = (text_center, game_state.screen_height*0.56)
        first_player_col = player_cols[game_info["next_first_player"]-1]
        texts = [(round_text,round_pos,pygame.font.Font(base_path / 'resources' / "boucherie.ttf", game_state.screen_height//7), game_state.text_col), 
                (first_player_text,first_player_pos,pygame.font.Font(base_path / 'resources' / "boucherie.ttf", game_state.screen_height//11), first_player_col)]
        # show popup
        popup_width = max([font.render(message, True, game_state.text_col).get_rect()[2] for message,_,font,_ in texts + [(f"Player goes first",first_player_pos,pygame.font.Font(base_path / 'resources' / "boucherie.ttf", game_state.screen_height//11), game_state.text_col)]])*1.1
        popup_height = (max([font.render(message, True, game_state.text_col).get_rect(center=pos)[1] for message,pos,font,_ in texts])
                        - min([font.render(message, True, game_state.text_col).get_rect(center=pos)[1] for message,pos,font,_ in texts])
                        + texts[1][2].render(round_text, True, game_state.text_col).get_rect(center=round_pos)[3])*1.17
        popup_left = text_center - popup_width/2
        popup_top = game_state.screen_height*0.475 - popup_height/2
        popup_rect = pygame.Rect((int(popup_left), int(popup_top), int(popup_width), int(popup_height)))
        
        cut_size = int(popup_height*0.15)
        border_radius = int(popup_height*0.07)
        popup = popup_dark if game_state.mode == "dark" else popup_light
        border_colour = "darkblue" if game_state.mode == "light" else "#D66600"
        # Crop the image to an octagon and add a border
        octagon_image = crop_image_to_octagon(popup, popup_rect, cut_size, border_colour, border_radius)
        # Draw the image
        screen.blit(octagon_image, (popup_rect[0] - border_radius, popup_rect[1] - border_radius))
        # show texts
        for message, pos, font, col in texts:
            text = font.render(message, True, col)
            text_pos = text.get_rect(center=pos)
            screen.blit(text, text_pos)
        game_state.font = pygame.font.Font(base_path / 'resources' / "boucherie.ttf", 24)
        update_rect = pygame.Rect(0,0,game_state.screen_width, game_state.screen_height)

    if new_round["current"] - new_round["start"] > 200:
        for f, factory in enumerate(factories):
            if new_round["current"] - new_round["start"] > 200 + (2000//len(factories))*f:
                for t, tile in enumerate(factory.tiles):
                    if new_round["current"] - new_round["start"] > 200 + (2000//len(factories))*f + (2000//(len(factories)*6))*t:
                        tile.draw(screen)
                        update_rect = tile.larger_rect

    if new_round["current"] - new_round["start"] > 200 + 2200:
        update_rect = pygame.Rect(game_state.screen_width*0.4,0,game_state.screen_width*0.6, game_state.screen_height)
        new_round["running"] = False
        new_round["cpu"] = True
        blit_background()
        draw_game(screen, game_boards, factories, pot, buttons, game_info, None, [])
        game_state.screen.blit(screen, (0,0))
        pygame.display.update(update_rect)

    new_round["run_once"] = True
    return new_round, update_rect


def draw_results(screen, game_over, game_boards, factories, pot, buttons, game_mode):
    game_over["running"] = False
    winner = game_boards[[g.score for g in game_boards].index(max([g.score for g in game_boards]))]
    #screen.fill(game_state.background_col)
    for game_board in game_boards:
        game_board.draw(screen)

    popup_width = game_state.screen_width * 0.325
    popup_height = game_state.screen_height * 0.8
    popup_left = game_state.screen_width * 0.075
    popup_top = game_state.screen_height * 0.1

    text_center = popup_left + popup_width/2
    if len([g for g in game_boards if g.score == winner.score]) >= 2:
        result_text = "It's a Draw!"
    else:
        if game_mode == "single":
            if winner.player == 1:
                result_text = "You Win"
            else:
                if game_state.number_of_players == 2:
                    result_text = "CPU Wins"
                else:
                    result_text = f"CPU {winner.player-1} Wins"
        else:
            #result_text = f"Player {winner.player} Wins"
            result_text = f"{game_state.player_names[winner.player-1]} Wins"
    result_pos = (text_center, popup_top + popup_height*0.1)
    players_texts = []
    scores_texts = []
    max_width = 0
    for i in range(game_state.number_of_players):
        if game_mode == "single":
            if i == 0:
                players_texts.append(f"You")
            else:
                if game_state.number_of_players == 2:
                    players_texts.append(f"CPU")
                else:
                    players_texts.append(f"CPU {i}")
        else:
            #players_texts.append(f"P{i+1}")
            text_surface = game_state.font.render(game_state.player_names[i], True, game_state.text_col)
            text_rect = text_surface.get_rect()
            while text_rect[2] >= popup_width*0.65:
                game_state.player_names[i] = game_state.player_names[i][:-1]
                text_surface = game_state.font.render(game_state.player_names[i], True, game_state.text_col)
                text_rect = text_surface.get_rect()
            if text_rect[2] > max_width:
                max_width = text_rect[2]
            players_texts.append(f"{game_state.player_names[i]}")
        scores_texts.append(f"{game_boards[i].score}")
    if game_mode == "single":
        center = popup_left+popup_width*0.575
    else:
        center = popup_left+popup_width*0.5 + max_width*0.6
    if game_state.number_of_players == 2:
        scores_poses = [(center,popup_top+popup_height*0.25), (center,popup_top+popup_height*0.45)]
    if game_state.number_of_players == 3:
        scores_poses = [(center,popup_top+popup_height*0.2), (center,popup_top+popup_height*0.35), (center,popup_top+popup_height*0.5)]
    if game_state.number_of_players == 4:
        scores_poses = [(center,popup_top+popup_height*0.175), (center,popup_top+popup_height*0.3), (center,popup_top+popup_height*0.425), (center,popup_top+popup_height*0.55)]
    
    if game_mode == "single" or result_text == "It's a Draw!":
        result_size = pygame.font.Font(base_path / 'resources' / "boucherie.ttf", game_state.screen_height//10)
    else:
        result_size = pygame.font.Font(base_path / 'resources' / "boucherie.ttf", game_state.screen_height//11)
    texts = [(result_text, result_pos, result_size, game_state.text_col)]
    player_cols = ["#0096F0", "red", "#00A43E", "#AF4CF2"] if game_state.mode=="dark" else ["#1C0074", "#CC0000", "#006600", "#740077"]
    p_texts = []
    s_texts = []
    for i in range(game_state.number_of_players):
        p_texts.append((f"{players_texts[i]}: ",scores_poses[i],pygame.font.Font(base_path / 'resources' / "boucherie.ttf", game_state.screen_height//10), player_cols[i]))
        s_texts.append((scores_texts[i],scores_poses[i],pygame.font.Font(base_path / 'resources' / "boucherie.ttf", game_state.screen_height//10), player_cols[i]))
    # show popup
    cut_size = int(popup_height*0.09)
    border_radius = int(popup_height*0.045)
    popup = popup_dark if game_state.mode == "dark" else popup_light
    popup_rect = [popup_left, popup_top, popup_width, popup_height]
    border_colour = "darkblue" if game_state.mode == "light" else "orange"
    # Crop the image to an octagon and add a border
    octagon_image = crop_image_to_octagon(popup, popup_rect, cut_size, border_colour, border_radius)
    # Draw the image
    screen.blit(octagon_image, (popup_rect[0] - border_radius, popup_rect[1] - border_radius))
    # show texts
    for message, pos, font, col in texts:
        text = font.render(message, True, col)
        text_pos = text.get_rect(center=pos)
        screen.blit(text, text_pos)
    for message, pos, font, col in p_texts:
        text = font.render(message, True, col)
        text_pos = text.get_rect(topright=pos)
        screen.blit(text, text_pos)
    for message, pos, font, col in s_texts:
        text = font.render(message, True, col)
        text_pos = text.get_rect(topleft=pos)
        screen.blit(text, text_pos)

    if len(buttons) == 1:
        button_height = game_state.screen_height*0.15
        game_over_menu_button = Button(button_height, (popup_left+popup_width*0.25,popup_top+popup_height*0.85),
                                            main_menu, main_menu_clicked,
                                            action=to_menu)
        play_again_button = Button(button_height, (popup_left+popup_width*0.75,popup_top+popup_height*0.85),
                                            play_again, play_again_clicked,
                                            action=run_game_again)
        buttons += [game_over_menu_button, play_again_button]

    for button in buttons[1:]:
        button.draw(screen)
    
    #game_over["show_results"] = False

    return game_over, buttons, pygame.Rect(0,0,game_state.screen_height, game_state.screen_width*0.6)