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

        # Initialisation des coordonnées des boutons et éléments
        self.init_button_positions()
        self.init_input_box()
        self.init_validate_button()

        # Variables pour stocker les meilleurs scores
        self.best_scores = {'facile': 'Aucun score', 'difficile': 'Aucun score'}
        self.player_id = None  # Pour stocker l'ID du joueur
        self.pseudo = ''
        self.load_best_scores()  # Charge les meilleurs scores au démarrage si un joueur est connecté

    def init_button_positions(self):
        """Initialise les positions des boutons du menu."""
        # Bouton Jouer Vert (mode facile)
        self.play_button_easy_rect = pygame.Rect(
            (self.settings.screen_width // 2) - 100,
            (self.settings.screen_height // 2) - 25,
            200,
            50
        )

        # Bouton Jouer Rouge (mode difficile)
        self.play_button_hard_rect = pygame.Rect(
            (self.settings.screen_width // 2) - 100,
            (self.settings.screen_height // 2) - 25,
            200,
            50
        )

        # Bouton Tableau des scores
        self.leaderboard_button_rect = pygame.Rect(
            (self.settings.screen_width // 2) - 100,
            (self.settings.screen_height // 2) - 100,
            200,
            50
        )

    def init_input_box(self):
        """Initialise la boîte de saisie pour le pseudo."""
        self.active = False
        self.input_box = pygame.Rect(
            self.settings.screen_width // 2 - 100,
            self.settings.screen_height // 2 - 50,
            200,
            50
        )
        self.input_font = pygame.font.Font(None, 32)
        self.prompt = "Entrez votre pseudo:"

    def init_validate_button(self):
        """Initialise le bouton de validation."""
        self.validate_button_rect = pygame.Rect(
            self.settings.screen_width // 2 - 50,
            self.settings.screen_height // 2 + 20,
            100,
            40
        )
        self.show_input = True

    def draw(self, screen):
        """Gère l'affichage en fonction de l'état du menu."""
        screen.fill(self.settings.bg_color)

        if self.show_input:
            self.draw_input_screen(screen)
        else:
            self.draw_main_menu(screen)
        
        pygame.display.flip()

    def draw_input_screen(self, screen):
        """Affiche l'écran de saisie du pseudo."""
        self.draw_text_centered(screen, self.prompt, self.font, self.settings.score_color, y_offset=-100)
        pygame.draw.rect(screen, (255, 255, 255), self.input_box, 2)
        txt_surface = self.input_font.render(self.pseudo, True, self.settings.score_color)
        screen.blit(txt_surface, (self.input_box.x + 10, self.input_box.y + 10))
        self.draw_button(screen, self.validate_button_rect, "Valider", self.input_font, (0, 255, 0), (0, 0, 0))

    def draw_main_menu(self, screen):
        """Affiche l'écran principal du menu."""
        self.draw_text_centered(screen, "Snake Game", self.title_font, self.settings.title_color, y_offset=-self.settings.screen_height // 4)
        
        # Espacement entre les boutons
        button_spacing = 70
        initial_y = self.settings.screen_height // 2 - button_spacing
        
        # Mise à jour des positions des boutons
        self.play_button_easy_rect.y = initial_y
        self.play_button_hard_rect.y = initial_y + button_spacing
        self.leaderboard_button_rect.y = initial_y + 2 * button_spacing

        # Dessiner les boutons
        self.draw_button(screen, self.play_button_easy_rect, "Jouer (Facile)", self.font, self.settings.button_color_easy, self.settings.button_text_color)
        self.draw_button(screen, self.play_button_hard_rect, "Jouer (Difficile)", self.font, self.settings.button_color_hard, self.settings.button_text_color)
        self.draw_button(screen, self.leaderboard_button_rect, "Classement", self.font, (0, 0, 255), self.settings.button_text_color)
        
        # Afficher les meilleurs scores
        top_score_y = self.settings.screen_height // 2 - 2 * button_spacing + 100  # Position au-dessus des boutons
        self.draw_best_scores_line(screen, top_score_y)

    def draw_button(self, screen, rect, text, font, bg_color, text_color):
        """Dessine un bouton avec du texte centré."""
        pygame.draw.rect(screen, bg_color, rect, border_radius=10)
        text_surface = font.render(text, True, text_color)
        text_rect = text_surface.get_rect(center=rect.center)
        screen.blit(text_surface, text_rect)

    def draw_text_centered(self, screen, text, font, color, x_offset=0, y_offset=0):
        """Affiche du texte centré horizontalement avec des décalages optionnels."""
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(self.settings.screen_width // 2 + x_offset, self.settings.screen_height // 2 + y_offset))
        screen.blit(text_surface, text_rect)

    def draw_best_scores_line(self, screen, y_offset):
        """Affiche les meilleurs scores pour les modes 'facile' et 'difficile' sur la même ligne."""
        score_text = f"Facile: {self.best_scores['facile']} | Difficile: {self.best_scores['difficile']}"

        # Calculer la position horizontale des scores
        screen_center_x = self.settings.screen_width // 2
        score_x = screen_center_x  # Centrer le texte des scores

        # Dessiner les meilleurs scores
        self.draw_text_centered(screen, score_text, self.font, self.settings.score_color, y_offset=y_offset)


    def handle_event(self, event):
        """Gère les événements utilisateurs."""
        if self.show_input:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.input_box.collidepoint(event.pos):
                    self.active = True
                else:
                    self.active = False

                if self.validate_button_rect.collidepoint(event.pos):
                    if self.pseudo.strip() != '':
                        self.player_id = self.create_or_get_player(self.pseudo.strip())
                        if self.player_id:
                            self.show_input = False
                            self.load_best_scores()  # Recharger les meilleurs scores pour le joueur

            if event.type == pygame.KEYDOWN:
                if self.active:
                    if event.key == pygame.K_BACKSPACE:
                        self.pseudo = self.pseudo[:-1]
                    elif event.key == pygame.K_RETURN:
                        if self.pseudo.strip() != '':
                            self.player_id = self.create_or_get_player(self.pseudo.strip())
                            if self.player_id:
                                self.show_input = False
                                self.load_best_scores()  # Recharger les meilleurs scores pour le joueur
                    else:
                        if len(self.pseudo) < 20:
                            self.pseudo += event.unicode
        else:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.play_button_easy_rect.collidepoint(event.pos):
                    return 'play_easy'
                elif self.play_button_hard_rect.collidepoint(event.pos):
                    return 'play_hard'
                elif self.leaderboard_button_rect.collidepoint(event.pos):
                    self.show_leaderboard()
        return None

    def create_or_get_player(self, pseudo):
        """Crée un joueur ou récupère un joueur existant."""
        print(f"[Menu] Création ou récupération du joueur: {pseudo}")
        conn = None
        cursor = None
        try:
            conn = mysql.connector.connect(
                host=self.settings.db_host,
                database=self.settings.db_name,
                user=self.settings.db_user,
                password=self.settings.db_password
            )
            cursor = conn.cursor()
            query = "SELECT player_id FROM players WHERE pseudo = %s"
            cursor.execute(query, (pseudo,))
            result = cursor.fetchone()
            if result:
                print(f"[Menu] Joueur existant trouvé avec player_id: {result[0]}")
                return result[0]
            else:
                insert_query = "INSERT INTO players (pseudo) VALUES (%s)"
                cursor.execute(insert_query, (pseudo,))
                conn.commit()
                new_player_id = cursor.lastrowid
                print(f"[Menu] Nouveau joueur créé avec player_id: {new_player_id}")

                modes = ['facile', 'difficile']
                for mode in modes:
                    score_hmac = self.encrypt_score(0)  # Initialisation avec un score de 0
                    insert_score_query = """
                        INSERT INTO scores (player_id, mode_id, score, score_hmac)
                        SELECT %s, gm.mode_id, %s, %s
                        FROM game_modes gm
                        WHERE gm.mode_name = %s
                    """
                    cursor.execute(insert_score_query, (new_player_id, 0, score_hmac, mode))
                    print(f"[Menu] Score initialisé à 0 pour le mode: {mode}")
                conn.commit()
                return new_player_id
        except mysql.connector.Error as err:
            print(f"[Menu] Erreur lors de la création/récupération du joueur: {err}")
            return None
        finally:
            if cursor is not None:
                cursor.close()
            if conn is not None and conn.is_connected():
                conn.close()

    def encrypt_score(self, score):
        """Chiffre le score avec HMAC."""
        key = self.settings.score_encryption_key.encode()
        message = str(score).encode()
        hmac_digest = hmac.new(key, message, hashlib.sha256).hexdigest()
        return hmac_digest

    def update_best_scores(self):
        self.best_scores = self.load_best_scores()  # Recharge les scores
        
    def load_best_scores(self):
        """Charge les meilleurs scores pour les deux modes pour le joueur actuel."""
        print("[Menu] Chargement des meilleurs scores.")
        self.best_scores['facile'] = self.get_top_score('facile')
        self.best_scores['difficile'] = self.get_top_score('difficile')

    def get_top_score(self, mode):
        """Récupère le meilleur score pour le joueur et le mode donné."""
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
                SELECT s.score
                FROM scores s
                JOIN game_modes gm ON s.mode_id = gm.mode_id
                WHERE s.player_id = %s
                AND gm.mode_name = %s
                AND s.score > 0
                ORDER BY s.score DESC, s.score_date ASC
                LIMIT 1
            """
            cursor.execute(query, (self.player_id, mode))
            result = cursor.fetchone()
            if result:
                print(f"[Menu] Meilleur score trouvé: {result[0]}")
                return f"{result[0]}"
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
        """Affiche le tableau des scores."""
        print("[Menu] Affichage du tableau des scores.")
        leaderboard = self.get_leaderboard()
        self.display_leaderboard(leaderboard)

    def get_leaderboard(self):
        """Récupère le leaderboard pour les deux modes de jeu."""
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
                    SELECT p.pseudo, max(s.score)
                    FROM scores s, players p, game_modes gm
                    WHERE s.player_id = p.player_id
                    AND s.mode_id = gm.mode_id
                    AND gm.mode_name = %s
                    AND s.score > 0
                    GROUP BY p.pseudo, p.player_id
                    ORDER BY max(s.score) DESC
                    LIMIT 5;
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
        """Affiche le leaderboard dans une nouvelle boucle Pygame."""
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

                for idx, (pseudo, score) in enumerate(leaderboard[mode], start=1):
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
