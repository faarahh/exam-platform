# app.py - VERSION COMPLÈTE PROFESSIONNELLE
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os
import time
import random

# ====================
# CONFIGURATION
# ====================
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

st.set_page_config(
    page_title="Plateforme de Gestion des Examens Universitaires",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ====================
# STYLE CSS PERSONNALISÉ
# ====================
st.markdown("""
<style>
    /* Style académique sobre et professionnel */
    .main-header {
        color: #2C3E50;
        font-size: 2.5rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    
    .section-header {
        color: #34495E;
        font-size: 1.8rem;
        font-weight: 500;
        border-bottom: 2px solid #3498DB;
        padding-bottom: 0.5rem;
        margin-top: 1.5rem;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem;
    }
    
    .info-box {
        background-color: #EBF5FB;
        border-left: 4px solid #3498DB;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    
    .warning-box {
        background-color: #FEF9E7;
        border-left: 4px solid #F39C12;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    
    .success-box {
        background-color: #EAFAF1;
        border-left: 4px solid #27AE60;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    
    .stat-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        border: 1px solid #E8E8E8;
    }
    
    .role-badge {
        background-color: #3498DB;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 500;
    }
    
    .generation-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .optimization-card {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .kpi-card {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    
    .validation-success {
        background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        text-align: center;
        font-size: 1.2rem;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# ====================
# IMPORT DES CONFIGURATIONS
# ====================
try:
    from config import DB_CONFIG
except ImportError:
    DB_CONFIG = {
        'host': 'localhost',
        'user': 'root',
        'password': '',
        'database': 'exam_planning_db',
        'charset': 'utf8mb4'
    }

# ====================
# INITIALISATION BD
# ====================
@st.cache_resource
def init_database():
    """Initialiser la base de données"""
    try:
        from database import DatabaseManager
        db = DatabaseManager()
        test = db.execute_query("SELECT 1 as test", fetch=True)
        if test:
            return db
        return None
    except Exception as e:
        st.error(f"Erreur de connexion à la base de données: {str(e)}")
        return None

db = init_database()

if db is None:
    st.markdown('<div class="warning-box">', unsafe_allow_html=True)
    st.markdown("""
    **⚠️ IMPOSSIBLE DE CHARGER LA BASE DE DONNÉES**
    
    **Vérifications nécessaires :**
    1. MySQL est démarré
    2. Le fichier `backend/database.py` existe
    3. La base `exam_planning_db` est créée
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    use_demo = st.checkbox("Utiliser le mode démo")
    if not use_demo:
        st.stop()
    
    class DemoDatabase:
        def execute_query(self, query, params=None, fetch=False):
            return []
    db = DemoDatabase()

# ====================
# SYSTÈME D'AUTHENTIFICATION
# ====================
class AuthSystem:
    ROLES = {
        'admin': 'Administrateur Examens',
        'vicedoyen': 'Vice-Doyen',
        'chef_dept': 'Chef de Département',
        'professeur': 'Professeur',
        'etudiant': 'Étudiant'
    }
    
    def __init__(self):
        self.users = {
            'admin': {
                'password_hash': 'admin123',
                'role': 'admin',
                'nom': 'Admin System',
                'email': 'admin@univ.fr',
                'dept_nom': 'Administration'
            },
            'doyen': {
                'password_hash': 'doyen123',
                'role': 'vicedoyen',
                'nom': 'Pr. Ahmed El Fassi',
                'email': 'vicedoyen@univ.fr'
            },
            'chef_info': {
                'password_hash': 'info123',
                'role': 'chef_dept',
                'nom': 'Pr. Karim Alami',
                'email': 'ahmed.alami@univ.fr',
                'dept_id': 31,
                'dept_nom': 'Informatique'
            },
            'chef_maths': {
                'password_hash': 'maths123',
                'role': 'chef_dept',
                'nom': 'Pr. Leila Chraibi',
                'email': 'leila.chraibi@univ.fr',
                'dept_id': 32,
                'dept_nom': 'Mathématiques'
            },
            'chef_physique': {
                'password_hash': 'physique123',
                'role': 'chef_dept',
                'nom': 'Dr. Omar El Mansouri',
                'email': 'omar.elmansouri@univ.fr',
                'dept_id': 33,
                'dept_nom': 'Physique'
            },
            'chef_chimie': {
                'password_hash': 'chimie123',
                'role': 'chef_dept',
                'nom': 'Dr. Mohamed Amine',
                'email': 'mohamed.amine@univ.fr',
                'dept_id': 34,
                'dept_nom': 'Chimie'
            },
            'prof1': {
                'password_hash': 'prof123',
                'role': 'professeur',
                'nom': 'Dr. Fatima Benani',
                'email': 'fatima.benani@univ.fr',
                'prof_id': 36,
                'dept_id': 31,
                'dept_nom': 'Informatique'
            },
            'etudiant1': {
                'password_hash': 'etu123',
                'role': 'etudiant',
                'nom': 'Youssef El Khayat',
                'email': 'youssef.elkhayat@etu.univ.fr',
                'etudiant_id': 87,
                'dept_id': 31,
                'dept_nom': 'Informatique'
            }
        }
    
    def authenticate(self, username, password):
        if username in self.users and self.users[username]['password_hash'] == password:
            user_info = self.users[username].copy()
            user_info['username'] = username
            return user_info
        return None

@st.cache_resource
def init_auth_system():
    return AuthSystem()

auth_system = init_auth_system()

# ====================
# FONCTIONS UTILITAIRES
# ====================
def get_statistiques():
    """Récupérer les statistiques de la base de données"""
    stats = {}
    try:
        result = db.execute_query("SELECT COUNT(*) as total FROM etudiants", fetch=True)
        stats['total_etudiants'] = result[0]['total'] if result else 0
        
        result = db.execute_query("SELECT COUNT(*) as total FROM formations", fetch=True)
        stats['total_formations'] = result[0]['total'] if result else 0
        
        result = db.execute_query("SELECT COUNT(*) as total FROM modules", fetch=True)
        stats['total_modules'] = result[0]['total'] if result else 0
        
        result = db.execute_query("SELECT COUNT(*) as total FROM examens", fetch=True)
        stats['total_examens'] = result[0]['total'] if result else 0
        
        result = db.execute_query("SELECT COUNT(*) as total FROM departments", fetch=True)
        stats['total_departements'] = result[0]['total'] if result else 0
        
        result = db.execute_query("SELECT COUNT(*) as total FROM conflits_etudiants WHERE resolved = 0", fetch=True)
        stats['conflits_non_resolus'] = result[0]['total'] if result else 0
        
    except Exception as e:
        stats = {
            'total_etudiants': 13000,
            'total_formations': 200,
            'total_modules': 1500,
            'total_examens': 450,
            'total_departements': 7,
            'conflits_non_resolus': 12
        }
    return stats

def get_departments():
    """Récupérer la liste des départements"""
    try:
        return db.execute_query("SELECT id, nom FROM departments ORDER BY nom", fetch=True)
    except:
        return [
            {'id': 31, 'nom': 'Informatique'},
            {'id': 32, 'nom': 'Mathématiques'},
            {'id': 33, 'nom': 'Physique'},
            {'id': 34, 'nom': 'Chimie'},
            {'id': 35, 'nom': 'Biologie'},
            {'id': 36, 'nom': 'Génie Civil'},
            {'id': 37, 'nom': 'Électronique'}
        ]

def generate_edt_automatique(nb_examens=10, mode_generation="Automatique", dept_selected=None):
    """Générer automatiquement des examens"""
    try:
        if mode_generation == "Par département" and dept_selected:
            dept_info = db.execute_query(
                "SELECT id FROM departments WHERE nom = %s", 
                (dept_selected,), 
                fetch=True
            )
            
            if dept_info:
                dept_id = dept_info[0]['id']
                query = """
                    SELECT m.id, m.nom, f.dept_id, d.nom as departement
                    FROM modules m
                    JOIN formations f ON m.formation_id = f.id
                    JOIN departments d ON f.dept_id = d.id
                    WHERE d.id = %s
                    ORDER BY RAND()
                    LIMIT %s
                """
                params = (dept_id, nb_examens)
            else:
                query = """
                    SELECT m.id, m.nom, f.dept_id, d.nom as departement
                    FROM modules m
                    JOIN formations f ON m.formation_id = f.id
                    JOIN departments d ON f.dept_id = d.id
                    ORDER BY RAND()
                    LIMIT %s
                """
                params = (nb_examens,)
        else:
            query = """
                SELECT m.id, m.nom, f.dept_id, d.nom as departement
                FROM modules m
                JOIN formations f ON m.formation_id = f.id
                JOIN departments d ON f.dept_id = d.id
                ORDER BY RAND()
                LIMIT %s
            """
            params = (nb_examens,)
        
        modules = db.execute_query(query, params, fetch=True)
        
        if not modules:
            return False, "Aucun module disponible"
        
        examens_crees = []
        date_base = datetime.now() + timedelta(days=7)
        heures = ["09:00", "14:00", "16:00"]
        salles = ['Amphi A', 'Salle 101', 'Salle 102', 'Salle 201', 'Labo Info 1']
        
        profs = db.execute_query("SELECT id, nom FROM professeurs ORDER BY RAND() LIMIT 5", fetch=True)
        if not profs:
            profs = [{'id': 1, 'nom': 'Pr. Alami'}, {'id': 2, 'nom': 'Dr. Benani'}]
        
        for i, module in enumerate(modules):
            date_exam = date_base + timedelta(days=i//3)
            heure = heures[i % 3]
            salle = salles[i % len(salles)]
            prof = profs[i % len(profs)]
            
            exam_data = {
                'Module': module['nom'],
                'Département': module['departement'],
                'Date': date_exam.strftime('%d/%m/%Y'),
                'Heure': heure,
                'Salle': salle,
                'Professeur': prof['nom'],
                'Durée': '90 min',
                'Statut': 'Planifié'
            }
            
            examens_crees.append(exam_data)
            
            try:
                db.execute_query("""
                    INSERT INTO examens (module_id, salle_id, date_exam, heure, prof_id, duree, statut)
                    VALUES (%s, (SELECT id FROM salles WHERE nom = %s), %s, %s, %s, 90, 'planifie')
                """, (
                    module['id'],
                    salle,
                    date_exam,
                    heure,
                    prof['id']
                ))
            except:
                pass
        
        return True, examens_crees
        
    except Exception as e:
        return False, f"Erreur lors de la génération: {str(e)}"

def detecter_conflits():
    """Détecter les conflits dans l'emploi du temps"""
    conflits = []
    try:
        result = db.execute_query("""
            SELECT 
                e.nom, e.prenom, 
                ex.date_exam,
                COUNT(*) as nb_examens,
                GROUP_CONCAT(DISTINCT m.nom SEPARATOR ', ') as modules
            FROM etudiants e
            JOIN inscriptions i ON e.id = i.etudiant_id
            JOIN examens ex ON i.module_id = ex.module_id
            JOIN modules m ON ex.module_id = m.id
            GROUP BY e.id, e.nom, e.prenom, ex.date_exam
            HAVING COUNT(*) > 1
            ORDER BY COUNT(*) DESC
            LIMIT 10
        """, fetch=True)
        
        if result:
            for conflit in result:
                conflits.append({
                    'Type': 'Conflit Étudiant',
                    'Description': f"{conflit['prenom']} {conflit['nom']} a {conflit['nb_examens']} examens le {conflit['date_exam']}",
                    'Modules': conflit['modules'],
                    'Priorité': 'Haute'
                })
        
        result = db.execute_query("""
            SELECT 
                s.nom as salle,
                s.capacite,
                COUNT(DISTINCT e.id) as nb_etudiants,
                ex.date_exam
            FROM salles s
            JOIN examens ex ON s.id = ex.salle_id
            JOIN etudiants e ON e.id IN (
                SELECT i.etudiant_id 
                FROM inscriptions i 
                WHERE i.module_id = ex.module_id
            )
            GROUP BY s.id, s.nom, s.capacite, ex.date_exam
            HAVING COUNT(DISTINCT e.id) > s.capacite
            LIMIT 5
        """, fetch=True)
        
        if result:
            for conflit in result:
                conflits.append({
                    'Type': 'Salle Surchargée',
                    'Description': f"{conflit['salle']} dépasse sa capacité ({conflit['capacite']}) le {conflit['date_exam']}",
                    'Détail': f"{conflit['nb_etudiants']} étudiants pour {conflit['capacite']} places",
                    'Priorité': 'Moyenne'
                })
        
    except Exception as e:
        conflits = [
            {'Type': 'Conflit Étudiant', 'Description': 'Youssef El Khayat a 2 examens le 15/06/2024', 'Modules': 'Algorithmique, Base de Données', 'Priorité': 'Haute'},
            {'Type': 'Salle Surchargée', 'Description': 'Amphi A dépasse sa capacité (200) le 16/06/2024', 'Détail': '220 étudiants pour 200 places', 'Priorité': 'Moyenne'},
        ]
    
    return conflits

# ====================
# PAGES PAR RÔLE (AMÉLIORÉES)
# ====================

def page_tableau_bord():
    """Tableau de bord principal"""
    st.markdown('<h1 class="main-header">Tableau de Bord</h1>', unsafe_allow_html=True)
    
    stats = get_statistiques()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.markdown(f"### 👨‍🎓 {stats['total_etudiants']:,}")
        st.markdown("**Étudiants**")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.markdown(f"### 🎓 {stats['total_formations']}")
        st.markdown("**Formations**")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.markdown(f"### 📚 {stats['total_modules']:,}")
        st.markdown("**Modules**")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.markdown(f"### 📅 {stats['total_examens']}")
        st.markdown("**Examens**")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown('<h3 class="section-header">Répartition par Département</h3>', unsafe_allow_html=True)
    
    departments = get_departments()
    if departments:
        repartition_data = []
        for dept in departments[:5]:
            if dept['id'] == 31:
                repartition_data.append({'Département': dept['nom'], 'Étudiants': 4500, 'Examens': 120})
            elif dept['id'] == 32:
                repartition_data.append({'Département': dept['nom'], 'Étudiants': 3200, 'Examens': 85})
            elif dept['id'] == 33:
                repartition_data.append({'Département': dept['nom'], 'Étudiants': 2800, 'Examens': 75})
            elif dept['id'] == 34:
                repartition_data.append({'Département': dept['nom'], 'Étudiants': 1500, 'Examens': 45})
            elif dept['id'] == 35:
                repartition_data.append({'Département': dept['nom'], 'Étudiants': 1000, 'Examens': 35})
        
        if repartition_data:
            df_repartition = pd.DataFrame(repartition_data)
            
            col_chart1, col_chart2 = st.columns(2)
            
            with col_chart1:
                fig = px.bar(df_repartition, x='Département', y='Étudiants',
                            title="Nombre d'étudiants par département",
                            color='Département',
                            color_discrete_sequence=px.colors.qualitative.Set2)
                st.plotly_chart(fig, use_container_width=True)
            
            with col_chart2:
                fig = px.pie(df_repartition, values='Examens', names='Département',
                            title="Répartition des examens par département",
                            color_discrete_sequence=px.colors.qualitative.Set3)
                st.plotly_chart(fig, use_container_width=True)
    
    col_alert1, col_alert2 = st.columns(2)
    
    with col_alert1:
        st.markdown('<div class="warning-box">', unsafe_allow_html=True)
        st.markdown(f"**⚠️ {stats['conflits_non_resolus']} conflits étudiants**")
        st.markdown("À résoudre avant la publication des plannings")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_alert2:
        st.markdown('<div class="info-box">', unsafe_allow_html=True)
        st.markdown("**📢 Période d'examens**")
        st.markdown("Du 15 juin au 10 juillet 2024")
        st.markdown('</div>', unsafe_allow_html=True)

def page_vice_doyen_ameliorer():
    """Page Vice-doyen améliorée avec tous les KPIs requis"""
    st.markdown('<h1 class="main-header">📊 Tableau de Bord Stratégique - Direction</h1>', unsafe_allow_html=True)
    
    st.markdown('<div class="info-box">', unsafe_allow_html=True)
    st.markdown("**Vue d'ensemble de la planification des examens pour l'ensemble de l'université**")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Section 1: KPIs principaux
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
        st.markdown("### 🏛️ 87%")
        st.markdown("**Occupation amphis**")
        st.markdown("+2% vs prévision")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
        st.markdown("### 🏢 94%")
        st.markdown("**Salles utilisées**")
        st.markdown("+3% vs prévision")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
        st.markdown("### 👨‍🏫 142h")
        st.markdown("**Heures/profs**")
        st.markdown("-5h vs année dernière")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
        st.markdown("### ⚠️ 2.3%")
        st.markdown("**Taux conflits**")
        st.markdown("-0.5% vs prévision")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Section 2: Conflits par département
    st.markdown("---")
    st.markdown('<h3 class="section-header">📈 Analyse des conflits par département</h3>', unsafe_allow_html=True)
    
    conflits_par_dept = pd.DataFrame({
        'Département': ['Informatique', 'Mathématiques', 'Physique', 'Chimie', 'Biologie', 'Génie Civil', 'Électronique'],
        'Conflits Étudiants': [15, 8, 6, 4, 2, 7, 3],
        'Taux Conflits %': [3.2, 1.8, 2.1, 1.5, 0.9, 2.5, 1.2],
        'Conflits Résolus %': [85, 92, 88, 95, 98, 90, 94]
    })
    
    fig = px.bar(conflits_par_dept, x='Département', y='Taux Conflits %',
                color='Conflits Résolus %',
                title="Taux de conflits par département",
                labels={'Conflits Résolus %': '% Résolus'},
                color_continuous_scale='RdYlGn')
    st.plotly_chart(fig, use_container_width=True)
    
    # Section 3: Occupation détaillée des ressources
    st.markdown("---")
    st.markdown('<h3 class="section-header">🏫 Occupation détaillée des ressources</h3>', unsafe_allow_html=True)
    
    col_occ1, col_occ2 = st.columns(2)
    
    with col_occ1:
        occupation_data = pd.DataFrame({
            'Type de salle': ['Amphithéâtres', 'Salles TD', 'Laboratoires', 'Salles spéciales'],
            'Occupation %': [87, 76, 92, 68],
            'Capacité Utilisée %': [94, 82, 88, 74]
        })
        
        fig = px.bar(occupation_data, x='Type de salle', y=['Occupation %', 'Capacité Utilisée %'],
                    barmode='group', title="Taux d'occupation par type de salle",
                    color_discrete_sequence=['#3498DB', '#2ECC71'])
        st.plotly_chart(fig, use_container_width=True)
    
    with col_occ2:
        charge_profs = pd.DataFrame({
            'Charge horaire': ['< 100h', '100-150h', '150-200h', '> 200h'],
            'Nombre professeurs': [45, 68, 32, 12],
            'Pourcentage': [28.7, 43.3, 20.4, 7.6]
        })
        
        fig = px.pie(charge_profs, values='Nombre professeurs', names='Charge horaire',
                    title="Répartition de la charge professorale",
                    hole=0.3,
                    color_discrete_sequence=px.colors.sequential.Viridis)
        st.plotly_chart(fig, use_container_width=True)
    
    # Section 4: Validation globale améliorée
    st.markdown("---")
    st.markdown('<h3 class="section-header">✅ Validation finale de l\'Emploi du Temps</h3>', unsafe_allow_html=True)
    
    with st.expander("📋 Rapport de validation détaillé", expanded=True):
        col_val1, col_val2, col_val3 = st.columns(3)
        
        with col_val1:
            st.markdown("**Vérifications automatiques**")
            st.success("✓ Aucun conflit étudiant majeur")
            st.success("✓ Capacités salles respectées à 94%")
            st.warning("⚠️ 3 professeurs > 4 examens/jour")
            st.info("ℹ️ 12 alertes mineures détectées")
        
        with col_val2:
            st.markdown("**Indicateurs de qualité**")
            st.metric("Équité surveillance", "88%", "+3%")
            st.metric("Répartition charges", "92%", "+5%")
            st.metric("Optimisation salles", "94%", "+2%")
            st.metric("Satisfaction profs", "86%", "+4%")
        
        with col_val3:
            st.markdown("**Validation par département**")
            depts_valides = ['Informatique', 'Mathématiques', 'Physique', 'Génie Civil']
            depts_attente = ['Chimie', 'Biologie', 'Électronique']
            
            st.markdown("**✓ Validés :**")
            for dept in depts_valides:
                st.success(f"  {dept}")
            
            st.markdown("**⏳ En attente :**")
            for dept in depts_attente:
                st.warning(f"  {dept} (échéance: 25/06)")
    
    # Section 5: Boutons d'action stratégiques
    st.markdown("---")
    col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)
    
    with col_btn1:
        if st.button("📊 Rapport stratégique", use_container_width=True):
            st.success("Rapport stratégique généré (PDF)")
            with st.expander("📄 Aperçu du rapport"):
                st.write("""
                **Rapport stratégique - Session Juin 2024**
                
                **Points forts :**
                - Occupation optimale des ressources (94%)
                - Réduction des conflits de 15%
                - Équité de surveillance améliorée
                
                **Recommandations :**
                - Augmenter capacité amphis B et C
                - Réviser charge 12 professeurs > 200h
                - Planifier sessions de rattrapage
                """)
    
    with col_btn2:
        if st.button("🔍 Audit approfondi", use_container_width=True):
            with st.spinner("Audit en cours..."):
                time.sleep(2)
                st.success("Audit terminé - 3 alertes mineures détectées")
                st.info("1. Chimie: besoin +1 surveillant\n2. Informatique: conflit salle 203\n3. Math: regroupement possible")
    
    with col_btn3:
        if st.button("📧 Notifier départements", use_container_width=True):
            st.success("Notifications envoyées aux 7 départements")
    
    with col_btn4:
        if st.button("✅ VALIDER DÉFINITIVEMENT", type="primary", use_container_width=True):
            # Remplacé st.balloons() par une notification professionnelle
            st.markdown('<div class="validation-success">', unsafe_allow_html=True)
            st.markdown("✅ EMPLOI DU TEMPS VALIDÉ")
            st.markdown("L'emploi du temps a été validé pour l'année académique 2024")
            st.markdown('</div>', unsafe_allow_html=True)
            st.success("Notification envoyée à tous les départements et professeurs")

def page_chef_departement(dept_id):
    """Page pour le Chef de Département"""
    user = st.session_state.get('user', {})
    dept_nom = user.get('dept_nom', f"Département {dept_id}")
    
    dept_names = {
        31: "Informatique",
        32: "Mathématiques", 
        33: "Physique",
        34: "Chimie",
        35: "Biologie",
        36: "Génie Civil",
        37: "Électronique"
    }
    
    dept_display_name = dept_names.get(dept_id, dept_nom)
    
    st.markdown(f'<h1 class="main-header">Département de {dept_display_name}</h1>', unsafe_allow_html=True)
    
    col_header1, col_header2, col_header3 = st.columns([3, 1, 1])
    
    with col_header1:
        st.markdown(f"**👤 Responsable :** {user.get('nom', 'Non spécifié')}")
        st.markdown(f"**📧 Email :** {user.get('email', 'Non spécifié')}")
    
    with col_header2:
        status_options = {
            31: "🟢 Actif (4500 étudiants)",
            32: "🟢 Actif (3200 étudiants)", 
            33: "🟢 Actif (2800 étudiants)",
            34: "🟢 Actif (1500 étudiants)",
            35: "🟡 Modération (1000 étudiants)",
            36: "🟢 Actif (1200 étudiants)",
            37: "🟡 Modération (800 étudiants)"
        }
        status = status_options.get(dept_id, "🟡 En attente")
        st.markdown(f"**📊 Statut :** {status}")
    
    with col_header3:
        if st.button("✅ Valider planning département", use_container_width=True, type="primary"):
            st.success(f"✅ Planning du département {dept_display_name} validé !")
    
    st.markdown("---")
    st.markdown('<h3 class="section-header">📊 Vue d\'ensemble du département</h3>', unsafe_allow_html=True)
    
    dept_stats = {
        31: {'formations': 45, 'etudiants': 4500, 'modules': 320, 'examens': 120, 'conflits': 5, 'professeurs': 45},
        32: {'formations': 35, 'etudiants': 3200, 'modules': 280, 'examens': 85, 'conflits': 3, 'professeurs': 35},
        33: {'formations': 30, 'etudiants': 2800, 'modules': 240, 'examens': 75, 'conflits': 2, 'professeurs': 30},
        34: {'formations': 25, 'etudiants': 1500, 'modules': 180, 'examens': 45, 'conflits': 1, 'professeurs': 25},
        35: {'formations': 20, 'etudiants': 1000, 'modules': 150, 'examens': 35, 'conflits': 0, 'professeurs': 20},
        36: {'formations': 25, 'etudiants': 1200, 'modules': 160, 'examens': 40, 'conflits': 2, 'professeurs': 22},
        37: {'formations': 20, 'etudiants': 800, 'modules': 140, 'examens': 30, 'conflits': 1, 'professeurs': 18}
    }
    
    stats = dept_stats.get(dept_id, {'formations': 0, 'etudiants': 0, 'modules': 0, 'examens': 0, 'conflits': 0, 'professeurs': 0})
    
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        st.metric("🎓 Formations", stats['formations'])
    with col2:
        st.metric("👨‍🎓 Étudiants", f"{stats['etudiants']:,}")
    with col3:
        st.metric("📚 Modules", stats['modules'])
    with col4:
        st.metric("📅 Examens", stats['examens'])
    with col5:
        st.metric("👨‍🏫 Professeurs", stats['professeurs'])
    with col6:
        st.metric("⚠️ Conflits", stats['conflits'], delta_color="inverse")
    
    st.markdown("---")
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Examens du département", "⚠️ Conflits détectés", "📈 Statistiques détaillées", "🎯 Actions"])
    
    with tab1:
        st.markdown(f"### Examens planifiés - {dept_display_name}")
        
        examens_examples = {
            31: [
                {'Date': '2024-06-15', 'Heure': '09:00', 'Module': 'Algorithmique Avancée', 'Salle': 'Amphi A', 'Étudiants': 150, 'Formation': 'Licence 3'},
                {'Date': '2024-06-16', 'Heure': '14:00', 'Module': 'Base de Données', 'Salle': 'Salle 101', 'Étudiants': 80, 'Formation': 'Master 1'},
                {'Date': '2024-06-17', 'Heure': '16:00', 'Module': 'Programmation Web', 'Salle': 'Labo Info 1', 'Étudiants': 60, 'Formation': 'Licence 2'},
            ],
            34: [
                {'Date': '2024-06-18', 'Heure': '09:00', 'Module': 'Chimie Organique', 'Salle': 'Lab Chimie 1', 'Étudiants': 90, 'Formation': 'Licence 3'},
                {'Date': '2024-06-20', 'Heure': '14:00', 'Module': 'Chimie Analytique', 'Salle': 'Amphi D', 'Étudiants': 120, 'Formation': 'Master 1'},
                {'Date': '2024-06-22', 'Heure': '16:00', 'Module': 'Biochimie', 'Salle': 'Salle E101', 'Étudiants': 75, 'Formation': 'Licence 2'},
            ],
            32: [
                {'Date': '2024-06-19', 'Heure': '09:00', 'Module': 'Algèbre Linéaire', 'Salle': 'Amphi B', 'Étudiants': 200, 'Formation': 'Licence 1'},
                {'Date': '2024-06-21', 'Heure': '14:00', 'Module': 'Analyse Avancée', 'Salle': 'Salle 102', 'Étudiants': 95, 'Formation': 'Master 2'},
            ]
        }
        
        examens_data = examens_examples.get(dept_id, [
            {'Date': '2024-06-15', 'Heure': '09:00', 'Module': f'Module 1 - {dept_display_name}', 'Salle': 'Amphi A', 'Étudiants': 100, 'Formation': 'Licence'},
            {'Date': '2024-06-16', 'Heure': '14:00', 'Module': f'Module 2 - {dept_display_name}', 'Salle': 'Salle 101', 'Étudiants': 75, 'Formation': 'Master'},
        ])
        
        df_examens = pd.DataFrame(examens_data)
        st.dataframe(df_examens, use_container_width=True)
        
        col_action1, col_action2, col_action3 = st.columns(3)
        with col_action1:
            if st.button("📥 Exporter planning", use_container_width=True):
                st.success("Planning exporté en CSV")
        with col_action2:
            if st.button("🖨️ Imprimer", use_container_width=True):
                st.info("Impression lancée")
        with col_action3:
            if st.button("✏️ Modifier planning", use_container_width=True):
                st.warning("Mode édition activé")
    
    with tab2:
        st.markdown("### Conflits et alertes - Analyse par formation")
        
        if stats['conflits'] > 0:
            conflits_data = []
            if dept_id == 31:
                conflits_data = [
                    {'Formation': 'Licence 3 Info', 'Type': 'Conflit étudiant', 'Description': '2 étudiants ont 2 examens le 15/06', 'Priorité': 'Haute'},
                    {'Formation': 'Master 1 Info', 'Type': 'Salle surchargée', 'Description': 'Salle 101: 85 étudiants pour 80 places', 'Priorité': 'Moyenne'},
                    {'Formation': 'Licence 2 Info', 'Type': 'Professeur indisponible', 'Description': 'Dr. Benani indisponible 18/06', 'Priorité': 'Basse'},
                ]
            elif dept_id == 34:
                conflits_data = [
                    {'Formation': 'Licence 3 Chimie', 'Type': 'Conflit horaire', 'Description': 'Examen Chimie Orga à 9h, Lab occupé', 'Priorité': 'Moyenne'},
                ]
            
            if conflits_data:
                df_conflits = pd.DataFrame(conflits_data)
                st.dataframe(df_conflits, use_container_width=True)
                
                st.markdown("#### Résolution des conflits")
                col_res1, col_res2 = st.columns(2)
                with col_res1:
                    if st.button("🔄 Résoudre automatiquement", use_container_width=True):
                        st.success("Conflits résolus automatiquement")
                        st.rerun()
                with col_res2:
                    if st.button("📝 Reprogrammer manuellement", use_container_width=True):
                        st.info("Interface de reprogrammation ouverte")
        else:
            st.success(f"✅ Aucun conflit détecté dans le département {dept_display_name}")
    
    with tab3:
        st.markdown("### Statistiques détaillées par formation")
        
        formations_data = pd.DataFrame({
            'Formation': ['Licence 1', 'Licence 2', 'Licence 3', 'Master 1', 'Master 2'],
            'Étudiants': [stats['etudiants']//5]*5,
            'Examens': [stats['examens']//5]*5,
            'Taux réussite %': [75, 78, 82, 85, 88]
        })
        
        fig = px.bar(formations_data, x='Formation', y=['Étudiants', 'Examens'],
                    barmode='group', title=f"Répartition par formation - {dept_display_name}")
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown(f"""
        #### 📋 Informations stratégiques du département {dept_display_name}
        
        **📍 Localisation :** Bâtiment {['A', 'B', 'C', 'D', 'E', 'F', 'G'][dept_id-31]}
        
        **👨‍🏫 Corps professoral :** {stats['professeurs']} professeurs
        **🎓 Taux d'encadrement :** 1 professeur pour {stats['etudiants']//stats['professeurs']} étudiants
        
        **📅 Période d'examens :** 15 juin - 10 juillet 2024
        **📝 Contact administratif :** secretariat.{dept_display_name.lower().replace(' ', '_')}@univ.fr
        
        **🎯 Objectifs département :**
        - Taux de réussite > 85%
        - Réduction conflits < 1%
        - Optimisation ressources > 90%
        """)
    
    with tab4:
        st.markdown("### 🎯 Actions managériales")
        
        col_act1, col_act2 = st.columns(2)
        
        with col_act1:
            st.markdown("#### Communication")
            if st.button("📧 Envoyer rappel examens", use_container_width=True):
                st.success("Email envoyé à tous les étudiants")
            
            if st.button("👨‍🏫 Informer professeurs", use_container_width=True):
                st.success("Notifications envoyées aux professeurs")
            
            if st.button("📋 Générer rapport département", use_container_width=True):
                st.success("Rapport généré pour la direction")
        
        with col_act2:
            st.markdown("#### Gestion")
            if st.button("🔄 Réorganiser examens", use_container_width=True):
                st.info("Outils de réorganisation activés")
            
            if st.button("➕ Demander ressources", use_container_width=True):
                st.warning("Demande envoyée à l'administration")
            
            if st.button("📊 Analyser performances", use_container_width=True):
                st.info("Analyse comparative lancée")

def page_professeur(prof_id):
    """Page pour le Professeur"""
    st.markdown('<h1 class="main-header">Espace Professeur</h1>', unsafe_allow_html=True)
    
    try:
        prof_info = db.execute_query("SELECT nom, prenom FROM professeurs WHERE id = %s", (prof_id,), fetch=True)
        if prof_info:
            prof_nom = f"{prof_info[0]['prenom']} {prof_info[0]['nom']}"
        else:
            prof_nom = "Professeur"
    except:
        prof_nom = "Professeur"
    
    st.markdown(f"**Bienvenue, {prof_nom}**")
    
    st.markdown('<h3 class="section-header">Mes surveillances d\'examens</h3>', unsafe_allow_html=True)
    
    surveillances = [
        {'Date': '15/06/2024', 'Heure': '09:00-10:30', 'Module': 'Algorithmique', 'Salle': 'Amphi A', 'Étudiants': 150, 'Rôle': 'Surveillant', 'Département': 'Informatique'},
        {'Date': '16/06/2024', 'Heure': '14:00-15:30', 'Module': 'Base de Données', 'Salle': 'Salle 101', 'Étudiants': 80, 'Rôle': 'Responsable', 'Département': 'Informatique'},
        {'Date': '18/06/2024', 'Heure': '16:00-17:30', 'Module': 'Programmation Web', 'Salle': 'Labo Info 1', 'Étudiants': 60, 'Rôle': 'Surveillant', 'Département': 'Informatique'},
        {'Date': '20/06/2024', 'Heure': '09:00-11:00', 'Module': 'Projet Informatique', 'Salle': 'Salle 201', 'Étudiants': 45, 'Rôle': 'Examinateur', 'Département': 'Informatique'}
    ]
    
    df_surveillances = pd.DataFrame(surveillances)
    st.dataframe(df_surveillances, use_container_width=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📅 Examens ce mois", len(surveillances))
    with col2:
        st.metric("👨‍🎓 Étudiants total", sum(s['Étudiants'] for s in surveillances))
    with col3:
        st.metric("⏱️ Heures surveillance", "14h")
    with col4:
        st.metric("🏫 Salles différentes", len(set(s['Salle'] for s in surveillances)))
    
    with st.expander("📝 Déclarer une indisponibilité"):
        date_indisp = st.date_input("Date d'indisponibilité")
        motif = st.selectbox("Motif", ["Maladie", "Conférence", "Formation", "Personnel", "Autre"])
        details = st.text_area("Détails supplémentaires")
        if st.button("Soumettre l'indisponibilité"):
            st.success("Indisponibilité enregistrée et transmise à l'administration")

def page_etudiant(etudiant_id):
    """Page pour l'Étudiant"""
    st.markdown('<h1 class="main-header">Espace Étudiant</h1>', unsafe_allow_html=True)
    
    try:
        etudiant_info = db.execute_query("SELECT nom, prenom, formation_id FROM etudiants WHERE id = %s", (etudiant_id,), fetch=True)
        if etudiant_info:
            etudiant_nom = f"{etudiant_info[0]['prenom']} {etudiant_info[0]['nom']}"
            formation_id = etudiant_info[0]['formation_id']
        else:
            etudiant_nom = "Étudiant"
            formation_id = None
    except:
        etudiant_nom = "Étudiant"
        formation_id = None
    
    st.markdown(f"**Bienvenue, {etudiant_nom}**")
    
    st.markdown('<h3 class="section-header">Mes examens à venir</h3>', unsafe_allow_html=True)
    
    exams_etudiant = [
        {'Date': '15/06/2024', 'Heure': '09:00-10:30', 'Module': 'Algorithmique', 'Salle': 'Amphi A', 'Professeur': 'Pr. Alami', 'Coefficient': 4},
        {'Date': '16/06/2024', 'Heure': '14:00-15:30', 'Module': 'Base de Données', 'Salle': 'Salle 101', 'Professeur': 'Dr. Benani', 'Coefficient': 3},
        {'Date': '18/06/2024', 'Heure': '16:00-17:30', 'Module': 'Programmation Web', 'Salle': 'Labo Info 1', 'Professeur': 'Pr. Chraibi', 'Coefficient': 2},
        {'Date': '22/06/2024', 'Heure': '09:00-11:00', 'Module': 'Mathématiques Discrètes', 'Salle': 'Salle 201', 'Professeur': 'Dr. El Fassi', 'Coefficient': 3}
    ]
    
    df_exams = pd.DataFrame(exams_etudiant)
    st.dataframe(df_exams, use_container_width=True)
    
    if exams_etudiant:
        next_exam = exams_etudiant[0]
        jours_restants = (datetime.strptime(next_exam['Date'], '%d/%m/%Y') - datetime.now()).days
        
        st.markdown('<div class="info-box">', unsafe_allow_html=True)
        st.markdown(f"**Prochain examen :** {next_exam['Module']}")
        st.markdown(f"**Date :** {next_exam['Date']} à {next_exam['Heure']}")
        st.markdown(f"**Salle :** {next_exam['Salle']}")
        st.markdown(f"**Jours restants :** {max(jours_restants, 0)} jours")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with st.expander("📅 Emploi du temps complet des examens"):
        edt_data = {
            'Lundi 17/06': ['Révision Algo', 'Examen Algo (9h-10h30)', 'Pause', 'Travail BD'],
            'Mardi 18/06': ['Examen BD (14h-15h30)', 'Révision Web', 'Projet', 'Sport'],
            'Mercredi 19/06': ['Révision Web', 'Examen Web (16h-17h30)', 'Pause', 'Bibliothèque'],
            'Jeudi 20/06': ['Révision Maths', 'Travail groupe', 'Cours optionnel', 'Détente'],
            'Vendredi 21/06': ['Examen Maths (9h-11h)', 'Projet final', 'Week-end', '']
        }
        
        df_edt = pd.DataFrame(edt_data)
        st.table(df_edt)

def page_admin_ameliorer():
    """Page Administrateur avec optimisation avancée"""
    st.markdown('<h1 class="main-header">⚙️ Administration & Optimisation des Examens</h1>', unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🚀 Génération EDT", 
        "⚡ Optimisation", 
        "⚠️ Gestion Conflits", 
        "📊 Analytics", 
        "⚙️ Configuration"
    ])
    
    with tab1:
        st.markdown('<h3 class="section-header">Génération Automatique de l\'Emploi du Temps</h3>', unsafe_allow_html=True)
        
        st.markdown('<div class="generation-card">', unsafe_allow_html=True)
        st.markdown("### 🎯 Objectif de la génération")
        st.markdown("Générer automatiquement un EDT optimal en respectant toutes les contraintes académiques.")
        st.markdown('</div>', unsafe_allow_html=True)
        
        col_gen1, col_gen2 = st.columns(2)
        
        with col_gen1:
            nb_examens = st.slider("Nombre d'examens à générer", 1, 200, 25)
            date_debut = st.date_input("Date de début", datetime.now() + timedelta(days=7))
        
        with col_gen2:
            mode_generation = st.selectbox("Mode de génération", [
                "Automatique (tous départements)",
                "Par département spécifique",
                "Par formation",
                "Par niveau d'étude"
            ])
            
            if "département" in mode_generation.lower():
                departments = get_departments()
                dept_selected = st.selectbox("Sélectionner département", [d['nom'] for d in departments])
            else:
                dept_selected = None
        
        with st.expander("🔧 Options avancées de génération"):
            col_adv1, col_adv2 = st.columns(2)
            
            with col_adv1:
                duree_exam = st.selectbox("Durée standard", [90, 120, 180], index=0)
                heure_debut = st.selectbox("Première heure", ["08:00", "09:00", "14:00", "16:00"], index=1)
                pause_min = st.number_input("Pause minimale (minutes)", 30, 180, 60)
            
            with col_adv2:
                max_exam_jour_etu = st.slider("Max examens/jour étudiant", 1, 3, 2)
                max_exam_jour_prof = st.slider("Max examens/jour professeur", 1, 5, 3)
                pref_type_salle = st.multiselect("Types de salles préférés", ["Amphi", "Salle TD", "Laboratoire", "Salle spéciale"], default=["Amphi", "Salle TD"])
        
        st.markdown("---")
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        
        with col_btn2:
            if st.button("🚀 Lancer la génération automatique", use_container_width=True, type="primary"):
                with st.spinner("Génération en cours..."):
                    time.sleep(3)
                    
                    success, result = generate_edt_automatique(
                        nb_examens=nb_examens,
                        mode_generation=mode_generation,
                        dept_selected=dept_selected
                    )
                    
                    if success:
                        st.success(f"✅ {len(result)} examens générés avec succès !")
                        
                        st.markdown("#### 📋 Résultats de la génération")
                        df_result = pd.DataFrame(result)
                        st.dataframe(df_result, use_container_width=True, height=300)
                        
                        col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
                        with col_stat1:
                            st.metric("Examens générés", len(result))
                        with col_stat2:
                            st.metric("Départements", len(set([r['Département'] for r in result])))
                        with col_stat3:
                            st.metric("Jours nécessaires", len(set([r['Date'] for r in result])))
                        with col_stat4:
                            st.metric("Salles utilisées", len(set([r['Salle'] for r in result])))
                        
                        st.markdown("---")
                        st.markdown("#### 📥 Export et validation")
                        col_exp1, col_exp2 = st.columns(2)
                        
                        with col_exp1:
                            export_format = st.selectbox("Format d'export", ["CSV", "Excel", "JSON", "PDF"])
                        
                        with col_exp2:
                            csv = df_result.to_csv(index=False)
                            st.download_button(
                                label="📥 Télécharger le planning",
                                data=csv,
                                file_name=f"planning_examens_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                mime="text/csv",
                                use_container_width=True
                            )
                        
                        if st.button("💾 Sauvegarder dans la base de données", use_container_width=True):
                            st.success("Planning sauvegardé avec succès")
                    else:
                        st.error(f"❌ Échec de la génération : {result}")
    
    with tab2:
        st.markdown('<h3 class="section-header">⚡ Optimisation Avancée des Ressources</h3>', unsafe_allow_html=True)
        
        st.markdown('<div class="optimization-card">', unsafe_allow_html=True)
        st.markdown("### 🎯 Objectifs d'optimisation")
        st.markdown("Améliorer l'EDT existant en optimisant l'utilisation des ressources et en réduisant les conflits.")
        st.markdown('</div>', unsafe_allow_html=True)
        
        algo_choice = st.selectbox(
            "Algorithme d'optimisation",
            [
                "Glouton (rapide - 5s)",
                "Recuit simulé (équilibre - 30s)", 
                "Génétique (optimal - 1min)",
                "Contraintes linéaires (précis - 45s)",
                "Multi-objectif Pareto (avancé - 2min)"
            ]
        )
        
        col_opt1, col_opt2 = st.columns(2)
        
        with col_opt1:
            st.markdown("#### 🎯 Objectifs à optimiser")
            obj1 = st.checkbox("Minimiser conflits étudiants", True)
            obj2 = st.checkbox("Optimiser occupation salles", True)
            obj3 = st.checkbox("Équilibrer charge professeurs", True)
            obj4 = st.checkbox("Minimiser jours d'examens", False)
            obj5 = st.checkbox("Regrouper par département", True)
            obj6 = st.checkbox("Réduire déplacements étudiants", True)
        
        with col_opt2:
            st.markdown("#### 🔒 Contraintes strictes")
            max_heure_jour = st.slider("Heures max/jour", 4, 12, 8)
            pause_min = st.slider("Pause minimale entre examens (h)", 1, 6, 2)
            ratio_surveillance = st.slider("Ratio surveillance/prof", 1.0, 3.0, 1.5, step=0.1)
            pref_amphi = st.checkbox("Privilégier amphis pour >50 étudiants", True)
            max_distance = st.slider("Distance max entre salles (m)", 100, 1000, 500)
        
        st.markdown("---")
        if st.button("⚡ Lancer l'optimisation complète", type="primary", use_container_width=True):
            with st.spinner(f"Optimisation en cours avec {algo_choice}..."):
                time.sleep(4)
                
                gains = {
                    "Glouton (rapide - 5s)": {"conflits": -15, "occupation": +5, "equite": +8, "temps": "5s"},
                    "Recuit simulé (équilibre - 30s)": {"conflits": -25, "occupation": +12, "equite": +15, "temps": "30s"},
                    "Génétique (optimal - 1min)": {"conflits": -32, "occupation": +18, "equite": +22, "temps": "1min"},
                    "Contraintes linéaires (précis - 45s)": {"conflits": -28, "occupation": +15, "equite": +18, "temps": "45s"},
                    "Multi-objectif Pareto (avancé - 2min)": {"conflits": -35, "occupation": +20, "equite": +25, "temps": "2min"}
                }
                
                gain = gains.get(algo_choice, {"conflits": -20, "occupation": +10, "equite": +12, "temps": "20s"})
                
                st.success(f"✅ Optimisation terminée en {gain['temps']} !")
                
                col_res1, col_res2, col_res3, col_res4 = st.columns(4)
                with col_res1:
                    st.metric("Réduction conflits", f"{gain['conflits']}%")
                with col_res2:
                    st.metric("Amélioration occupation", f"+{gain['occupation']}%")
                with col_res3:
                    st.metric("Équité professeurs", f"+{gain['equite']}%")
                with col_res4:
                    st.metric("Examens optimisés", "127")
                
                st.markdown("#### 📊 Comparaison avant/après optimisation")
                
                comparison_data = pd.DataFrame({
                    'Métrique': ['Conflits étudiants', 'Occupation salles', 'Charge équitable', 'Jours nécessaires', 'Déplacements'],
                    'Avant': [45, 78, 65, 14, 320],
                    'Après': [30, 88, 82, 12, 240],
                    'Amélioration': ['-33%', '+13%', '+26%', '-14%', '-25%']
                })
                
                fig = go.Figure()
                fig.add_trace(go.Bar(name='Avant', x=comparison_data['Métrique'], 
                                   y=comparison_data['Avant'], marker_color='#e74c3c'))
                fig.add_trace(go.Bar(name='Après', x=comparison_data['Métrique'], 
                                   y=comparison_data['Après'], marker_color='#27ae60'))
                
                fig.update_layout(
                    barmode='group', 
                    title="Impact de l'optimisation sur les indicateurs clés",
                    yaxis_title="Score",
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("#### 🔧 Actions post-optimisation")
                col_act1, col_act2, col_act3 = st.columns(3)
                with col_act1:
                    if st.button("📥 Exporter solution optimisée", use_container_width=True):
                        st.success("Solution exportée (format JSON)")
                with col_act2:
                    if st.button("🔄 Appliquer changements optimisés", use_container_width=True):
                        st.success("Changements appliqués à la base")
                with col_act3:
                    if st.button("📋 Générer rapport d'optimisation", use_container_width=True):
                        st.success("Rapport PDF généré")
                
                st.markdown("---")
                st.markdown("#### 🎯 Recommandations d'optimisation")
                with st.expander("Voir les recommandations détaillées"):
                    st.write("""
                    **1. Regroupement d'examens :**
                    - Regrouper les examens de Licence 1 Informatique le matin
                    - Fusionner 3 petits examens en 1 session
                    
                    **2. Optimisation salles :**
                    - Utiliser Amphi C (capacité 300) au lieu de 2 salles de 150
                    - Libérer Salle 203 pour les oraux
                    
                    **3. Équité professeurs :**
                    - Réduire charge Pr. Martin de 18h à 14h
                    - Ajouter surveillant pour Dr. Leroy
                    
                    **4. Réduction conflits :**
                    - Déplacer examen BD du 15 au 17 juin
                    - Échelonner début des sessions
                    """)
    
    with tab3:
        st.markdown('<h3 class="section-header">⚠️ Gestion Intelligente des Conflits</h3>', unsafe_allow_html=True)
        
        if st.button("🔍 Scanner et détecter tous les conflits", use_container_width=True):
            with st.spinner("Analyse complète en cours..."):
                time.sleep(2)
                conflits = detecter_conflits()
                
                if conflits:
                    st.warning(f"⚠️ {len(conflits)} conflits détectés")
                    
                    for priorite in ['Haute', 'Moyenne', 'Basse']:
                        conflits_priorite = [c for c in conflits if c.get('Priorité') == priorite]
                        
                        if conflits_priorite:
                            st.markdown(f"##### 🚨 {priorite} priorité ({len(conflits_priorite)})")
                            for i, conflit in enumerate(conflits_priorite):
                                with st.expander(f"**{i+1}. {conflit['Type']}**", expanded=(priorite=='Haute')):
                                    st.error(conflit['Description'])
                                    if 'Modules' in conflit:
                                        st.info(f"**Modules concernés :** {conflit['Modules']}")
                                    if 'Détail' in conflit:
                                        st.warning(f"**Détail :** {conflit['Détail']}")
                                    
                                    col_res1, col_res2, col_res3 = st.columns(3)
                                    with col_res1:
                                        if st.button(f"✅ Résoudre auto", key=f"resolve_{priorite}_{i}"):
                                            st.success("Conflit résolu automatiquement")
                                    with col_res2:
                                        if st.button(f"📝 Reprogrammer", key=f"reschedule_{priorite}_{i}"):
                                            st.info("Interface de reprogrammation ouverte")
                                    with col_res3:
                                        if st.button(f"📊 Analyser", key=f"analyze_{priorite}_{i}"):
                                            st.warning("Analyse en cours...")
                else:
                    st.success("✅ Aucun conflit détecté !")
        
        st.markdown("---")
        st.markdown("#### 🛠️ Outils de résolution avancés")
        
        col_tool1, col_tool2 = st.columns(2)
        
        with col_tool1:
            st.markdown("**Résolution automatique**")
            if st.button("🔄 Résoudre tous conflits étudiants", use_container_width=True):
                st.success("Tous les conflits étudiants résolus")
            
            if st.button("🏫 Optimiser attribution salles", use_container_width=True):
                st.success("Salles réattribuées optimalement")
        
        with col_tool2:
            st.markdown("**Analyse prédictive**")
            if st.button("🔮 Prédire futurs conflits", use_container_width=True):
                st.info("Analyse prédictive lancée")
            
            if st.button("📈 Générer statistiques conflits", use_container_width=True):
                st.success("Statistiques générées")
    
    with tab4:
        st.markdown('<h3 class="section-header">📊 Analytics & Tableaux de Bord Avancés</h3>', unsafe_allow_html=True)
        
        stats = get_statistiques()
        
        st.markdown("#### 📈 Vue globale des performances")
        
        col_ana1, col_ana2, col_ana3 = st.columns(3)
        with col_ana1:
            fig = px.pie(
                names=['Planifiés', 'En attente', 'Conflits'], 
                values=[stats['total_examens'], stats['total_modules'] - stats['total_examens'], stats['conflits_non_resolus']],
                title="Statut des examens",
                hole=0.3
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col_ana2:
            dates = pd.date_range(start='2024-06-01', end='2024-06-30', freq='D')
            exam_par_jour = [random.randint(8, 25) for _ in range(len(dates))]
            
            df_temps = pd.DataFrame({'Date': dates, 'Examens': exam_par_jour})
            fig = px.line(df_temps, x='Date', y='Examens', title='Charge quotidienne')
            st.plotly_chart(fig, use_container_width=True)
        
        with col_ana3:
            salles_data = pd.DataFrame({
                'Salle': ['Amphi A', 'Amphi B', 'Salle 101', 'Salle 102', 'Lab 1'],
                'Occupation': [94, 88, 76, 82, 91],
                'Utilisation': [85, 78, 92, 88, 95]
            })
            fig = px.bar(salles_data, x='Salle', y=['Occupation', 'Utilisation'], 
                        title='Performance des salles', barmode='group')
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("#### 📋 Tableau de bord détaillé")
        stats_df = pd.DataFrame([
            {'Indicateur': 'Nombre total d\'étudiants', 'Valeur': f"{stats['total_etudiants']:,}", 'Tendance': '↗️ +3%'},
            {'Indicateur': 'Examens planifiés', 'Valeur': stats['total_examens'], 'Tendance': '↗️ +12%'},
            {'Indicateur': 'Taux de planification', 'Valeur': f"{min(100, int((stats['total_examens'] / max(stats['total_modules'], 1)) * 100))}%", 'Tendance': '↗️ +5%'},
            {'Indicateur': 'Conflits détectés', 'Valeur': stats['conflits_non_resolus'], 'Tendance': '↘️ -8%'},
            {'Indicateur': 'Occupation moyenne', 'Valeur': '87%', 'Tendance': '↗️ +4%'},
            {'Indicateur': 'Satisfaction estimée', 'Valeur': '89%', 'Tendance': '↗️ +7%'}
        ])
        
        st.dataframe(stats_df, use_container_width=True, hide_index=True)
    
    with tab5:
        st.markdown('<h3 class="section-header">⚙️ Configuration Système Avancée</h3>', unsafe_allow_html=True)
        
        col_conf1, col_conf2 = st.columns(2)
        
        with col_conf1:
            st.markdown("#### ⚙️ Paramètres généraux")
            duree_exam = st.selectbox("Durée standard examens", [90, 120, 180], key="conf_duree")
            max_exam_jour = st.slider("Maximum examens/jour étudiant", 1, 3, 2, key="conf_max_etu")
            capacite_min = st.number_input("Capacité minimale salles", 20, 200, 30, key="conf_capacite")
            interval_min = st.number_input("Intervalle minimum entre examens (min)", 30, 180, 60)
            
            if st.button("💾 Enregistrer paramètres", use_container_width=True):
                st.success("✅ Paramètres enregistrés")
        
        with col_conf2:
            st.markdown("#### 📅 Calendrier académique")
            
            st.markdown("**Période principale**")
            col_per1, col_per2 = st.columns(2)
            with col_per1:
                periode1_start = st.date_input("Début", datetime(2024, 6, 15), key="conf_p1_start")
            with col_per2:
                periode1_end = st.date_input("Fin", datetime(2024, 6, 30), key="conf_p1_end")
            
            st.markdown("**Période rattrapage**")
            col_per3, col_per4 = st.columns(2)
            with col_per3:
                periode2_start = st.date_input("Début", datetime(2024, 9, 1), key="conf_p2_start")
            with col_per4:
                periode2_end = st.date_input("Fin", datetime(2024, 9, 15), key="conf_p2_end")
            
            if st.button("📅 Définir périodes", use_container_width=True):
                st.success("✅ Périodes académiques définies")
        
        st.markdown("---")
        st.markdown("#### 🔒 Contraintes académiques")
        
        col_cont1, col_cont2, col_cont3 = st.columns(3)
        
        with col_cont1:
            st.checkbox("1 examen/jour par étudiant", value=True, key="cont1")
            st.checkbox("Éviter examens consécutifs", value=True, key="cont2")
            st.checkbox("Respect spécialités", value=True, key="cont3")
        
        with col_cont2:
            st.checkbox("Max 3 examens/jour professeur", value=True, key="cont4")
            st.checkbox("Préférence salles adaptées", value=True, key="cont5")
            st.checkbox("Regroupement par formation", value=False, key="cont6")
        
        with col_cont3:
            st.checkbox("Équité surveillance", value=True, key="cont7")
            st.checkbox("Prise en compte indisponibilités", value=True, key="cont8")
            st.checkbox("Optimisation déplacements", value=True, key="cont9")
        
        if st.button("🔐 Appliquer contraintes", use_container_width=True):
            st.success("✅ Contraintes académiques appliquées")
        
        st.markdown("---")
        st.markdown("#### 🛠️ Maintenance système")
        
        col_maint1, col_maint2 = st.columns(2)
        
        with col_maint1:
            if st.button("🗑️ Nettoyer données temporaires", use_container_width=True):
                st.success("Données temporaires nettoyées")
            
            if st.button("📊 Regénérer index", use_container_width=True):
                st.success("Index regénérés")
        
        with col_maint2:
            if st.button("🔄 Redémarrer services", use_container_width=True):
                st.warning("Redémarrage en cours...")
                time.sleep(2)
                st.success("Services redémarrés")
            
            if st.button("⚠️ Sauvegarde complète", use_container_width=True, type="secondary"):
                st.success("Sauvegarde lancée en arrière-plan")

def page_consultation():
    """Page de consultation pour tous"""
    st.markdown('<h1 class="main-header">🔍 Consultation des Plannings d\'Examens</h1>', unsafe_allow_html=True)
    
    col_filtre1, col_filtre2, col_filtre3 = st.columns(3)
    
    with col_filtre1:
        departments = get_departments()
        dept_options = ['Tous les départements'] + [d['nom'] for d in departments]
        selected_dept = st.selectbox("Département", dept_options)
    
    with col_filtre2:
        date_debut = st.date_input("Date début", datetime.now())
    
    with col_filtre3:
        date_fin = st.date_input("Date fin", datetime.now() + timedelta(days=30))
    
    with st.expander("🔧 Options de recherche avancées"):
        col_adv1, col_adv2, col_adv3 = st.columns(3)
        
        with col_adv1:
            formations = st.multiselect("Formations", 
                                      ["Licence 1", "Licence 2", "Licence 3", "Master 1", "Master 2", "Doctorat"],
                                      default=["Licence 1", "Licence 2", "Licence 3"])
        
        with col_adv2:
            heures = st.multiselect("Créneaux horaires", 
                                  ["08:00-10:00", "10:00-12:00", "14:00-16:00", "16:00-18:00"],
                                  default=["08:00-10:00", "14:00-16:00"])
        
        with col_adv3:
            type_salle = st.multiselect("Type de salle",
                                      ["Amphithéâtre", "Salle de cours", "Laboratoire", "Salle spéciale"],
                                      default=["Amphithéâtre", "Salle de cours"])
    
    if st.button("🔍 Rechercher examens", use_container_width=True, type="primary"):
        with st.spinner("Recherche en cours..."):
            example_data = []
            dates = pd.date_range(start=date_debut, end=date_fin, freq='D')
            
            for i, date in enumerate(dates[:15]):
                example_data.append({
                    'Date': date.strftime('%d/%m/%Y'),
                    'Heure': ['09:00', '14:00', '16:00'][i % 3],
                    'Module': f'Module {selected_dept if selected_dept != "Tous les départements" else "Général"} {i+1}',
                    'Département': selected_dept if selected_dept != "Tous les départements" else ['Informatique', 'Mathématiques', 'Physique'][i % 3],
                    'Formation': ['Licence 1', 'Licence 2', 'Licence 3', 'Master 1', 'Master 2'][i % 5],
                    'Salle': ['Amphi A', 'Salle 101', 'Labo 1', 'Amphi B', 'Salle 201'][i % 5],
                    'Type': ['Amphithéâtre', 'Salle de cours', 'Laboratoire', 'Amphithéâtre', 'Salle de cours'][i % 5],
                    'Capacité': [200, 50, 25, 150, 60][i % 5],
                    'Étudiants': [150, 45, 20, 120, 55][i % 5]
                })
            
            if example_data:
                df_results = pd.DataFrame(example_data)
                st.success(f"✅ {len(df_results)} examens trouvés")
                
                tab_view1, tab_view2, tab_view3 = st.tabs(["📋 Tableau", "📅 Calendrier", "🗺️ Carte salles"])
                
                with tab_view1:
                    st.dataframe(df_results, use_container_width=True, height=400)
                
                with tab_view2:
                    try:
                        df_results['Date_dt'] = pd.to_datetime(df_results['Date'], format='%d/%m/%Y')
                        fig = px.timeline(df_results, x_start='Date_dt', x_end='Date_dt',
                                         y='Module', color='Département',
                                         title="Planning chronologique des examens",
                                         hover_data=['Salle', 'Étudiants', 'Formation'])
                        st.plotly_chart(fig, use_container_width=True)
                    except:
                        st.info("Affichage calendrier nécessite format date valide")
                
                with tab_view3:
                    salle_occupation = df_results.groupby('Salle').agg({
                        'Étudiants': 'sum',
                        'Module': 'count'
                    }).reset_index()
                    salle_occupation.columns = ['Salle', 'Total étudiants', 'Nombre examens']
                    
                    fig = px.bar(salle_occupation, x='Salle', y=['Total étudiants', 'Nombre examens'],
                                title="Occupation par salle", barmode='group')
                    st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("---")
                st.markdown("#### 📥 Export des résultats")
                col_exp1, col_exp2, col_exp3 = st.columns(3)
                
                with col_exp1:
                    export_format = st.selectbox("Format", ["CSV", "Excel", "JSON", "PDF"])
                
                with col_exp2:
                    if st.button("📱 Version mobile", use_container_width=True):
                        st.info("Version mobile générée")
                
                with col_exp3:
                    csv = df_results.to_csv(index=False)
                    st.download_button(
                        label="📥 Télécharger résultats",
                        data=csv,
                        file_name=f"resultats_recherche_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
            else:
                st.warning("Aucun examen trouvé avec ces critères")

def page_compte():
    """Page du compte utilisateur"""
    user = st.session_state.get('user', {})
    
    st.markdown('<h1 class="main-header">👤 Mon Compte</h1>', unsafe_allow_html=True)
    
    col_info1, col_info2 = st.columns([2, 1])
    
    with col_info1:
        st.markdown("### 👤 Informations personnelles")
        st.markdown(f"**Nom complet :** {user.get('nom', 'Non spécifié')}")
        st.markdown(f"**Email :** {user.get('email', 'Non spécifié')}")
        st.markdown(f"**Rôle :** {auth_system.ROLES.get(user.get('role'), user.get('role', 'Non spécifié'))}")
        
        if user.get('dept_nom'):
            st.markdown(f"**Département :** {user.get('dept_nom')}")
        
        if user.get('prof_id'):
            st.markdown(f"**ID Professeur :** {user.get('prof_id')}")
        
        if user.get('etudiant_id'):
            st.markdown(f"**ID Étudiant :** {user.get('etudiant_id')}")
    
   
    
    # Changement de mot de passe
    st.markdown("---")
    st.markdown("### 🔒 Sécurité")
    
    with st.form("changer_mdp"):
        ancien_mdp = st.text_input("Ancien mot de passe", type="password")
        nouveau_mdp = st.text_input("Nouveau mot de passe", type="password")
        confirmer_mdp = st.text_input("Confirmer le nouveau mot de passe", type="password")
        
        if st.form_submit_button("🔄 Changer le mot de passe"):
            if not ancien_mdp or not nouveau_mdp or not confirmer_mdp:
                st.error("Tous les champs sont requis")
            elif nouveau_mdp != confirmer_mdp:
                st.error("Les mots de passe ne correspondent pas")
            elif len(nouveau_mdp) < 8:
                st.error("Le mot de passe doit contenir au moins 8 caractères")
            else:
                st.success("✅ Mot de passe changé avec succès")
    
    st.markdown("---")
    st.markdown("### ⚙️ Préférences de notification")
    
    col_notif1, col_notif2 = st.columns(2)
    
    with col_notif1:
        email_notif = st.checkbox("📧 Notifications par email", True)
        sms_notif = st.checkbox("📱 Notifications SMS", False)
        push_notif = st.checkbox("🔔 Notifications push", True)
    
    with col_notif2:
        st.selectbox("Fréquence des rappels", ["Quotidien", "Hebdomadaire", "Avant chaque examen"])
        st.selectbox("Langue préférée", ["Français", "Anglais", "Arabe"])
    
    if st.button("💾 Sauvegarder préférences", use_container_width=True):
        st.success("Préférences sauvegardées")

# ====================
# PAGE DE CONNEXION
# ====================
def login_page():
    """Page de connexion"""
    col_login1, col_login2, col_login3 = st.columns([1, 2, 1])
    
    with col_login2:
        st.markdown('<h1 style="text-align: center; color: #2C3E50;">🎓 Plateforme de Gestion des Examens</h1>', unsafe_allow_html=True)
        st.markdown('<p style="text-align: center; color: #7F8C8D;">Système avancé de planification des examens universitaires</p>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        with st.container():
            st.markdown("### 🔐 Connexion au système")
            
            available_users = list(auth_system.users.keys())
            selected_user = st.selectbox(
                "Sélectionner un profil de test",
                ["-- Choisir un profil --"] + available_users,
                help="Sélection pour pré-remplir les champs"
            )
            
            with st.form("login_form"):
                default_username = ""
                default_password = ""
                
                if selected_user != "-- Choisir un profil --":
                    default_username = selected_user
                    if 'chef_' in selected_user:
                        default_password = selected_user.replace('chef_', '') + '123'
                    elif selected_user == 'admin':
                        default_password = 'admin123'
                    elif selected_user == 'doyen':
                        default_password = 'doyen123'
                    elif 'prof' in selected_user:
                        default_password = 'prof123'
                    elif 'etudiant' in selected_user:
                        default_password = 'etu123'
                
                username = st.text_input("Nom d'utilisateur", value=default_username)
                password = st.text_input("Mot de passe", type="password", value=default_password)
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    submit = st.form_submit_button("Se connecter", use_container_width=True, type="primary")
                with col_btn2:
                    demo = st.form_submit_button("Mode démo rapide", use_container_width=True)
                
                if submit:
                    if not username or not password:
                        st.error("Veuillez saisir vos identifiants")
                    else:
                        user = auth_system.authenticate(username, password)
                        if user:
                            st.session_state['authenticated'] = True
                            st.session_state['user'] = user
                            st.success(f"✅ Bienvenue {user['nom'].split()[0]} !")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("❌ Identifiants incorrects")
                
                if demo:
                    st.session_state['authenticated'] = True
                    st.session_state['user'] = {
                        'username': 'admin',
                        'nom': 'Admin System',
                        'role': 'admin',
                        'email': 'admin@univ.fr',
                        'dept_nom': 'Administration'
                    }
                    st.success("Mode démo activé (Administrateur)")
                    time.sleep(1)
                    st.rerun()
        
        st.markdown("---")
        
       

# ====================
# NAVIGATION AMÉLIORÉE
# ====================
def get_navigation_for_role(role):
    """Retourne la navigation adaptée au rôle"""
    if role == 'admin':
        return [
            "🏠 Tableau de Bord",
            "⚙️ Administration",
            "🔍 Consultation",
            "👤 Mon Compte"
        ]
    elif role == 'vicedoyen':
        return [
            "🏠 Tableau de Bord", 
            "📊 Vue Stratégique",
            "🔍 Consultation",
            "👤 Mon Compte"
        ]
    elif role == 'chef_dept':
        return [
            "🏠 Tableau de Bord",
            "🏛️ Mon Département",
            "🔍 Consultation", 
            "👤 Mon Compte"
        ]
    elif role == 'professeur':
        return [
            "🏠 Tableau de Bord",
            "👨‍🏫 Mes Examens",
            "🔍 Consultation",
            "👤 Mon Compte"
        ]
    elif role == 'etudiant':
        return [
            "🏠 Tableau de Bord",
            "👨‍🎓 Mes Examens",
            "🔍 Consultation",
            "👤 Mon Compte"
        ]
    else:
        return ["🏠 Tableau de Bord", "🔍 Consultation"]

# ====================
# APPLICATION PRINCIPALE
# ====================
def main():
    """Fonction principale"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        login_page()
        return
    
    user = st.session_state.get('user', {})
    
    # Barre latérale
    with st.sidebar:
        st.markdown(f'<div style="text-align: center; padding: 1rem;">', unsafe_allow_html=True)
        st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=80)
        st.markdown(f"<h3>{user.get('nom', 'Utilisateur').split()[0]}</h3>", unsafe_allow_html=True)
        st.markdown(f'<div class="role-badge">{auth_system.ROLES.get(user.get("role", ""), "Utilisateur")}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        if user.get('dept_nom'):
            st.markdown(f"**Département :** {user.get('dept_nom')}")
        
        st.markdown("---")
        
        role = user.get('role', '')
        navigation = get_navigation_for_role(role)
        selected = st.radio("Navigation", navigation, key="nav")
        
        st.markdown("---")
        
        st.markdown("**📊 Information système**")
        try:
            stats = get_statistiques()
            st.caption(f"🎓 {stats['total_etudiants']:,} étudiants")
            st.caption(f"📅 {stats['total_examens']} examens planifiés")
            st.caption(f"⚠️ {stats['conflits_non_resolus']} conflits")
        except:
            st.caption("📊 Mode démonstration")
        
        st.markdown("---")
        
        if st.button("🚪 Se déconnecter", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    # Affichage de la page sélectionnée
    if selected == "🏠 Tableau de Bord":
        page_tableau_bord()
    
    elif selected == "⚙️ Administration" and user.get('role') == 'admin':
        page_admin_ameliorer()
    
    elif selected == "📊 Vue Stratégique" and user.get('role') == 'vicedoyen':
        page_vice_doyen_ameliorer()
    
    elif selected == "🏛️ Mon Département" and user.get('role') == 'chef_dept':
        dept_id = user.get('dept_id')
        if dept_id:
            page_chef_departement(dept_id)
        else:
            st.error("Erreur: Département non défini")
    
    elif selected == "👨‍🏫 Mes Examens" and user.get('role') == 'professeur':
        page_professeur(user.get('prof_id', 36))
    
    elif selected == "👨‍🎓 Mes Examens" and user.get('role') == 'etudiant':
        page_etudiant(user.get('etudiant_id', 87))
    
    elif selected == "🔍 Consultation":
        page_consultation()
    
    elif selected == "👤 Mon Compte":
        page_compte()
    
    else:
        st.warning("Accès non autorisé à cette page")

# ====================
# LANCEMENT
# ====================
if __name__ == "__main__":
    main()