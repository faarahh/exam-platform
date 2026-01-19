import mysql.connector
import random

conn = mysql.connector.connect(
    user="root",
    password="",  # vide car root n'a pas de mot de passe dans LAMPP
    database="exam_planning_db",
    unix_socket="/opt/lampp/var/mysql/mysql.sock"
)

cursor = conn.cursor()

# Récupérer les IDs des étudiants et des modules existants
cursor.execute("SELECT id FROM etudiants")
etudiants_ids = [row[0] for row in cursor.fetchall()]

cursor.execute("SELECT id FROM modules")
modules_ids = [row[0] for row in cursor.fetchall()]

# Générer des inscriptions réalistes
for etu_id in etudiants_ids:
    nb_modules = random.randint(5, 8)
    modules_choisis = random.sample(modules_ids, nb_modules)
    for module_id in modules_choisis:
        annee = random.choice([2023, 2024, 2025])
        cursor.execute(
            "INSERT IGNORE INTO inscriptions (etudiant_id, module_id, annee_inscription) VALUES (%s, %s, %s)",
            (etu_id, module_id, annee)
        )

conn.commit()
cursor.close()
conn.close()

print("✅ Inscriptions générées avec succès sans doublons !")
