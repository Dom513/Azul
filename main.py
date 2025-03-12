import pygame
pygame.init()
from pygame.locals import *
from globals import *
from menu import *
from settings import *
from single_player import *
from local_multiplayer import *

pygame.display.set_caption("Azul")

menu_screen = pygame.Surface((game_state.screen_width, game_state.screen_height), pygame.SRCALPHA)
settings_screen = pygame.Surface((game_state.screen_width, game_state.screen_height), pygame.SRCALPHA)
profile_screen = pygame.Surface((game_state.screen_width, game_state.screen_height), pygame.SRCALPHA)
single_player_screen = pygame.Surface((game_state.screen_width, game_state.screen_height), pygame.SRCALPHA)
local_multiplayer_screen = pygame.Surface((game_state.screen_width, game_state.screen_height), pygame.SRCALPHA)
subscreens = [menu_screen, settings_screen, local_multiplayer_screen, single_player_screen]

app_open = True
while app_open: 

    get_background()
    #print([game_state.new_menu, game_state.new_settings, game_state.new_single_player, game_state.new_local_multiplayer])
    if not any(state for state in [game_state.new_menu, game_state.new_settings, 
           game_state.new_single_player, game_state.new_local_multiplayer]):
        app_open = False

    ########################
    ######### Menu #########
    ########################

    if game_state.new_menu:
        menu_screen = pygame.Surface((game_state.screen_width, game_state.screen_height), pygame.SRCALPHA)
        game_state.menu_running = True
        buttons, resized_title = create_menu(game_state)
        game_state.new_menu = False

        while game_state.menu_running:
            pygame.time.Clock().tick(30)  # Limit frame rate to 60 FPS

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_state.menu_running = False

                if event.type == VIDEORESIZE:
                    resize(event)
                    menu_screen = pygame.Surface((game_state.screen_width, game_state.screen_height), pygame.SRCALPHA)
                    get_background()
                    buttons, resized_title = create_menu(game_state)

                buttons, resized_title = run_menu(game_state, event, buttons, resized_title)

            # Draw
            game_state.screen.blit(game_state.background, (0,0))
            draw_menu(menu_screen, buttons, resized_title)
            game_state.screen.blit(menu_screen, (0,0))
            pygame.display.update()


    ######################
    ###### Settings ######
    ######################

    elif game_state.new_settings:
        settings_screen = pygame.Surface((game_state.screen_width, game_state.screen_height), pygame.SRCALPHA)
        game_state.settings_running = True
        settings_buttons, settings_texts, settings_title = create_settings(game_state)
        game_state.new_settings = False

        while game_state.settings_running:
            pygame.time.Clock().tick(30)  # Limit frame rate to 60 FPS

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_state.settings_running = False

                if event.type == VIDEORESIZE:
                    resize(event)
                    settings_screen = pygame.Surface((game_state.screen_width, game_state.screen_height), pygame.SRCALPHA)
                    get_background()
                    settings_buttons, settings_texts, settings_title = create_settings(game_state)

                settings_buttons, settings_texts, settings_title = run_settings(game_state, event, settings_buttons, settings_texts, settings_title)
                
            # Draw
            game_state.screen.blit(game_state.background, (0,0))
            draw_settings(game_state, settings_screen, settings_buttons, settings_texts, settings_title)
            game_state.screen.blit(settings_screen, (0,0))
            pygame.display.update()

    #############################
    ##### Local Multiplayer #####
    #############################

    elif game_state.new_local_multiplayer:
        local_multiplayer_screen = pygame.Surface((game_state.screen_width, game_state.screen_height), pygame.SRCALPHA)
        game_state.input_running = True
        player_buttons = create_number_of_players(game_state)
        while game_state.input_running:
            game_state.number_of_players = None
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_state.input_running = False
                    game_state.new_local_multiplayer = False

                if event.type == VIDEORESIZE:
                    resize(event)
                    get_background()
                    player_buttons = create_number_of_players(game_state)
                
                player_buttons = run_number_of_players(game_state, event, player_buttons)
            
            # Draw
            game_state.screen.blit(game_state.background, (0,0))
            draw_number_of_players(game_state, game_state.screen, player_buttons)
            pygame.display.update()

        try:
            game_boards, factories, pot, game_info = create_game(game_state)
            game_state.write_names = True
            text_rects, name_button = create_write_names(game_state)
            editing_index = None
            menu_button = player_buttons[0]
            local_multiplayer_buttons = [menu_button, name_button]
            game_state.local_multiplayer_running = True
            game_state.new_local_multiplayer = False
            new_round = {"running": True,
                        "game_created": False}
            game_over = {"running": False,
                        "show_results": False}
            round_of_turns_start = None
            end_of_round_start = None
            end_of_game_start = None
        except:
            game_state.write_names = False

        # run write names
        while game_state.write_names:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_state.write_names = False
                    game_state.new_local_multiplayer = False
                    game_state.local_multiplayer_running = False

                if event.type == VIDEORESIZE:
                    resize(event)
                    get_background()
                    text_rects, name_button = create_write_names(game_state)
                    player_buttons = create_number_of_players(game_state)
                    local_multiplayer_buttons = [player_buttons[0], name_button]
                
                local_multiplayer_buttons, editing_index = run_write_names(game_state, event, text_rects, local_multiplayer_buttons, editing_index)

            # Draw
            game_state.screen.blit(game_state.background, (0,0))
            draw_write_names(game_state, game_state.screen, text_rects, local_multiplayer_buttons, editing_index)
            pygame.display.update()
        local_multiplayer_buttons = local_multiplayer_buttons[:-1]
        local_multiplayer_screen = pygame.Surface((game_state.screen_width, game_state.screen_height), pygame.SRCALPHA)
            
        while game_state.local_multiplayer_running:
            pygame.time.Clock().tick(30)  # Limit frame rate to 60 FPS
            if new_round["running"]:
                if not new_round["game_created"]:
                    game_boards, factories, pot, game_info = create_game(game_state, game_boards=game_boards, game_info=game_info, new_round=new_round)
                    new_round["game_created"] = True
                    new_round["start"] = pygame.time.get_ticks()
                new_round["current"] = pygame.time.get_ticks()
                round_over = None

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_state.local_multiplayer_running = False

                if event.type == VIDEORESIZE:
                    resize(event)
                    local_multiplayer_screen = pygame.Surface((game_state.screen_width, game_state.screen_height), pygame.SRCALPHA)
                    get_background()
                    game_boards, factories, pot, game_info = create_game(game_state, game_boards, factories, pot, game_info)
                    local_multiplayer_buttons = [create_number_of_players(game_state)[0]]

                game_boards, factories, pot, local_multiplayer_buttons, game_info, round_of_turns_start = run_local_multiplayer(game_state, event, game_boards, factories, pot, local_multiplayer_buttons, game_info, round_of_turns_start)

            round_of_turns_current = pygame.time.get_ticks()
            if round_of_turns_start:
                if round_of_turns_current - round_of_turns_start > 500:
                    rotate_game_boards(game_state, game_boards)
                    round_of_turns_start = None

            # Check if round is over
            if all(factory.tiles == [] for factory in factories+[pot]) and not game_over["show_results"]:
                if not round_over:
                    states = {"wait":0, "score_tower":1, "show_tower_score":2, "score_minus":3, "show_minus_score":4, "reset":5}
                    
                    round_over = {}
                    round_over["current_state"] = states["wait"]
                    round_over["start"] = pygame.time.get_ticks()
                    reordered_game_boards = [(g.player, g.player_pos) for g in game_boards]
                    while reordered_game_boards[0][1] != 1:
                        reordered_game_boards = list(reordered_game_boards[1:]) + [reordered_game_boards[0]]
                    round_over["player_poses"] = iter([x[0] for x in reordered_game_boards])
                    round_over["current_player"] = next(round_over["player_poses"])
                    round_over["current_tower"] = 1
                    round_over["current_minus_tile"] = 0
                    round_over["score_shown"] = False
                    round_over["add_score"] = None
                    round_over["done"] = False
                
                round_over["current"] = pygame.time.get_ticks()

                round_over, game_boards, factories, pot, local_multiplayer_buttons, game_info, new_round = local_multiplayer_round_over(game_state, round_over, states, game_boards, factories, pot, local_multiplayer_buttons, game_info, new_round)
                add_score = round_over["add_score"]    
            
                # Check if game is over
                if any([any([None not in row for row in game_board.tiles]) for game_board in game_boards]) and round_over["done"]:
                    if not game_over["running"]:
                        game_over["running"] = True
                        over_states = {"wait":0, "score_block":1, "show_block_score":2, "reset":3}
                        
                        game_over["current_state"] = over_states["wait"]
                        game_over["start"] = pygame.time.get_ticks()
                        reordered_game_boards = [(g.player, g.player_pos) for g in game_boards]
                        while reordered_game_boards[0][1] != 1:
                            reordered_game_boards = list(reordered_game_boards[1:]) + [reordered_game_boards[0]]
                        game_over["player_poses"] = iter([x[0] for x in reordered_game_boards])
                        game_over["current_player"] = next(game_over["player_poses"])
                        game_over["current_block"] = 0
                        game_over["score_shown"] = False
                        game_over["add_score"] = None
                        game_over["glow_tiles"] = []
                    
                    game_over["current"] = pygame.time.get_ticks()

                    game_over, new_round = local_multiplayer_game_over(game_over, new_round, over_states, game_boards, game_state)
                    add_score = game_over["add_score"]
                    glow_tiles = game_over["glow_tiles"]
            else:
                add_score = None
                glow_tiles = []

            # Draw
            #game_over["show_results"] = True
            game_state.screen.blit(game_state.background, (0,0))
            if new_round["running"] and new_round["game_created"]:
                new_round = draw_new_round(local_multiplayer_screen, game_boards, factories, pot, local_multiplayer_buttons, game_info, new_round, "local")
            elif game_over["show_results"]:
                game_over, local_multiplayer_buttons = draw_results(local_multiplayer_screen, game_over, game_boards, factories, pot, local_multiplayer_buttons, "local")
            else:
                draw_game(local_multiplayer_screen, game_boards, factories, pot, local_multiplayer_buttons, game_info, add_score, glow_tiles)
            game_state.screen.blit(local_multiplayer_screen, (0,0))
            pygame.display.update()

    
    #############################
    ####### Single Player #######
    #############################

    elif game_state.new_single_player:
        single_player_screen = pygame.Surface((game_state.screen_width, game_state.screen_height), pygame.SRCALPHA)
        game_state.input_running = True
        player_buttons = create_number_of_players(game_state)
        while game_state.input_running:
            game_state.number_of_players = None
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_state.input_running = False
                    game_state.new_single_player = False

                if event.type == VIDEORESIZE:
                    resize(event)
                    get_background()
                    player_buttons = create_number_of_players(game_state)
                
                player_buttons = run_number_of_players(game_state, event, player_buttons)
            
            # Draw
            game_state.screen.blit(game_state.background, (0,0))
            draw_number_of_players(game_state, game_state.screen, player_buttons)
            pygame.display.update()
        try:
            game_boards, factories, pot, game_info = create_game(game_state)
            menu_button = player_buttons[0]
            single_player_buttons = [menu_button]
            game_state.single_player_running = True
            game_state.new_single_player = False
            new_round = {"running": True,
                         "game_created": False,
                         "cpu": False}
            game_over = {"running": False,
                         "show_results": False}
            round_of_turns_start = None
            end_of_round_start = None
            end_of_game_start = None
            player_moved = None
            pre_cpu_start = None
        except:
            game_state.single_player_running = False
            
        while game_state.single_player_running:
            pygame.time.Clock().tick(30)  # Limit frame rate to 60 FPS
            if new_round["running"]:
                if not new_round["game_created"]:
                    game_boards, factories, pot, game_info = create_game(game_state, game_boards=game_boards, game_info=game_info, new_round=new_round)
                    new_round["game_created"] = True
                    new_round["start"] = pygame.time.get_ticks()
                new_round["current"] = pygame.time.get_ticks()
                round_over = None
            if new_round["cpu"]:
                game_state.screen.blit(game_state.background, (0,0))
                draw_game(single_player_screen, game_boards, factories, pot, single_player_buttons, game_info, add_score, glow_tiles)
                game_state.screen.blit(single_player_screen, (0,0))
                pygame.display.update()
                if not pre_cpu_start:
                    pre_cpu_start = pygame.time.get_ticks()
                pre_cpu_current = pygame.time.get_ticks()
                #if not player_moved:
                player_moved = [False]*game_state.number_of_players
                ### Check if any computers need to go first then resume loop of player and rest of comps
                cpus_moved = False
                if game_info["next_first_player"] != 1:
                    for i in range(game_info["next_first_player"]-1):
                        player_moved[i] = True
                    for i in range(game_info["next_first_player"]-1,game_state.number_of_players):
                        if not player_moved[i] and all(player_moved[game_info["next_first_player"]-1:i]) and not all(factory.tiles == [] for factory in factories+[pot]):
                            # CPU Move
                            player_moved, pre_cpu_start, game_boards, factories, pot, single_player_buttons, game_info, single_player_screen = make_computer_move(i, game_boards, factories, pot, game_state, game_info, single_player_buttons, pre_cpu_current, pre_cpu_start, player_moved, i, single_player_screen)

                    if player_moved[game_info["next_first_player"]-1:] == [True]*(len(game_boards)-game_info["next_first_player"]+1):
                        pre_cpu_start = None
                        cpus_moved = True
                        player_moved = None
                else:
                    cpus_moved = True
                    player_moved = None
            else:
                cpus_moved = True
            new_round["cpu"] = False
    
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_state.single_player_running = False

                if event.type == VIDEORESIZE:
                    resize(event)
                    single_player_screen = pygame.Surface((game_state.screen_width, game_state.screen_height), pygame.SRCALPHA)
                    get_background()
                    game_boards, factories, pot, game_info = create_game(game_state, game_boards, factories, pot, game_info)
                    single_player_buttons = [create_number_of_players(game_state)[0]]
                
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
                            except:
                                pass
                        button.shown_image = button.image

                if not new_round["running"]:
                    if not player_moved:
                        player_moved = [False]*game_state.number_of_players

                    round_of_turns_current = pygame.time.get_ticks()
                    if not player_moved[0] and cpus_moved:  # player move
                        game_info["placed"] = False
                        game_boards, factories, pot, single_player_buttons, game_info = run_single_player(game_state, event, game_boards, factories, pot, single_player_buttons, game_info)
                        if game_info["placed"] == True:
                            player_moved[0] = True
                            round_of_turns_start = pygame.time.get_ticks()

            if not new_round["running"]:
                if not player_moved:
                    player_moved = [False]*game_state.number_of_players
                round_of_turns_current = pygame.time.get_ticks()
                cpus_moved = False
                if player_moved[0]:
                    for i in range(1,game_state.number_of_players):
                        if not player_moved[i] and all(player_moved[:i]) and not all(factory.tiles == [] for factory in factories+[pot]):
                            # CPU Move
                            player_moved, round_of_turns_start, game_boards, factories, pot, single_player_buttons, game_info, single_player_screen = make_computer_move(i, game_boards, factories, pot, game_state, game_info, single_player_buttons, round_of_turns_current, round_of_turns_start, player_moved, i, single_player_screen)

                    if player_moved == [True]*len(game_boards):
                        round_of_turns_start = None
                        player_moved = None
                        cpus_moved = True

            # Check if round is over
            if all(factory.tiles == [] for factory in factories+[pot]) and not game_over["show_results"]:
                if not round_over:
                    states = {"wait":0, "score_tower":1, "show_tower_score":2, "score_minus":3, "show_minus_score":4, "reset":5}
                    
                    round_over = {}
                    round_over["current_state"] = states["wait"]
                    round_over["start"] = pygame.time.get_ticks()
                    reordered_game_boards = [(g.player, g.player_pos) for g in game_boards]
                    while reordered_game_boards[0][1] != 1:
                        reordered_game_boards = list(reordered_game_boards[1:]) + [reordered_game_boards[0]]
                    round_over["player_poses"] = iter([x[0] for x in reordered_game_boards])
                    round_over["current_player"] = next(round_over["player_poses"])
                    round_over["current_tower"] = 1
                    round_over["current_minus_tile"] = 0
                    round_over["score_shown"] = False
                    round_over["add_score"] = None
                    round_over["done"] = False
                
                round_over["current"] = pygame.time.get_ticks()

                round_over, game_boards, factories, pot, single_player_buttons, game_info, new_round = single_player_round_over(game_state, round_over, states, game_boards, factories, pot, single_player_buttons, game_info, new_round)
                add_score = round_over["add_score"]    
            
                # Check if game is over
                if any([any([None not in row for row in game_board.tiles]) for game_board in game_boards]) and round_over["done"]:
                    if not game_over["running"]:
                        game_over["running"] = True
                        over_states = {"wait":0, "score_block":1, "show_block_score":2, "reset":3}
                        
                        game_over["current_state"] = over_states["wait"]
                        game_over["start"] = pygame.time.get_ticks()
                        reordered_game_boards = [(g.player, g.player_pos) for g in game_boards]
                        while reordered_game_boards[0][1] != 1:
                            reordered_game_boards = list(reordered_game_boards[1:]) + [reordered_game_boards[0]]
                        game_over["player_poses"] = iter([x[0] for x in reordered_game_boards])
                        game_over["current_player"] = next(game_over["player_poses"])
                        game_over["current_block"] = 0
                        game_over["score_shown"] = False
                        game_over["add_score"] = None
                        game_over["glow_tiles"] = []
                    
                    game_over["current"] = pygame.time.get_ticks()

                    game_over, new_round = single_player_game_over(game_over, new_round, over_states, game_boards, game_state)
                    add_score = game_over["add_score"]
                    glow_tiles = game_over["glow_tiles"]
            else:
                add_score = None
                glow_tiles = []

            # Draw
            #game_over["show_results"] = True
            game_state.screen.blit(game_state.background, (0,0))
            if new_round["running"] and new_round["game_created"]:
                new_round = draw_new_round(single_player_screen, game_boards, factories, pot, single_player_buttons, game_info, new_round, "single")
            elif game_over["show_results"]:
                game_over, single_player_buttons = draw_results(single_player_screen, game_over, game_boards, factories, pot, single_player_buttons, "single")
            else:
                draw_game(single_player_screen, game_boards, factories, pot, single_player_buttons, game_info, add_score, glow_tiles)
            game_state.screen.blit(single_player_screen, (0,0))
            pygame.display.update()


# Quit Pygame
pygame.quit()