import pygame
from settings import Settings

class Menu:
    def __init__(self):
        self.settings = Settings()
        self.font = pygame.font.Font(None, self.settings.font_size)
        self.title_font = pygame.font.Font(None, self.settings.title_font_size)

        # Bouton Jouer Local
        self.play_local_button_rect = pygame.Rect(
            (self.settings.screen_width // 2) - 150,
            (self.settings.screen_height // 2) - 25,
            300,
            50
        )

        # Bouton Multijoueur
        self.play_multiplayer_button_rect = pygame.Rect(
            (self.settings.screen_width // 2) - 150,
            (self.settings.screen_height // 2) + 50,
            300,
            50
        )

    def draw(self, screen):
        screen.fill(self.settings.bg_color)

        # Dessiner le titre
        title_surface = self.title_font.render("Snake Game", True, self.settings.title_color)
        title_rect = title_surface.get_rect(center=(self.settings.screen_width // 2, self.settings.screen_height // 4))
        screen.blit(title_surface, title_rect)

        # Dessiner le bouton "Jouer Local"
        pygame.draw.rect(screen, (0, 255, 0), self.play_local_button_rect)  # Vert
        play_local_text = self.font.render("Jouer Local", True, (255, 255, 255))
        play_local_text_rect = play_local_text.get_rect(center=self.play_local_button_rect.center)
        screen.blit(play_local_text, play_local_text_rect)

        # Dessiner le bouton "Multijoueur"
        pygame.draw.rect(screen, (255, 0, 0), self.play_multiplayer_button_rect)  # Rouge
        play_multiplayer_text = self.font.render("Multijoueur", True, (255, 255, 255))
        play_multiplayer_text_rect = play_multiplayer_text.get_rect(center=self.play_multiplayer_button_rect.center)
        screen.blit(play_multiplayer_text, play_multiplayer_text_rect)

        pygame.display.flip()

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.play_local_button_rect.collidepoint(event.pos):
                return 'play_local'  # Démarre le jeu en local
            elif self.play_multiplayer_button_rect.collidepoint(event.pos):
                return 'play_multiplayer'  # Démarre le mode multijoueur

        return None
