import mysql.connector

try:
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',  # Vide pour XAMPP
        database='exam_planning_db'
    )
    
    if conn.is_connected():
        print("✅ Connexion MySQL réussie!")
        
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT COUNT(*) as nb FROM etudiants")
        result = cursor.fetchone()
        print(f"📊 Nombre d'étudiants: {result['nb']}")
        
        cursor.close()
        conn.close()
    else:
        print("❌ Connexion échouée")
        
except Exception as e:
    print(f"❌ Erreur: {e}")