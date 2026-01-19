
import mysql.connector

try:
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='exam_planning_db'
    )
    
    cursor = conn.cursor(dictionary=True)
    
    # Tester CHAQUE table
    tables = ['etudiants', 'professeurs', 'salles', 'modules', 'examens', 'departments']
    
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
        result = cursor.fetchone()
        print(f"{table}: {result['count']}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"ERREUR: {e}")