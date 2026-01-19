# test_ultime.py
import mysql.connector

print("=" * 60)
print("🔍 TEST ULTIME - DIAGNOSTIC COMPLET")
print("=" * 60)

# 1. Test connexion MySQL
try:
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='exam_planning_db'
    )
    print("✅ 1. MySQL CONNECTÉ")
    
    cursor = conn.cursor(dictionary=True)
    
    # 2. Test des tables
    print("\n✅ 2. TABLES ET DONNÉES:")
    tables = ['etudiants', 'professeurs', 'salles', 'modules', 'examens']
    
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
        result = cursor.fetchone()
        print(f"   {table}: {result['count']}")
    
    # 3. Tester une insertion DIRECTE
    print("\n✅ 3. TEST D'INSERTION DIRECTE:")
    
    # Prendre un module
    cursor.execute("SELECT id, nom FROM modules LIMIT 1")
    module = cursor.fetchone()
    
    # Prendre un prof  
    cursor.execute("SELECT id, nom FROM professeurs LIMIT 1")
    prof = cursor.fetchone()
    
    # Prendre une salle
    cursor.execute("SELECT id, nom FROM salles LIMIT 1")
    salle = cursor.fetchone()
    
    if module and prof and salle:
        cursor.execute("""
            INSERT INTO examens (module_id, prof_id, salle_id, date_exam, heure, duree)
            VALUES (%s, %s, %s, '2024-06-10', '09:00', 90)
        """, (module['id'], prof['id'], salle['id']))
        
        conn.commit()
        print(f"   ✅ Examen créé: {module['nom']}")
        print(f"      👨‍🏫 Professeur: {prof['nom']}")
        print(f"      🏫 Salle: {salle['nom']}")
    else:
        print("   ❌ Données manquantes pour l'insertion")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ ERREUR: {e}")
    print("\n💡 SOLUTION:")
    print("1. Démarrez MySQL (XAMPP > Start MySQL)")
    print("2. Vérifiez que la base 'exam_planning_db' existe")
    print("3. Exécutez database/create_database.sql")

print("\n" + "=" * 60)