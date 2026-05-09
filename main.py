import streamlit as st
import pandas as pd
from supabase import create_client
from datetime import datetime
import requests
from groq import Groq

st.set_page_config(
    page_title="ASYMAS Agent",
    page_icon="🤖",
    layout="wide"
)

@st.cache_resource
def init_supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

@st.cache_resource
def init_groq():
    return Groq(api_key=st.secrets["GROQ_API_KEY"])

supabase = init_supabase()
groq = init_groq()

def send_whatsapp(tel, message):
    try:
        url = f"https://graph.facebook.com/v18.0/{st.secrets['WA_PHONE_ID']}/messages"
        headers = {
            "Authorization": f"Bearer {st.secrets['WA_TOKEN']}",
            "Content-Type": "application/json"
        }
        data = {
            "messaging_product": "whatsapp",
            "to": tel,
            "type": "text",
            "text": {"body": message}
        }
        r = requests.post(url, headers=headers, json=data, timeout=10)
        return r.status_code == 200
    except Exception as e:
        st.error(f"Erreur WhatsApp: {e}")
        return False

def log_conversation(identifiant, message, canal, direction="envoye"):
    is_email = "@" in identifiant
    field = "email" if is_email else "tel"
    
    contact = supabase.table("contacts").select("id").eq(field, identifiant).execute()
    
    if contact.data:
        contact_id = contact.data[0]['id']
    else:
        new_contact = supabase.table("contacts").insert({
            field: identifiant, 
            "nom": "Auto",
            "canal_prefere": canal
        }).execute()
        contact_id = new_contact.data[0]['id']

    supabase.table("conversations").insert({
        "contact_id": contact_id,
        "canal": canal,
        "direction": direction,
        "message": message,
        "statut": "envoye",
        "agent_auto": True
    }).execute()

def ia_generer_message_commercial(profil):
    prompt = f"""Tu es le commercial senior d'ASYMAS, entreprise IT à Bukavu, RDC.
    ASYMAS propose : développement d'applications de gestion, automatisation de processus, formation digitale pour PME.
    
    Profil du prospect LinkedIn : {profil}
    
    Rédige un premier message de prospection.
    Contraintes OBLIGATOIRES :
    1. 350 caractères maximum
    2. Parle du problème du prospect, pas de toi
    3. Zéro phrase bateau "j'espère que vous allez bien"
    4. Propose une valeur claire en 1 phrase
    5. Termine par : "Dispo pour 15min jeudi ou vendredi?"
    """

    try:
        res = groq.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=150
        )
        return res.choices[0].message.content
    except Exception as e:
        return f"Erreur IA: {e}"

st.title("🤖 ASYMAS Agent")
st.caption("Agent Commercial + Inventaire + Broadcast + CRM avec mémoire")

menu = st.sidebar.selectbox(
    "Choisir un module",
    ["1. Commercial IA", "2. Envoi Rapide", "3. Inventaire IA", "4. CRM Mémoire"]
)

if menu == "1. Commercial IA":
    st.subheader("Génère un message LinkedIn qui convertit")
    profil_linkedin = st.text_area(
        "Colle le profil LinkedIn brut du prospect",
        height=150,
        placeholder="Ex: Aline Mbayo, DG Pharmacie du Lac, 12 employés. Poste: On perd 2h par jour sur l'inventaire manuel..."
    )
    
    if st.button("🧠 Générer avec IA", type="primary"):
        if profil_linkedin:
            with st.spinner("L'agent analyse le profil..."):
                message = ia_generer_message_commercial(profil_linkedin)
            st.success("Message prêt à copier-coller sur LinkedIn :")
            st.code(message, language=None)
        else:
            st.warning("Colle un profil LinkedIn d'abord")

elif menu == "2. Envoi Rapide":
    st.subheader("📲 Envoie WhatsApp/Email + l'agent mémorise")
    
    destinataires = st.text_area(
        "Numéros ou emails séparés par virgule",
        placeholder="0971234567, jean@kivu.cd, 0819876543"
    )
    message_a_envoyer = st.text_area("Ton message", height=100)
    canal = st.radio("Canal d'envoi", ["WhatsApp", "Email"], horizontal=True)

    if st.button("Envoyer à tous + Mémoriser", type="primary"):
        if destinataires and message_a_envoyer:
            liste_dests = [d.strip() for d in destinataires.split(',') if d.strip()]
            succes = 0
            
            progress = st.progress(0)
            for i, dest in enumerate(liste_dests):
                envoye = False
                if canal == "WhatsApp" and dest.startswith("0"):
                    envoye = send_whatsapp(dest, message_a_envoyer)
                    if envoye: succes += 1
                
                log_conversation(dest, message_a_envoyer, canal.lower())
                progress.progress((i + 1) / len(liste_dests))
            
            st.success(f"Terminé : {succes}/{len(liste_dests)} envoyés via {canal} + tout mémorisé ✅")
            st.balloons()
        else:
            st.warning("Remplis les destinataires ET le message")

elif menu == "3. Inventaire IA":
    st.subheader("📦 Agent Stock ASYMAS")
    
    if st.button("Analyser le stock maintenant"):
        try:
            stock = supabase.table("stock").select("*").execute()
            if stock.data:
                df = pd.DataFrame(stock.data)
                ruptures = df[df['quantite'] <= df['seuil_alerte']]
                
                if not ruptures.empty:
                    st.error("🚨 ALERTES STOCK - Action requise")
                    st.dataframe(ruptures[['produit', 'quantite', 'seuil_alerte', 'fournisseur']], use_container_width=True)
                    
                    if st.button("Générer l'email de commande fournisseur"):
                        texte_commande = "Bonjour,\n\nCommande urgente ASYMAS :\n"
                        for _, row in ruptures.iterrows():
                            texte_commande += f"- {row['produit']}: 50 unités\n"
                        texte_commande += "\nMerci, \nASYMAS"
                        st.code(texte_commande)
                else:
                    st.success("✅ Tout le stock est OK. Aucune rupture.")
            else:
                st.info("Table 'stock' vide. Va dans Supabase et ajoute des produits.")
        except Exception as e:
            st.error(f"Erreur Supabase: {e}")

elif menu == "4. CRM Mémoire":
    st.subheader("🧠 Tout ce que l'agent a retenu")
    
    tab1, tab2 = st.tabs(["📇 Contacts", "💬 Historique Conversations"])
    
    with tab1:
        try:
            contacts = supabase.table("contacts").select("*").order("created_at", desc=True).execute()
            if contacts.data:
                df_contacts = pd.DataFrame(contacts.data)
                st.dataframe(df_contacts[['nom', 'entreprise', 'tel', 'email', 'canal_prefere', 'tags']], use_container_width=True)
            else:
                st.info("Aucun contact mémorisé. Utilise 'Envoi Rapide' pour commencer.")
        except Exception as e:
            st.error(f"Erreur: {e}")
    
    with tab2:
        try:
            hist = supabase.table("conversations").select("*, contacts(nom,tel,email)").order("date", desc=True).limit(100).execute()
            if hist.data:
                for h in hist.data:
                    contact_info = h['contacts']
                    nom = contact_info.get('nom') or contact_info.get('tel') or contact_info.get('email')
                    with st.expander(f"{nom} - {h['date'][:16]} via {h['canal'].upper()}"):
                        st.write(f"**Message :** {h['message']}")
                        st.caption(f"Direction: {h['direction']} | Statut: {h['statut']}")
            else:
                st.info("Aucune conversation mémorisée.")
        except Exception as e:
            st.error(f"Erreur: {e}")
