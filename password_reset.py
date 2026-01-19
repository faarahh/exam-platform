import streamlit as st
import re

st.set_page_config(page_title="Réinitialisation mot de passe", page_icon="🔑")

st.title("🔑 Réinitialisation du mot de passe")

st.info("""
Si vous avez oublié votre mot de passe, veuillez contacter l'administration:
- 📧 support-edt@univ.fr
- 📞 01 23 45 67 89
- 🏢 Bureau A12, Bâtiment Principal
""")

with st.form("reset_request"):
    email = st.text_input("Adresse email universitaire", 
                         placeholder="prenom.nom@univ.fr")
    
    submitted = st.form_submit_button("Demander une réinitialisation")
    
    if submitted:
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            st.error("Veuillez entrer une adresse email valide")
        else:
            # Simuler l'envoi d'email
            st.success(f"📧 Un email de réinitialisation a été envoyé à {email}")
            st.info("""
            **Instructions simulées:**
            1. Vérifiez votre boîte mail
            2. Cliquez sur le lien de réinitialisation
            3. Choisissez un nouveau mot de passe
            4. Reconnectez-vous avec vos nouveaux identifiants
            """)

st.markdown("---")
st.markdown("**Rappel:** Votre nom d'utilisateur est généralement votre numéro étudiant ou votre email universitaire.")

if st.button("Retour à la connexion"):
    st.switch_page("app.py")