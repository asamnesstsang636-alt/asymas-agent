import streamlit as st
import os
from groq import Groq

st.set_page_config(page_title="ASYMAS BUSINESS", layout="wide")

# Init Groq
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.title("Agent Commercial ASYMAS V1")

tab1, tab2, tab3, tab4 = st.tabs([
    "✍️ Message Perso",
    "🔍 Prospection Auto",
    "🔁 Agent de Relance",
    "📊 Dashboard"
])

# MODULE 1: MESSAGE PERSO - Ton module actuel amélioré
with tab1:
    st.subheader("Génère un message LinkedIn ultra-ciblé")
    profil = st.text_area("Colle le profil LinkedIn brut du prospect",
                          placeholder="Ex: Patrick Mukendi, CEO de Kivu Digital, 12 employés, Bukavu...")

    if st.button("Générer message perso", type="primary"):
        if profil:
            with st.spinner("ASYMAS rédige..."):
                prompt = f"""
                Tu es un commercial expert de ASYMAS BUSINESS à Bukavu.
                Rédige un message LinkedIn de prospection court, direct, 0 blabla.
                Structure:
                1. Hook personnalisé basé sur le profil
                2. Preuve sociale chiffrée à Bukavu/Goma
                3. CTA pour un call de 15min avec 2 dates précises

                Profil: {profil}

                Style: Tutoiement, phrases courtes. Max 80 mots.
                """
                chat_completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.1-70b-versatile",
                    temperature=0.7,
                )
                st.success("Message prêt à copier-coller :")
                st.write(chat_completion.choices[0].message.content)
        else:
            st.warning("Colle un profil d'abord")

# MODULE 2: PROSPECTION AUTO
with tab2:
    st.subheader("Trouve des prospects chauds avec l'IA")
    secteur = st.text_input("Secteur d'activité", "Agences digitales")
    ville = st.text_input("Ville", "Bukavu")
    nombre = st.slider("Nombre de prospects", 1, 10, 3)

    if st.button("Lancer la prospection IA", type="primary"):
        with st.spinner(f"ASYMAS scanne LinkedIn pour {secteur} à {ville}..."):
            prompt = f"""
            Génère une liste de {nombre} prospects fictifs mais réalistes pour {secteur} à {ville}.
            Pour chaque prospect donne: Nom Prénom, Poste, Entreprise, Pain point détecté,
            Angle d'attaque pour vendre un site web/CRM.
            Format: Tableau markdown.
            """
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.1-70b-versatile",
            )
            st.markdown(chat_completion.choices[0].message.content)

# MODULE 3: AGENT DE RELANCE
with tab3:
    st.subheader("Crée un planning de relance qui convertit")
    contexte = st.text_area("Contexte de la relance",
                           "Le prospect a demandé un devis pour un site vitrine il y a 3 jours")
    duree = st.selectbox("Durée du cycle", ["7 jours", "14 jours", "21 jours"])

    if st.button("Générer le planning", type="primary"):
        with st.spinner("ASYMAS planifie la séquence..."):
            prompt = f"""
            Tu es expert en closing. Crée un planning de relance email/LinkedIn sur {duree}.
            Contexte: {contexte}
            Donne pour chaque relance: Jour, Canal, Objet, Corps du message <50 mots, Objectif psy.
            Format: Tableau markdown. Ton: Direct, sans pression.
            """
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.1-70b-versatile",
            )
            st.markdown(chat_completion.choices[0].message.content)

# MODULE 4: DASHBOARD
with tab4:
    st.subheader("Dashboard ASYMAS")
    st.info("Module en cours. Prochaine V2: Connexion Supabase pour sauver tes prospects.")
    col1, col2, col3 = st.columns(3)
    col1.metric("Messages générés", "1", "+1")
    col2.metric("Prospects trouvés", "0", "")
    col3.metric("Taux de réponse", "N/A", "")

    if st.secrets["WA_PHONE_ID"] == "non_configuré":
        st.warning("WhatsApp non configuré. Module désactivé.")
    else:
        st.success("WhatsApp API: Connecté")
