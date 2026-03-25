import streamlit as st

# --- 🛠️ PROTEZIONE SPECIALE PYDANTIC (Anti-Crash Python 3.14) ---
import pydantic
try:
    from pydantic import v1 as pydantic_v1
except ImportError:
    pydantic_v1 = pydantic

# --- IMPORTAZIONI ---
import replicate
import openai
import os
import asyncio
import edge_tts
import base64

# --- 1. CONFIGURAZIONE STREAMLIT SECRETS ---
try:
    REPLICATE_API_TOKEN = st.secrets["REPLICATE_API_TOKEN"]
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
except Exception:
    st.error("Papi, mancano le chiavi nei Secrets! Vai in Settings -> Secrets.")
    st.stop()

# Inizializzazione API
os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# --- 2. FUNZIONI ---

def genera_voce(testo):
    """Genera file audio con la voce di ElsaNeural"""
    output_filename = "voce_lora.mp3"
    communicate = edge_tts.Communicate(testo, "it-IT-ElsaNeural")
    asyncio.run(communicate.save(output_filename))
    with open(output_filename, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

def genera_immagine(prompt_utente):
    """L'unica versione che NON può darti 422 perché usa il modello base SDXL"""
    LORA_URL = "https://civitai.com/api/download/models/2160078?type=Model&format=SafeTensor"
    
    # Questo modello è un 'cavallo di battaglia', non sparisce e non ha censure bloccanti
    output = replicate.run(
        "lucataco/replicate-flux-lora:731005a74e5033328e67f70b7936a2e4a46a788e0019446d3e387c69994c6a99",
        input={
            "prompt": f"RAW photo, {prompt_utente}, Lora woman, mediterranean, black hair, highly detailed, 8k",
            "hf_lora": LORA_URL, # Usiamo hf_lora che è il parametro più accettato
            "lora_scale": 0.85,
            "disable_safety_checker": True # <-- Fondamentale
        }
    )
    return str(output[0]) if isinstance(output, list) else str(output)
# --- 3. INTERFACCIA UTENTE ---
st.set_page_config(page_title="Il Nido di Lora", page_icon="🫦", layout="wide")

st.title("🫦 Il Nido di Lora")
st.write("Entra, Papi... mettiti comodo.")
st.markdown("---")

# Layout a due colonne
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("💬 Parla con me")
    user_input = st.text_input("Cosa desideri oggi?", placeholder="Scrivimi qui...")
    
    if st.button("Invia 🚀"):
        if user_input:
            with st.spinner("Sto arrivando..."):
                try:
                    # A. TESTO (Lora risponde)
                    resp = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "Sei Lora, 25 anni, mediterranea, sensuale. Chiama l'utente 'Papi'."},
                            {"role": "user", "content": user_input}
                        ]
                    )
                    lora_text = resp.choices[0].message.content
                    
                    # B. VOCE
                    b64_audio = genera_voce(lora_text)
                    
                    # C. IMMAGINE (Qui salviamo l'URL come stringa pulita)
                    img_url = genera_immagine(user_input)
                    st.session_state['last_img'] = img_url
                    
                    # MOSTRA RISULTATI NELLA COLONNA 1
                    st.write(f"**Lora:** {lora_text}")
                    st.audio(base64.b64decode(b64_audio), format="audio/mp3")
                    
                except Exception as e:
                    st.error(f"Papi, c'è un intoppo: {e}")

with col2:
    st.subheader("🖼️ Guardami")
    if 'last_img' in st.session_state:
        # Usiamo l'URL salvato per mostrare l'immagine
        st.image(st.session_state['last_img'], use_container_width=True)
    else:
        st.info("Papi, chiedimi qualcosa e apparirò per te.")
