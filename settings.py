class Settings:
    def __init__(self):
        # Dimensions de la fenêtre et de la grille
        self.cell_size = 20
        self.grid_width = 30  # Nombre de cellules en largeur
        self.grid_height = 20  # Nombre de cellules en hauteur
        self.screen_width = self.cell_size * self.grid_width
        self.screen_height = self.cell_size * self.grid_height

        # Couleurs
        self.bg_color = (0, 0, 0)          # Noir pour l'arrière-plan
        self.snake_color = (0, 255, 0)     # Vert pour le serpent du joueur
        self.enemy_snake_color = (255, 165, 0)  # Orange pour le serpent ennemi
        self.food_color = (255, 0, 0)      # Rouge pour la nourriture
        self.score_color = (255, 255, 255) # Blanc pour le score

        # Paramètres du jeu
        self.fps = 10          # Images par seconde (vitesse du jeu)
        self.font_size = 36    # Taille de la police pour le score

        # Paramètres du serpent ennemi
        self.enemy_move_delay = 2  # Le serpent ennemi se déplace toutes les 10 frames

        # Paramètres de l'écran d'accueil
        self.title_font_size = 72
        self.title_color = (255, 255, 255)  # Blanc pour le titre
        self.button_color_easy = (0, 255, 0)     # Vert pour le bouton "Jouer" sans ennemi
        self.button_color_hard = (255, 0, 0)     # Rouge pour le bouton "Jouer" avec ennemi
        self.button_text_color = (255, 255, 255)  # Blanc pour le texte du bouton

        # Paramètres du Game Over
        self.game_over_font_size = 72
        self.game_over_color = (255, 0, 0)  # Rouge pour le texte "Game Over"

        # Informations de connexion à la base de données MySQL
        self.db_host = '153.92.220.151'
        self.db_name = 'u161682765_snake'
        self.db_user = 'u161682765_snake'
        self.db_password = 'z12T$Xy|F'

        # Clé secrète pour le chiffrement du score
        self.score_encryption_key = 'ma_clé_secrète_complexe_123!'  # Remplacez par une clé secrète robuste
