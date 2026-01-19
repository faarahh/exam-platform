import streamlit as st
import mysql.connector
from datetime import datetime, timedelta

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'examens'
}

st.set_page_config(page_title="Mon activité", page_icon="📋")

st.title("📋 Mon activité")

if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.warning("Veuillez vous connecter d'abord")
    st.stop()

user_data = st.session_state.user_data

# Connexion à la base
conn = mysql.connector.connect(**DB_CONFIG)
cursor = conn.cursor(dictionary=True)

try:
    # Historique des connexions
    st.subheader("📊 Historique des connexions")
    
    cursor.execute("""
        SELECT login_time, ip_address, success
        FROM login_logs
        WHERE user_id = %s
        ORDER BY login_time DESC
        LIMIT 10
    """, (user_data['user_id'],))
    
    logins = cursor.fetchall()
    
    if logins:
        import pandas as pd
        df_logins = pd.DataFrame(logins)
        df_logins['login_time'] = pd.to_datetime(df_logins['login_time']).dt.strftime('%d/%m/%Y %H:%M')
        df_logins['success'] = df_logins['success'].apply(lambda x: '✅ Réussi' if x else '❌ Échoué')
        
        st.dataframe(
            df_logins.rename(columns={
                'login_time': 'Date/Heure',
                'ip_address': 'Adresse IP',
                'success': 'Statut'
            }),
            use_container_width=True
        )
    else:
        st.info("Aucune connexion enregistrée")
    
    # Statistiques
    st.subheader("📈 Statistiques d'utilisation")
    
    cursor.execute("""
        SELECT 
            COUNT(*) as total_logins,
            SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_logins,
            MIN(login_time) as first_login,
            MAX(login_time) as last_login
        FROM login_logs
        WHERE user_id = %s
    """, (user_data['user_id'],))
    
    stats = cursor.fetchone()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Connexions totales", stats['total_logins'])
    with col2:
        if stats['total_logins'] > 0:
            taux = (stats['successful_logins'] / stats['total_logins']) * 100
            st.metric("Taux de succès", f"{taux:.1f}%")
    with col3:
        if stats['first_login']:
            st.metric("Première connexion", stats['first_login'].strftime('%d/%m/%Y'))

except mysql.connector.Error as err:
    st.error(f"Erreur: {err}")
finally:
    cursor.close()
    conn.close()

st.markdown("---")
if st.button("Retour à l'accueil"):
    st.switch_page("app.py")