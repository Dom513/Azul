import pygame
import math
import copy
from globals import *

###############################
### Monte Carlo Tree Search ###
###############################

class Node:
    def __init__(self, state, prev_player, parent=None, move=None):
        self.prev_player = prev_player
        self.next_player = (prev_player+1) % len(state["Gameboards"])
        self.state = state
        self.move = move
        self.parent = parent  # Parent node
        self.children = []  # Child nodes
        self.visits = 0  # Number of times the node has been visited
        self.wins = 0  # Number of wins for this node

    def is_fully_expanded(self):
        return len(self.children) == len(self.get_legal_moves())
    
    def get_legal_moves(self):
        legal_moves = []
        all_factories = self.state["Factories"]+[self.state["Pot"]]
        legal_factories = [factory for factory in self.state["Factories"]+[self.state["Pot"]] if (factory != [] and factory != ["o"])]
        for factory in legal_factories:
            factory_num = all_factories.index(factory)
            legal_colours = set(factory)
            for colour in legal_colours:
                if colour != 'o':
                    tiles = [ti for ti in factory if ti == colour]
                    for tower_cat, tower in enumerate(self.state["Towers"][self.next_player]):
                        legal_moves.append((factory_num, factory, tiles, tower_cat, tower))
        allowed_moves = []
        for (factory_num, factory, tiles, tower_cat, tower) in legal_moves:
            if (tower_cat != 0 and able_to_be_placed_col(tower, tower_cat, self.state["Gameboards"][self.next_player], tiles)) or tower_cat == 0:
                allowed_moves.append((factory_num, factory, tiles, tower_cat, tower))
        allowed_moves = sorted(allowed_moves, key=lambda x: len(x[2]), reverse=True) # put best options first
        # remove minus tower options if possible
        recommended_moves = [move for move in allowed_moves if move[3] != 0]
        if recommended_moves != []:
            great_moves = [move for move in recommended_moves if move[3]-len(move[4]) == len(move[2])]
            if great_moves != []:
                #print([print_move(move, self.next_player) for move in great_moves])
                return great_moves
            return recommended_moves
        return allowed_moves
    
    def make_move(self, move):
        factory_num, factory, tiles, tower_cat, tower = move
        pot_tiles = [t for t in factory if t not in tiles]
        state = copy.deepcopy(self.state)
        pot = state["Pot"]
        game_boards = state["Gameboards"]
        towers = state["Towers"]
        factories = state["Factories"]
        minus_tower = towers[self.next_player][0]
        if factory_num == len(factories) and "o" in pot:
            minus_tower.append("o")
            pot.remove('o')
        if tower_cat != 0:  # if not a minus tower
            for tile in tiles:
                if len(towers[self.next_player][tower_cat]) < tower_cat:
                    towers[self.next_player][tower_cat].append(tile)
                else:
                    if len(minus_tower) < 7:
                        minus_tower.append(tile)
                if factory_num == len(factories):
                    pot.remove(tile)
                else:
                    factories[factory_num].remove(tile)
        else:  # adding to minus tower
            for tile in tiles:
                if len(minus_tower) < 7:
                    minus_tower.append(tile)
                if factory_num == len(factories):
                    pot.remove(tile)
                else:
                    factories[factory_num].remove(tile)
        if factory_num != len(factories):
            for tile in pot_tiles:
                pot.append(tile)
                factories[factory_num].remove(tile)

        state = get_state(game_boards, towers, factories, pot)
        return state      

    def get_reward(self):
        grid_colours = ["p", "g", "r", "y", "b", "p", "g", "r", "y", "b"]
        coord_cols = [[grid_colours[i+j] for i in range(5)] for j in range(5)]
        coord_cols = [[coord_cols[row][col] for row in range(5)] for col in range(5)]
        game_boards = self.state["Gameboards"]
        total_new_score = [0]*len(game_boards)
        for i,game_board in enumerate(game_boards):
            test_game_board = copy.deepcopy(game_board)
            # tile scores
            for tower_cat, tower in enumerate(self.state["Towers"][i][1:]):
                if tower_cat+1 == len(tower):
                    row = tower_cat
                    col = coord_cols[row].index(tower[0])
                    test_game_board[row][col] = tower[0]
                    score = calculate_tile_score(test_game_board, (row,col))
                    tower_score = (tower_cat)
                    total_new_score[i] += (score + tower_score)
            # end scores
            for row in game_board:
                if all([t != "-" for t in row]):
                    total_new_score[i] += 2
                    if total_new_score[i] == max(total_new_score):
                        total_new_score[i] += 5  # incentive to end game if ahead
            for col in [[row[i] for row in game_board] for i in range(5)]:
                if all(t != "-" for t in col):
                    total_new_score[i] += 7
            for colour in ["r", "g", "b", "y", "p"]:
                if all([colour in row for row in game_board]):
                    total_new_score[i] += 10
                
            # minus score
            if len(self.state["Towers"][i][0]) >= 1:
                minus_scores = [-1,-2,-4,-6,-8,-11,-14]
                score = minus_scores[len(self.state["Towers"][i][0])-1]
                total_new_score[i] += score
        return total_new_score


class MCTS:
    def __init__(self, iterations=1000):
        self.iterations = iterations

    def search(self, root, single_player_buttons, game_state, player):
        max_reward = 0
        for i in range(self.iterations):
            #exit
            button_pressed=False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_state.single_player_running = False

                if event.type == VIDEORESIZE:
                    return event

                if event.type == pygame.FINGERDOWN:
                    event.pos = (int(event.x * game_state.screen_width), int(event.y * game_state.screen_height))
                    for button in single_player_buttons:
                        if button.rect.collidepoint(event.pos):
                            button.shown_image = button.clicked_image
                if event.type == pygame.FINGERUP:
                    event.pos = (int(event.x * game_state.screen_width), int(event.y * game_state.screen_height))
                    for button in single_player_buttons:
                        if button.rect.collidepoint(event.pos):
                            try:
                                button.action(game_state)
                                button_pressed = True
                            except:
                                pass
                        button.shown_image = button.image
            if button_pressed:
                break
            node = self._select(root)
            if not is_terminal(node.state):
                node, move = self._expand(node)
                reward = self._simulate(node, player)
                if reward > max_reward:
                    max_reward = reward
                    #print(f"----------- Move {i+1} of {self.iterations}")
                    #print(print_move(move, node.prev_player))
                    #print("player", player, "reward", reward)
                self._backpropagate(node, reward)
                #print("reward", node.wins)
                #print("best move", print_move(self._get_best_move(root).move, self._get_best_move(root).prev_player))
        return self._get_best_move(root).move

    def _select(self, node):
        # Select the best child node based on UCT
        while node.children and node.is_fully_expanded():
            node = self._uct_select(node)
        return node

    def _expand(self, node):
        test_node = Node(copy.deepcopy(node.state), node.prev_player)
        # Expand by adding a new child node for an unexplored move
        untried_moves = [move for move in test_node.get_legal_moves() if move not in [child.move for child in node.children]]
        #move = random.choice(untried_moves)  # Choose a random unexplored move
        try:
            move = untried_moves[0]
        except:
            move = test_node.get_legal_moves()[0]
        new_state = node.make_move(move)
        child_node = Node(new_state, node.next_player, parent=node, move=move)
        node.children.append(child_node)
        return child_node, move

    def _simulate(self, node, player):
        test_node = Node(copy.deepcopy(node.state), node.prev_player)
        #Perform a random simulation from this node
        current_node = test_node
        certain_rewards = current_node.get_reward()
        while not is_terminal(current_node.state):
            legal_moves = current_node.get_legal_moves()
            move = legal_moves[0]
            current_node = Node(current_node.make_move(move), current_node.next_player)
        current_game_boards = current_node.state["Gameboards"]
        potential_rewards = current_node.get_reward()
        if game_state.difficulty == "easy":
            rewards = [certain_rewards[i] for i in range(len(certain_rewards))]
        else:
            rewards = [certain_rewards[i] + potential_rewards[i] for i in range(len(certain_rewards))]
        #print("rewards", rewards)
        #print("player", player, "reward", rewards[player] - (sum(rewards[i] for i in range(len(rewards)) if i != player))/(len(current_game_boards)-1))
        if game_state.difficulty == "easy":
            return rewards[player]
        else:
            return rewards[player] - (sum(rewards[i] for i in range(len(rewards)) if i != player and rewards[i]>rewards[player]*0.9))/(len(current_game_boards)-1)

    def _backpropagate(self, node, reward):
        # Update stats for all nodes on the path back to the root
        while node is not None:
            node.visits += 1
            node.wins += reward
            node = node.parent

    def _uct_select(self, node):
        # Use UCT formula to select the best child
        def uct_value(child):
            if child.visits == 0:
                return float("inf")  # Encourage exploration
            return (child.wins / child.visits) + 2*math.sqrt(2 * math.log(node.visits) / child.visits)

        if not node.children:
            raise ValueError("No children found for UCT selection.")
        return max(node.children, key=uct_value)
    
    def _get_best_move(self, node):
        if not node.children:
            raise ValueError("No children to select the best move from.")
        return max(node.children, key=lambda child: child.visits)

def get_state(game_boards, towers, factories, pot):
    state = {"Gameboards": game_boards,
            "Towers": towers,
            "Factories": factories,
            "Pot": pot}
    return state

def is_terminal(state):
    return all(factory == [] for factory in state["Factories"]+[state["Pot"]])

def able_to_be_placed_col(tower, tower_cat, game_board, dragged_tiles):
    if tower==[]:
        if not dragged_tiles[0] in game_board[tower_cat-1]:
            return True
    elif len(tower) != tower_cat:
        if tower[0]==dragged_tiles[0]:
            return True
    return False
    
def print_move(move, player):
    if move:
        factory_num, factory, tiles, tower_cat, tower = move
        try:
            factory = f"Factory {factory_num}"
        except:
            factory = "Pot"
        return "Take tiles", tiles, "from", factory, "into tower", tower_cat, "of gameboard", player
    
#def print_state(state, player):
    #print("Factories")
    #print([factory for factory in state["Factories"]+[state["Pot"]]])
    #print("Player =", player)
    #for i in range(len(state["Gameboards"])):
        #print(f"Player {i} Towers")
        #print(state["Towers"][player])
        #print(f"Player {i} Gameboard")
        #print(state["Gameboards"][player])


def make_computer_move(next_player, game_boards, factories, pot, game_state, game_info, single_player_buttons, current, start, player_moved, i, single_player_screen):
    move_found = False
    while not move_found:
        copy_game_boards = [[[t.colour if t else "-" for t in row] for row in game_board.tiles] for game_board in game_boards]
        copy_towers = [[[t.colour for t in tower.tiles] for tower in game_board.towers] for game_board in game_boards]
        copy_factories = [[t.colour for t in factory.tiles] for factory in factories]
        copy_pot = [t.colour for t in pot.tiles]
        start_state = get_state(copy_game_boards, copy_towers, copy_factories, copy_pot)
        root = Node(start_state, next_player-1)
        mcts = MCTS(iterations=300 + 33*len(game_boards))
        best_move = mcts.search(root, single_player_buttons, game_state, next_player)
        try:  # if resized
            event = best_move
            resize(event)
            single_player_screen = pygame.Surface((game_state.screen_width, game_state.screen_height), pygame.SRCALPHA)
            get_background()
            game_boards, factories, pot, game_info = create_game(game_state, game_boards, factories, pot, game_info)
            single_player_buttons = [create_number_of_players(game_state)[0]]
            game_state.screen.blit(game_state.background, (0,0))
            draw_game(single_player_screen, game_boards, factories, pot, single_player_buttons, game_info, None, None)
            game_state.screen.blit(single_player_screen, (0,0))
            pygame.display.update()
        except:
            factory_num, factory, tiles, tower_cat, tower = best_move
            try:
                ##print("Factory", factories.index(factory))
                actual_factory = factories[factory_num]
            except:
                ##print("Pot")
                actual_factory = pot
            ##print("Take tiles", [t.colour for t in tiles])
            ##print("Into gameboard", game_board.player)
            ##print("In tower of length", tower.category)
            actual_tiles = [t for t in actual_factory.tiles if t.colour == tiles[0]]
            actual_game_board = game_boards[next_player]
            actual_tower = actual_game_board.towers[tower_cat]
            move_found = True
    current = pygame.time.get_ticks()
    if current-start > 1000:
        tiles_to_move, new_coords, new_heights = make_actual_move(game_state, game_info, actual_factory, actual_tiles, actual_game_board, actual_tower, pot)
        move(tiles_to_move, new_coords, new_heights, game_boards, factories, pot, single_player_buttons, game_info)
        start = pygame.time.get_ticks()
        player_moved[i] = True
    return player_moved, start, game_boards, factories, pot, single_player_buttons, game_info, single_player_screen

def make_actual_move(game_state, game_info, factory, tiles, game_board, tower, pot):
    spaces_to_minus = 7 - len(game_board.towers[0].tiles)
    if tower.category != 0:  # if not a minus tower
        tiles_to_tower, tower_new_coords, tower_new_heights, tiles_to_minus = tower.add_tiles(tiles) 
        tiles_to_minus, minus_new_coords, minus_new_heights, tiles_remaining = game_board.towers[0].add_tiles(tiles_to_minus, factory, pot, spaces_to_minus)
        # Add tiles to relevant towers and remove from factory
        for tile in tiles_to_tower:
            factory.tiles.remove(tile)
        for tile in tiles_to_minus:
            factory.tiles.remove(tile)
        for tile in tiles_remaining:
            factory.tiles.remove(tile)
    else:  # if a minus tower, add regardless of colour
        tiles_to_minus, minus_new_coords, minus_new_heights, tiles_remaining = tower.add_tiles(tiles, factory, pot, spaces_to_minus)
        tiles_to_tower = []
        tower_new_coords = []
        tower_new_heights = []
        # Add tiles to relevant towers and remove from factory
        for tile in tiles_to_minus:
            factory.tiles.remove(tile)
        for tile in tiles_remaining:
            factory.tiles.remove(tile)

    #game_info["next_player"] = current_game_board.player+1
    #if game_info["next_player"] > game_state.number_of_players:
    #    game_info["next_player"] = 1
    if isinstance(factory, Pot):  # if taking from the pot
        number_in_pot = 0
        tiles_to_pot = pot.tiles
    else:      # if taking normally
        number_in_pot = len(pot.tiles)
        tiles_to_pot = factory.tiles
        pot.tiles += factory.tiles
        factory.tiles = []
    pot_new_coords = pot.next_coords(len(tiles_to_pot), number_in_pot)
    pot_new_heights = [game_state.large_tile_height]*len(tiles_to_pot)
    
    if "o" in [tile.colour for tile in pot.tiles] and isinstance(factory, Pot):
        one = tiles_to_pot[0]
        tiles_to_pot = tiles_to_pot[1:]
        pot_new_coords = pot_new_coords[:-1]
        pot_new_heights = pot_new_heights[1:]
        tiles_to_minus = [one] + tiles_to_minus
        try:
            minus_new_coords.append(game_board.towers[0].coords[len(game_board.towers[0].tiles)])
        except:
            minus_new_coords.append((0,0))
        game_info["next_first_player"] = game_board.player
        minus_new_heights.append(game_board.tile_height)
        pot.tiles.remove(one)
        game_board.towers[0].tiles.append(one)
    else:
        one = "placeholder"
    
    tiles_to_move = tiles_to_tower + tiles_to_minus + tiles_to_pot
    new_coords = tower_new_coords + minus_new_coords + pot_new_coords
    new_heights = tower_new_heights + minus_new_heights + pot_new_heights
    tiles = []
    game_info["offsets"] = []
    return tiles_to_move, new_coords, new_heights


#######################
#### Single Player ####
#######################

def run_single_player(game_state, event, game_boards, factories, pot, single_player_buttons, game_info):
    large_tile_height = game_state.large_tile_height
    small_tile_height = game_state.small_tile_height
    
    if event.type == pygame.FINGERDOWN:
        event.pos = (int(event.x * game_state.screen_width), int(event.y * game_state.screen_height))
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
                ##print("tower", [t.colour for t in tiles_to_tower])
                ##print([(round(coord[0],2),round(coord[1],2)) for coord in tower_new_coords])
                ##print([round(height,2) for height in tower_new_heights])
                ##print("minus", [t.colour for t in tiles_to_minus])
                ##print([(round(coord[0],2),round(coord[1],2)) for coord in minus_new_coords])
                ##print([round(height,2) for height in minus_new_heights])
                ##print("pot", [t.colour for t in tiles_to_pot])
                ##print([(round(coord[0],2),round(coord[1],2)) for coord in pot_new_coords])
                ##print([round(height,2) for height in pot_new_heights])
                tiles_to_move = tiles_to_tower + tiles_to_minus + tiles_to_pot
                new_coords = tower_new_coords + minus_new_coords + pot_new_coords
                new_heights = tower_new_heights + minus_new_heights + pot_new_heights
                game_info["dragged_tiles"] = []
                if tiles_to_move:
                    move(tiles_to_move, new_coords, new_heights, game_boards, factories, pot, single_player_buttons, game_info)

                game_info["placed"] = True
            game_info["dragged_tiles"] = []
            game_info["offsets"] = []
            
        
    if event.type == pygame.FINGERMOTION:
        event.pos = (int(event.x * game_state.screen_width), int(event.y * game_state.screen_height))
        if game_info["dragged_tiles"] != []:
            mouse_pos = event.pos
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

    return game_boards, factories, pot, single_player_buttons, game_info


def single_player_round_over(game_state, round_over, states, game_boards, factories, pot, single_player_buttons, game_info, new_round):

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
                move(tiles_to_collect, collect_coords, collect_heights, game_boards, factories, pot, single_player_buttons, game_info)
                for tile in tiles_to_collect:
                    tower.tiles.remove(tile)
                move(tiles_to_move, new_coords, new_heights, game_boards, factories, pot, single_player_buttons, game_info)
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
            round_over["done"] = True
            round_over["start"] = round_over["current"]
            round_over["current_state"] = -1

        if round_over["current"] - round_over["start"] >= 600:  # Wait 0.4 seconds before resetting
            round_over["start"] = round_over["current"]
            round_over["current_state"] = -1
            new_round["running"] = True
            new_round["game_created"] = False 

    return round_over, game_boards, factories, pot, single_player_buttons, game_info, new_round


def single_player_game_over(game_over, new_round, states, game_boards, game_state):

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