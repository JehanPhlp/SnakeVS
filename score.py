import pygame
from settings import Settings
import mysql.connector
import hmac
import hashlib

class Score:
    def __init__(self, mode, player_id):
        self.settings = Settings()
        self.value = 0
        self.mode = mode  # 'facile' ou 'difficile'
        self.player_id = player_id
        self.font = pygame.font.Font(None, self.settings.font_size)
        self.best_score = self.load_best_score()
        print(f"[Score] Initialisé pour le joueur_id: {self.player_id}, mode: {self.mode}, meilleur score: {self.best_score}")

    def increment(self):
        self.value += 1
        print(f"[Score] Score incrémenté: {self.value}")
      

    def reset(self):
        self.value = 0
        print("[Score] Score réinitialisé.")

    def draw(self, screen):
        score_surface = self.font.render(f"Score: {self.value}", True, self.settings.score_color)
        score_rect = score_surface.get_rect(topleft=(10, 10))
        screen.blit(score_surface, score_rect)

    def save_best_score(self):
        if self.mode not in ['facile', 'difficile']:
            print("[Score] Mode de jeu invalide pour le score.")
            return

        if self.value > self.best_score:
            self.best_score = self.value
            score_hmac = self.encrypt_score(self.best_score)
            print(f"[Score] Enregistrement du meilleur score: {self.best_score}, HMAC: {score_hmac}")
            
            try:
                conn = mysql.connector.connect(
                    host=self.settings.db_host,
                    database=self.settings.db_name,
                    user=self.settings.db_user,
                    password=self.settings.db_password
                )
                cursor = conn.cursor()

                # Vérifier si des meilleurs scores existent pour ce joueur et ce mode
                check_query = """
                    SELECT score_id FROM scores
                    WHERE player_id = %s AND mode_id = (SELECT mode_id FROM game_modes WHERE mode_name = %s)
                """
                cursor.execute(check_query, (self.player_id, self.mode))
                existing_scores = cursor.fetchall()

                # Supprimer les anciens scores si trouvés
                if existing_scores:
                    delete_query = """
                        DELETE FROM scores WHERE score_id IN (%s)
                    """ % ','.join([str(score[0]) for score in existing_scores])
                    cursor.execute(delete_query)
                    print(f"[Score] {len(existing_scores)} ancien(s) meilleur(s) score(s) supprimé(s) pour le joueur {self.player_id} en mode {self.mode}.")

                # Insérer le nouveau meilleur score
                insert_query = """
                    INSERT INTO scores (player_id, mode_id, score, score_hmac)
                    VALUES (%s, (SELECT mode_id FROM game_modes WHERE mode_name = %s), %s, %s)
                """
                cursor.execute(insert_query, (self.player_id, self.mode, self.best_score, score_hmac))
                conn.commit()
                print("[Score] Nouveau meilleur score inséré avec succès dans la base de données.")

            except mysql.connector.Error as err:
                print(f"[Score] Erreur lors de l'insertion du score: {err}")
            finally:
                # Assurez-vous de toujours fermer le curseur et la connexion
                if cursor:
                    cursor.close()
                if conn:
                    conn.close()



    def load_best_score(self):
        print(f"[Score] Chargement du meilleur score pour le joueur_id: {self.player_id}, mode: {self.mode}")
        try:
            conn = mysql.connector.connect(
                host=self.settings.db_host,
                database=self.settings.db_name,
                user=self.settings.db_user,
                password=self.settings.db_password
            )
            cursor = conn.cursor()
            query = """
                SELECT s.score, s.score_hmac
                FROM scores s
                WHERE s.player_id = %s AND s.mode_id = (SELECT mode_id FROM game_modes WHERE mode_name = %s)
                ORDER BY s.score DESC, s.score_date ASC
                LIMIT 1
            """
            cursor.execute(query, (self.player_id, self.mode))
            result = cursor.fetchone()
            if result:
                score, score_hmac = result
                print(f"[Score] Score trouvé: {score}, HMAC: {score_hmac}")
                if self.verify_score(score, score_hmac):
                    print("[Score] HMAC vérifié avec succès.")
                    return score
                else:
                    print("[Score] HMAC invalide, score corrompu.")
                    return 0
            else:
                print("[Score] Aucun score trouvé, retour à 0.")
                return 0
        except mysql.connector.Error as err:
            print(f"[Score] Erreur lors de la récupération du meilleur score: {err}")
            return 0
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

    def verify_score(self, score, hmac_digest):
        key = self.settings.score_encryption_key.encode()
        message = str(score).encode()
        expected_digest = hmac.new(key, message, hashlib.sha256).hexdigest()
        is_valid = hmac.compare_digest(hmac_digest, expected_digest)
        print(f"[Score] Vérification HMAC: {'Valide' if is_valid else 'Invalide'}")
        return is_valid
