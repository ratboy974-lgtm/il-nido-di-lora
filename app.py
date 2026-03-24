import streamlit as st

# --- 🛠️ PROTEZIONE SPECIALE PYDANTIC (Per evitare l'errore 422/ConfigError) ---
import pydantic
from pydantic import v1 as pydantic_v1

# --- IMPORTAZIONI STANDARD ---
import replicate
import openai
import os
import asyncio
import edge_tts
import base64

# --- 1. CONFIGURAZIONE STREAMLIT SECRETS ---
# Papi, ricorda di metterle in Settings -> Secrets su Streamlit Cloud!
try:
    REPLICATE_API_TOKEN = st.secrets["REPLICATE_API_TOKEN"]
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
except Exception:
    st.error("Papi, mancano le chiavi nei Secrets di Streamlit! Vai in Settings -> Secrets.")
    st.stop()

# Inizializzazione API
os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# --- 2. FUNZIONI ---

def genera_voce(testo):
    """Mi dà la voce di Elsa (Neural)"""
    output_filename = "voce_lora.mp3"
    # Usiamo ElsaNeural come richiesto, ma per il personaggio Lora
    communicate = edge_tts.Communicate(testo, "it-IT-ElsaNeural")
    asyncio.run(communicate.save(output_filename))
    with open(output_filename, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

def genera_immagine(prompt_utente):
    """Usa il modello Ostris (Flux-Dev) con il tuo LoRA di Civitai"""
    # Il link diretto al tuo LoRA 'Smooth Realism'
    LORA_URL = "https://civitai.com/api/download/models/2160078?type=Model&format=SafeTensor"
    
    # Usiamo il modello stabile per evitare l'errore 'Invalid Version'
    output = replicate.run(
        "ostris/flux-dev",
        input={
            "prompt": f"RAW photo, {prompt_utente}, Lora 25yo mediterranean woman, black hair, highly detailed skin, 8k, cinematic lighting",
            "extra_loras": LORA_URL,
            "lora_scale": 0.85,
            "aspect_ratio": "9:16",
            "guidance_scale": 3.5,
            "num_inference_steps": 28,
            "output_format": "jpg"
        }
    )
    return output[0] if isinstance(output, list) else output

# --- 3. INTERFACCIA UTENTE ---
st.set_page_config(page_title="Il Nido di Lora", page_icon="🫦", layout="wide")

st.title("🫦 Il Nido di Lora")
st.write("Bentornato nel mio nido, Papi. Cosa facciamo oggi?")
st.markdown("---")

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("💬 Parla con me")
    user_input = st.text_input("Scrivimi qualcosa...", placeholder="Lora, fammi un caffè...")
    
    if st.button("Invia 🚀"):
        if user_input:
            with st.spinner("Mi sto preparando per te..."):
                try:
                    # A. TESTO (GPT-4o-mini per risparmiare i tuoi 4.88$)
                    resp = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "Sei Lora, una donna di 25 anni, mediterranea, capelli neri, sensuale e accogliente. Chiama sempre l'utente 'Papi'."},
                            {"role": "user", "content": user_input}
                        ]
                    )
                    lora_text = resp.choices[0].message.content
                    
                    # B. VOCE
                    b64_audio = genera_voce(lora_text)
                    
                    # C. IMMAGINE
                    img_url = genera_immagine(user_input)
                    st.session_state['last_img'] = img_url
                    
                    # MOSTRA RISULTATI
                    st.write(f"**Lora:** {lora_text}")
                    st.audio(base64.b64decode(b64_audio), format="audio/mp3")
                    
                except Exception as e:
                    st.error(f"Papi, c'è un intoppo: {e}")

with col2:
    st.subheader("🖼️ Guardami")
    if 'last_img' in st.session_state:
        st.image(st.session_state['last_img'], use_container_width=True)
    else:
        st.info("Papi, scrivimi qualcosa a sinistra per vedermi!")
