import pygame
import random
import sys
import time
import math
from pygame.locals import *

red_tile = pygame.image.load("red_tile.png")
blue_tile = pygame.image.load("blue_tile.png")
yellow_tile = pygame.image.load("yellow_tile.png")
green_tile = pygame.image.load("green_tile.png")
purple_tile = pygame.image.load("purple_tile.png")
one_tile = pygame.image.load("one_tile.png")
game_board_long = pygame.image.load("game_board.png")
game_board_compressed = pygame.image.load("game_board_compressed.png")
factory_image = pygame.image.load("factory.png")

# Initialize Pygame
pygame.init()

# Screen dimensions
min_screen_ratio = 2.25
max_screen_ratio = 2.35
default_screen_ratio = 2.3
screen_height = 500
screen_width = screen_height * default_screen_ratio
large_tile_size = screen_height/12
screen = pygame.display.set_mode((screen_width, screen_height), RESIZABLE)
font = pygame.font.Font(None, 36)
pygame.display.set_caption("Azul Game")

number_of_players = int(input("How many players? "))
while number_of_players > 4 or number_of_players < 2:
    number_of_players = int(input("How many players? (Has to be between 2 and 4): "))

if number_of_players == 4:
    tile_size_multiplier = 0.42
elif number_of_players == 3:
    tile_size_multiplier = 0.5
else:  # number of players = 2
    tile_size_multiplier = 0.65
small_tile_size = large_tile_size * tile_size_multiplier

# Tile class
class Tile:
    def __init__(self, image, position, size):
        self.original_image = image
        self.image = pygame.transform.smoothscale(image, (size, size))
        self.position = position
        self.rect = self.image.get_rect(topleft=position)
        self.size = size
        self.speed = large_tile_size*100

    def draw(self, screen):
        screen.blit(self.image, self.position)

    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)
    
    def snap(self, new_position):
        self.position = new_position
        self.rect = self.image.get_rect(topleft=self.position)

    
tile_images = [red_tile, blue_tile, yellow_tile, green_tile, purple_tile]

# Factory class to hold tiles
class Factory:
    def __init__(self, x, y, tiles=[], removed_tiles=[]):
        self.x = x
        self.y = y
        self.tiles = tiles
        self.removed_tiles = removed_tiles
        self.generate_tiles()
        self.radius = large_tile_size*2.8
        self.image = pygame.transform.smoothscale(factory_image, (self.radius, self.radius))
        
    def generate_tiles(self):
        size = large_tile_size
        gap = large_tile_size / 50
        if self.tiles != []:
            self.tiles = [Tile(self.tiles[0].original_image, (self.x-large_tile_size-gap, self.y +gap), size),
                          Tile(self.tiles[1].original_image, (self.x+gap, self.y+gap), size),
                          Tile(self.tiles[2].original_image, (self.x-large_tile_size-gap, self.y-large_tile_size-gap), size),
                          Tile(self.tiles[3].original_image, (self.x+gap, self.y-large_tile_size-gap), size),]
        elif self.removed_tiles == []:
            self.tiles = [Tile(random.choice(tile_images), (self.x-large_tile_size-gap, self.y +gap), size),
                        Tile(random.choice(tile_images), (self.x+gap, self.y+gap), size),
                        Tile(random.choice(tile_images), (self.x-large_tile_size-gap, self.y-large_tile_size-gap), size),
                        Tile(random.choice(tile_images), (self.x+gap, self.y-large_tile_size-gap), size)]

    def draw(self, screen):
        x = self.x - self.radius/2
        y = self.y - self.radius/2
        screen.blit(self.image, (x,y))
        for tile in self.tiles + self.removed_tiles:
            tile.draw(screen)


class Pot:
    def __init__(self, screen_height, tiles=None, removed_tiles=None):
        self.x = screen_height/2
        self.y = screen_height/2
        self.generate_coords(screen_height)
        self.order_coords()
        if tiles == None and removed_tiles == None:
            self.tiles = [Tile(one_tile, self.next_coords(1,0)[0], large_tile_size)]
        else:
            self.tiles = [Tile(tiles[i].original_image, self.next_coords(1,i)[0], large_tile_size) for i in range(len(tiles))]
        if removed_tiles == None:
            self.removed_tiles = []
        else:
            self.removed_tiles = [Tile(tiles[i].original_image, self.next_coords(1,i)[0], large_tile_size) for i in range(len(removed_tiles))]
        
    def generate_coords(self, screen_height):
        diameter=screen_height/3
        spacing = diameter/4 + large_tile_size/25
        self.coords = [(self.x + x*spacing - large_tile_size/2, self.y + y*spacing - large_tile_size/2) for x in range(-2,3) for y in range(-2,3)]
        # now add bonus 3 tile spaces for worst case scenario
        self.coords += [(self.x + 3*spacing - large_tile_size/2, self.y - large_tile_size/2),
                      (self.x - 3*spacing - large_tile_size/2, self.y - large_tile_size/2),
                      (self.x - large_tile_size/2, self.y + 3*spacing - large_tile_size/2)]

    def order_coords(self):
        centre_x = self.x - large_tile_size/2
        centre_y = self.y - large_tile_size/2
        distances = [(coord, math.sqrt((coord[0]-centre_x)**2 + (coord[1]-centre_y)**2)) for coord in self.coords]
        sorted_distances = sorted(distances, key=lambda x: x[1])
        sorted_coords = [coord for coord, distance in sorted_distances]
        self.coords = sorted_coords
    
    def next_coords(self, new_tiles, existing_tiles):
        return self.coords[existing_tiles : existing_tiles+new_tiles]

    def draw(self, screen):
        for tile in self.tiles + self.removed_tiles:
            tile.draw(screen)


class GameBoard:
    def __init__(self, player, right, top, tiles=None):
        self.player = player
        if player == 1 or (player == 2 and number_of_players == 2):
            self.original_image = game_board_long
        else:
            self.original_image = game_board_compressed
        if tiles == None:
            self.tiles = [[],[],[],[],[],[]]
        else:
            self.tiles = tiles
        self.right = right
        self.top = top
        self.get_pos()
        self.generate_towers()

    def get_pos(self):
        if self.player == 1:
            tile_size = large_tile_size
        else:
            tile_size = small_tile_size
        tile_gap = tile_size/25
        game_board_dimensions = self.original_image.get_rect()[2:4]
        if self.player == 1 or (self.player == 2 and number_of_players == 2):
            game_board_desired_height = 2*tile_gap + 5*(tile_size+tile_gap*4)
        else:
            game_board_desired_height = 2*tile_gap + 5*(tile_size+tile_gap*4) + (tile_gap*14+tile_size)
        multiplier =  game_board_desired_height / game_board_dimensions[1]
        game_board_size = tuple(dimension*multiplier for dimension in game_board_dimensions)
        self.image = pygame.transform.smoothscale(self.original_image, game_board_size)

        self.left = self.right - game_board_size[0]
        left_anchor = self.left
        top_anchor = self.top
        self.position = (left_anchor, top_anchor)

    def generate_towers(self):
        tiles=self.tiles
        if self.player == 1:
            tile_size = large_tile_size
        else:
            tile_size = small_tile_size
        tile_gap = tile_size/25
        left_anchor = self.position[0]+tile_gap*2
        top_anchor = self.position[1]+tile_gap*2
        self.towers = [
            Tower((left_anchor+(tile_size+tile_gap)*4, top_anchor), 1, self.player, tiles[0]),  # from left, from top, width, height
            Tower((left_anchor+(tile_size+tile_gap)*3, top_anchor+(tile_size+tile_gap*4)), 2, self.player, tiles[1]),
            Tower((left_anchor+(tile_size+tile_gap)*2, top_anchor+(tile_size+tile_gap*4)*2), 3, self.player, tiles[2]),
            Tower((left_anchor+(tile_size+tile_gap), top_anchor+(tile_size+tile_gap*4)*3), 4, self.player, tiles[3]),
            Tower((left_anchor, top_anchor+(tile_size+tile_gap*4)*4), 5, self.player, tiles[4])
        ]
        if self.player == 1 or (self.player == 2 and number_of_players == 2):
            left_anchor = self.position[0]+tile_size*12
            top_anchor = self.position[1]+tile_size*2/3
            self.towers.append(Tower((left_anchor, top_anchor), 0, self.player, tiles[5]))
        else:
            left_anchor = self.position[0]+tile_size*3.5
            top_anchor = self.position[1]+tile_size*6.2
            self.towers.append(Tower((left_anchor, top_anchor), 0, self.player, tiles[5]))
        
    def draw(self, screen):
        screen.blit(self.image, self.position)
        #for i, tower in enumerate(self.towers):
         #   tower.draw(screen)
        for tower in self.towers:
            for tile in tower.tiles:
                tile.draw(screen)
        

class Tower:
    def __init__(self, pos, category, player, tiles=None):
        self.category = category
        if tiles == None:
            self.tiles = []
        else:
            self.tiles = tiles
        self.pos = pos
        self.player = player
        self.generate_coords()
        self.generate_tiles()
        self.rect = pygame.Rect(self.rectpos)

    def add_tiles(self, tiles):
        remaining_tiles = []
        for tile in tiles:
            if self.player != 1:
                tile.size = small_tile_size
                tile.image = pygame.transform.smoothscale(tile.original_image, (tile.size, tile.size))
            try:
                tile.snap(self.coords[len(self.tiles)])
                self.tiles.append(tile)
            except:
                remaining_tiles.append(tile)

        return remaining_tiles

    def generate_coords(self):
        if self.player == 1:
            tile_size = large_tile_size
        else:
            tile_size = small_tile_size
        tile_gap = tile_size/25
        left_anchor = self.pos[0]
        top_anchor = self.pos[1]
        if self.category != 0:  # normal tower
            length = int(self.category)
            left_coords = [left_anchor+tile_gap + (tile_size+tile_gap)*i for i in range(length)]
            top_coords = [top_anchor+tile_gap]*length
            self.coords = list(zip(left_coords, top_coords))[::-1]
            if length == 1:
                top_anchor += (tile_gap)
                height = tile_size*4/5
            elif length == 5:
                top_anchor += (tile_size*1/5+tile_gap)
                height = tile_size*4/5
            else:
                top_anchor += (tile_size*1/5+tile_gap)
                height = tile_size*3/5
            self.rectpos = (left_anchor, top_anchor,  (tile_size+tile_gap)*(length)+tile_gap,  height)
        else:  # minus tower
            if self.player == 1 or (self.player == 2 and number_of_players == 2):  #zig zag
                lc1 = left_anchor + tile_gap
                lc2 = left_anchor + tile_gap*5 + tile_size
                left_coords = [lc1, lc2, lc1, lc2, lc1, lc2, lc1]
                top_coords = [top_anchor + tile_gap + (tile_size+tile_gap*4)/2*i for i in range(7)]
                self.coords = list(zip(left_coords, top_coords))
                self.rectpos = (left_anchor, top_anchor, tile_size*2+tile_gap*6, tile_size*4+tile_gap*14)
            else:  # straight minus
                length = 7
                left_coords = [left_anchor+tile_gap*3 + (tile_size+tile_gap*4)*i for i in range(length)]
                top_coords = [top_anchor+tile_gap*3]*length
                self.coords = list(zip(left_coords, top_coords))[::-1]
                left_anchor += tile_gap
                top_anchor += (tile_size*1/5+tile_gap)
                height = tile_size*4/5
                self.rectpos = (left_anchor, top_anchor,  (tile_size+tile_gap*4)*(length),  height)

    def next_coords(self, new_tiles, existing_tiles):
        return self.coords[existing_tiles : existing_tiles+new_tiles]

    def generate_tiles(self):
        size = (large_tile_size, large_tile_size)
        if self.tiles != []:
            self.tiles = [Tile(self.tiles[i].original_image, self.next_coords(1,i)[0], size) for i in range(len(self.tiles))]

    def draw(self, screen):
        pygame.draw.rect(screen, "blue", self.rect)


def generate_x_agon(x, screen_height):
    radius = screen_height*0.36
    cx, cy = screen_height/2, screen_height/2
    angle_step = 2 * math.pi / x  # Angle between vertices
    vertices = []

    for i in range(x):
        angle = i * angle_step - math.pi/2
        px = cx + radius * math.cos(angle)
        py = cy + radius * math.sin(angle)
        vertices.append((px, py))
    
    return vertices


def DraggedTiles(mouse_pos):
    for factory in factories + [pot]:
        for tile in factory.tiles:
            if tile.is_clicked(mouse_pos):
                return [t for t in factory.tiles if (t.original_image == tile.original_image and tile.original_image != one_tile)]

def ArrangeGameboards(number_of_players):
    if number_of_players == 4:
        start_game_board_gap = screen_height * 1/20
        game_board_gap = screen_height * 9/20
        game_board_top = screen_height * 0.625
    elif number_of_players == 3:
        start_game_board_gap = screen_height * 1/8
        game_board_gap = screen_height * 12/20
        game_board_top = screen_height * 0.6
    else:  # number of players = 2
        start_game_board_gap = screen_height * 6/20
        game_board_gap = screen_height * 15/20  #redundant
        game_board_top = screen_height * 0.6
    p1_game_board = GameBoard(1, screen_width-screen_height/20, screen_height/20)
    p2_game_board = GameBoard(2, screen_width-start_game_board_gap, game_board_top)
    p3_game_board = GameBoard(3, screen_width-start_game_board_gap-game_board_gap, game_board_top)
    p4_game_board = GameBoard(4, screen_width-start_game_board_gap-game_board_gap*2, game_board_top)
    game_boards = [p1_game_board, p2_game_board, p3_game_board, p4_game_board]
    return game_boards

def draw():
    screen.fill("white")
    for i in range(number_of_players):
        game_boards[i].draw(screen)
    for factory in factories:
        factory.draw(screen)
    pot.draw(screen)

def move(tiles_to_move, target_coords, target_size=None):
    if target_size == None:
        target_size = [large_tile_size]*len(tiles_to_move)
    component_dists = []
    for i, tile in enumerate(tiles_to_move):
        component_dists.append([tile.position[0]-target_coords[i][0], tile.position[1]-target_coords[i][1]])
    distances = [math.sqrt(dist[0]**2 + dist[1]**2) for dist in component_dists]
    original_dists = distances
    speed = [dist**(1/3) for dist in distances]

    while any(distances[i] > target_size[i]/2 for i in range(len(distances))):
        for i, tile in enumerate(tiles_to_move):
            if distances[i] >= target_size[i]/2:
                x_pos = tile.position[0]
                y_pos = tile.position[1]
                x_pos -= component_dists[i][0] * speed[i]/distances[i] * 3
                y_pos -= component_dists[i][1] * speed[i]/distances[i] * 3
                tile.position = (x_pos, y_pos)
                tile.size = target_size[i] + (distances[i]/original_dists[i])*(large_tile_size-target_size[i])
                tile.image = pygame.transform.smoothscale(tile.original_image, (tile.size, tile.size))      
                tile.rect = tile.image.get_rect(topleft=tile.position)

                component_dists = []
                for i, tile in enumerate(tiles_to_move):
                    component_dists.append([tile.position[0]-target_coords[i][0], tile.position[1]-target_coords[i][1]])
                distances = [math.sqrt(dist[0]**2 + dist[1]**2) for dist in component_dists]
            else:
                tile.size = target_size[i]
                tile.position = target_coords[i]
                tile.image = pygame.transform.smoothscale(tile.original_image, (tile.size, tile.size))      
                tile.rect = tile.image.get_rect(topleft=tile.position)
        
        draw()
        pygame.display.update()
        pygame.time.delay(10)
    
    for i, tile in enumerate(tiles_to_move):
        tile.size = target_size
        tile.position = target_coords[i]
        tile.rect = tile.image.get_rect(topleft=tile.position)
    draw()
    pygame.display.update()


def Setup(number_of_players):
    game_boards = ArrangeGameboards(number_of_players)
    factory_points = generate_x_agon(2*number_of_players + 1, screen_height)
    factories = [Factory(x,y) for (x,y) in factory_points]
    pot = Pot(screen_height)
    return game_boards, factories, pot


# Game state
new_round = True
input_active = True
user_input = ""
selected_tile = None
dragging = False
dragging_tiles = []
offsets = []

# Game loop
running = True
while running:
    # Cap the frame rate
    pygame.time.Clock().tick(60)
        
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False          

        if input_active:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:  # Pressing Enter finishes input
                    print("Final Input:", user_input)
                    input_active = False  # Close the pop-up or handle the input
                elif event.key == pygame.K_BACKSPACE:  # Handle backspace
                    user_input = user_input[:-1]
                else:  # Add typed character to the input
                    user_input += event.unicode
            
        if event.type == VIDEORESIZE:
            screen_height = event.h
            screen_width = min(max_screen_ratio, max(min_screen_ratio, (event.w / event.h))) * event.h
            if (screen_width, screen_height) != event.size:
                screen = pygame.display.set_mode((screen_width, screen_height), RESIZABLE)
                large_tile_size = screen_height/12
                small_tile_size = large_tile_size * tile_size_multiplier
                factory_points = generate_x_agon(2*number_of_players+1, screen_height)
                for i, factory in enumerate(factories):
                    factories[i] = Factory(factory_points[i][0], factory_points[i][1], factory.tiles, factory.removed_tiles)
                pot = Pot(screen_height, pot.tiles, pot.removed_tiles)
                game_boards = ArrangeGameboards(number_of_players)
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            tiles_to_move = []
            for factory in factories + [pot]:
                for tile in factory.tiles:
                    if tile.rect.collidepoint(event.pos):
                        selected_tile = tile
                        dragging = True
                        placed = False
                        dragging_tiles = DraggedTiles(event.pos)
                        current_factory = factory
                        positions_in_factory = [tile.position for tile in dragging_tiles]
                        if dragging_tiles:
                            offsets = [(large_tile_size/2 + large_tile_size*26/25*i, large_tile_size/2) for i in range(len(dragging_tiles))]

        if event.type == pygame.MOUSEBUTTONUP:
            if dragging and selected_tile:
                for game_board in game_boards:
                    for tower in game_board.towers:
                        if tower.rect.collidepoint(event.pos):  # Place tile in the player board area
                            current_tower = tower
                            current_game_board = game_board
                            if current_tower.category != 0:
                                if (current_tower.tiles == []) or (current_tower.tiles != [] and current_tower.tiles[0].original_image == dragging_tiles[0].original_image):
                                    remaining_tiles = tower.add_tiles(dragging_tiles)
                                    for tile in dragging_tiles:
                                        current_factory.tiles.remove(tile)
                                    placed = True
                            else:  # minus tower
                                remaining_tiles = tower.add_tiles(dragging_tiles)
                                for tile in dragging_tiles:
                                    current_factory.tiles.remove(tile)
                                placed = True

                if placed == False:
                    for i, tile in enumerate(dragging_tiles):
                        tile.size = large_tile_size
                        tile.image = pygame.transform.smoothscale(tile.original_image, (tile.size, tile.size))
                        tile.snap(positions_in_factory[i])
                else:
                    if isinstance(current_factory, Pot):
                        number_in_pot = 0
                        tiles_to_move = pot.tiles
                    else:
                        number_in_pot = len(pot.tiles)
                        pot.tiles += current_factory.tiles
                        tiles_to_move = current_factory.tiles
                        current_factory.tiles = []
                    next_coords = pot.next_coords(len(tiles_to_move), number_in_pot)
                    target_sizes = [large_tile_size]*len(tiles_to_move)

                    tiles_to_move += remaining_tiles
                    next_coords += game_boards[current_tower.player-1].towers[-1].next_coords(len(remaining_tiles), len(game_boards[current_tower.player-1].towers[-1].tiles))
                    if current_game_board.player == 1:
                        target_sizes += [large_tile_size]*len(remaining_tiles)
                    else:
                        target_sizes += [small_tile_size]*len(remaining_tiles)
                    game_boards[current_tower.player-1].towers[-1].tiles += remaining_tiles

                    if one_tile in [tile.original_image for tile in pot.tiles] and isinstance(current_factory, Pot):
                        one = tiles_to_move[0]
                        tiles_to_move = tiles_to_move[1:] + [one]
                        next_coords[-1] = game_boards[current_tower.player-1].towers[-1].next_coords(1, len(game_boards[current_tower.player-1].towers[-1].tiles))[0]
                        if current_game_board.player == 1:
                            target_sizes[-1] = large_tile_size
                        else:
                            target_sizes[-1] = small_tile_size
                        pot.tiles.remove(one)
                        pot.removed_tiles.append(one)
                        game_boards[current_tower.player-1].towers[-1].tiles.append(one)
                    else:
                        one = "placeholder"
                    if tiles_to_move:
                        move(tiles_to_move, next_coords, target_sizes)
                    
                dragging = False
                dragged_tiles = []
                offsets = []

            
        if event.type == pygame.MOUSEMOTION:
            if dragging and dragging_tiles:
                mouse_pos = pygame.mouse.get_pos()
                for i, tile in enumerate(dragging_tiles):
                    new_pos = (mouse_pos[0]-offsets[i][0], mouse_pos[1]-offsets[i][1])
                    tile.snap(new_pos)

                if any(pygame.Rect([game_board.left,game_board.top] + game_board.image.get_rect()[2:4]).collidepoint(event.pos) for game_board in game_boards[1:]): #if hovering over smaller gameboard
                    for tile in dragging_tiles:
                        tile.size = small_tile_size
                        tile.image = pygame.transform.smoothscale(tile.original_image, (tile.size, tile.size))      
                        offsets = [(small_tile_size/2 + small_tile_size*26/25*i, small_tile_size/2) for i in range(len(dragging_tiles))]
                else:    
                    for tile in dragging_tiles:
                        tile.size = large_tile_size
                        tile.image = pygame.transform.smoothscale(tile.original_image, (tile.size, tile.size))      
                        offsets = [(large_tile_size/2 + large_tile_size*26/25*i, large_tile_size/2) for i in range(len(dragging_tiles))]

    if new_round:
        input_active = True
        user_input = ""  # Reset the input when pop-up reopens
        game_boards, factories, pot = Setup(number_of_players)
        new_round=False

    # Draw everything
    draw()

    if input_active:
        popup_width, popup_height = 400, 200
        popup_x = (screen_width - popup_width) // 2
        popup_y = (screen_height - popup_height) // 2
        # Draw pop-up box
        pygame.draw.rect(screen, "grey", (popup_x, popup_y, popup_width, popup_height))  # Background
        pygame.draw.rect(screen, "black", (popup_x, popup_y, popup_width, popup_height), 3)  # Border
        # Render the message
        text_surface = font.render("Enter name", True, "black")
        text_rect = text_surface.get_rect(center=(popup_x + popup_width // 2, popup_y + 50))
        screen.blit(text_surface, text_rect)
        # Render the user's input text
        input_surface = font.render(user_input, True, "black")
        input_rect = input_surface.get_rect(center=(popup_x + popup_width // 2, popup_y + 120))
        screen.blit(input_surface, input_rect)

    # Update the display
    pygame.display.update()

    # Check if round is over
    if all(factory.tiles == [] for factory in factories+[pot]):
        pygame.time.delay(2000)
        new_round=True



# Quit Pygame
pygame.quit()


##### USER TEXT INPUT
message = "How many players?"
error_message = ""
user_input = ""

while input_active:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            input_active = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:  # Pressing Enter finishes input
                try:
                    if int(user_input) >= 2 and int(user_input) <= 4:
                        game_state.number_of_players = int(user_input)
                        input_active = False  # Close the pop-up or handle the input
                    else:
                        error_message = "Must be between 2 and 4"
                        user_input = ""
                        game_state.number_of_players = None
                except:
                    error_message = "Must be a number"
                    user_input = ""
                    game_state.number_of_players = None
                
            elif event.key == pygame.K_BACKSPACE:  # Handle backspace
                user_input = user_input[:-1]
            else:  # Add typed character to the input
                user_input += event.unicode
    if input_active:
        draw_popup(game_state, game_state.screen, message, error_message, user_input)
    pygame.display.update()