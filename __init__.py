# init_db.py
import mysql.connector
from config import DB_CONFIG, DEPARTMENTS_CONFIG

def initialize_database():
    """Initialise la base de données avec les 5 départements."""
    try:
        # Se connecter sans base de données spécifique
        config = DB_CONFIG.copy()
        config.pop('database', None)
        
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        
        # Créer la base de données
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
        cursor.execute(f"USE {DB_CONFIG['database']}")
        
        print(f"✅ Base de données '{DB_CONFIG['database']}' créée ou déjà existante")
        
        # Table des départements
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS departments (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nom VARCHAR(100) UNIQUE NOT NULL,
                code VARCHAR(10) UNIQUE NOT NULL,
                description TEXT,
                formations TEXT,
                nombre_etudiants INT DEFAULT 0,
                nombre_professeurs INT DEFAULT 0,
                salles TEXT,
                couleur VARCHAR(20),
                chef_nom VARCHAR(100),
                chef_email VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Insérer les départements
        for dept_id, dept_info in DEPARTMENTS_CONFIG.items():
            cursor.execute("""
                INSERT INTO departments 
                (id, nom, code, description, nombre_etudiants, nombre_professeurs, couleur, chef_nom, chef_email)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                nom = VALUES(nom),
                code = VALUES(code),
                description = VALUES(description),
                nombre_etudiants = VALUES(nombre_etudiants),
                nombre_professeurs = VALUES(nombre_professeurs),
                couleur = VALUES(couleur),
                chef_nom = VALUES(chef_nom),
                chef_email = VALUES(chef_email)
            """, (
                dept_id,
                dept_info['nom'],
                dept_info['code'],
                dept_info['description'],
                dept_info['nombre_etudiants'],
                dept_info['nombre_professeurs'],
                dept_info['couleur'],
                dept_info['chef_nom'],
                dept_info['chef_email']
            ))
        
        print(f"✅ {len(DEPARTMENTS_CONFIG)} départements insérés")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("🎉 Initialisation de la base de données terminée avec succès!")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation: {e}")

if __name__ == "__main__":
    initialize_database()