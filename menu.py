import hashlib
import hmac
import pygame
from settings import Settings
from score import Score
import mysql.connector
from pygame.locals import *
import random
import json

class Menu:
    def randomTitle():
        title = [
        "Snake of Duty",
        "Assassin's Snake",
        "Red Snake Redemption",
        "BorderSnake",
        "Need for Snake",
        "SnakeCraft II",
        "Snake League",
        "League of Snake",
        "BattleSnake 2",
        "OverSnake 2",
        "World of Snake",
        "Snakestone",
        "Elden Snake",
        "Snake TD 6",
        "Snake Sport Resort",
        "Snakevilisation 6",
        "Snakepack Joyride",
        "Snake Ninja",
        "Minesnake",
        "Age of Snake",
        "Angry Snake",
        "Counter Snake: Global Offensive",
        "Lethal Snake",
        "Grand Theft Snake V",
        "Snake Us",
        "The Legend of Snake",
        "Rainbow Snake: Siege",
        "The Last of Snake"
        ]
        selected_title = random.choice(title)  # Select a random title
        print(selected_title)  # Print the selected title
        return selected_title  # Return the selected title

    title = randomTitle()
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

        # Bouton Multijoueur
        self.play_button_multiplayer_rect = pygame.Rect(
            (self.settings.screen_width // 2) - 100,
            (self.settings.screen_height // 2) + 50,
            200,
            50
        )

        # Bouton Tableau des scores
        self.leaderboard_button_rect = pygame.Rect(
            (self.settings.screen_width // 2) - 100,
            (self.settings.screen_height // 2) + 125,
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
        self.draw_text_centered(screen, self.title, self.title_font, self.settings.title_color, y_offset=-self.settings.screen_height // 2 + 60)
        
        # Espacement entre les boutons
        button_spacing = 70
        initial_y = self.settings.screen_height // 2 - button_spacing
        
        # Mise à jour des positions des boutons

        #4 boutons 2 lignes 2 colonnes centré au milieu de l'écran
        self.play_button_easy_rect.x = self.settings.screen_width // 2 - 220
        self.play_button_easy_rect.y = initial_y

        self.play_button_hard_rect.x = self.settings.screen_width // 2 + 30
        self.play_button_hard_rect.y = initial_y

        self.play_button_multiplayer_rect.x = self.settings.screen_width // 2 - 220
        self.play_button_multiplayer_rect.y = initial_y + button_spacing

        self.leaderboard_button_rect.x = self.settings.screen_width // 2 + 30
        self.leaderboard_button_rect.y = initial_y + button_spacing


        # Dessiner les boutons
        self.draw_button(screen, self.play_button_easy_rect, "Jouer (Facile)", self.font, self.settings.button_color_easy, self.settings.button_text_color)
        self.draw_button(screen, self.play_button_hard_rect, "Jouer (Difficile)", self.font, self.settings.button_color_hard, self.settings.button_text_color)
        self.draw_button(screen, self.play_button_multiplayer_rect, "Multijoueur", self.font, (255, 155, 0), self.settings.button_text_color)
        self.draw_button(screen, self.leaderboard_button_rect, "Classement", self.font, (0, 0, 255), self.settings.button_text_color)
        
        # Afficher les meilleurs scores
        top_score_y = self.settings.screen_height // 2 - 2 * button_spacing + 50  # Position au-dessus des boutons
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
                elif self.play_button_multiplayer_rect.collidepoint(event.pos):
                    print("Multijoueur non implémenté.")
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
        self.load_best_scores()
        
    def load_best_scores(self):
        """Charge les meilleurs scores pour les deux modes pour le joueur actuel."""
        print("[Menu] Chargement des meilleurs scores.")
        if self.best_scores is None:
            self.best_scores = {'facile': 0, 'difficile': 0}  # Réinitialisation si nécessaire
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
        """Affiche le leaderboard avec une barre de défilement visible et des fonctionnalités de défilement supplémentaires."""
        print("[Menu] Affichage du leaderboard.")
        running = True

        # Variables pour gérer le défilement
        scroll_y = 0  # Position de défilement
        scroll_speed = 20  # Vitesse de défilement (flèches et molette)
        is_scrolling = False  # Pour vérifier si la souris est maintenue enfoncée pour scroller
        last_mouse_y = 0  # Dernière position de la souris pour calculer le mouvement

        # Créer une surface virtuelle pour les scores
        leaderboard_surface_height = 600  # Hauteur virtuelle pour les scores
        leaderboard_surface = pygame.Surface((self.settings.screen_width, leaderboard_surface_height))

        # Calculer la hauteur totale du leaderboard (dépend de la taille du contenu)
        total_height = 100 + len(leaderboard['facile']) * 30 + len(leaderboard['difficile']) * 30 + 200
        max_scroll = max(0, total_height - self.settings.screen_height + 100)  # Marge en bas

        # Calculer la hauteur de la barre de défilement en fonction du contenu total
        visible_ratio = self.settings.screen_height / total_height
        scrollbar_height = max(20, self.settings.screen_height * visible_ratio)  # Hauteur minimale de la barre
        scrollbar_width = 15  # Largeur de la barre
        scrollbar_color = (100, 100, 100)  # Couleur de la barre de scroll
        scrollbar_x = self.settings.screen_width - scrollbar_width - 10  # Position X de la scrollbar

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_DOWN:  # Flèche bas pour défiler vers le bas
                        scroll_y = min(scroll_y + scroll_speed, max_scroll)
                    elif event.key == pygame.K_UP:  # Flèche haut pour défiler vers le haut
                        scroll_y = max(scroll_y - scroll_speed, 0)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 4:  # Molette vers le haut
                        scroll_y = max(scroll_y - scroll_speed, 0)
                    elif event.button == 5:  # Molette vers le bas
                        scroll_y = min(scroll_y + scroll_speed, max_scroll)
                    elif event.button == 1:  # Clic gauche pour activer le défilement
                        is_scrolling = True
                        last_mouse_y = event.pos[1]  # Enregistrer la position initiale de la souris
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:  # Relâcher le clic gauche
                        is_scrolling = False
                elif event.type == pygame.MOUSEMOTION:
                    if is_scrolling:  # Si le bouton est maintenu, on calcule le défilement
                        mouse_y = event.pos[1]
                        delta_y = mouse_y - last_mouse_y  # Calcul de la différence de mouvement
                        scroll_y = min(max(scroll_y - delta_y, 0), max_scroll)  # Mise à jour du défilement
                        last_mouse_y = mouse_y  # Mise à jour de la dernière position de la souris

            screen = pygame.display.get_surface()
            screen.fill(self.settings.bg_color)

            # Remplir la surface virtuelle avec le leaderboard
            leaderboard_surface.fill(self.settings.bg_color)

            # Afficher le titre
            title_surface = self.title_font.render("Tableau des Scores", True, self.settings.title_color)
            title_rect = title_surface.get_rect(center=(self.settings.screen_width // 2, 50))
            leaderboard_surface.blit(title_surface, title_rect)

            y_offset = 100
            for mode in ['facile', 'difficile']:
                mode_title = self.font.render(f"Mode: {mode.capitalize()}", True, self.settings.score_color)
                mode_rect = mode_title.get_rect(center=(self.settings.screen_width // 2, y_offset))
                leaderboard_surface.blit(mode_title, mode_rect)
                y_offset += 40

                for idx, (pseudo, score) in enumerate(leaderboard[mode], start=1):
                    score_text = self.font.render(f"{idx}. {pseudo} - {score}", True, self.settings.score_color)
                    score_rect = score_text.get_rect(center=(self.settings.screen_width // 2, y_offset))
                    leaderboard_surface.blit(score_text, score_rect)
                    y_offset += 30

                y_offset += 20  # Espacement entre les modes

            info_surface = self.font.render("Appuyez sur Échap pour retourner au menu", True, self.settings.score_color)
            info_rect = info_surface.get_rect(center=(self.settings.screen_width // 2, leaderboard_surface_height - 50))
            leaderboard_surface.blit(info_surface, info_rect)

            # Dessiner la surface virtuelle à la position scrollée
            screen.blit(leaderboard_surface, (0, 0), (0, scroll_y, self.settings.screen_width, self.settings.screen_height))

            # Calculer la position de la barre de défilement en fonction de la position de scroll
            if total_height > self.settings.screen_height:
                scrollbar_y = (scroll_y / max_scroll) * (self.settings.screen_height - scrollbar_height)
                pygame.draw.rect(screen, scrollbar_color, (scrollbar_x, scrollbar_y, scrollbar_width, scrollbar_height))

            pygame.display.flip()
            pygame.time.Clock().tick(self.settings.fps)
