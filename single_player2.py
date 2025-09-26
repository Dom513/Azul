import copy, math, random
from globals2 import *

def make_nice_state(game_boards, factories, pot):
    """Convert the object-oriented game state into a simple dict for MCTS."""
    state = {"Gameboards": [], "Towers": [], "Factories": [], "Pot": []}

    state["Factories"] = [[t.colour for t in factory.tiles] for factory in factories]
    state["Pot"] = [t.colour for t in pot.tiles]

    for board in game_boards:
        # Flatten game board into 5x5 grid of letters
        nice_board = [next((tile.colour for tile in board.tiles if tile.pos == coord), "-")
                      for coord in board.tile_coords]
        state["Gameboards"].append([nice_board[i*5:i*5+5] for i in range(5)])
        # Towers as lists of letters
        state["Towers"].append([[tile.colour for tile in tower.tiles] for tower in board.towers])

    return state


def get_state(game_boards, towers, factories, pot):
    """Return a simple dict-state (used by Node.make_move)."""
    return {
        "Gameboards": game_boards,
        "Towers": towers,
        "Factories": factories,
        "Pot": pot,
    }


def is_terminal(state):
    """Terminal when all factories and the pot are empty."""
    return all(factory == [] for factory in state["Factories"] + [state["Pot"]])


def able_to_be_placed_col(tower, tower_cat, game_board, dragged_tiles):
    """Rules whether dragged_tiles (list of same-colour letters) can go into tower (tower_cat)."""
    # tower_cat is index in towers array (0 == minus). For placement validity, ignore minus.
    if tower_cat == 0:
        return True
    # If tower empty, cannot place if that colour already on corresponding wall row
    if tower == []:
        return dragged_tiles[0] not in game_board[tower_cat - 1]
    # If tower partially filled, must be same colour and not full
    if len(tower) < tower_cat and tower[0] == dragged_tiles[0]:
        return True
    return False


def calculate_tile_score(after, coord):
    """Score contribution for placing a tile at pos=(row,col)."""
    row, col = coord
    score = 1

    # count horizontal (left)
    left = col - 1
    while left >= 0 and after[row][left] != "-":
        score += 1
        left -= 1
    # right
    right = col + 1
    while right < 5 and after[row][right] != "-":
        score += 1
        right += 1

    # vertical
    up = row - 1
    vertical = 0
    while up >= 0 and after[up][col] != "-":
        vertical += 1
        up -= 1
    down = row + 1
    while down < 5 and after[down][col] != "-":
        vertical += 1
        down += 1

    if vertical > 0:
        score += vertical
    return score


class Node:
    """
    state: dict with keys "Factories","Pot","Towers","Gameboards"
    prev_player: index (0-based) of player who moved to produce this state
    next_player: (prev_player + 1) % n  (player to move in this state)
    """
    def __init__(self, state, prev_player, parent=None, move=None):
        self.state = state
        self.prev_player = prev_player
        # next_player is the player who should move in this node's state
        self.next_player = (prev_player + 1) % len(state["Gameboards"])
        self.parent = parent
        self.move = move  # the move that produced this node (from parent)
        self.children = []
        self.visits = 0
        self.wins = 0.0

    def is_fully_expanded(self):
        return len(self.children) == len(self.get_legal_moves())

    def terminal(self):
        return is_terminal(self.state)

    def get_legal_moves(self):
        """
        Return list of moves in canonical form:
          (factory_idx, factory_list, tiles_list, tower_cat, tower_list)
        factory_idx: 0..len(factories)-1, pot index == len(factories)
        tower_cat: 0..n (0 is minus tower)
        """
        legal_moves = []
        all_factories = self.state["Factories"] + [self.state["Pot"]]
        # legal factories: exclude empty lists and single 'one' marker if any
        legal_factories = [f for f in all_factories if f and f != ["one"]]

        for factory in legal_factories:
            factory_idx = all_factories.index(factory)
            for colour in set(factory):
                if colour == "one":
                    continue
                tiles = [t for t in factory if t == colour]
                # iterate towers for the player to move (next_player), towers indexed 0..5 (0 is minus)
                for tower_cat, tower in enumerate(self.state["Towers"][self.next_player]):
                    if able_to_be_placed_col(tower, tower_cat, self.state["Gameboards"][self.next_player], tiles):
                        legal_moves.append((factory_idx, factory, tiles, tower_cat, tower))

        # prioritize by tile count (desc); prefer moves that fill a pattern line exactly
        allowed = sorted(legal_moves, key=lambda x: len(x[2]), reverse=True)
        recommended = [m for m in allowed if m[3] != 0]  # prefer non-minus
        if recommended:
            # prefer moves that exactly fill the tower space (tower_cat - existing_len == len(tiles))
            great = [m for m in recommended if (m[3] - len(m[4])) == len(m[2])]
            return great or recommended
        return allowed

    def make_move(self, move):
        """
        Apply move to a deep-copied state and return new state dict (not Node).
        Move uses lists from this Node.state (they are lists of letters).
        """
        factory_idx, factory, tiles, tower_cat, tower = move

        # copy the logical state
        state = copy.deepcopy(self.state)
        factories = state["Factories"]
        pot = state["Pot"]
        towers = state["Towers"]
        game_boards = state["Gameboards"]

        # the player who is placing is next_player (player to move in this state)
        player = self.next_player
        minus_tower = towers[player][0]

        # handle 'one' token when taking from pot
        if factory_idx == len(factories) and "one" in pot:
            # 'one' goes to minus tower
            if len(minus_tower) < 7:
                minus_tower.append("one")
            if "one" in pot:
                pot.remove("one")

        # take tiles from source (pot or factory)
        source = pot if factory_idx == len(factories) else factories[factory_idx]
        taken = []
        for _ in range(len(tiles)):
            # remove colour occurrences from source
            if tiles[0] in source:
                source.remove(tiles[0])
                taken.append(tiles[0])

        # if taken from a factory, move leftovers into pot and clear factory
        if factory_idx != len(factories):
            leftovers = list(factories[factory_idx])  # remaining after removals
            for t in leftovers:
                pot.append(t)
            factories[factory_idx] = []

        # place tiles in tower or minus tower (overflow to minus)
        if tower_cat == 0:
            for t in taken:
                if len(minus_tower) < 7:
                    minus_tower.append(t)
        else:
            for t in taken:
                if len(towers[player][tower_cat]) < tower_cat:
                    towers[player][tower_cat].append(t)
                else:
                    if len(minus_tower) < 7:
                        minus_tower.append(t)

        return get_state(game_boards, towers, factories, pot)

    def get_reward(self):
        """
        Return list of scores (one per player) for this state's heuristic.
        Uses tile/tower scoring, row/col/colour bonuses, minus penalties.
        """
        grid_colours = ["purple", "green", "red", "yellow", "blue",
                        "purple", "green", "red", "yellow", "blue"]
        coord_cols = [[grid_colours[i + j] for i in range(5)] for j in range(5)]
        coord_cols = [[coord_cols[r][c] for r in range(5)] for c in range(5)]

        scores = [0] * len(self.state["Gameboards"])
        for i, game_board in enumerate(self.state["Gameboards"]):
            test_board = copy.deepcopy(game_board)

            # tile/tower scoring
            for t_idx, tower in enumerate(self.state["Towers"][i][1:], start=1):
                if t_idx == len(tower):
                    row = t_idx - 1
                    # find column where that colour sits in the wall pattern
                    col = coord_cols[row].index(tower[0])
                    test_board[row][col] = tower[0]
                    scores[i] += calculate_tile_score(test_board, (row, col)) + (t_idx - 1)
                else:
                    scores[i] -= t_idx/3

            # row bonuses
            for row in game_board:
                if all(t != "-" for t in row):
                    scores[i] += 2
                    # incentive to be ahead if you've finished a row (small)
                    if scores[i] == max(scores):
                        scores[i] += 5

            # column bonuses
            for col in zip(*game_board):
                if all(t != "-" for t in col):
                    scores[i] += 7

            # colour bonuses
            for colour in ["red", "green", "blue", "yellow", "purple"]:
                if all(colour in row for row in game_board):
                    scores[i] += 10

            # minus tower penalties
            minus_len = len(self.state["Towers"][i][0])
            if minus_len > 0:
                penalties = [-1, -2, -4, -6, -8, -11, -14]
                idx = min(minus_len - 1, len(penalties) - 1)
                scores[i] += penalties[idx]

        return scores


class MCTS:
    def __init__(self, iterations=1000, c_param=1.4):
        self.iterations = iterations
        self.c = c_param

    def search(self, root, player):
        """
        root: Node already constructed
        player: UI player index (1-based) of the CPU (so convert when indexing)
        """
        for _ in range(self.iterations):
            node = self._select(root)
            if not node.terminal():
                node, _ = self._expand(node)
            reward = self._simulate(node, player)
            self._backpropagate(node, reward)

        return self._get_best_move(root).move

    def _uct(self, parent, child):
        if child.visits == 0:
            return float("inf")
        return (child.wins / child.visits) + self.c * math.sqrt(math.log(parent.visits + 1) / child.visits)

    def _select(self, node):
        while node.children and node.is_fully_expanded():
            node = max(node.children, key=lambda ch: self._uct(node, ch))
        return node

    def _expand(self, node):
        test_node = Node(copy.deepcopy(node.state), node.prev_player)
        untried_moves = [m for m in test_node.get_legal_moves() if m not in [c.move for c in node.children]]
        try:
            move = untried_moves[0]
        except IndexError:
            move = test_node.get_legal_moves()[0]
        new_state = node.make_move(move)
        # prev_player for child is the player who moved (node.next_player)
        child_node = Node(new_state, node.next_player, parent=node, move=move)
        node.children.append(child_node)
        return child_node, move

    def _simulate(self, node, ui_player_idx):
        current_node = Node(copy.deepcopy(node.state), node.prev_player)
        certain_rewards = current_node.get_reward()
        # random/simplified rollout: pick first legal move each step (deterministic) to keep speed.
        while not current_node.terminal():
            legal = current_node.get_legal_moves()
            mv = legal[0] if game_state.difficulty=="hard" else random.choice(legal)
            new_state = current_node.make_move(mv)
            # prev_player for next node is current.next_player (the one who just moved)
            current_node = Node(new_state, current_node.next_player)
        potential_rewards = current_node.get_reward()
        cpu_idx0 = (ui_player_idx - 1)  # convert UI 1-based to 0-based state index
        if game_state.difficulty == "easy":
            rewards = [certain_rewards[i] for i in range(len(certain_rewards))]
            return rewards[cpu_idx0]
        else:
            rewards = [certain_rewards[i] + potential_rewards[i] for i in range(len(certain_rewards))]
            # return CPU's score minus average of opponents who are competitive
            own = rewards[cpu_idx0]
            others = [rewards[i] for i in range(len(rewards)) if i != cpu_idx0 and rewards[i] > own * 0.9]
            if others:
                return own - (sum(others) / len(others))
            else:  # if no close opponents, compare to average of all others
                other_all = [rewards[i] for i in range(len(rewards)) if i != cpu_idx0]
                if other_all:
                    return own - (sum(other_all) / len(other_all))
                return own

    def _backpropagate(self, node, value):
        while node is not None:
            node.visits += 1
            node.wins += value
            node = node.parent

    def _uct_select(self, node):
        def uct(child):
            if child.visits == 0:
                return float("inf")
            return (child.wins / child.visits) + 2 * math.sqrt(2 * math.log(node.visits) / child.visits)
        return max(node.children, key=uct)

    def _get_best_move(self, node):
        if not node.children:
            raise ValueError("No children to select the best move from.")
        return max(node.children, key=lambda child: child.visits)


# ------------------------------------------------------
# --------------- SINGLE PLAYER PAGE -------------------
# ------------------------------------------------------

class SinglePlayer(GamePage):
    def __init__(self):
        self.player_names = ["You"] + [f"CPU {i+1}" for i in range(3)]
        super().__init__()
        self.making_computer_move = False
        self.current_player_idx = 1  # UI 1-based player index (1 == human)
        self.computer_move_timer = 0
        self.mcts = None
        self.mcts_root = None
        self.pending_move = None
        self.mcts_max_reward = -1e9

    def handle_event(self, event):
        event.scaled_pos = get_event_pos(event)
        for button in self.buttons: button.handle_event(event)
        for input_box in self.text_inputs: input_box.handle_event(event)
        for popup in self.popups: popup.handle_event(event)
        if self.current_player_idx == 1:
            for sprite in self.sprites:
                sprite.handle_event(event)

    def start_next_turn(self):
        # Called when round advances to next player. If that player is CPU (not 1),
        # prepare MCTS root. Important: pass prev_player so Node.next_player matches UI player.
        if self.current_player_idx != 1:
            num_players = len(self.game_boards)
            # convert UI 1-based current_player_idx to 0-based state index for next_player:
            next_player_state_idx = (self.current_player_idx - 1)  # 0-based
            # prev_player must be (next_player_state_idx - 1) mod n so next_player = prev+1 == next_player_state_idx
            prev_player = (next_player_state_idx - 1) % num_players
            state = make_nice_state(self.game_boards, self.factories, self.pot)
            self.mcts_root = Node(state, prev_player=prev_player)
            self.mcts = MCTS()
            self.pending_move = None
            self.computer_move_timer = 0
            self.mcts_max_reward = -1e9

    def animate_game_boards(self, dt):
        # keep your original implementation unchanged
        if self.scoring:
            self.scoring_timer += dt
            if self.scoring_phase == 0:  # wait between round end and scoring
                if self.scoring_timer >= 0.8:
                    self.next_round_starting_game_board = [g for g in self.game_boards if "one" in [t.colour for t in list(g.towers)[0].tiles]][0]
                    self.game_boards_scored = 0
                    self.current_player_idx = 1
                    self.scoring_timer = 0
                    self.scoring_phase = 1

            elif self.scoring_phase == 1:   # wait before scoring first tower
                if self.scoring_timer >= 0.2:
                    self.game_boards_scored += 1
                    self.scoring_timer = 0
                    self.scoring_phase = 2
                    self.current_tower_idx = 1

            elif self.scoring_phase == 2:   # wait between each tower
                game_board = [g for g in self.game_boards if g.player_pos==self.current_player_idx][0]
                tile_score_text = [text for text in game_board.texts if text.idx==3][0]
                if self.current_tower_idx < len(game_board.towers):
                    tower = [t for t in game_board.towers if t.idx==self.current_tower_idx][0]
                    if len(tower.tiles)==tower.idx or hasattr(tower, "last_tile"):
                        if self.scoring_timer >= 0.4:
                            hide(tile_score_text)
                            for text in game_board.texts:
                                text.update(0)
                                game_state.rects_to_draw.append(text.rect)
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
                                    game_state.rects_to_draw.append(tile.rect)
                                    tower.tiles.remove(tile)
                            if not tower.last_tile.animating:  # tile getting added to gameboard
                                game_board_row_colours = game_board.tile_colours[tower.idx-1:] + game_board.tile_colours[:tower.idx-1]
                                game_board_colour_index = game_board_row_colours.index(tower.last_tile.colour)
                                game_board_tile_index = (tower.idx-1)*5+game_board_colour_index+1
                                game_board_tile_pos = game_board.tile_coords[game_board_tile_index-1]
                                game_board.add_tile(tower.last_tile, game_board_tile_index)
                                game_board.score_tile(game_board_tile_pos)
                                for text in game_board.texts:
                                    text.update(0)
                                    game_state.rects_to_draw.append(text.rect)
                                del tower.last_tile
                                del tower.scored
                    else:
                        self.scoring_timer = 0
                        self.current_tower_idx += 1

                elif self.current_tower_idx == len(game_board.towers): # idx = 6, but is minus tower
                    minus_tower = [t for t in game_board.towers if t.idx==0][0]
                    if self.scoring_timer > 0.4:
                        hide(tile_score_text)
                        for text in game_board.texts:
                            text.update(0)
                            game_state.rects_to_draw.append(text.rect)
                        self.scoring_timer = 0
                        self.scoring_phase = 3 if len(minus_tower.tiles) > 0 else 4

            elif self.scoring_phase == 3:   # minus tower
                game_board = [g for g in self.game_boards if g.player_pos==self.current_player_idx][0]
                tower = [t for t in game_board.towers if t.idx==0][0]
                tile_score_text = [text for text in game_board.texts if text.idx==3][0]
                if len(tower.tiles) > 0 or tile_score_text.visible==True:
                    if 0.3 <= self.scoring_timer < 0.5:
                        hide(tile_score_text)
                        for text in game_board.texts:
                            text.update(0)
                            game_state.rects_to_draw.append(text.rect)
                    if len(tower.tiles)>0 and self.scoring_timer >= 0.5:
                        tile_to_remove = list(tower.tiles)[0]
                        game_board.score_tile(tile_to_remove.idx, minus_tower=True)
                        game_state.rects_to_draw.append(tile_to_remove.rect)
                        for text in game_board.texts:
                            text.update(0)
                            game_state.rects_to_draw.append(text.rect)
                        tower.tiles.remove(tile_to_remove)
                        self.scoring_timer = 0
                else:
                    self.scoring_timer = 0
                    self.scoring_phase = 4

            elif self.scoring_phase == 4: # wait before rotating or starting new round
                if self.game_boards_scored < game_state.number_of_players:
                    self.scoring_phase = 1
                    self.scoring_timer = 0
                    self.current_player_idx = (self.current_player_idx)%len(self.game_boards) +1
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
                                self.current_player_idx = 1
                        if not self.scoring_end_game:
                            self.current_player_idx = self.next_round_starting_game_board.idx
                            self.new_round_popup.build()
                            show(self.new_round_popup)
                            self.start_new_round()
                            self.start_next_turn()

        elif self.scoring_end_game:
            self.scoring_timer += dt
            if self.scoring_phase == 0:  # scoring rows, cols, diags
                game_board = [g for g in self.game_boards if g.player_pos==self.current_player_idx][0]
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
                game_board = [g for g in self.game_boards if g.player_pos==self.current_player_idx][0]
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
                            for text in game_board.texts:
                                text.update(0)
                                game_state.rects_to_draw.append(text.rect)
                        if self.scoring_timer >=0.9:
                            for tile in block:
                                tile.show_glow = False
                                hide(tile_score_text)
                                for text in game_board.texts:
                                    text.update(0)
                                    game_state.rects_to_draw.append(text.rect)
                        if self.scoring_timer >= 1:
                            self.block_idx += 1
                            self.scoring_timer = 0
                    else:
                        self.block_idx += 1
                        self.scoring_timer = 0
                else:  # all blocks done
                    self.scoring_phase = 2
                    self.scoring_timer = 0

            elif self.scoring_phase == 2:   # wait before rotating
                if self.game_boards_scored < game_state.number_of_players:
                    self.scoring_phase = 0
                    self.scoring_timer = 0
                    self.current_player_idx = (self.current_player_idx)%len(self.game_boards) +1
                else:
                    if self.scoring_timer > 0.5:
                        self.scoring_end_game = False
                        for factory in self.factories:
                            hide(factory)
                        self.end_game_popup.build()
                        show(self.end_game_popup)
                        for button in self.end_game_popup.buttons:
                            show(button)
                        for button in self.buttons:
                            hide(button)


    def update(self, dt):
        self.computer_move_timer += dt
        if self.animating or self.new_round_popup.visible:
            self.computer_move_timer = 0
        elif self.mcts and not self.pending_move and self.computer_move_timer > 0.5:
            # run batches each frame to accumulate visits and not act instantly
            for i in range(20):  # tweak batch size
                node = self.mcts._select(self.mcts_root)
                if not node.is_fully_expanded():
                    node, suggested_move = self.mcts._expand(node)
                reward = self.mcts._simulate(node, self.current_player_idx)
                if reward > self.mcts_max_reward:
                    self.mcts_max_reward = reward
                    # debugging prints
                    # print(f"----------- Move {i+1}")
                    # print(print_move(suggested_move, node.prev_player))
                    # print("player", node.next_player, "reward", reward)
                self.mcts._backpropagate(node, reward)
            #print([child.visits for child in self.mcts_root.children])
            # Decide move only after enough visits or time
            if self.computer_move_timer >= 1:
                self.pending_move = self.mcts._get_best_move(self.mcts_root).move

        if self.pending_move:
            # pending_move is (pool_idx, pool_list, tiles_list, tower_idx, tower_list)
            pool_idx, pool_tiles, colours, tower_idx, tower_tiles = self.pending_move
            colour = colours[0]
            # ---- Map indices back to game objects ----
            if pool_idx == len(self.factories):
                factory = self.pot
                tiles_to_move = [t for t in self.pot.tiles if t.colour == colour]
                tiles_to_pot = []
                game_board = [g for g in self.game_boards if g.idx == self.current_player_idx][0]
                tower = [to for to in game_board.towers if to.idx == tower_idx][0]
            else:
                factory = self.factories[pool_idx]
                tiles_to_move = [t for t in factory.tiles if t.colour == colour]
                tiles_to_pot = [t for t in factory.tiles if t.colour != colour]
                game_board = [g for g in self.game_boards if g.idx == self.current_player_idx][0]
                tower = [to for to in game_board.towers if to.idx == tower_idx][0]

            # ---- Execute actual game move (same flow as previous code) ----
            minus_tower = [to for to in game_board.towers if to.idx == 0][0]
            pot = self.pot
            parent_factory = tiles_to_move[0].parent
            tiles_in_pot = [tile for tile in pot.tiles if tile not in tiles_to_move + tiles_to_pot]
            tiles_to_pot = tiles_in_pot + tiles_to_pot
            if parent_factory == pot:
                one_tile = [tile for tile in pot.tiles if tile.colour == "one"]
                tiles_to_move = [tile for tile in tiles_to_move if tile.colour != "one"]
                tiles_to_move = one_tile + tiles_to_move
                tiles_to_pot = [tile for tile in tiles_to_pot if tile.colour != "one"]
            sizes = [tower.tile_size]*len(tiles_to_move)
            new_pot_sizes = [tile.size for tile in tiles_to_pot]
            poses = transfer_tiles(tiles_to_move, parent_factory, tower, minus_tower, parent_factory==pot)
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
            game_board.move_made = True

            # reset MCTS after executing the move
            self.pending_move = None
            self.mcts = None
            self.mcts_root = None

        super().update(dt, single_player=True)


def print_move(move, player):
    if move:
        factory_num, factory, tiles, tower_cat, tower = move
        if factory_num != len(factory):  # may be fragile - kept for debug only
            factory_desc = f"Factory {factory_num} {[t[0] for t in factory]}"
        else:
            factory_desc = f"Pot {[t[0] for t in factory]}"
        return f"Take {[t[0] for t in tiles]} from {factory_desc} into tower {tower_cat} of gameboard {player}"
    return "None"
