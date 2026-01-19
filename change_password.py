import streamlit as st
from auth import get_auth_system

st.set_page_config(page_title="Changer mot de passe", page_icon="🔐")

auth = get_auth_system()

st.title("🔐 Changer mon mot de passe")

if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.warning("Veuillez vous connecter d'abord")
    st.stop()

user_data = st.session_state.user_data

with st.form("change_password_form"):
    st.write(f"Utilisateur: **{user_data['username']}**")
    
    old_password = st.text_input("Ancien mot de passe", type="password")
    new_password = st.text_input("Nouveau mot de passe", type="password")
    confirm_password = st.text_input("Confirmer le nouveau mot de passe", type="password")
    
    submitted = st.form_submit_button("Changer le mot de passe", type="primary")
    
    if submitted:
        if not old_password or not new_password:
            st.error("Veuillez remplir tous les champs")
        elif new_password != confirm_password:
            st.error("Les nouveaux mots de passe ne correspondent pas")
        elif len(new_password) < 6:
            st.error("Le mot de passe doit contenir au moins 6 caractères")
        else:
            success, message = auth.change_password(
                user_data['user_id'],
                old_password,
                new_password
            )
            
            if success:
                st.success(message)
                st.balloons()
            else:
                st.error(message)

st.markdown("---")
if st.button("Retour à l'accueil"):
    st.switch_page("app.py")