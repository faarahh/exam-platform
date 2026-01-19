import streamlit as st

# Simuler une base d'utilisateurs
USERS = {
    "admin": "admin123",
    "user": "password123"
}

def check_login(username, password):
    return USERS.get(username) == password

def login_page():
    st.title("🔐 Connexion")
    
    with st.form("login_form"):
        username = st.text_input("Nom d'utilisateur")
        password = st.text_input("Mot de passe", type="password")
        submitted = st.form_submit_button("Se connecter")
        
        if submitted:
            if check_login(username, password):
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.success("Connexion réussie !")
                st.rerun()
            else:
                st.error("Identifiants incorrects")

def main_app():
    st.title("Bienvenue sur l'app")
    st.write(f"Connecté en tant que {st.session_state['username']}")
    # Ton app principale ici

# Initialisation de la session
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# Router
if st.session_state["logged_in"]:
    main_app()
else:
    login_page()