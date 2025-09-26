import pygame
from pygame.locals import *
pygame.init()
from globals2 import *
from menu2 import *
from settings2 import *
from single_player2 import *
from multiplayer2 import *


# Initialize game
pygame.display.set_caption("Flip7")
clock = pygame.time.Clock()

# Scene registry
game_state.scenes = {
    "menu": Menu(),
    "settings": Settings()
}

switch_scene("menu")  # Start with the menu scene

def main_loop():
    first_frame = True
    while game_state.running:
        if first_frame:
            first_frame = False  # skip clearing on very first frame
        else:
            game_state.rects_to_draw = []
    
        dt = clock.tick(FPS) / 1000  # Delta time in seconds
    
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_state.running = False
            elif event.type == VIDEORESIZE and sys.platform in ("win32", "cygwin"):
                build(event, game_state.scenes)
                game_state.get_background()
            else:
                game_state.scenes[game_state.current_scene].handle_event(event)

        # Update
        current_scene = game_state.scenes[game_state.current_scene]
        current_scene.update(dt)

        # Draw
        try:
            rect_to_draw = game_state.rects_to_draw[0].unionall(game_state.rects_to_draw[1:])
            #print(rect_to_draw)
            game_state.fullscreen.blit(game_state.bg_image, rect_to_draw.topleft, rect_to_draw)
            current_scene.draw(current_scene.screen)
            scaled_current_scene = pygame.transform.scale(current_scene.screen, game_state.fullscreen.get_size())
            game_state.fullscreen.blit(scaled_current_scene, rect_to_draw.topleft, rect_to_draw)
        except:
            pass

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main_loop()