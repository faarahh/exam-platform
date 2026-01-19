import mysql.connector
from faker import Faker
import random

fake = Faker('fr_FR')

conn = mysql.connector.connect(
    user="root",
    password="",  # vide car root n'a pas de mot de passe dans LAMPP
    database="exam_planning_db",
    unix_socket="/opt/lampp/var/mysql/mysql.sock"
)

cursor = conn.cursor()

# Récupérer les IDs de formations existants
cursor.execute("SELECT id FROM formations")
formations_ids = [row[0] for row in cursor.fetchall()]

# Générer 500 étudiants fictifs
for i in range(1, 501):
    nom = fake.last_name()
    prenom = fake.first_name()
    formation_id = random.choice(formations_ids)  # choisir parmi les formations valides
    promo = random.choice([2023, 2024, 2025])
    email = f"{prenom.lower()}.{nom.lower()}@etu.univ.fr"

    cursor.execute(
        "INSERT INTO etudiants (nom, prenom, formation_id, promo, email) VALUES (%s, %s, %s, %s, %s)",
        (nom, prenom, formation_id, promo, email)
    )

conn.commit()
cursor.close()
conn.close()

print("✅ 500 étudiants fictifs insérés avec succès dans exam_planning_db !")
