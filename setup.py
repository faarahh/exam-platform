#!/usr/bin/env python3
"""
Script d'installation et de configuration du projet
"""

import os
import subprocess
import sys

def check_python_version():
    """Vérifier la version de Python"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 ou supérieur est requis")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} détecté")
    return True

def install_requirements():
    """Installer les dépendances"""
    print("\n📦 Installation des dépendances...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dépendances installées avec succès")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Échec de l'installation des dépendances: {e}")
        return False

def setup_database():
    """Configurer la base de données"""
    print("\n🗄️ Configuration de la base de données...")
    
    # Demander les informations de connexion MySQL
    print("\nVeuillez entrer vos informations MySQL:")
    host = input("Host (default: localhost): ") or "localhost"
    user = input("User (default: root): ") or "root"
    password = input("Password: ")
    
    # Mettre à jour la configuration
    config_content = f'''# Configuration de la base de données
DB_CONFIG = {{
    'host': '{host}',
    'user': '{user}',
    'password': '{password}',
    'database': 'exam_planning_db',
    'charset': 'utf8mb4'
}}

# Paramètres de planification
PLANNING_CONFIG = {{
    'start_date': '2024-06-01',
    'end_date': '2024-06-30',
    'exam_duration': 90,  # minutes
    'exam_start_hours': ['09:00', '14:00'],
    'max_exams_per_day_student': 1,
    'max_exams_per_day_prof': 3,
    'min_days_between_exams': 0
}}
'''
    
    with open('backend/config.py', 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    print("✅ Configuration de la base de données mise à jour")
    
    # Créer la base de données
    try:
        import mysql.connector
        
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password
        )
        cursor = conn.cursor()
        
        # Créer la base de données
        with open('database/create_database.sql', 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        for statement in sql_script.split(';'):
            if statement.strip():
                cursor.execute(statement)
        
        # Insérer les données
        with open('database/insert_data.sql', 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        for statement in sql_script.split(';'):
            if statement.strip():
                cursor.execute(statement)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ Base de données créée et remplie avec succès")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la création de la base de données: {e}")
        return False

def run_tests():
    """Exécuter les tests"""
    print("\n🧪 Exécution des tests...")
    try:
        subprocess.check_call([sys.executable, "tests/test_data.py"])
        print("✅ Tous les tests ont réussi")
        return True
    except subprocess.CalledProcessError:
        print("❌ Certains tests ont échoué")
        return False

def show_instructions():
    """Afficher les instructions d'utilisation"""
    print("\n" + "="*50)
    print("📋 INSTRUCTIONS D'UTILISATION")
    print("="*50)
    print("\n1. Lancer l'application Streamlit:")
    print("   streamlit run frontend/app.py")
    print("\n2. Accéder à l'application:")
    print("   http://localhost:8501")
    print("\n3. Structure du projet:")
    print("   - backend/: Logique métier et gestion de la base de données")
    print("   - frontend/: Interface utilisateur Streamlit")
    print("   - database/: Scripts SQL")
    print("   - tests/: Tests unitaires")
    print("\n4. Fonctionnalités principales:")
    print("   - Génération automatique des emplois du temps")
    print("   - Gestion des étudiants, professeurs, salles")
    print("   - Vérification des contraintes")
    print("   - Statistiques et rapports")
    print("\n5. Pour réinitialiser la base de données:")
    print("   Exécutez à nouveau ce script")
    print("="*50)

def main():
    """Fonction principale"""
    print("="*50)
    print("🛠️  INSTALLATION DU PROJET - PLATEFORME EDT EXAMENS")
    print("="*50)
    
    # Vérifier Python
    if not check_python_version():
        return
    
    # Installer les dépendances
    if not install_requirements():
        return
    
    # Configurer la base de données
    if not setup_database():
        return
    
    # Exécuter les tests
    run_tests()
    
    # Afficher les instructions
    show_instructions()

if __name__ == "__main__":
    main()