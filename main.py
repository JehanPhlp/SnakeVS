import pygame
from game import Game
from menu import Menu
from settings import Settings

def main():
    pygame.init()
    settings = Settings()
    screen = pygame.display.set_mode((settings.screen_width, settings.screen_height))
    
    pygame.display.set_caption("Snake Something")
    clock = pygame.time.Clock()

    menu = Menu()
    running = True
    current_screen = 'menu'

    while running:
        if current_screen == 'menu':
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                else:
                    action = menu.handle_event(event)
                    if action == 'play_easy':
                        if menu.player_id:
                            game = Game('facile', menu.player_id)
                            current_screen = 'game'
                        else:
                            print("[Main] player_id non défini.")
                    elif action == 'play_hard':
                        if menu.player_id:
                            game = Game('difficile', menu.player_id)
                            current_screen = 'game'
                        else:
                            print("[Main] player_id non défini.")
            menu.draw(screen)
            pygame.display.flip()
            clock.tick(settings.fps)
        
        elif current_screen == 'game':
            result = game.run()
            if result == 'quit':
                running = False
            else:
                menu.update_best_scores()  # Actualise les meilleurs scores affichés dans le menu
                current_screen = 'menu'
        else:
            running = False

    pygame.quit()

if __name__ == "__main__":
    main()
