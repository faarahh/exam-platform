import streamlit as st
import mysql.connector
import pandas as pd
from auth import get_auth_system

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'examens'
}

st.set_page_config(page_title="Gestion des utilisateurs", page_icon="👥")

auth = get_auth_system()

st.title("👥 Gestion des utilisateurs")

# Vérifier les permissions
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.warning("Veuillez vous connecter d'abord")
    st.stop()

user_data = st.session_state.user_data
if not auth.has_permission(user_data, 'all_permissions'):
    st.error("⛔ Accès réservé aux administrateurs")
    st.stop()

# Onglets
tab1, tab2, tab3 = st.tabs(["Utilisateurs", "Ajouter", "Statistiques"])

with tab1:
    st.subheader("📋 Liste des utilisateurs")
    
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT u.id, u.username, u.email, u.nom, u.prenom, 
                   r.nom as role, u.is_active, u.created_at
            FROM utilisateurs u
            JOIN roles r ON u.role_id = r.id
            ORDER BY u.created_at DESC
        """)
        
        users = cursor.fetchall()
        
        if users:
            df = pd.DataFrame(users)
            df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%d/%m/%Y')
            df['is_active'] = df['is_active'].apply(lambda x: '✅' if x else '❌')
            
            st.dataframe(
                df.rename(columns={
                    'username': 'Nom utilisateur',
                    'email': 'Email',
                    'nom': 'Nom',
                    'prenom': 'Prénom',
                    'role': 'Rôle',
                    'is_active': 'Actif',
                    'created_at': 'Créé le'
                }),
                use_container_width=True,
                hide_index=True
            )
            
            # Actions rapides
            st.subheader("⚡ Actions rapides")
            
            user_id = st.number_input("ID utilisateur", min_value=1, step=1)
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Désactiver", type="secondary"):
                    cursor.execute(
                        "UPDATE utilisateurs SET is_active = FALSE WHERE id = %s",
                        (user_id,)
                    )
                    conn.commit()
                    st.success(f"Utilisateur {user_id} désactivé")
                    st.rerun()
            
            with col2:
                if st.button("Réactiver", type="secondary"):
                    cursor.execute(
                        "UPDATE utilisateurs SET is_active = TRUE WHERE id = %s",
                        (user_id,)
                    )
                    conn.commit()
                    st.success(f"Utilisateur {user_id} réactivé")
                    st.rerun()
        
        else:
            st.info("Aucun utilisateur trouvé")
    
    except mysql.connector.Error as err:
        st.error(f"Erreur: {err}")
    finally:
        cursor.close()
        conn.close()

with tab2:
    st.subheader("➕ Ajouter un utilisateur")
    
    with st.form("add_user_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            username = st.text_input("Nom d'utilisateur *")
            email = st.text_input("Email *")
            password = st.text_input("Mot de passe *", type="password")
        
        with col2:
            nom = st.text_input("Nom")
            prenom = st.text_input("Prénom")
            
            cursor = conn.cursor()
            cursor.execute("SELECT id, nom FROM roles ORDER BY nom")
            roles = cursor.fetchall()
            role_options = {nom: id for id, nom in roles}
            selected_role = st.selectbox("Rôle *", list(role_options.keys()))
        
        submitted = st.form_submit_button("Créer l'utilisateur", type="primary")
        
        if submitted:
            if not username or not email or not password or not selected_role:
                st.error("Veuillez remplir les champs obligatoires (*)")
            else:
                success, message = auth.register_user(
                    username, email, password, selected_role.lower(),
                    nom=nom, prenom=prenom
                )
                
                if success:
                    st.success(message)
                    st.balloons()
                else:
                    st.error(message)

with tab3:
    st.subheader("📊 Statistiques des utilisateurs")
    
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT r.nom as role, COUNT(u.id) as nb_users,
                   SUM(CASE WHEN u.is_active = 1 THEN 1 ELSE 0 END) as actifs,
                   MIN(u.created_at) as premier_inscrit,
                   MAX(u.last_login) as derniere_connexion
            FROM roles r
            LEFT JOIN utilisateurs u ON r.id = u.role_id
            GROUP BY r.id
            ORDER BY nb_users DESC
        """)
        
        stats = cursor.fetchall()
        
        if stats:
            df_stats = pd.DataFrame(stats)
            
            # Graphique
            st.bar_chart(df_stats.set_index('role')[['nb_users', 'actifs']])
            
            # Tableau détaillé
            st.dataframe(
                df_stats.rename(columns={
                    'role': 'Rôle',
                    'nb_users': 'Total',
                    'actifs': 'Actifs',
                    'premier_inscrit': 'Premier inscrit',
                    'derniere_connexion': 'Dernière connexion'
                }),
                use_container_width=True
            )
        
        # Activité récente
        st.subheader("🕒 Activité récente (24h)")
        
        cursor.execute("""
            SELECT u.username, ll.login_time, ll.ip_address, ll.success
            FROM login_logs ll
            JOIN utilisateurs u ON ll.user_id = u.id
            WHERE ll.login_time >= DATE_SUB(NOW(), INTERVAL 1 DAY)
            ORDER BY ll.login_time DESC
            LIMIT 20
        """)
        
        recent = cursor.fetchall()
        
        if recent:
            df_recent = pd.DataFrame(recent)
            df_recent['login_time'] = pd.to_datetime(df_recent['login_time']).dt.strftime('%H:%M')
            df_recent['success'] = df_recent['success'].apply(lambda x: '✅' if x else '❌')
            
            st.dataframe(
                df_recent.rename(columns={
                    'username': 'Utilisateur',
                    'login_time': 'Heure',
                    'ip_address': 'IP',
                    'success': 'Succès'
                }),
                use_container_width=True
            )
        else:
            st.info("Aucune activité récente")
    
    except mysql.connector.Error as err:
        st.error(f"Erreur: {err}")
    finally:
        cursor.close()
        conn.close()

st.markdown("---")
if st.button("Retour à l'accueil"):
    st.switch_page("app.py")