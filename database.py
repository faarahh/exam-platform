import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG
import time

class DatabaseManager:
    def __init__(self):
        self.connection = None
        self.connect()
    
    def connect(self):
        """Établir la connexion à la base de données"""
        try:
            self.connection = mysql.connector.connect(**DB_CONFIG)
            if self.connection.is_connected():
                return True
        except Error as e:
            print(f"❌ ERREUR MySQL: {e}")
            self.connection = None
        return False
    
    def execute_query(self, query, params=None, fetch=False):
        """Exécuter une requête SQL - SIMPLE ET FIABLE"""
        try:
            # Si pas de connexion, tenter de se reconnecter
            if not self.connection or not self.connection.is_connected():
                if not self.connect():
                    return [] if fetch else 0
            
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            
            if fetch:
                result = cursor.fetchall()
            else:
                self.connection.commit()
                result = cursor.rowcount
            
            cursor.close()
            return result
            
        except Error as e:
            print(f"❌ ERREUR SQL: {e}")
            # Retourner toujours une valeur sûre
            return [] if fetch else 0
    
    # ===== MÉTHODES POUR LES DÉPARTEMENTS =====
    
    def get_all_departments(self):
        """Récupérer tous les départements"""
        query = """
        SELECT id, nom, code, description, nombre_etudiants, nombre_professeurs, couleur, chef_nom
        FROM departments
        ORDER BY nom
        """
        return self.execute_query(query, fetch=True)
    
    def get_department_by_id(self, dept_id):
        """Récupérer un département par son ID"""
        query = """
        SELECT id, nom, code, description, nombre_etudiants, nombre_professeurs, couleur, chef_nom, chef_email
        FROM departments
        WHERE id = %s
        """
        result = self.execute_query(query, (dept_id,), fetch=True)
        return result[0] if result and len(result) > 0 else None
    
    def get_department_statistics(self, dept_id):
        """Récupérer les statistiques d'un département"""
        query = """
        SELECT 
            d.nom as departement,
            d.nombre_etudiants,
            d.nombre_professeurs,
            COUNT(DISTINCT f.id) as nb_formations,
            COUNT(DISTINCT m.id) as nb_modules,
            COUNT(DISTINCT e.id) as nb_examens
        FROM departments d
        LEFT JOIN formations f ON d.id = f.dept_id
        LEFT JOIN modules m ON f.id = m.formation_id
        LEFT JOIN examens e ON m.id = e.module_id
        WHERE d.id = %s
        GROUP BY d.id, d.nom, d.nombre_etudiants, d.nombre_professeurs
        """
        result = self.execute_query(query, (dept_id,), fetch=True)
        return result[0] if result and len(result) > 0 else {
            'departement': f'Département {dept_id}',
            'nombre_etudiants': 0,
            'nombre_professeurs': 0,
            'nb_formations': 0,
            'nb_modules': 0,
            'nb_examens': 0
        }
    
    def get_modules_by_department(self, dept_id):
        """Récupérer les modules d'un département"""
        query = """
        SELECT m.id, m.nom, f.nom as formation, COUNT(i.etudiant_id) as nb_etudiants
        FROM modules m
        JOIN formations f ON m.formation_id = f.id
        LEFT JOIN inscriptions i ON m.id = i.module_id
        WHERE f.dept_id = %s
        GROUP BY m.id, m.nom, f.nom
        ORDER BY nb_etudiants DESC
        """
        return self.execute_query(query, (dept_id,), fetch=True)
    
    def get_exams_by_department(self, dept_id, start_date=None, end_date=None):
        """Récupérer les examens d'un département"""
        base_query = """
        SELECT 
            e.id,
            m.nom as module,
            CONCAT(p.nom, ' ', p.prenom) as professeur,
            s.nom as salle,
            e.date_exam,
            e.heure,
            e.duree
        FROM examens e
        JOIN modules m ON e.module_id = m.id
        JOIN formations f ON m.formation_id = f.id
        JOIN professeurs p ON e.prof_id = p.id
        JOIN salles s ON e.salle_id = s.id
        WHERE f.dept_id = %s
        """
        
        params = [dept_id]
        
        if start_date and end_date:
            base_query += " AND e.date_exam BETWEEN %s AND %s"
            params.extend([start_date, end_date])
        
        base_query += " ORDER BY e.date_exam, e.heure"
        
        return self.execute_query(base_query, tuple(params), fetch=True)
    
    def get_department_conflicts(self, dept_id):
        """Détecter les conflits dans un département"""
        # Conflits étudiants par département
        query = """
        SELECT 
            CONCAT(e.nom, ' ', e.prenom) as etudiant,
            ex.date_exam,
            COUNT(*) as nb_examens
        FROM etudiants e
        JOIN inscriptions i ON e.id = i.etudiant_id
        JOIN examens ex ON i.module_id = ex.module_id
        JOIN modules m ON ex.module_id = m.id
        JOIN formations f ON m.formation_id = f.id
        WHERE f.dept_id = %s
        GROUP BY e.id, e.nom, e.prenom, ex.date_exam
        HAVING COUNT(*) > 1
        ORDER BY COUNT(*) DESC
        """
        return self.execute_query(query, (dept_id,), fetch=True)
    
    def get_all_departments_stats(self):
        """Récupérer les statistiques pour tous les départements"""
        query = """
        SELECT 
            d.id,
            d.nom,
            d.code,
            d.couleur,
            d.nombre_etudiants,
            d.nombre_professeurs,
            COUNT(DISTINCT f.id) as nb_formations,
            COUNT(DISTINCT m.id) as nb_modules,
            COUNT(DISTINCT ex.id) as nb_examens
        FROM departments d
        LEFT JOIN formations f ON d.id = f.dept_id
        LEFT JOIN modules m ON f.id = m.formation_id
        LEFT JOIN examens ex ON m.id = ex.module_id
        GROUP BY d.id, d.nom, d.code, d.couleur, d.nombre_etudiants, d.nombre_professeurs
        ORDER BY d.nom
        """
        return self.execute_query(query, fetch=True)
    
    # ===== MÉTHODES CRITIQUES POUR LE SCHEDULER =====
    
    def get_all_modules(self):
        """Récupérer tous les modules - MÉTHODE ESSENTIELLE"""
        query = """
        SELECT 
            m.id, 
            m.nom, 
            f.nom as formation,
            d.nom as departement,
            d.id as dept_id,
            COUNT(i.etudiant_id) as nb_etudiants
        FROM modules m
        JOIN formations f ON m.formation_id = f.id
        JOIN departments d ON f.dept_id = d.id
        LEFT JOIN inscriptions i ON m.id = i.module_id
        GROUP BY m.id, m.nom, f.nom, d.nom, d.id
        ORDER BY nb_etudiants DESC
        """
        return self.execute_query(query, fetch=True)
    
    def get_students_by_module(self, module_id):
        """Récupérer les étudiants inscrits à un module"""
        query = """
        SELECT e.id, e.nom, e.prenom, e.formation_id
        FROM etudiants e
        JOIN inscriptions i ON e.id = i.etudiant_id
        WHERE i.module_id = %s
        """
        return self.execute_query(query, (module_id,), fetch=True)
    
    def get_available_rooms(self, date_exam, heure, capacite_min):
        """Récupérer les salles disponibles pour un créneau"""
        query = """
        SELECT s.id, s.nom, s.capacite, s.type
        FROM salles s
        WHERE s.disponibilite = TRUE 
        AND s.capacite >= %s
        AND s.id NOT IN (
            SELECT salle_id 
            FROM examens 
            WHERE date_exam = %s 
            AND heure = %s
        )
        ORDER BY s.capacite
        """
        return self.execute_query(query, (capacite_min, date_exam, heure), fetch=True)
    
    def get_professor_load(self, prof_id, date_exam):
        """Vérifier la charge d'un professeur pour une date"""
        query = """
        SELECT COUNT(*) as nb_examens
        FROM examens
        WHERE prof_id = %s AND date_exam = %s
        """
        result = self.execute_query(query, (prof_id, date_exam), fetch=True)
        return result[0]['nb_examens'] if result and len(result) > 0 else 0
    
    def check_student_conflict(self, student_id, date_exam):
        """Vérifier si un étudiant a déjà un examen à cette date"""
        query = """
        SELECT COUNT(*) as nb_examens
        FROM examens e
        JOIN inscriptions i ON e.module_id = i.module_id
        WHERE i.etudiant_id = %s AND e.date_exam = %s
        """
        result = self.execute_query(query, (student_id, date_exam), fetch=True)
        return result[0]['nb_examens'] > 0 if result and len(result) > 0 else False
    
    def insert_exam(self, module_id, prof_id, salle_id, date_exam, heure, duree=90):
        """Insérer un nouvel examen"""
        query = """
        INSERT INTO examens (module_id, prof_id, salle_id, date_exam, heure, duree)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        return self.execute_query(query, (module_id, prof_id, salle_id, date_exam, heure, duree))
    
    # ===== MÉTHODES POUR L'INTERFACE =====
    
    def get_all_exams(self, dept_id=None, start_date=None, end_date=None):
        """Récupérer tous les examens planifiés avec filtre optionnel par département"""
        if dept_id:
            # Version avec filtre département
            base_query = """
            SELECT 
                e.id,
                m.nom as module,
                CONCAT(p.nom, ' ', p.prenom) as professeur,
                s.nom as salle,
                d.nom as departement,
                e.date_exam,
                e.heure,
                e.duree
            FROM examens e
            JOIN modules m ON e.module_id = m.id
            JOIN formations f ON m.formation_id = f.id
            JOIN departments d ON f.dept_id = d.id
            JOIN professeurs p ON e.prof_id = p.id
            JOIN salles s ON e.salle_id = s.id
            WHERE d.id = %s
            """
            
            params = [dept_id]
            
            if start_date:
                base_query += " AND e.date_exam >= %s"
                params.append(start_date)
            
            if end_date:
                base_query += " AND e.date_exam <= %s"
                params.append(end_date)
            
            base_query += " ORDER BY e.date_exam, e.heure"
            
            return self.execute_query(base_query, tuple(params), fetch=True)
        else:
            # Version sans filtre (tous les examens)
            query = """
            SELECT 
                e.id,
                m.nom as module,
                CONCAT(p.nom, ' ', p.prenom) as professeur,
                s.nom as salle,
                d.nom as departement,
                e.date_exam,
                e.heure,
                e.duree
            FROM examens e
            JOIN modules m ON e.module_id = m.id
            JOIN formations f ON m.formation_id = f.id
            JOIN departments d ON f.dept_id = d.id
            JOIN professeurs p ON e.prof_id = p.id
            JOIN salles s ON e.salle_id = s.id
            ORDER BY e.date_exam, e.heure, d.nom
            """
            return self.execute_query(query, fetch=True)
    
    def detect_conflicts(self, dept_id=None):
        """Détecter les conflits d'emploi du temps"""
        # Conflits étudiants
        if dept_id:
            query_students = """
            SELECT 
                e.id as etudiant_id,
                CONCAT(e.nom, ' ', e.prenom) as etudiant,
                ex.date_exam,
                COUNT(DISTINCT ex.id) as nb_examens
            FROM etudiants e
            JOIN inscriptions i ON e.id = i.etudiant_id
            JOIN examens ex ON i.module_id = ex.module_id
            JOIN modules m ON ex.module_id = m.id
            JOIN formations f ON m.formation_id = f.id
            WHERE f.dept_id = %s
            GROUP BY e.id, ex.date_exam
            HAVING nb_examens > 1
            """
            student_conflicts = self.execute_query(query_students, (dept_id,), fetch=True)
        else:
            query_students = """
            SELECT 
                e.id as etudiant_id,
                CONCAT(e.nom, ' ', e.prenom) as etudiant,
                ex.date_exam,
                COUNT(DISTINCT ex.id) as nb_examens
            FROM etudiants e
            JOIN inscriptions i ON e.id = i.etudiant_id
            JOIN examens ex ON i.module_id = ex.module_id
            GROUP BY e.id, ex.date_exam
            HAVING nb_examens > 1
            """
            student_conflicts = self.execute_query(query_students, fetch=True)
        
        # Conflits professeurs
        if dept_id:
            query_profs = """
            SELECT 
                p.id as prof_id,
                CONCAT(p.nom, ' ', p.prenom) as professeur,
                ex.date_exam,
                COUNT(*) as nb_examens
            FROM professeurs p
            JOIN examens ex ON p.id = ex.prof_id
            JOIN modules m ON ex.module_id = m.id
            JOIN formations f ON m.formation_id = f.id
            WHERE f.dept_id = %s
            GROUP BY p.id, ex.date_exam
            HAVING nb_examens > 3
            """
            professor_conflicts = self.execute_query(query_profs, (dept_id,), fetch=True)
        else:
            query_profs = """
            SELECT 
                p.id as prof_id,
                CONCAT(p.nom, ' ', p.prenom) as professeur,
                ex.date_exam,
                COUNT(*) as nb_examens
            FROM professeurs p
            JOIN examens ex ON p.id = ex.prof_id
            GROUP BY p.id, ex.date_exam
            HAVING nb_examens > 3
            """
            professor_conflicts = self.execute_query(query_profs, fetch=True)
        
        return {
            'student_conflicts': student_conflicts if isinstance(student_conflicts, list) else [],
            'professor_conflicts': professor_conflicts if isinstance(professor_conflicts, list) else []
        }
    
    def get_statistics(self, dept_id=None):
        """Récupérer les statistiques globales ou par département"""
        if dept_id:
            # Statistiques par département
            query = """
            SELECT 
                d.nom as departement,
                d.nombre_etudiants as total_etudiants,
                d.nombre_professeurs as total_professeurs,
                COUNT(DISTINCT f.id) as total_formations,
                COUNT(DISTINCT m.id) as total_modules,
                COUNT(DISTINCT e.id) as examens_planifies,
                COUNT(DISTINCT e.date_exam) as jours_examens
            FROM departments d
            LEFT JOIN formations f ON d.id = f.dept_id
            LEFT JOIN modules m ON f.id = m.formation_id
            LEFT JOIN examens e ON m.id = e.module_id
            WHERE d.id = %s
            GROUP BY d.id, d.nom, d.nombre_etudiants, d.nombre_professeurs
            """
            result = self.execute_query(query, (dept_id,), fetch=True)
        else:
            # Statistiques globales
            query = """
            SELECT 
                (SELECT COUNT(*) FROM etudiants) as total_etudiants,
                (SELECT COUNT(*) FROM professeurs) as total_professeurs,
                (SELECT COUNT(*) FROM salles) as total_salles,
                (SELECT COUNT(*) FROM modules) as total_modules,
                (SELECT COUNT(*) FROM examens) as examens_planifies,
                (SELECT COUNT(DISTINCT date_exam) FROM examens) as jours_examens
            """
            result = self.execute_query(query, fetch=True)
        
        # Retourner un dictionnaire par défaut si pas de résultat
        if result and len(result) > 0:
            return result
        else:
            default_stats = {
                'total_etudiants': 0,
                'total_professeurs': 0,
                'total_salles': 0,
                'total_modules': 0,
                'examens_planifies': 0,
                'jours_examens': 0
            }
            if dept_id:
                default_stats['departement'] = f"Département {dept_id}"
                default_stats['total_formations'] = 0
            return [default_stats]
    
    def get_available_professors(self, date_exam, dept_id=None):
        """Récupérer les professeurs disponibles pour une date"""
        if dept_id:
            query = """
            SELECT p.id, p.nom, p.prenom,
                   (SELECT COUNT(*) FROM examens WHERE prof_id = p.id AND date_exam = %s) as current_load
            FROM professeurs p
            WHERE p.dept_id = %s
            HAVING current_load < 3
            """
            return self.execute_query(query, (date_exam, dept_id), fetch=True)
        else:
            query = """
            SELECT p.id, p.nom, p.prenom,
                   (SELECT COUNT(*) FROM examens WHERE prof_id = p.id AND date_exam = %s) as current_load
            FROM professeurs p
            HAVING current_load < 3
            """
            return self.execute_query(query, (date_exam,), fetch=True)
    
    # ===== MÉTHODES DE TEST ET VÉRIFICATION =====
    
    def test_connection(self):
        """Tester la connexion"""
        try:
            result = self.execute_query("SELECT 1 as test", fetch=True)
            return result and len(result) > 0
        except:
            return False
    
    def get_table_info(self):
        """Obtenir des infos sur toutes les tables"""
        tables = ['etudiants', 'professeurs', 'salles', 'modules', 'examens', 'inscriptions', 'departments', 'formations']
        info = {}
        
        for table in tables:
            result = self.execute_query(f"SELECT COUNT(*) as count FROM {table}", fetch=True)
            info[table] = result[0]['count'] if result and len(result) > 0 else 0
        
        return info
    
    def check_tables_exist(self):
        """Vérifier si toutes les tables nécessaires existent"""
        required_tables = ['departments', 'etudiants', 'professeurs', 'salles', 'modules', 'examens', 'inscriptions']
        existing_tables = []
        missing_tables = []
        
        for table in required_tables:
            try:
                result = self.execute_query(f"SELECT 1 FROM {table} LIMIT 1", fetch=True)
                if result is not None:
                    existing_tables.append(table)
                else:
                    missing_tables.append(table)
            except:
                missing_tables.append(table)
        
        return existing_tables, missing_tables

# ===== TEST SI EXÉCUTÉ DIRECTEMENT =====
if __name__ == "__main__":
    print("🧪 Test de la classe DatabaseManager...")
    db = DatabaseManager()
    
    if db.test_connection():
        print("✅ Connexion OK")
        
        # Vérifier les tables
        existing, missing = db.check_tables_exist()
        print(f"\n📋 Tables existantes: {len(existing)}")
        for table in existing:
            print(f"  ✅ {table}")
        
        if missing:
            print(f"\n⚠️ Tables manquantes: {len(missing)}")
            for table in missing:
                print(f"  ❌ {table}")
        else:
            print("\n✅ Toutes les tables existent")
        
        # Tester les méthodes départementales
        print("\n🎓 Test des méthodes départementales:")
        
        # 1. Liste des départements
        depts = db.get_all_departments()
        if depts:
            print(f"✅ {len(depts)} départements trouvés:")
            for dept in depts[:5]:  # Afficher les 5 premiers
                print(f"   {dept['id']}. {dept['nom']} ({dept.get('code', 'N/A')}) - {dept.get('nombre_etudiants', 0)} étudiants")
        else:
            print("❌ Aucun département trouvé")
            print("   Essayez d'exécuter init_db.py pour créer les départements")
        
        # 2. Statistiques par département
        print("\n📊 Statistiques par département:")
        all_stats = db.get_all_departments_stats()
        if all_stats:
            for stats in all_stats:
                print(f"   {stats['nom']}: {stats['nb_examens']} examens, {stats['nb_formations']} formations, {stats['nombre_etudiants']} étudiants")
        else:
            print("   Aucune statistique disponible")
            
        # 3. Table info
        print("\n📋 Contenu de la base:")
        info = db.get_table_info()
        for table, count in info.items():
            print(f"   {table}: {count}")
            
        # 4. Tester get_all_modules
        print("\n🔍 Test de get_all_modules():")
        modules = db.get_all_modules()
        if modules:
            print(f"  ✅ {len(modules)} modules trouvés")
            for i, module in enumerate(modules[:3]):  # Afficher les 3 premiers
                dept = module.get('departement', 'Non spécifié')
                print(f"     {i+1}. {module['nom']} ({dept}) - {module['nb_etudiants']} étudiants")
        else:
            print("  ❌ Aucun module trouvé")
            
    else:
        print("❌ Échec de connexion")
        print("\nVérifiez:")
        print("1. MySQL est démarré (XAMPP > Start MySQL)")
        print("2. Le fichier config.py contient:")
        print("   DB_CONFIG = {")
        print("       'host': 'localhost',")
        print("       'user': 'root',")
        print("       'password': '',")
        print("       'database': 'exam_planning_db'")
        print("   }")
        print("\3. La base de données 'exam_planning_db' existe")