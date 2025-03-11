import pygame
from globals import Pot, move, get_dragged_tiles, able_to_be_placed, rotate_game_boards

def run_online_multiplayer(game_state, event, game_boards, factories, pot, online_multiplayer_buttons, game_info, end_of_turn_start):
    large_tile_height = game_state.large_tile_height
    small_tile_height = game_state.small_tile_height
    
    if event.type == pygame.FINGERDOWN:
        event.pos = (int(event.x * game_state.screen_width), int(event.y * game_state.screen_height))
        for button in online_multiplayer_buttons:
            if button.rect.collidepoint(event.pos):
                button.shown_image = button.clicked_image

        for factory in factories + [pot]:
            for tile in factory.tiles:
                if tile.rect.collidepoint(event.pos):
                    game_info["selected_tile"] = tile
                    game_info["dragged_tiles"] = get_dragged_tiles(factory, tile)
                    game_info["current_factory"] = factory
                    game_info["positions_in_factory"] = [tile.top_left for tile in game_info["dragged_tiles"]]
                    if game_info["dragged_tiles"]:
                        game_info["offsets"] = [(tile.height/2 + tile.height*26/25*i, tile.height/2) for i in range(len(game_info["dragged_tiles"]))]

    if event.type == pygame.FINGERUP:
        event.pos = (int(event.x * game_state.screen_width), int(event.y * game_state.screen_height))
        for button in online_multiplayer_buttons:
            if button.rect.collidepoint(event.pos):
                try:
                    button.action(game_state)
                except:
                    pass
            button.shown_image = button.image
        
        if game_info["dragged_tiles"] != []:
            placed = False
            game_board = [g for g in game_boards if g.player_pos==1][0]
            for tower in game_board.towers:
                if tower.rect.collidepoint(event.pos):  # tiles placed in towers
                    spaces_to_minus = 7 - len(game_board.towers[0].tiles)
                    if tower.category != 0:  # if not a minus tower
                        # add if empty or existing colour is dragged colour
                        if able_to_be_placed(tower, game_board, game_info["dragged_tiles"]):
                            tiles_to_tower, tower_new_coords, tower_new_heights, tiles_to_minus = tower.add_tiles(game_info["dragged_tiles"]) 
                            tiles_to_minus, minus_new_coords, minus_new_heights, tiles_remaining = game_board.towers[0].add_tiles(tiles_to_minus, game_info["current_factory"], pot, spaces_to_minus)
                            # Add tiles to relevant towers and remove from factory
                            for tile in tiles_to_tower:
                                game_info["current_factory"].tiles.remove(tile)
                            for tile in tiles_to_minus:
                                game_info["current_factory"].tiles.remove(tile)
                            for tile in tiles_remaining:
                                game_info["current_factory"].tiles.remove(tile)
                            placed=True
                    else:  # if a minus tower, add regardless of colour
                        tiles_to_minus, minus_new_coords, minus_new_heights, tiles_remaining = tower.add_tiles(game_info["dragged_tiles"], game_info["current_factory"], pot, spaces_to_minus)
                        tiles_to_tower = []
                        tower_new_coords = []
                        tower_new_heights = []
                        # Add tiles to relevant towers and remove from factory
                        for tile in tiles_to_minus:
                            game_info["current_factory"].tiles.remove(tile)
                        for tile in tiles_remaining:
                            game_info["current_factory"].tiles.remove(tile)
                        placed = True
                    current_game_board = game_board
                  

            if placed == False:  # if not placed in tower, snap back to factory
                for i, tile in enumerate(game_info["dragged_tiles"]):
                    tile.snap(large_tile_height, game_info["positions_in_factory"][i])
            
            else:  # if tiles were placed
                game_info["next_player"] = current_game_board.player+1
                if game_info["next_player"] > game_state.number_of_players:
                    game_info["next_player"] = 1
                if isinstance(game_info["current_factory"], Pot):  # if taking from the pot
                    number_in_pot = 0
                    tiles_to_pot = pot.tiles
                else:      # if taking normally
                    number_in_pot = len(pot.tiles)
                    tiles_to_pot = game_info["current_factory"].tiles
                    pot.tiles += game_info["current_factory"].tiles
                    game_info["current_factory"].tiles = []
                pot_new_coords = pot.next_coords(len(tiles_to_pot), number_in_pot)
                pot_new_heights = [large_tile_height]*len(tiles_to_pot)
                
                if "o" in [tile.colour for tile in pot.tiles] and isinstance(game_info["current_factory"], Pot):
                    one = tiles_to_pot[0]
                    tiles_to_pot = tiles_to_pot[1:]
                    pot_new_coords = pot_new_coords[:-1]
                    pot_new_heights = pot_new_heights[1:]
                    tiles_to_minus = [one] + tiles_to_minus
                    try:
                        minus_new_coords.append(current_game_board.towers[0].coords[len(current_game_board.towers[0].tiles)])
                    except:
                        minus_new_coords.append((0,0))
                    game_info["next_first_player"] = current_game_board.player
                    minus_new_heights.append(current_game_board.tile_height)
                    pot.tiles.remove(one)
                    current_game_board.towers[0].tiles.append(one)
                else:
                    one = "placeholder"
                #print("tower", [t.colour for t in tiles_to_tower])
                #print([(round(coord[0],2),round(coord[1],2)) for coord in tower_new_coords])
                #print([round(height,2) for height in tower_new_heights])
                #print("minus", [t.colour for t in tiles_to_minus])
                #print([(round(coord[0],2),round(coord[1],2)) for coord in minus_new_coords])
                #print([round(height,2) for height in minus_new_heights])
                #print("pot", [t.colour for t in tiles_to_pot])
                #print([(round(coord[0],2),round(coord[1],2)) for coord in pot_new_coords])
                #print([round(height,2) for height in pot_new_heights])
                tiles_to_move = tiles_to_tower + tiles_to_minus + tiles_to_pot
                new_coords = tower_new_coords + minus_new_coords + pot_new_coords
                new_heights = tower_new_heights + minus_new_heights + pot_new_heights
                game_info["dragged_tiles"] = []
                if tiles_to_move:
                    move(tiles_to_move, new_coords, new_heights, game_boards, factories, pot, online_multiplayer_buttons, game_info)

                if not all(factory.tiles == [] for factory in factories+[pot]):  # if not end of game
                    if not end_of_turn_start:
                        end_of_turn_start = pygame.time.get_ticks()

            game_info["dragged_tiles"] = []
            game_info["offsets"] = []

        
    if event.type == pygame.FINGERMOTION:
        event.pos = (int(event.x * game_state.screen_width), int(event.y * game_state.screen_height))
        if game_info["dragged_tiles"] != []:
            new_pos = [None]*len(game_info["dragged_tiles"])
            mouse_pos = pygame.mouse.get_pos()
            current_game_board = next((g for g in game_boards if g.player_pos == 1), None)
            if current_game_board.image.get_rect().collidepoint(event.pos): #if hovering over game_board
                for i, tile in enumerate(game_info["dragged_tiles"]):
                    tile.height = current_game_board.tile_height
                    game_info["offsets"][i] = (tile.height/2 + tile.height*26/25*i, tile.height/2)
                    new_top_left = (mouse_pos[0]-game_info["offsets"][i][0], mouse_pos[1]-game_info["offsets"][i][1])
                    tile.snap(tile.height, new_top_left)
            else:
                for i, tile in enumerate(game_info["dragged_tiles"]):
                    tile.height = game_state.large_tile_height
                    game_info["offsets"][i] = (tile.height/2 + tile.height*26/25*i, tile.height/2)
                    new_top_left = (mouse_pos[0]-game_info["offsets"][i][0], mouse_pos[1]-game_info["offsets"][i][1])
                    tile.snap(tile.height, new_top_left)

    return game_boards, factories, pot, online_multiplayer_buttons, game_info, end_of_turn_start


def online_multiplayer_round_over(game_state, round_over, states, game_boards, factories, pot, online_multiplayer_buttons, game_info, new_round):

    if round_over["current_state"] == states["wait"]:
        # Wait for 1 second before starting
        if round_over["current"] - round_over["start"] >= 1000:
            round_over["start"] = round_over["current"]
            round_over["current_state"] = states["score_tower"]

    elif round_over["current_state"] == states["score_tower"]:
        game_board = game_boards[round_over["current_player"]-1]  # Access the current player's game_board
        towers = game_board.towers
        if round_over["current_tower"] < len(towers): # if one of 5 towers
            tower = towers[round_over["current_tower"]]
            player = tower.player
            if len(tower.tiles) == tower.category:  # if the tower is full
                round_over["tile_score"], tiles_to_collect, collect_coords, collect_heights, tiles_to_move, new_coords, new_heights = game_boards[player-1].add_tiles(tower)
                move(tiles_to_collect, collect_coords, collect_heights, game_boards, factories, pot, online_multiplayer_buttons, game_info)
                for tile in tiles_to_collect:
                    tower.tiles.remove(tile)
                move(tiles_to_move, new_coords, new_heights, game_boards, factories, pot, online_multiplayer_buttons, game_info)
                tower.tiles.remove(tower.tiles[0])
                round_over["start"] = round_over["current"]
                round_over["current_state"] = states["show_tower_score"]
            else: 
                round_over["current_tower"] += 1  # Skip to the next tower if not full
        elif round_over["current"] - round_over["start"] >= 300:  # Done with towers, move to minus tower
            round_over["current_tower"] = 1
            round_over["current_state"] = states["score_minus"]


    elif round_over["current_state"] == states["show_tower_score"]:
        if not round_over["score_shown"]:
            game_boards[round_over["current_player"]-1].score += round_over["tile_score"]
            round_over["add_score"] = (round_over["current_player"], round_over["tile_score"])
            round_over["score_shown"] = True
            round_over["start"] = round_over["current"]
        elif round_over["current"] - round_over["start"] >= 300:  # Wait 0.5 seconds before hiding the score and moving to next tower
            round_over["add_score"] = None
            round_over["score_shown"] = False
            round_over["current_tower"] += 1
            round_over["start"] = round_over["current"]
            round_over["current_state"] = states["score_tower"]


    elif round_over["current_state"] == states["score_minus"]:
        round_over["add_score"] = None
        minus_tower = game_boards[round_over["current_player"]-1].towers[0]
        if round_over["current_minus_tile"] == 0:
            round_over["full_minus_tower"] = list(minus_tower.tiles)
        if round_over["current_minus_tile"] < len(round_over["full_minus_tower"]) and round_over["full_minus_tower"] != []:
            tile = round_over["full_minus_tower"][round_over["current_minus_tile"]]
            minus_scores = [-1,-1,-2,-2,-2,-3,-3]
            round_over["tile_score"] = minus_scores[round_over["full_minus_tower"].index(tile)]
            if round_over["current"] - round_over["start"] >= 150:  # gap after tile score disappears
                minus_tower.tiles.remove(tile)  # Remove the tile from the minus tower
                game_boards[round_over["current_player"]-1].score += round_over["tile_score"]
                if game_boards[round_over["current_player"]-1].score < 0:
                    game_boards[round_over["current_player"]-1].score = 0
                round_over["start"] = round_over["current"]
                round_over["current_state"] = states["show_minus_score"]

        elif round_over["current"] - round_over["start"] >= 300:  # Done with minus tower, move to the next player or reset
            try:
                round_over["current_player"] = next(round_over["player_poses"])
                rotate_game_boards(game_state, game_boards)
                round_over["current_tower"] = 1
                round_over["current_minus_tile"] = 0
                round_over["current_state"] = states["wait"]
                
            except:
                round_over["current_state"] = states["reset"]
                

    elif round_over["current_state"] == states["show_minus_score"]:
        if not round_over["score_shown"]:
            round_over["add_score"] = (round_over["current_player"], round_over["tile_score"])
            round_over["score_shown"] = True
            round_over["start"] = round_over["current"]

        elif round_over["current"] - round_over["start"] >= 300:  # Wait 0.3 seconds before hiding the score
            game_info["add_score"] = None
            round_over["current_minus_tile"] += 1
            round_over["start"] = round_over["current"]
            round_over["current_state"] = states["score_minus"]
            round_over["score_shown"] = False


    elif round_over["current_state"] == states["reset"]:
        if any([any([None not in row for row in game_board.tiles]) for game_board in game_boards]) and round_over["current"] - round_over["start"] >= 500:  # if game over
            rotate_game_boards(game_state, game_boards)
            round_over["done"] = True
            round_over["start"] = round_over["current"]
            round_over["current_state"] = -1

        if round_over["current"] - round_over["start"] >= 600:  # Wait 0.4 seconds before resetting
            round_over["start"] = round_over["current"]
            round_over["current_state"] = -1
            new_round["running"] = True
            new_round["game_created"] = False 

    return round_over, game_boards, factories, pot, online_multiplayer_buttons, game_info, new_round


def online_multiplayer_game_over(game_over, new_round, states, game_boards, game_state):

    if game_over["current_state"] == states["wait"]:
        if game_over["current"] - game_over["start"] >= 500:  # wait 0.5 seconds before starting
            game_over["start"] = game_over["current"]
            game_over["current_state"] = states["score_block"]

    elif game_over["current_state"] == states["score_block"]:
        game_board = game_boards[game_over["current_player"]-1]  # Access the current player's game_board
        rows = [row for row in game_board.tiles]
        cols = [[row[i] for row in game_board.tiles] for i in range(5)]
        diags = []
        for i in range(5):
            diag = []
            for j in range(5):
                if i+5-j > 4:
                    i -= 5
                diag.append(game_board.tiles[i+5-j][j])
            diags.append(diag)
        blocks = rows + cols + diags
        game_over["blocks"] = blocks
        categories = ["row"]*5 + ["col"]*5 + ["diag"]*5
        
        if game_over["current_block"] < len(blocks): # if one of possible scoring blocks
            block = blocks[game_over["current_block"]]
            category = categories[game_over["current_block"]]
            if None not in block:  # if the block is full
                if category == "row":
                    game_over["block_score"] = 2
                elif category == "col":
                    game_over["block_score"] = 7
                elif category == "diag":
                    game_over["block_score"] = 10

                game_over["start"] = game_over["current"]
                game_over["current_state"] = states["show_block_score"]
            else:
                game_over["current_block"] += 1  # Skip to the next block

        elif game_over["current"] - game_over["start"] >= 300:  # Done with blocks
            try:
                game_over["current_player"] = next(game_over["player_poses"])
                rotate_game_boards(game_state, game_boards)
                game_over["current_block"] = 0
                game_over["current_state"] = states["wait"]
                game_over["start"] = game_over["current"]
            except:
                game_over["current_state"] = states["reset"]


    elif game_over["current_state"] == states["show_block_score"]:
        if not game_over["score_shown"] and game_over["current"] - game_over["start"] >= 160:
            game_boards[game_over["current_player"]-1].score += game_over["block_score"]
            game_over["add_score"] = (game_over["current_player"], game_over["block_score"])
            game_over["score_shown"] = True
            game_over["start"] = game_over["current"]
            game_over["glow_tiles"] = game_over["blocks"][game_over["current_block"]]
        elif game_over["current"] - game_over["start"] >=700:  # Wait 0.7 seconds before hiding the score and moving to next block
            game_over["add_score"] = None
            game_over["glow_tiles"] = []
            game_over["score_shown"] = False
            game_over["current_block"] += 1
            game_over["start"] = game_over["current"]
            game_over["current_state"] = states["score_block"]
        elif game_over["current"] - game_over["start"] < 160 and len(game_over["glow_tiles"]) != 5:
            block = game_over["blocks"][game_over["current_block"]]
            number_of_tiles = (game_over["current"] - game_over["start"])//40 + 1
            game_over["glow_tiles"] = block[:number_of_tiles]
        else:
            game_over["glow_tiles"] = game_over["blocks"][game_over["current_block"]]
        

    elif game_over["current_state"] == states["reset"]:
        if game_over["current"] - game_over["start"] >= 600:  # Wait 0.6 seconds before showing results
            game_over["start"] = game_over["current"]
            game_over["current_state"] = -1
            game_over["show_results"] = True
            game_over["running"] = False
            new_round["running"] = False

    return game_over, new_round