import hashlib
import hmac
import pygame
from settings import Settings
from score import Score
import mysql.connector
from pygame.locals import *

class Menu:
    def __init__(self):
        self.settings = Settings()
        self.font = pygame.font.Font(None, self.settings.font_size)
        self.title_font = pygame.font.Font(None, self.settings.title_font_size)

        # Bouton Jouer Vert (mode facile)
        self.play_button_easy_rect = pygame.Rect(
            (self.settings.screen_width // 2) - 150,
            (self.settings.screen_height // 2) - 25,
            200,
            50
        )

        # Bouton Jouer Rouge (mode difficile)
        self.play_button_hard_rect = pygame.Rect(
            (self.settings.screen_width // 2) + 50,
            (self.settings.screen_height // 2) - 25,
            200,
            50
        )

        # Bouton Tableau des scores
        self.leaderboard_button_rect = pygame.Rect(
            (self.settings.screen_width // 2) - 100,
            (self.settings.screen_height // 2) + 100,
            200,
            50
        )

        # Variables pour la saisie du pseudo
        self.pseudo = ''
        self.active = False
        self.input_box = pygame.Rect(self.settings.screen_width // 2 - 100, self.settings.screen_height // 2 - 100, 200, 50)
        self.input_font = pygame.font.Font(None, 32)
        self.prompt = "Entrez votre pseudo:"

        # Flag pour afficher l'écran de saisie du pseudo
        self.show_input = True

        # Player ID
        self.player_id = None

    def draw(self, screen):
        if self.show_input:
            screen.fill(self.settings.bg_color)
            # Afficher le prompt
            prompt_surface = self.font.render(self.prompt, True, self.settings.score_color)
            prompt_rect = prompt_surface.get_rect(center=(self.settings.screen_width // 2, self.settings.screen_height // 2 - 100))
            screen.blit(prompt_surface, prompt_rect)

            # Dessiner la boîte de saisie
            pygame.draw.rect(screen, (255, 255, 255), self.input_box, 2)
            txt_surface = self.input_font.render(self.pseudo, True, self.settings.score_color)
            screen.blit(txt_surface, (self.input_box.x + 5, self.input_box.y + 10))
            pygame.display.flip()
        else:
            screen.fill(self.settings.bg_color)
            # Dessine le titre
            title_surface = self.title_font.render("Snake Game", True, self.settings.title_color)
            title_rect = title_surface.get_rect(center=(self.settings.screen_width // 2, self.settings.screen_height // 4))
            screen.blit(title_surface, title_rect)

            # Dessine le bouton "Jouer" Vert (mode facile)
            pygame.draw.rect(screen, self.settings.button_color_easy, self.play_button_easy_rect)
            play_text_easy = self.font.render("Jouer (Facile)", True, self.settings.button_text_color)
            play_text_easy_rect = play_text_easy.get_rect(center=self.play_button_easy_rect.center)
            screen.blit(play_text_easy, play_text_easy_rect)

            # Dessine le bouton "Jouer" Rouge (mode difficile)
            pygame.draw.rect(screen, self.settings.button_color_hard, self.play_button_hard_rect)
            play_text_hard = self.font.render("Jouer (Difficile)", True, self.settings.button_text_color)
            play_text_hard_rect = play_text_hard.get_rect(center=self.play_button_hard_rect.center)
            screen.blit(play_text_hard, play_text_hard_rect)

            # Dessine le bouton "Tableau des scores"
            pygame.draw.rect(screen, (0, 0, 255), self.leaderboard_button_rect)  # Bleu pour différencier
            leaderboard_text = self.font.render("Scores", True, self.settings.button_text_color)
            leaderboard_rect = leaderboard_text.get_rect(center=self.leaderboard_button_rect.center)
            screen.blit(leaderboard_text, leaderboard_rect)

            # Affiche le meilleur score pour le mode facile
            top_score_easy = self.get_top_score('facile')
            best_score_easy_text = self.font.render(f"Meilleur score (facile): {top_score_easy}", True, self.settings.score_color)
            best_score_easy_rect = best_score_easy_text.get_rect(center=(self.settings.screen_width // 2, self.settings.screen_height // 2 + 50))
            screen.blit(best_score_easy_text, best_score_easy_rect)

            # Affiche le meilleur score pour le mode difficile
            top_score_hard = self.get_top_score('difficile')
            best_score_hard_text = self.font.render(f"Meilleur score (difficile): {top_score_hard}", True, self.settings.score_color)
            best_score_hard_rect = best_score_hard_text.get_rect(center=(self.settings.screen_width // 2, self.settings.screen_height // 2 + 100))
            screen.blit(best_score_hard_text, best_score_hard_rect)

            pygame.display.flip()

    def handle_event(self, event):
        if self.show_input:
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Si la boîte de saisie est cliquée, activer l'entrée
                if self.input_box.collidepoint(event.pos):
                    self.active = True
                else:
                    self.active = False
            if event.type == pygame.KEYDOWN:
                if self.active:
                    if event.key == pygame.K_RETURN:
                        if self.pseudo.strip() != '':
                            self.player_id = self.create_or_get_player(self.pseudo.strip())
                            if self.player_id:
                                self.show_input = False
                    elif event.key == pygame.K_BACKSPACE:
                        self.pseudo = self.pseudo[:-1]
                    else:
                        if len(self.pseudo) < 20:  # Limite de caractères
                            self.pseudo += event.unicode
        else:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.play_button_easy_rect.collidepoint(event.pos):
                    return 'play_easy'  # Démarrer le jeu en mode facile
                elif self.play_button_hard_rect.collidepoint(event.pos):
                    return 'play_hard'  # Démarrer le jeu en mode difficile
                elif self.leaderboard_button_rect.collidepoint(event.pos):
                    self.show_leaderboard()
        return None

    def create_or_get_player(self, pseudo):
        print(f"[Menu] Création ou récupération du joueur: {pseudo}")
        try:
            conn = mysql.connector.connect(
                host=self.settings.db_host,
                database=self.settings.db_name,
                user=self.settings.db_user,
                password=self.settings.db_password
            )
            cursor = conn.cursor()
            # Vérifier si le joueur existe
            query = "SELECT player_id FROM players WHERE pseudo = %s"
            cursor.execute(query, (pseudo,))
            result = cursor.fetchone()
            if result:
                print(f"[Menu] Joueur existant trouvé avec player_id: {result[0]}")
                return result[0]
            else:
                # Créer un nouveau joueur
                insert_query = "INSERT INTO players (pseudo) VALUES (%s)"
                cursor.execute(insert_query, (pseudo,))
                conn.commit()
                new_player_id = cursor.lastrowid
                print(f"[Menu] Nouveau joueur créé avec player_id: {new_player_id}")

                # Initialiser les scores à 0 pour chaque mode de jeu
                modes = ['facile', 'difficile']
                for mode in modes:
                    score_hmac = self.encrypt_score(0)
                    insert_score_query = """
                        INSERT INTO scores (player_id, mode_id, score, score_hmac)
                        VALUES (%s, (SELECT mode_id FROM game_modes WHERE mode_name = %s), %s, %s)
                    """
                    cursor.execute(insert_score_query, (new_player_id, mode, 0, score_hmac))
                    print(f"[Menu] Score initialisé à 0 pour le mode: {mode}")
                conn.commit()
                return new_player_id
        except mysql.connector.Error as err:
            print(f"[Menu] Erreur lors de la création/récupération du joueur: {err}")
            return None
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def encrypt_score(self, score):
        key = self.settings.score_encryption_key.encode()
        message = str(score).encode()
        hmac_digest = hmac.new(key, message, hashlib.sha256).hexdigest()
        return hmac_digest

    def get_top_score(self, mode):
        print(f"[Menu] Récupération du meilleur score pour le mode: {mode}")
        try:
            conn = mysql.connector.connect(
                host=self.settings.db_host,
                database=self.settings.db_name,
                user=self.settings.db_user,
                password=self.settings.db_password
            )
            cursor = conn.cursor()
            query = """
                SELECT p.pseudo, s.score
                FROM scores s
                JOIN players p ON s.player_id = p.player_id
                JOIN game_modes gm ON s.mode_id = gm.mode_id
                WHERE gm.mode_name = %s
                ORDER BY s.score DESC, s.score_date ASC
                LIMIT 1
            """
            cursor.execute(query, (mode,))
            result = cursor.fetchone()
            if result:
                print(f"[Menu] Meilleur score trouvé: {result[0]} avec {result[1]}")
                return f"{result[0]}: {result[1]}"
            else:
                print("[Menu] Aucun score trouvé pour ce mode.")
                return "Aucun score"
        except mysql.connector.Error as err:
            print(f"[Menu] Erreur lors de la récupération du meilleur score: {err}")
            return "Erreur"
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def show_leaderboard(self):
        print("[Menu] Affichage du tableau des scores.")
        # Afficher le tableau des scores
        leaderboard = self.get_leaderboard()
        self.display_leaderboard(leaderboard)

    def get_leaderboard(self):
        print("[Menu] Récupération du leaderboard.")
        leaderboard = {'facile': [], 'difficile': []}
        try:
            conn = mysql.connector.connect(
                host=self.settings.db_host,
                database=self.settings.db_name,
                user=self.settings.db_user,
                password=self.settings.db_password
            )
            cursor = conn.cursor()
            for mode in ['facile', 'difficile']:
                query = """
                    SELECT p.pseudo, s.score, s.score_date
                    FROM scores s
                    JOIN players p ON s.player_id = p.player_id
                    JOIN game_modes gm ON s.mode_id = gm.mode_id
                    WHERE gm.mode_name = %s
                    ORDER BY s.score DESC, s.score_date ASC
                    LIMIT 10
                """
                cursor.execute(query, (mode,))
                results = cursor.fetchall()
                leaderboard[mode] = results
                print(f"[Menu] Top scores pour {mode}: {results}")
        except mysql.connector.Error as err:
            print(f"[Menu] Erreur lors de la récupération du leaderboard: {err}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        return leaderboard

    def display_leaderboard(self, leaderboard):
        # Afficher le leaderboard dans une nouvelle boucle Pygame
        print("[Menu] Affichage du leaderboard.")
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False

            screen = pygame.display.get_surface()
            screen.fill(self.settings.bg_color)

            # Afficher le titre
            title_surface = self.title_font.render("Tableau des Scores", True, self.settings.title_color)
            title_rect = title_surface.get_rect(center=(self.settings.screen_width // 2, 50))
            screen.blit(title_surface, title_rect)

            y_offset = 100
            for mode in ['facile', 'difficile']:
                mode_title = self.font.render(f"Mode: {mode.capitalize()}", True, self.settings.score_color)
                mode_rect = mode_title.get_rect(center=(self.settings.screen_width // 2, y_offset))
                screen.blit(mode_title, mode_rect)
                y_offset += 40

                for idx, (pseudo, score, score_date) in enumerate(leaderboard[mode], start=1):
                    score_text = self.font.render(f"{idx}. {pseudo} - {score}", True, self.settings.score_color)
                    score_rect = score_text.get_rect(center=(self.settings.screen_width // 2, y_offset))
                    screen.blit(score_text, score_rect)
                    y_offset += 30

                y_offset += 20  # Espacement entre les modes

            info_surface = self.font.render("Appuyez sur Échap pour retourner au menu", True, self.settings.score_color)
            info_rect = info_surface.get_rect(center=(self.settings.screen_width // 2, self.settings.screen_height - 50))
            screen.blit(info_surface, info_rect)

            pygame.display.flip()
            pygame.time.Clock().tick(self.settings.fps)
