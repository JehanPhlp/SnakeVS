# database.py
import mysql.connector
from mysql.connector import errorcode
from settings import Settings

class Database:
    def __init__(self):
        self.settings = Settings()
        try:
            self.conn = mysql.connector.connect(
                host='153.92.220.151',  # ou l'adresse de votre serveur MySQL
                user=self.settings.db_user,
                password=self.settings.db_password,
                database=self.settings.db_name
            )
            self.cursor = self.conn.cursor(dictionary=True)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Erreur d'authentification : Vérifiez votre nom d'utilisateur ou mot de passe")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("La base de données n'existe pas")
            else:
                print(err)
            self.conn = None

    def create_tables(self):
        TABLES = {}
        TABLES['players'] = (
            "CREATE TABLE IF NOT EXISTS players ("
            "  player_id INT AUTO_INCREMENT PRIMARY KEY,"
            "  pseudo VARCHAR(50) UNIQUE NOT NULL"
            ") ENGINE=InnoDB"
        )

        TABLES['game_modes'] = (
            "CREATE TABLE IF NOT EXISTS game_modes ("
            "  mode_id INT AUTO_INCREMENT PRIMARY KEY,"
            "  mode_name VARCHAR(20) UNIQUE NOT NULL"
            ") ENGINE=InnoDB"
        )

        TABLES['scores'] = (
            "CREATE TABLE IF NOT EXISTS scores ("
            "  score_id INT AUTO_INCREMENT PRIMARY KEY,"
            "  player_id INT NOT NULL,"
            "  mode_id INT NOT NULL,"
            "  score INT NOT NULL,"
            "  score_date DATETIME DEFAULT CURRENT_TIMESTAMP,"
            "  FOREIGN KEY (player_id) REFERENCES players(player_id),"
            "  FOREIGN KEY (mode_id) REFERENCES game_modes(mode_id)"
            ") ENGINE=InnoDB"
        )

        for table_name in TABLES:
            table_description = TABLES[table_name]
            try:
                print(f"Création de la table {table_name}...", end='')
                self.cursor.execute(table_description)
                print("OK")
            except mysql.connector.Error as err:
                if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                    print("La table existe déjà.")
                else:
                    print(err.msg)

    def insert_player(self, pseudo):
        try:
            self.cursor.execute(
                "INSERT INTO players (pseudo) VALUES (%s)",
                (pseudo,)
            )
            self.conn.commit()
            return self.cursor.lastrowid
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_DUP_ENTRY:
                print("Ce pseudo est déjà pris.")
                return None
            else:
                print(err)
                return None

    def get_player_id(self, pseudo):
        self.cursor.execute(
            "SELECT player_id FROM players WHERE pseudo = %s",
            (pseudo,)
        )
        result = self.cursor.fetchone()
        if result:
            return result['player_id']
        else:
            return None

    def insert_score(self, player_id, mode_name, score):
        try:
            # Obtenir mode_id
            self.cursor.execute(
                "SELECT mode_id FROM game_modes WHERE mode_name = %s",
                (mode_name,)
            )
            mode = self.cursor.fetchone()
            if not mode:
                print(f"Mode de jeu '{mode_name}' introuvable.")
                return
            mode_id = mode['mode_id']

            self.cursor.execute(
                "INSERT INTO scores (player_id, mode_id, score) VALUES (%s, %s, %s)",
                (player_id, mode_id, score)
            )
            self.conn.commit()
        except mysql.connector.Error as err:
            print(err)

    def get_leaderboard(self, mode_name, limit=10):
        try:
            query = """
                SELECT p.pseudo, s.score, s.score_date
                FROM scores s
                JOIN players p ON s.player_id = p.player_id
                JOIN game_modes gm ON s.mode_id = gm.mode_id
                WHERE gm.mode_name = %s
                ORDER BY s.score DESC, s.score_date ASC
                LIMIT %s
            """
            self.cursor.execute(query, (mode_name, limit))
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            print(err)
            return []

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
