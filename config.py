import os
from datetime import datetime

# ====================
# CONFIGURATION DE LA BASE DE DONNÉES
# ====================

# Configuration principale (développement)
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # Mettre votre mot de passe MySQL
    'database': 'exam_planning_db',
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_unicode_ci',
    'port': 3306,  # Port MySQL par défaut
    'autocommit': True,  # Validation automatique des transactions
    'buffered': True,  # Résultats en mémoire pour éviter les erreurs de non-consommation
}

# Configuration alternative pour différents environnements
DB_CONFIGS = {
    'development': DB_CONFIG,
    'production': {
        'host': 'localhost',
        'user': 'exam_user',
        'password': 'SecurePassword123!',
        'database': 'exam_planning_prod',
        'charset': 'utf8mb4',
        'collation': 'utf8mb4_unicode_ci',
        'port': 3306,
    },
    'testing': {
        'host': 'localhost',
        'user': 'test_user',
        'password': 'test123',
        'database': 'exam_planning_test',
        'charset': 'utf8mb4',
        'collation': 'utf8mb4_unicode_ci',
        'port': 3306,
    }
}

# ====================
# CONFIGURATION DES DÉPARTEMENTS (NOUVEAU)
# ====================

# Configuration des 5 départements
DEPARTMENTS_CONFIG = {
    1: {
        'id': 1,
        'nom': 'Informatique',
        'code': 'INFO',
        'description': 'Département d\'Informatique et Génie Logiciel',
        'formations': [
            'LICENCE Informatique',
            'LICENCE MIAGE',
            'MASTER Intelligence Artificielle',
            'MASTER Cybersécurité',
            'MASTER Génie Logiciel'
        ],
        'couleur': '#4CC9F0',
        'couleur_foncee': '#3A9DC7',
        'nombre_etudiants': 320,
        'nombre_professeurs': 25,
        'salles_principales': ['Amphi A', 'Lab Info 1', 'Lab Info 2', 'Salle B201', 'Salle B202'],
        'chef_nom': 'Sophie Martin',
        'chef_email': 'chef.info@univ.fr'
    },
    2: {
        'id': 2,
        'nom': 'Mathématiques',
        'code': 'MATH',
        'description': 'Département de Mathématiques et Applications',
        'formations': [
            'LICENCE Mathématiques',
            'MASTER Mathématiques Appliquées',
            'MASTER Statistiques',
            'MASTER Recherche Opérationnelle'
        ],
        'couleur': '#F72585',
        'couleur_foncee': '#C51B6A',
        'nombre_etudiants': 250,
        'nombre_professeurs': 20,
        'salles_principales': ['Amphi B', 'Salle C101', 'Salle C102', 'Salle C103'],
        'chef_nom': 'Pierre Leroy',
        'chef_email': 'chef.maths@univ.fr'
    },
    3: {
        'id': 3,
        'nom': 'Physique',
        'code': 'PHYS',
        'description': 'Département de Physique et Sciences de la Matière',
        'formations': [
            'LICENCE Physique',
            'MASTER Physique Quantique',
            'MASTER Astrophysique',
            'MASTER Physique des Matériaux'
        ],
        'couleur': '#7209B7',
        'couleur_foncee': '#5A078F',
        'nombre_etudiants': 180,
        'nombre_professeurs': 18,
        'salles_principales': ['Amphi C', 'Lab Physique 1', 'Lab Physique 2', 'Salle D201'],
        'chef_nom': 'Marie Curie',
        'chef_email': 'chef.physique@univ.fr'
    },
    4: {
        'id': 4,
        'nom': 'Chimie',
        'code': 'CHIM',
        'description': 'Département de Chimie et Sciences Moléculaires',
        'formations': [
            'LICENCE Chimie',
            'MASTER Chimie Organique',
            'MASTER Biochimie',
            'MASTER Chimie Analytique'
        ],
        'couleur': '#3A0CA3',
        'couleur_foncee': '#2E0A82',
        'nombre_etudiants': 150,
        'nombre_professeurs': 15,
        'salles_principales': ['Amphi D', 'Lab Chimie 1', 'Lab Chimie 2', 'Salle E101'],
        'chef_nom': 'Antoine Lavoisier',
        'chef_email': 'chef.chimie@univ.fr'
    },
    5: {
        'id': 5,
        'nom': 'Biologie',
        'code': 'BIO',
        'description': 'Département de Biologie et Sciences du Vivant',
        'formations': [
            'LICENCE Biologie',
            'MASTER Biologie Moléculaire',
            'MASTER Écologie',
            'MASTER Microbiologie'
        ],
        'couleur': '#4361EE',
        'couleur_foncee': '#354FC7',
        'nombre_etudiants': 140,
        'nombre_professeurs': 14,
        'salles_principales': ['Amphi E', 'Lab Bio 1', 'Lab Bio 2', 'Salle F201'],
        'chef_nom': 'Louis Pasteur',
        'chef_email': 'chef.bio@univ.fr'
    }
}

# Configuration des utilisateurs de démonstration par département
DEMO_USERS_CONFIG = {
    # Administrateurs
    'admin': {
        'username': 'admin',
        'password': 'admin123',
        'role': 'admin',
        'nom': 'Administrateur Système',
        'email': 'admin@univ.fr'
    },
    'vicedoyen': {
        'username': 'vicedoyen',
        'password': 'doyen123',
        'role': 'vicedoyen',
        'nom': 'Jean Dupont',
        'email': 'vicedoyen@univ.fr'
    },
    
    # Chefs de département
    'chef_info': {
        'username': 'chef_info',
        'password': 'info123',
        'role': 'chef_dept',
        'nom': 'Sophie Martin',
        'email': 'chef.info@univ.fr',
        'dept_id': 1,
        'dept_nom': 'Informatique'
    },
    'chef_maths': {
        'username': 'chef_maths',
        'password': 'maths123',
        'role': 'chef_dept',
        'nom': 'Pierre Leroy',
        'email': 'chef.maths@univ.fr',
        'dept_id': 2,
        'dept_nom': 'Mathématiques'
    },
    'chef_physique': {
        'username': 'chef_physique',
        'password': 'physique123',
        'role': 'chef_dept',
        'nom': 'Marie Curie',
        'email': 'chef.physique@univ.fr',
        'dept_id': 3,
        'dept_nom': 'Physique'
    },
    'chef_chimie': {
        'username': 'chef_chimie',
        'password': 'chimie123',
        'role': 'chef_dept',
        'nom': 'Antoine Lavoisier',
        'email': 'chef.chimie@univ.fr',
        'dept_id': 4,
        'dept_nom': 'Chimie'
    },
    'chef_bio': {
        'username': 'chef_bio',
        'password': 'bio123',
        'role': 'chef_dept',
        'nom': 'Louis Pasteur',
        'email': 'chef.bio@univ.fr',
        'dept_id': 5,
        'dept_nom': 'Biologie'
    },
    
    # Professeurs (un par département)
    'prof_info': {
        'username': 'prof_info',
        'password': 'prof123',
        'role': 'professeur',
        'nom': 'Alami Ahmed',
        'email': 'ahmed.alami@univ.fr',
        'prof_id': 1,
        'dept_id': 1,
        'dept_nom': 'Informatique'
    },
    'prof_maths': {
        'username': 'prof_maths',
        'password': 'prof123',
        'role': 'professeur',
        'nom': 'Khalid Benjelloun',
        'email': 'khalid.benjelloun@univ.fr',
        'prof_id': 2,
        'dept_id': 2,
        'dept_nom': 'Mathématiques'
    },
    
    # Étudiants (un par département)
    'etudiant_info': {
        'username': 'etudiant_info',
        'password': 'etu123',
        'role': 'etudiant',
        'nom': 'Hafidi Aicha',
        'email': 'aicha.hafidi@etu.univ.fr',
        'etudiant_id': 1,
        'dept_id': 1,
        'dept_nom': 'Informatique'
    },
    'etudiant_maths': {
        'username': 'etudiant_maths',
        'password': 'etu123',
        'role': 'etudiant',
        'nom': 'Karim Alami',
        'email': 'karim.alami@etu.univ.fr',
        'etudiant_id': 2,
        'dept_id': 2,
        'dept_nom': 'Mathématiques'
    }
}

# ====================
# CONFIGURATION DE PLANIFICATION
# ====================

# Dates par défaut (prochaine session d'examens)
default_start_date = datetime.now().replace(day=1, month=6 if datetime.now().month < 6 else 1)
if datetime.now().month >= 6:
    default_start_date = default_start_date.replace(year=datetime.now().year + 1)

default_end_date = default_start_date.replace(day=30)

PLANNING_CONFIG = {
    # Dates
    'start_date': default_start_date.strftime('%Y-%m-%d'),
    'end_date': default_end_date.strftime('%Y-%m-%d'),
    
    # Durées
    'exam_duration': 90,  # minutes
    'short_exam_duration': 60,  # pour les QCM
    'long_exam_duration': 180,  # pour les examens pratiques
    
    # Horaires
    'exam_start_hours': ['08:30', '10:30', '14:00', '16:00'],
    'morning_slots': ['08:30', '10:30'],
    'afternoon_slots': ['14:00', '16:00'],
    
    # Contraintes étudiantes
    'max_exams_per_day_student': 1,
    'min_days_between_exams': 0,
    'max_consecutive_exams': 2,
    
    # Contraintes professeurs
    'max_exams_per_day_prof': 3,
    'max_hours_per_day_prof': 6,
    'max_exams_per_week_prof': 10,
    
    # Contraintes salles
    'min_room_capacity_margin': 0.1,  # 10% de marge
    'max_room_usage_per_day': 4,  # max 4 examens par salle par jour
    
    # Algorithmes
    'default_algorithm': 'greedy',
    'available_algorithms': ['greedy', 'backtracking', 'genetic', 'manual'],
    
    # Priorités
    'priorities': {
        'student_conflicts': 10,  # Priorité maximale
        'room_capacity': 8,
        'professor_workload': 6,
        'consecutive_exams': 4,
        'room_optimization': 2,
    },
    
    # Configuration par département
    'departments': DEPARTMENTS_CONFIG
}

# ====================
# CONFIGURATION DE L'APPLICATION
# ====================

APP_CONFIG = {
    'name': 'EDT Examens Master',
    'version': '1.0.0',
    'author': 'Université XYZ',
    'debug': True,  # Mettre à False en production
    'secret_key': 'votre_clé_secrète_pour_les_sessions',  # À changer en production
    'session_timeout': 3600,  # 1 heure en secondes
    'max_login_attempts': 5,
    'password_min_length': 8,
    'available_departments': list(DEPARTMENTS_CONFIG.keys()),
    'departments_info': DEPARTMENTS_CONFIG,
    'demo_users': DEMO_USERS_CONFIG
}

# ====================
# CONFIGURATION DES RÔLES ET PERMISSIONS
# ====================

ROLES_CONFIG = {
    'admin': {
        'display_name': 'Administrateur',
        'permissions': [
            'view_global_dashboard', 'validate_edt', 'view_all_stats', 'export_reports',
            'generate_edt', 'detect_conflicts', 'optimize_resources', 'manage_exams',
            'manage_users', 'view_all_departments'
        ],
        'dashboard_access': 'global',
        'department_access': 'all'  # Accès à tous les départements
    },
    'vicedoyen': {
        'display_name': 'Vice-Doyen/Doyen',
        'permissions': [
            'view_global_dashboard', 'validate_edt', 'view_all_stats', 'export_reports',
            'view_department_stats', 'filter_by_department'
        ],
        'dashboard_access': 'global',
        'department_access': 'all'  # Accès à tous les départements
    },
    'chef_dept': {
        'display_name': 'Chef de Département',
        'permissions': [
            'view_department_dashboard', 'validate_department_edt', 'view_department_stats',
            'export_department_reports', 'manage_department_exams'
        ],
        'dashboard_access': 'department',
        'department_access': 'own'  # Accès uniquement à son département
    },
    'professeur': {
        'display_name': 'Professeur',
        'permissions': [
            'view_personal_schedule', 'view_surveillance', 'export_calendar',
            'view_department_calendar', 'filter_by_department'
        ],
        'dashboard_access': 'personal',
        'department_access': 'own'  # Accès uniquement à son département
    },
    'etudiant': {
        'display_name': 'Étudiant',
        'permissions': [
            'view_personal_schedule', 'search_exams', 'export_calendar',
            'view_department_exams', 'filter_by_department'
        ],
        'dashboard_access': 'personal',
        'department_access': 'own'  # Accès uniquement à son département
    }
}

# ====================
# CHEMINS DES FICHIERS
# ====================

# Chemins absolus
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = os.path.join(BASE_DIR, 'backend')
FRONTEND_DIR = os.path.join(BASE_DIR, 'frontend')
DATA_DIR = os.path.join(BASE_DIR, 'data')
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
EXPORTS_DIR = os.path.join(BASE_DIR, 'exports')
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
DEPARTMENTS_DATA_DIR = os.path.join(DATA_DIR, 'departments')

# Fichiers spécifiques
USERS_FILE = os.path.join(DATA_DIR, 'users.json')
LOGS_FILE = os.path.join(LOGS_DIR, 'app.log')
SQL_SCHEMA_FILE = os.path.join(BACKEND_DIR, 'database', 'schema.sql')
DEMO_DATA_FILE = os.path.join(DATA_DIR, 'demo_data.json')
CONFIG_FILE = os.path.join(BACKEND_DIR, 'config.py')

# Fichiers par département
for dept_id in DEPARTMENTS_CONFIG:
    dept_dir = os.path.join(DEPARTMENTS_DATA_DIR, str(dept_id))
    os.makedirs(dept_dir, exist_ok=True)

# ====================
# CONFIGURATION DES LOGS
# ====================

LOG_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'detailed': {
            'format': '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
            'level': 'INFO'
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_FILE,
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'formatter': 'detailed',
            'level': 'DEBUG'
        },
        'department_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOGS_DIR, 'departments.log'),
            'maxBytes': 5242880,  # 5MB
            'backupCount': 3,
            'formatter': 'detailed',
            'level': 'INFO'
        }
    },
    'loggers': {
        '': {  # Root logger
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True
        },
        'database': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': False
        },
        'auth': {
            'handlers': ['file'],
            'level': 'WARNING',
            'propagate': False
        },
        'departments': {
            'handlers': ['department_file'],
            'level': 'INFO',
            'propagate': False
        }
    }
}

# ====================
# CONFIGURATION DES EXPORTS
# ====================

EXPORT_CONFIG = {
    'formats': {
        'pdf': {
            'enabled': True,
            'default_orientation': 'landscape',
            'margins': [10, 10, 10, 10],  # mm
        },
        'excel': {
            'enabled': True,
            'include_charts': True,
        },
        'ical': {
            'enabled': True,
            'timezone': 'Europe/Paris',
        },
        'json': {
            'enabled': True,
            'pretty_print': True,
        }
    },
    'default_format': 'pdf',
    'retention_days': 30,  # Fichiers gardés pendant 30 jours
    'department_exports': {
        'enabled': True,
        'separate_files': True,  # Fichiers séparés par département
        'include_stats': True,   # Inclure les statistiques par département
    }
}

# ====================
# FONCTIONS UTILITAIRES (NOUVELLES)
# ====================

def get_department_config(dept_id):
    """
    Récupère la configuration d'un département.
    
    Args:
        dept_id (int): ID du département
        
    Returns:
        dict: Configuration du département ou None
    """
    return DEPARTMENTS_CONFIG.get(dept_id)

def get_department_by_name(dept_name):
    """
    Récupère la configuration d'un département par son nom.
    
    Args:
        dept_name (str): Nom du département
        
    Returns:
        dict: Configuration du département ou None
    """
    for dept_id, config in DEPARTMENTS_CONFIG.items():
        if config['nom'].lower() == dept_name.lower():
            return config
    return None

def get_all_departments():
    """
    Retourne la liste de tous les départements.
    
    Returns:
        list: Liste des configurations de départements
    """
    return list(DEPARTMENTS_CONFIG.values())

def get_department_color(dept_id):
    """
    Récupère la couleur d'un département.
    
    Args:
        dept_id (int): ID du département
        
    Returns:
        str: Code couleur hexadécimal ou couleur par défaut
    """
    dept = get_department_config(dept_id)
    if dept and 'couleur' in dept:
        return dept['couleur']
    return '#808080'  # Gris par défaut

def get_department_demo_users():
    """
    Retourne la liste des utilisateurs de démonstration par département.
    
    Returns:
        dict: Dictionnaire des utilisateurs de démo par département
    """
    dept_users = {}
    for dept_id in DEPARTMENTS_CONFIG:
        dept_users[dept_id] = []
        for username, user_config in DEMO_USERS_CONFIG.items():
            if user_config.get('dept_id') == dept_id:
                dept_users[dept_id].append({
                    'username': username,
                    'role': user_config['role'],
                    'nom': user_config['nom']
                })
    return dept_users

def get_database_config(env='development'):
    """
    Récupère la configuration de la base de données pour un environnement donné.
    
    Args:
        env (str): Environnement ('development', 'production', 'testing')
    
    Returns:
        dict: Configuration de la base de données
    """
    return DB_CONFIGS.get(env, DB_CONFIGS['development'])

def create_directories():
    """
    Crée tous les répertoires nécessaires s'ils n'existent pas.
    """
    directories = [DATA_DIR, LOGS_DIR, EXPORTS_DIR, DEPARTMENTS_DATA_DIR]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ Répertoire créé/vérifié: {directory}")
    
    # Créer les sous-répertoires pour chaque département
    for dept_id in DEPARTMENTS_CONFIG:
        dept_dir = os.path.join(DEPARTMENTS_DATA_DIR, str(dept_id))
        os.makedirs(dept_dir, exist_ok=True)

def get_current_academic_year():
    """
    Retourne l'année académique actuelle au format '2024-2025'.
    
    Returns:
        str: Année académique
    """
    now = datetime.now()
    current_year = now.year
    
    # Si nous sommes après août, l'année académique commence
    if now.month >= 9:
        return f"{current_year}-{current_year + 1}"
    else:
        return f"{current_year - 1}-{current_year}"

def get_next_exam_session():
    """
    Retourne les dates de la prochaine session d'examens.
    
    Returns:
        tuple: (date_debut, date_fin)
    """
    now = datetime.now()
    
    # Sessions prédéfinies (janvier et juin)
    sessions = [
        (datetime(now.year, 1, 10), datetime(now.year, 1, 31)),
        (datetime(now.year, 6, 10), datetime(now.year, 6, 30))
    ]
    
    # Trouver la prochaine session
    for start, end in sessions:
        if now < end:
            return start, end
    
    # Si toutes les sessions sont passées, prendre la première de l'année suivante
    return datetime(now.year + 1, 1, 10), datetime(now.year + 1, 1, 31)

def get_department_statistics(dept_id=None):
    """
    Retourne les statistiques pour un département ou tous les départements.
    
    Args:
        dept_id (int, optional): ID du département spécifique
        
    Returns:
        dict: Statistiques des départements
    """
    if dept_id:
        dept = get_department_config(dept_id)
        if not dept:
            return {}
        
        return {
            'departement': dept['nom'],
            'etudiants': dept['nombre_etudiants'],
            'professeurs': dept['nombre_professeurs'],
            'formations': len(dept['formations']),
            'salles': len(dept['salles_principales']),
            'chef': dept['chef_nom']
        }
    else:
        stats = []
        for dept_id, dept in DEPARTMENTS_CONFIG.items():
            stats.append({
                'id': dept_id,
                'departement': dept['nom'],
                'etudiants': dept['nombre_etudiants'],
                'professeurs': dept['nombre_professeurs'],
                'formations': len(dept['formations']),
                'salles': len(dept['salles_principales']),
                'chef': dept['chef_nom'],
                'couleur': dept['couleur']
            })
        return stats

# ====================
# INITIALISATION
# ====================

# Créer les répertoires au démarrage
create_directories()

# Informations de debug
if APP_CONFIG['debug']:
    print(f"=== CONFIGURATION CHARGÉE ===")
    print(f"Application: {APP_CONFIG['name']} v{APP_CONFIG['version']}")
    print(f"Base de données: {DB_CONFIG['database']}@{DB_CONFIG['host']}")
    print(f"Année académique: {get_current_academic_year()}")
    print(f"Nombre de départements: {len(DEPARTMENTS_CONFIG)}")
    print(f"Répertoire données: {DATA_DIR}")
    print("\n🎓 DÉPARTEMENTS CONFIGURÉS:")
    for dept_id, dept in DEPARTMENTS_CONFIG.items():
        print(f"  {dept_id}. {dept['nom']} ({dept['code']}) - {dept['nombre_etudiants']} étudiants")
    print("=" * 50)