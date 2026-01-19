# auth.py - Système d'authentification complet AVEC 5 DÉPARTEMENTS
import mysql.connector
import bcrypt
import json
import os
from datetime import datetime
from config import DB_CONFIG, ROLES_CONFIG

class AuthSystem:
    def __init__(self, db_config=None):
        """
        Initialise le système d'authentification.
        
        Args:
            db_config (dict, optional): Configuration de la base de données.
                                      Si None, utilise DB_CONFIG de config.py
        """
        self.db_config = db_config or DB_CONFIG
        self.users = {}  # Cache des utilisateurs
        self.ROLES = {
            'admin': 'Administrateur',
            'vicedoyen': 'Vice-Doyen',
            'chef_dept': 'Chef de Département',
            'professeur': 'Professeur',
            'etudiant': 'Étudiant'
        }
        
        # Dictionnaire des départements
        self.DEPARTEMENTS = {
            1: {'nom': 'Informatique', 'couleur': '#4CC9F0'},
            2: {'nom': 'Mathématiques', 'couleur': '#F72585'},
            3: {'nom': 'Physique', 'couleur': '#7209B7'},
            4: {'nom': 'Chimie', 'couleur': '#3A0CA3'},
            5: {'nom': 'Biologie', 'couleur': '#4361EE'}
        }
        
        # Charger les utilisateurs depuis la base de données
        self.load_users_from_db()
        
        # Créer les utilisateurs de démo si la base est vide
        if not self.users:
            self.create_demo_users()
    
    def connect_db(self):
        """Établit une connexion à la base de données."""
        try:
            conn = mysql.connector.connect(**self.db_config)
            return conn
        except mysql.connector.Error as err:
            print(f"❌ Erreur de connexion à la base de données: {err}")
            return None
    
    def load_users_from_db(self):
        """Charge les utilisateurs depuis la base de données."""
        try:
            conn = self.connect_db()
            if not conn:
                return
            
            cursor = conn.cursor(dictionary=True)
            
            # Vérifier si la table utilisateurs existe
            cursor.execute("""
                SELECT TABLE_NAME 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'utilisateurs'
            """, (self.db_config['database'],))
            
            table_exists = cursor.fetchone()
            
            if not table_exists:
                print("⚠️ Table 'utilisateurs' non trouvée. Création des utilisateurs de démo.")
                return
            
            # Charger les utilisateurs
            cursor.execute("""
                SELECT username, password_hash, role, nom, email, 
                       departement_id, professeur_id, etudiant_id
                FROM utilisateurs
                WHERE is_active = TRUE
            """)
            
            users = cursor.fetchall()
            
            for user in users:
                dept_nom = None
                if user['departement_id']:
                    dept_nom = self.DEPARTEMENTS.get(user['departement_id'], {}).get('nom')
                
                self.users[user['username']] = {
                    'password_hash': user['password_hash'],
                    'role': user['role'],
                    'nom': user['nom'],
                    'email': user['email'],
                    'dept_id': user['departement_id'],
                    'dept_nom': dept_nom,  # Ajouter le nom du département
                    'prof_id': user['professeur_id'],
                    'etudiant_id': user['etudiant_id']
                }
            
            print(f"✅ {len(self.users)} utilisateurs chargés depuis la base de données")
            
        except mysql.connector.Error as err:
            print(f"❌ Erreur lors du chargement des utilisateurs: {err}")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()
    
    def create_demo_users(self):
        """Crée les utilisateurs de démonstration avec les 5 départements."""
        print("🔄 Création des utilisateurs de démonstration pour les 5 départements...")
        
        # Utilisateurs de démo avec mots de passe hashés
        demo_users = [
            # Administrateur et Vice-doyen
            {
                'username': 'admin',
                'password': 'admin123',
                'role': 'admin',
                'nom': 'Administrateur Système',
                'email': 'admin@univ.fr'
            },
            {
                'username': 'vicedoyen',
                'password': 'doyen123',
                'role': 'vicedoyen',
                'nom': 'Jean Dupont',
                'email': 'vicedoyen@univ.fr'
            },
            
            # Chefs des 5 départements
            {
                'username': 'chef_info',
                'password': 'info123',
                'role': 'chef_dept',
                'nom': 'Sophie Martin',
                'email': 'chef.info@univ.fr',
                'dept_id': 1,
                'dept_nom': 'Informatique'
            },
            {
                'username': 'chef_maths',
                'password': 'maths123',
                'role': 'chef_dept',
                'nom': 'Pierre Leroy',
                'email': 'chef.maths@univ.fr',
                'dept_id': 2,
                'dept_nom': 'Mathématiques'
            },
            {
                'username': 'chef_physique',
                'password': 'physique123',
                'role': 'chef_dept',
                'nom': 'Marie Curie',
                'email': 'chef.physique@univ.fr',
                'dept_id': 3,
                'dept_nom': 'Physique'
            },
            {
                'username': 'chef_chimie',
                'password': 'chimie123',
                'role': 'chef_dept',
                'nom': 'Antoine Lavoisier',
                'email': 'chef.chimie@univ.fr',
                'dept_id': 4,
                'dept_nom': 'Chimie'
            },
            {
                'username': 'chef_bio',
                'password': 'bio123',
                'role': 'chef_dept',
                'nom': 'Louis Pasteur',
                'email': 'chef.bio@univ.fr',
                'dept_id': 5,
                'dept_nom': 'Biologie'
            },
            
            # Professeur (département Informatique)
            {
                'username': 'prof1',
                'password': 'prof123',
                'role': 'professeur',
                'nom': 'Alami Ahmed',
                'email': 'ahmed.alami@univ.fr',
                'prof_id': 1,
                'dept_id': 1,
                'dept_nom': 'Informatique'
            },
            
            # Étudiant (département Informatique)
            {
                'username': 'etudiant1',
                'password': 'etu123',
                'role': 'etudiant',
                'nom': 'Hafidi Aicha',
                'email': 'aicha.hafidi@etu.univ.fr',
                'etudiant_id': 1,
                'dept_id': 1,
                'dept_nom': 'Informatique'
            }
        ]
        
        for user_data in demo_users:
            # Hasher le mot de passe
            password_hash = self.hash_password(user_data['password'])
            
            # Ajouter au cache
            self.users[user_data['username']] = {
                'password_hash': password_hash,
                'role': user_data['role'],
                'nom': user_data['nom'],
                'email': user_data['email'],
                'dept_id': user_data.get('dept_id'),
                'dept_nom': user_data.get('dept_nom'),  # Ajouter le nom du département
                'prof_id': user_data.get('prof_id'),
                'etudiant_id': user_data.get('etudiant_id')
            }
        
        print(f"✅ {len(demo_users)} utilisateurs de démo créés (5 départements)")
        
        # Sauvegarder dans la base de données
        self.save_users_to_db()
    
    def save_users_to_db(self):
        """Sauvegarde les utilisateurs dans la base de données."""
        try:
            conn = self.connect_db()
            if not conn:
                return
            
            cursor = conn.cursor()
            
            # Créer la table si elle n'existe pas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS utilisateurs (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    role VARCHAR(20) NOT NULL,
                    nom VARCHAR(100),
                    email VARCHAR(100),
                    departement_id INT NULL,
                    professeur_id INT NULL,
                    etudiant_id INT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP NULL,
                    FOREIGN KEY (departement_id) REFERENCES departments(id) ON DELETE SET NULL,
                    FOREIGN KEY (professeur_id) REFERENCES professeurs(id) ON DELETE SET NULL,
                    FOREIGN KEY (etudiant_id) REFERENCES etudiants(id) ON DELETE SET NULL
                )
            """)
            
            # Vérifier si la table departments existe
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS departments (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nom VARCHAR(100) UNIQUE NOT NULL,
                    description TEXT,
                    formations TEXT,
                    nombre_etudiants INT,
                    nombre_professeurs INT,
                    salles TEXT,
                    couleur VARCHAR(20),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Insérer les départements s'ils n'existent pas
            for dept_id, dept_info in self.DEPARTEMENTS.items():
                cursor.execute("""
                    INSERT INTO departments (id, nom, couleur, nombre_etudiants, nombre_professeurs)
                    VALUES (%s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                    nom = VALUES(nom),
                    couleur = VALUES(couleur),
                    nombre_etudiants = VALUES(nombre_etudiants),
                    nombre_professeurs = VALUES(nombre_professeurs)
                """, (
                    dept_id,
                    dept_info['nom'],
                    dept_info['couleur'],
                    dept_info.get('nombre_etudiants', 0),
                    dept_info.get('nombre_professeurs', 0)
                ))
            
            # Insérer ou mettre à jour les utilisateurs
            for username, user_data in self.users.items():
                cursor.execute("""
                    INSERT INTO utilisateurs 
                    (username, password_hash, role, nom, email, departement_id, professeur_id, etudiant_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                    password_hash = VALUES(password_hash),
                    role = VALUES(role),
                    nom = VALUES(nom),
                    email = VALUES(email),
                    departement_id = VALUES(departement_id),
                    professeur_id = VALUES(professeur_id),
                    etudiant_id = VALUES(etudiant_id)
                """, (
                    username,
                    user_data['password_hash'],
                    user_data['role'],
                    user_data['nom'],
                    user_data['email'],
                    user_data.get('dept_id'),
                    user_data.get('prof_id'),
                    user_data.get('etudiant_id')
                ))
            
            conn.commit()
            print("✅ Utilisateurs et départements sauvegardés dans la base de données")
            
        except mysql.connector.Error as err:
            print(f"❌ Erreur lors de la sauvegarde des utilisateurs: {err}")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()
    
    def hash_password(self, password):
        """Hashe un mot de passe avec bcrypt."""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password, hashed_password):
        """Vérifie si un mot de passe correspond au hash."""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
        except Exception:
            return False
    
    def authenticate(self, username, password):
        """
        Authentifie un utilisateur.
        
        Args:
            username (str): Nom d'utilisateur
            password (str): Mot de passe
            
        Returns:
            dict: Informations de l'utilisateur ou None si échec
        """
        if username not in self.users:
            return None
        
        user_data = self.users[username]
        
        # Vérifier le mot de passe
        if not self.verify_password(password, user_data['password_hash']):
            return None
        
        # Retourner les informations de l'utilisateur
        user_info = {
            'username': username,
            'role': user_data['role'],
            'nom': user_data['nom'],
            'email': user_data['email'],
            'dept_id': user_data.get('dept_id'),
            'prof_id': user_data.get('prof_id'),
            'etudiant_id': user_data.get('etudiant_id')
        }
        
        # Ajouter le nom du département si disponible
        if user_data.get('dept_nom'):
            user_info['dept_nom'] = user_data.get('dept_nom')
        elif user_data.get('dept_id'):
            # Récupérer le nom du département depuis le dictionnaire
            dept_nom = self.DEPARTEMENTS.get(user_data.get('dept_id'), {}).get('nom')
            if dept_nom:
                user_info['dept_nom'] = dept_nom
        
        return user_info
    
    def register_user(self, username, password, role, nom, email, **kwargs):
        """
        Enregistre un nouvel utilisateur.
        
        Args:
            username (str): Nom d'utilisateur
            password (str): Mot de passe
            role (str): Rôle de l'utilisateur
            nom (str): Nom complet
            email (str): Adresse email
            **kwargs: Paramètres supplémentaires (dept_id, prof_id, etudiant_id)
            
        Returns:
            bool: True si succès, False si échec
        """
        if username in self.users:
            return False
        
        # Hasher le mot de passe
        password_hash = self.hash_password(password)
        
        # Déterminer le nom du département si dept_id est fourni
        dept_nom = None
        if kwargs.get('dept_id'):
            dept_nom = self.DEPARTEMENTS.get(kwargs.get('dept_id'), {}).get('nom')
        
        # Ajouter l'utilisateur
        self.users[username] = {
            'password_hash': password_hash,
            'role': role,
            'nom': nom,
            'email': email,
            'dept_id': kwargs.get('dept_id'),
            'dept_nom': dept_nom,  # Ajouter le nom du département
            'prof_id': kwargs.get('prof_id'),
            'etudiant_id': kwargs.get('etudiant_id')
        }
        
        # Sauvegarder dans la base de données
        self.save_users_to_db()
        
        return True
    
    def get_user(self, username):
        """
        Récupère les informations d'un utilisateur.
        
        Args:
            username (str): Nom d'utilisateur
            
        Returns:
            dict: Informations de l'utilisateur ou None
        """
        return self.users.get(username)
    
    def update_user(self, username, **kwargs):
        """
        Met à jour les informations d'un utilisateur.
        
        Args:
            username (str): Nom d'utilisateur
            **kwargs: Champs à mettre à jour
            
        Returns:
            bool: True si succès, False si échec
        """
        if username not in self.users:
            return False
        
        # Mettre à jour les champs
        for key, value in kwargs.items():
            if key in self.users[username]:
                self.users[username][key] = value
        
        # Si dept_id est mis à jour, mettre à jour dept_nom
        if 'dept_id' in kwargs:
            dept_nom = self.DEPARTEMENTS.get(kwargs['dept_id'], {}).get('nom')
            if dept_nom:
                self.users[username]['dept_nom'] = dept_nom
            else:
                self.users[username].pop('dept_nom', None)
        
        # Sauvegarder dans la base de données
        self.save_users_to_db()
        
        return True
    
    def change_password(self, username, old_password, new_password):
        """
        Change le mot de passe d'un utilisateur.
        
        Args:
            username (str): Nom d'utilisateur
            old_password (str): Ancien mot de passe
            new_password (str): Nouveau mot de passe
            
        Returns:
            bool: True si succès, False si échec
        """
        if username not in self.users:
            return False
        
        user_data = self.users[username]
        
        # Vérifier l'ancien mot de passe
        if not self.verify_password(old_password, user_data['password_hash']):
            return False
        
        # Hasher le nouveau mot de passe
        new_hash = self.hash_password(new_password)
        
        # Mettre à jour
        self.users[username]['password_hash'] = new_hash
        
        # Sauvegarder dans la base de données
        self.save_users_to_db()
        
        return True
    
    def delete_user(self, username):
        """
        Supprime un utilisateur.
        
        Args:
            username (str): Nom d'utilisateur
            
        Returns:
            bool: True si succès, False si échec
        """
        if username not in self.users:
            return False
        
        # Supprimer de la base de données
        try:
            conn = self.connect_db()
            if conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE utilisateurs SET is_active = FALSE WHERE username = %s",
                    (username,)
                )
                conn.commit()
                cursor.close()
                conn.close()
        except:
            pass
        
        # Supprimer du cache
        del self.users[username]
        
        return True
    
    def get_all_users(self):
        """
        Retourne la liste de tous les utilisateurs.
        
        Returns:
            list: Liste des utilisateurs
        """
        users_list = []
        for username, user_data in self.users.items():
            user_info = {
                'username': username,
                'role': user_data['role'],
                'nom': user_data['nom'],
                'email': user_data['email']
            }
            
            # Ajouter le département si disponible
            if user_data.get('dept_nom'):
                user_info['departement'] = user_data['dept_nom']
            elif user_data.get('dept_id'):
                dept_nom = self.DEPARTEMENTS.get(user_data.get('dept_id'), {}).get('nom')
                if dept_nom:
                    user_info['departement'] = dept_nom
            
            users_list.append(user_info)
        
        return users_list
    
    def get_users_by_department(self, dept_id):
        """
        Retourne la liste des utilisateurs d'un département.
        
        Args:
            dept_id (int): ID du département
            
        Returns:
            list: Liste des utilisateurs du département
        """
        users_list = []
        for username, user_data in self.users.items():
            if user_data.get('dept_id') == dept_id:
                user_info = {
                    'username': username,
                    'role': user_data['role'],
                    'nom': user_data['nom'],
                    'email': user_data['email']
                }
                
                # Ajouter le nom du département
                dept_nom = self.DEPARTEMENTS.get(dept_id, {}).get('nom')
                if dept_nom:
                    user_info['departement'] = dept_nom
                
                users_list.append(user_info)
        
        return users_list
    
    def get_department_info(self, dept_id):
        """
        Retourne les informations d'un département.
        
        Args:
            dept_id (int): ID du département
            
        Returns:
            dict: Informations du département ou None
        """
        return self.DEPARTEMENTS.get(dept_id)
    
    def get_all_departments(self):
        """
        Retourne la liste de tous les départements.
        
        Returns:
            dict: Dictionnaire des départements
        """
        return self.DEPARTEMENTS
    
    def log_login(self, username, success):
        """
        Journalise une tentative de connexion.
        
        Args:
            username (str): Nom d'utilisateur
            success (bool): True si connexion réussie
        """
        try:
            conn = self.connect_db()
            if not conn:
                return
            
            cursor = conn.cursor()
            
            # Mettre à jour la dernière connexion
            if success:
                cursor.execute("""
                    UPDATE utilisateurs 
                    SET last_login = NOW() 
                    WHERE username = %s
                """, (username,))
            
            # Journaliser la tentative (vous pourriez créer une table login_logs)
            conn.commit()
            
        except mysql.connector.Error:
            pass
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

# Fonction utilitaire pour tester l'authentification
def test_auth_system():
    """Teste le système d'authentification."""
    auth = AuthSystem()
    
    # Test d'authentification
    print("\n🔍 Test d'authentification:")
    
    # Test avec admin
    result = auth.authenticate('admin', 'admin123')
    if result:
        print(f"✅ Admin authentifié: {result}")
    else:
        print("❌ Échec authentification admin")
    
    # Test avec chef_info
    result = auth.authenticate('chef_info', 'info123')
    if result:
        print(f"✅ Chef Informatique authentifié: {result}")
        print(f"   Département: {result.get('dept_nom', 'Non spécifié')}")
    else:
        print("❌ Échec authentification chef_info")
    
    # Test avec chef_maths
    result = auth.authenticate('chef_maths', 'maths123')
    if result:
        print(f"✅ Chef Mathématiques authentifié: {result}")
        print(f"   Département: {result.get('dept_nom', 'Non spécifié')}")
    else:
        print("❌ Échec authentification chef_maths")
    
    # Test avec mauvais mot de passe
    result = auth.authenticate('admin', 'wrongpass')
    if not result:
        print("✅ Test mauvais mot de passe réussi (échec attendu)")
    
    # Liste des départements
    print("\n🎓 Liste des départements:")
    for dept_id, dept_info in auth.get_all_departments().items():
        print(f"  {dept_id}. {dept_info['nom']} ({dept_info['couleur']})")
    
    # Liste des utilisateurs par département
    print("\n👥 Utilisateurs par département:")
    for dept_id in range(1, 6):
        users = auth.get_users_by_department(dept_id)
        dept_nom = auth.DEPARTEMENTS.get(dept_id, {}).get('nom', 'Inconnu')
        print(f"  {dept_nom}: {len(users)} utilisateurs")

if __name__ == "__main__":
    test_auth_system()
    import streamlit as st
from auth import AuthSystem


