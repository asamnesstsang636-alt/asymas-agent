import streamlit as st
import os
from groq import Groq
from database import init_db, get_inventaire, get_clients, add_product, add_client, delete_item

st.set_page_config(page_title="ASYMAS BUSINESS", layout="wide")

# Init DB + Groq
init_db()
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def get_asymas_context():
    """Récupère tout le cerveau ASYMAS depuis la DB"""
    inventaire = get_inventaire()
    clients = get_clients()

    context = f"""
    === INVENTAIRE ASYMAS LIVE ===
    {inventaire.to_string(index=False)}

    === PREUVES CLIENTS ASYMAS ===
    {clients.to_string(index=False)}

    RÈGLES OBLIGATOIRES :
    1. Utilise UNIQUEMENT ces données ASYMAS. N'invente rien.
    2. Ne révèle JAMAIS les prix d'achat au client. Calcule la marge en interne.
    3. Cite TOUJOURS un vrai client ASYMAS dans tes messages.
    4. Si stock = 0, propose une alternative ou précommande.
    """
    return context

st.title("Agent Commercial ASYMAS V2")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "✍️ Message Perso",
    "🔍 Prospection Auto",
    "🔁 Agent de Relance",
    "📊 Dashboard",
    "⚙️ Admin ASYMAS"
])

# MODULE 1: MESSAGE PERSO
with tab1:
    st.subheader("Génère un message LinkedIn avec l'inventaire ASYMAS réel")
    profil = st.text_area("Colle le profil LinkedIn brut du prospect",
                          height=150,
                          placeholder="Ex: Patrick Mukendi, CEO de Kivu Digital, 12 employés, Bukavu. Site web 2018, pas responsive...")

    if st.button("Générer message perso", type="primary"):
        if profil:
            with st.spinner("ASYMAS rédige avec les vraies données..."):
                system_prompt = get_asymas_context()
                user_prompt = f"""
                Prospect : {profil}

                Rédige un message LinkedIn de prospection court, direct, 0 blabla.
                Structure obligatoire:
                1. Hook personnalisé basé sur le profil
                2. Preuve sociale : cite 1 client ASYMAS de la base + résultat chiffré
                3. Propose 1 service/article ASYMAS en stock qui règle son pain point
                4. CTA pour un call de 15min avec 2 dates précises cette semaine

                Style: Tutoiement, phrases courtes. Max 80 mots.
                """
                chat_completion = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    model="llama-3.1-70b-versatile",
                    temperature=0.7,
                )
                st.success("Message prêt à copier-coller :")
                st.code(chat_completion.choices[0].message.content, language=None)
        else:
            st.warning("Colle un profil d'abord")

# MODULE 2: PROSPECTION AUTO
with tab2:
    st.subheader("Trouve des prospects pour les produits ASYMAS en stock")
    col1, col2 = st.columns(2)
    with col1:
        secteur = st.text_input("Secteur d'activité", "Cliniques")
        ville = st.text_input("Ville", "Bukavu")
    with col2:
        nombre = st.slider("Nombre de prospects", 1, 10, 3)

    if st.button("Lancer la prospection IA", type="primary"):
        with st.spinner(f"ASYMAS scanne {secteur} à {ville}..."):
            system_prompt = get_asymas_context()
            user_prompt = f"""
            Génère {nombre} prospects réalistes pour {secteur} à {ville}, RDC.
            Pour chaque prospect donne: Nom Prénom | Poste | Entreprise | Pain point | Quel produit/service ASYMAS en stock lui proposer
            Format: Tableau markdown uniquement. Base-toi sur l'inventaire ASYMAS fourni.
            """
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model="llama-3.1-70b-versatile",
            )
            st.markdown(chat_completion.choices[0].message.content)

# MODULE 3: AGENT DE RELANCE
with tab3:
    st.subheader("Crée un planning de relance avec preuves ASYMAS")
    contexte = st.text_area("Contexte de la relance",
                           "Le prospect a demandé un devis pour un site vitrine il y a 3 jours")
    duree = st.selectbox("Durée du cycle", ["7 jours", "14 jours", "21 jours"])

    if st.button("Générer le planning", type="primary"):
        with st.spinner("ASYMAS planifie avec tes vrais clients..."):
            system_prompt = get_asymas_context()
            user_prompt = f"""
            Crée un planning de relance email/LinkedIn sur {duree}.
            Contexte: {contexte}
            Pour chaque relance donne: Jour | Canal | Objet | Corps <50 mots | Objectif
            Obligation: Cite 1 client ASYMAS différent à chaque relance comme preuve.
            Format: Tableau markdown. Ton: Direct, valeur, sans pression. 3 à 5 relances max.
            """
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model="llama-3.1-70b-versatile",
            )
            st.markdown(chat_completion.choices[0].message.content)

# MODULE 4: DASHBOARD
with tab4:
    st.subheader("Dashboard ASYMAS LIVE")
    inv = get_inventaire()
    cli = get_clients()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Articles en stock", len(inv))
    col2.metric("Clients ASYMAS", len(cli))
    col3.metric("Valeur stock", f"{(inv['prix_vente'] * inv['stock']).sum():.0f}$")
    col4.metric("CA Clients", f"{cli['montant_paye'].sum():.0f}$")

    st.dataframe(inv, use_container_width=True)

# MODULE 5: ADMIN ASYMAS
with tab5:
    st.header("⚙️ Cerveau ASYMAS - Ajoute tes données ici")

    admin_tab1, admin_tab2 = st.tabs(["📦 Inventaire", "🏆 Clients Preuves"])

    with admin_tab1:
        st.subheader("Ajouter Service / Article")
        with st.form("add_product"):
            col1, col2 = st.columns(2)
            nom = col1.text_input("Nom*")
            type_prod = col2.selectbox("Type", ["Service", "Article", "Formation"])
            col3, col4, col5 = st.columns(3)
            prix_achat = col3.number_input("Prix Achat $", min_value=0.0, step=10.0)
            prix_vente = col4.number_input("Prix Vente $*", min_value=0.0, step=10.0)
            stock = col5.number_input("Stock*", min_value=0, value=999 if type_prod=="Service" else 1)
            desc = st.text_area("Description")
            if st.form_submit_button("Ajouter", type="primary"):
                if nom and prix_vente:
                    add_product(nom, prix_achat, prix_vente, stock, desc, type_prod)
                    st.success(f"{nom} ajouté au cerveau ASYMAS!")
                    st.rerun()

        st.subheader("Inventaire Actuel")
        st.dataframe(get_inventaire(), use_container_width=True)

    with admin_tab2:
        st.subheader("Ajouter Preuve Client")
        with st.form("add_client"):
            col1, col2 = st.columns(2)
            nom = col1.text_input("Nom Client*")
            entreprise = col2.text_input("Entreprise*")
            resultat = st.text_input("Résultat chiffré*", placeholder="Ex: +80 RDV/mois en 45j")
            montant = st.number_input("Montant payé $*", min_value=0.0, step=50.0)
            if st.form_submit_button("Ajouter Preuve", type="primary"):
                if nom and entreprise and resultat:
                    add_client(nom, entreprise, resultat, montant)
                    st.success(f"Preuve {entreprise} ajoutée!")
                    st.rerun()

        st.subheader("Clients ASYMAS")
        st.dataframe(get_clients(), use_container_width=True)

# Check WhatsApp
if st.secrets.get("WA_PHONE_ID", "non_configuré") == "non_configuré":
    st.sidebar.warning("WhatsApp Business API non configuré")
else:
    st.sidebar.success("WhatsApp API: Connecté ✅")
