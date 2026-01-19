import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../backend'))

from database import DatabaseManager
from scheduler import ExamScheduler

def test_database_connection():
    """Tester la connexion à la base de données"""
    print("Test de connexion à la base de données...")
    db = DatabaseManager()
    
    if db.connection.is_connected():
        print("✅ Connexion réussie")
        return True
    else:
        print("❌ Échec de la connexion")
        return False

def test_get_modules():
    """Tester la récupération des modules"""
    print("\nTest de récupération des modules...")
    db = DatabaseManager()
    modules = db.get_all_modules()
    
    if modules and len(modules) > 0:
        print(f"✅ {len(modules)} modules récupérés")
        for module in modules[:3]:  # Afficher les 3 premiers
            print(f"  - {module['nom']}: {module['nb_etudiants']} étudiants")
        return True
    else:
        print("❌ Aucun module récupéré")
        return False

def test_schedule_generation():
    """Tester la génération de l'emploi du temps"""
    print("\nTest de génération de l'emploi du temps...")
    scheduler = ExamScheduler()
    
    # Effacer les examens existants
    scheduler.clear_schedule()
    
    # Générer un nouvel emploi du temps
    scheduled, failed = scheduler.generate_schedule()
    
    if scheduled:
        print(f"✅ {len(scheduled)} examens planifiés")
        if failed:
            print(f"⚠️ {len(failed)} modules non planifiés")
        return True
    else:
        print("❌ Échec de la planification")
        return False

def test_conflict_detection():
    """Tester la détection des conflits"""
    print("\nTest de détection des conflits...")
    db = DatabaseManager()
    conflicts = db.detect_conflicts()
    
    student_conflicts = len(conflicts['student_conflicts'])
    professor_conflicts = len(conflicts['professor_conflicts'])
    
    print(f"Conflits étudiants détectés: {student_conflicts}")
    print(f"Conflits professeurs détectés: {professor_conflicts}")
    
    if student_conflicts == 0 and professor_conflicts == 0:
        print("✅ Aucun conflit détecté")
    else:
        print("⚠️ Conflits détectés")
    
    return conflicts

def test_constraint_checking():
    """Tester la vérification des contraintes"""
    print("\nTest de vérification des contraintes...")
    from constraints import ConstraintChecker
    
    db = DatabaseManager()
    checker = ConstraintChecker(db)
    constraints = checker.check_all_constraints()
    
    for constraint_name, result in constraints.items():
        if constraint_name != 'compliance_score':
            status = "✅" if result['passed'] else "❌"
            print(f"{status} {constraint_name}: {result['message']}")
    
    compliance = constraints.get('compliance_score', 0)
    print(f"\nScore de conformité global: {compliance:.1f}%")
    
    return compliance >= 80  # Considéré comme bon si >= 80%

def run_all_tests():
    """Exécuter tous les tests"""
    print("=" * 50)
    print("EXÉCUTION DES TESTS")
    print("=" * 50)
    
    tests = [
        ("Connexion BD", test_database_connection),
        ("Récupération modules", test_get_modules),
        ("Génération EDT", test_schedule_generation),
        ("Détection conflits", test_conflict_detection),
        ("Vérification contraintes", test_constraint_checking)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ Erreur lors du test '{test_name}': {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("RÉSUMÉ DES TESTS")
    print("=" * 50)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests réussis ({passed/total*100:.0f}%)")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)