import random
from database import DatabaseManager

db = DatabaseManager()

# Générer 50 étudiants supplémentaires
formations = [1, 2, 3, 4, 5]
noms = ['Leroy', 'Moreau', 'Simon', 'Laurent', 'Michel', 'Durand', 'Lefebvre', 'Garcia']
prenoms = ['Alex', 'Maxime', 'Clara', 'Sarah', 'Tom', 'Hugo', 'Emma', 'Louis']

for i in range(50):
    nom = random.choice(noms)
    prenom = random.choice(prenoms)
    formation_id = random.choice(formations)
    promo = random.choice([2023, 2024])
    email = f"{prenom.lower()}.{nom.lower()}{i}@etu.univ.fr"
    
    query = "INSERT INTO etudiants (nom, prenom, formation_id, promo, email) VALUES (%s, %s, %s, %s, %s)"
    db.execute_query(query, (nom, prenom, formation_id, promo, email))

print("50 étudiants ajoutés avec succès!")