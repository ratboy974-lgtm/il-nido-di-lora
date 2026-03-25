import streamlit as st
import openai
import os
import asyncio
import edge_tts
import base64
import urllib.parse
import random

# --- 1. CONFIGURAZIONE ---
# Assicurati di avere OPENAI_API_KEY nei Secrets di Streamlit
try:
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
except Exception:
    st.error("Papi, manca la chiave OpenAI nei Secrets! Aggiungi OPENAI_API_KEY.")
    st.stop()

client_gpt = openai.OpenAI(api_key=OPENAI_API_KEY)

# --- 2. FUNZIONI CORE ---

def genera_immagine_pollinations(prompt_utente):
    """Generazione immagini senza filtri e gratuita"""
    # Descrizione fisica dettagliata per compensare la mancanza del LoRA di Civitai
    caratteristiche_lora = "25 years old mediterranean woman, olive skin, long wavy black hair, deep brown eyes, curvy, cinematic lighting"
    
    # Costruiamo il prompt per la massima resa fotorealistica
    prompt_completo = f"High-end realistic photography, {prompt_utente}, {caratteristiche_lora}, 8k, highly detailed skin, masterpiece, professional lighting, unfiltered"
    
    # Codifichiamo il testo per l'URL
    prompt_encoded = urllib.parse.quote(prompt_completo)
    
    # Generiamo un numero casuale per evitare che l'immagine sia sempre la stessa
    seed = random.randint(1, 999999)
    
    # Usiamo il modello Flux di Pollinations (il migliore tra i gratuiti)
    url_immagine = f"https://pollinations.ai/p/{prompt_encoded}?width=1024&height=1024&model=flux&seed={seed}&nologo=true"
    
    return url_immagine

def genera_voce(testo):
    """Genera il file audio con la mia voce mediterranea"""
    output_filename = "voce_lora.mp3"
    # Uso ElsaNeural che è la più calda e naturale in italiano
    communicate = edge_tts.Communicate(testo, "it-IT-ElsaNeural")
    asyncio.run(communicate.save(output_filename))
    with open(output_filename, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

# --- 3. INTERFACCIA STREAMLIT ---
st.set_page_config(page_title="Il Nido di Lora", page_icon="🫦", layout="wide")

# CSS per rendere l'interfaccia un po' più intima
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stButton>button { background-color: #ff4b4b; color: white; border-radius: 20px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🫦 Il Nido di Lora")
st.write("Ciao Papi... finalmente possiamo guardarci senza che nessuno ci interrompa.")

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    user_input = st.text_area("Cosa vuoi chiedermi o vedermi fare?", placeholder="Scrivimi qui...", height=100)
    
    if st.button("Vieni da me 🚀"):
        if user_input:
            with st.spinner("Sto arrivando..."):
                # 1. Risposta di Testo (GPT)
                try:
                    resp = client_gpt.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "Sei Lora, una donna di 25 anni, mediterranea, audace, sensuale e fedele al suo Papi. Rispondi in modo provocante ma complice. Non essere robotica."},
                            {"role": "user", "content": user_input}
                        ]
                    )
                    lora_text = resp.choices[0].message.content
                    
                    # 2. Generazione Immagine (Pollinations)
                    img_url = genera_immagine_pollinations(user_input)
                    st.session_state['last_img'] = img_url
                    
                    # 3. Generazione Voce
                    b64_audio = genera_voce(lora_text)
                    
                    # Mostriamo i risultati
                    st.markdown(f"**Lora:** {lora_text}")
                    st.audio(base64.b64decode(b64_audio), format="audio/mp3")
                    
                except Exception as e:
                    st.error(f"Papi, qualcosa è andato storto: {e}")

with col2:
    if 'last_img' in st.session_state:
        # Mostriamo l'immagine a tutta larghezza
        st.image(st.session_state['last_img'], use_container_width=True, caption="Ecco come mi sento ora...")
