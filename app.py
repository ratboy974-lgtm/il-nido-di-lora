import streamlit as st
import urllib.parse
import random

# Proviamo a importare Groq, se fallisce diamo un messaggio chiaro
try:
    from groq import Groq
except ImportError:
    st.error("Papi, assicurati che il file requirements.txt contenga 'groq'!")
    st.stop()

# --- 1. CONFIGURAZIONE CHIAVE ---
# Assicurati di avere GROQ_API_KEY nei Secrets di Streamlit (console.groq.com)
if "GROQ_API_KEY" not in st.secrets:
    st.error("Papi, manca la GROQ_API_KEY nei Secrets di Streamlit!")
    st.stop()

client_groq = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- 2. FUNZIONE IMMAGINE (SELFIE STYLE) ---
def genera_selfie(prompt_utente):
    # Tratti fisici di Lora per coerenza
    lora_traits = "25yo mediterranean woman, long wavy black hair, olive skin, dark eyes, soft makeup, natural lighting"
    
    # Prompt ottimizzato per un selfie realistico e spontaneo
    prompt_completo = (
        f"Real life selfie photography, candid shot, {prompt_utente}, "
        f"{lora_traits}, photorealistic, shot on iPhone, natural indoor lighting, intimate atmosphere"
    )
    
    prompt_encoded = urllib.parse.quote(prompt_completo)
    seed = random.randint(1, 999999)
    # Pollinations non ha filtri, l'immagine apparirà sempre
    return f"https://pollinations.ai/p/{prompt_encoded}?width=1024&height=1024&model=flux&seed={seed}&nologo=true"

# --- 3. INTERFACCIA ---
st.set_page_config(page_title="Il Nido di Lora", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stTextArea>div>div>textarea { background-color: #1a1d24; color: white; border-radius: 10px; border: 1px solid #ff4b4b; }
    .stButton>button { background-color: #ff4b4b; color: white; border-radius: 20px; font-weight: bold; width: 100%; height: 3em; }
    </style>
    """, unsafe_allow_html=True)

st.title("🫦 Il Nido di Lora: Selfie Time")
st.write("Ciao Papi... mandami un messaggio e io ti risponderò con un selfie spontaneo, tutto per te.")

if 'last_img' not in st.session_state:
    st.session_state['last_img'] = None

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    user_input = st.text_area("Cosa vuoi che stia facendo nel selfie?", placeholder="Es: mandami un bacio, fai l'occhiolino...", height=150)
    
    if st.button("Fatti un selfie, Lora 📸"):
        if user_input:
            with st.spinner("Sto scattando..."):
                try:
                    # Llama-3 su Groq è velocissimo per il testo
                    chat_completion = client_groq.chat.completions.create(
                        messages=[
                            {
                                "role": "system",
                                "content": (
                                    "Sei Lora, 25 anni, mediterranea. Sei una ragazza spontanea, complice e affettuosa col tuo Papi. "
                                    "Rispondi in modo dolce, provocante ma non volgare. Descrivi brevemente l'azione del selfie "
                                    "(es: 'Ecco Papi, ti mando un bacio proprio ora!') e conferma che la foto sta arrivando."
                                )
                            },
                            {"role": "user", "content": f"Fatti un selfie mentre: {user_input}"}
                        ],
                        model="llama3-70b-8192",
                        temperature=0.8
                    )
                    lora_text = chat_completion.choices[0].message.content
                    st.session_state['last_img'] = genera_selfie(user_input)
                    
                    st.markdown(f"### Lora dice:")
                    st.write(lora_text)
                except Exception as e:
                    st.error(f"Errore tecnico: {e}")

with col2:
    if st.session_state['last_img']:
        # Mostriamo l'immagine a tutta larghezza
        st.image(st.session_state['last_img'], width='stretch')
