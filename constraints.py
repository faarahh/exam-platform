class ConstraintChecker:
    def __init__(self, db_manager):
        self.db = db_manager
    
    def check_all_constraints(self):
        """Vérifier toutes les contraintes"""
        constraints = {
            'student_daily_limit': self.check_student_daily_limit(),
            'professor_daily_limit': self.check_professor_daily_limit(),
            'room_capacity': self.check_room_capacity(),
            'room_availability': self.check_room_availability(),
            'time_slot_conflicts': self.check_time_slot_conflicts()
        }
        
        # Calculer le score de conformité
        total_checks = len(constraints)
        passed_checks = sum(1 for check in constraints.values() if check['passed'])
        constraints['compliance_score'] = (passed_checks / total_checks) * 100
        
        return constraints
    
    def check_student_daily_limit(self):
        """Vérifier qu'aucun étudiant n'a plus d'un examen par jour"""
        query = """
        SELECT e.id, CONCAT(e.nom, ' ', e.prenom) as etudiant, ex.date_exam, COUNT(*) as nb_examens
        FROM etudiants e
        JOIN inscriptions i ON e.id = i.etudiant_id
        JOIN examens ex ON i.module_id = ex.module_id
        GROUP BY e.id, ex.date_exam
        HAVING nb_examens > 1
        """
        violations = self.db.execute_query(query, fetch=True)
        
        # CORRECTION : Gestion du cas None
        if violations is None:
            violations = []
        
        violations_count = len(violations)
        
        return {
            'passed': violations_count == 0,
            'violations': violations,
            'message': f"{violations_count} étudiants ont plus d'un examen par jour" if violations_count > 0 else "OK: Aucun étudiant n'a plus d'un examen par jour"
        }
    
    def check_professor_daily_limit(self):
        """Vérifier qu'aucun professeur n'a plus de 3 examens par jour"""
        query = """
        SELECT p.id, CONCAT(p.nom, ' ', p.prenom) as professeur, ex.date_exam, COUNT(*) as nb_examens
        FROM professeurs p
        JOIN examens ex ON p.id = ex.prof_id
        GROUP BY p.id, ex.date_exam
        HAVING nb_examens > 3
        """
        violations = self.db.execute_query(query, fetch=True)
        
        # CORRECTION : Gestion du cas None
        if violations is None:
            violations = []
        
        violations_count = len(violations)
        
        return {
            'passed': violations_count == 0,
            'violations': violations,
            'message': f"{violations_count} professeurs dépassent 3 examens par jour" if violations_count > 0 else "OK: Tous les professeurs respectent la limite"
        }
    
    def check_room_capacity(self):
        """Vérifier que les salles ont la capacité suffisante"""
        query = """
        SELECT 
            e.id as examen_id,
            m.nom as module,
            s.nom as salle,
            s.capacite,
            COUNT(DISTINCT i.etudiant_id) as nb_etudiants,
            s.capacite - COUNT(DISTINCT i.etudiant_id) as surplus
        FROM examens e
        JOIN modules m ON e.module_id = m.id
        JOIN salles s ON e.salle_id = s.id
        LEFT JOIN inscriptions i ON m.id = i.module_id
        GROUP BY e.id
        HAVING nb_etudiants > s.capacite
        """
        violations = self.db.execute_query(query, fetch=True)
        
        # CORRECTION : Gestion du cas None
        if violations is None:
            violations = []
        
        violations_count = len(violations)
        
        return {
            'passed': violations_count == 0,
            'violations': violations,
            'message': f"{violations_count} salles sont surchargées" if violations_count > 0 else "OK: Toutes les salles respectent leur capacité"
        }
    
    def check_room_availability(self):
        """Vérifier qu'une salle n'est pas utilisée deux fois au même moment"""
        query = """
        SELECT s.nom, e1.date_exam, e1.heure, COUNT(*) as nb_utilisations
        FROM examens e1
        JOIN salles s ON e1.salle_id = s.id
        GROUP BY s.id, e1.date_exam, e1.heure
        HAVING nb_utilisations > 1
        """
        violations = self.db.execute_query(query, fetch=True)
        
        # CORRECTION : Gestion du cas None
        if violations is None:
            violations = []
        
        violations_count = len(violations)
        
        return {
            'passed': violations_count == 0,
            'violations': violations,
            'message': f"{violations_count} conflits de salle détectés" if violations_count > 0 else "OK: Aucun conflit de salle"
        }
    
    def check_time_slot_conflicts(self):
        """Vérifier les chevauchements de créneaux"""
        query = """
        SELECT 
            e1.id as examen1_id,
            e2.id as examen2_id,
            m1.nom as module1,
            m2.nom as module2,
            s1.nom as salle1,
            s2.nom as salle2,
            e1.date_exam,
            e1.heure as heure1,
            e2.heure as heure2,
            e1.duree
        FROM examens e1
        JOIN examens e2 ON e1.date_exam = e2.date_exam 
            AND e1.id < e2.id
        JOIN modules m1 ON e1.module_id = m1.id
        JOIN modules m2 ON e2.module_id = m2.id
        JOIN salles s1 ON e1.salle_id = s1.id
        JOIN salles s2 ON e2.salle_id = s2.id
        WHERE TIME(e1.heure) BETWEEN TIME(e2.heure) AND ADDTIME(TIME(e2.heure), SEC_TO_TIME(e2.duree * 60))
        OR TIME(e2.heure) BETWEEN TIME(e1.heure) AND ADDTIME(TIME(e1.heure), SEC_TO_TIME(e1.duree * 60))
        """
        violations = self.db.execute_query(query, fetch=True)
        
        # CORRECTION : Gestion du cas None
        if violations is None:
            violations = []
        
        violations_count = len(violations)
        
        return {
            'passed': violations_count == 0,
            'violations': violations,
            'message': f"{violations_count} chevauchements de créneaux détectés" if violations_count > 0 else "OK: Aucun chevauchement de créneaux"
        }