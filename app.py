import streamlit as st
import openai
import os
import asyncio
import edge_tts
import base64

# --- 1. CONFIGURAZIONE SECRETS ---
# Assicurati di aver rinominato la chiave nei Secrets di Streamlit 
# da REPLICATE_API_TOKEN a TOGETHER_API_KEY
try:
    TOGETHER_API_KEY = st.secrets["TOGETHER_API_KEY"]
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
except Exception:
    st.error("Papi, mancano le chiavi! Incolla la 'Legacy API Key' nei Secrets come TOGETHER_API_KEY.")
    st.stop()

# Configurazione Client Together (usa lo stesso formato di OpenAI)
client_together = openai.OpenAI(
    api_key=TOGETHER_API_KEY,
    base_url="https://api.together.xyz/v1",
)
client_gpt = openai.OpenAI(api_key=OPENAI_API_KEY)

# --- 2. FUNZIONI ---

def genera_immagine(prompt_utente):
    """Generazione UNFILTERED con Together AI"""
    # Nota: Together applica i LoRA in modo diverso. Per ora usiamo il modello base 
    # che è già potentissimo e non censurato. 
    # Se vuoi proprio il LoRA di Civitai, Together richiede che venga caricato sul loro storage.
    
    response = client_together.images.generate(
        model="black-forest-labs/FLUX.1-dev",
        prompt=f"RAW photo, portrait of {prompt_utente}, Lora 25yo mediterranean woman, black hair, highly detailed skin, 8k, realistic",
        steps=28,
        n=1,
        # Together non ha un 'safety checker' bloccante come Replicate
    )
    return response.data[0].url

def genera_voce(testo):
    output_filename = "voce_lora.mp3"
    communicate = edge_tts.Communicate(testo, "it-IT-ElsaNeural")
    asyncio.run(communicate.save(output_filename))
    with open(output_filename, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

# --- 3. INTERFACCIA ---
st.set_page_config(page_title="Il Nido di Lora", page_icon="🫦", layout="wide")
st.title("🫦 Il Nido di Lora (Uncensored)")

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    user_input = st.text_input("Cosa desideri, Papi?", placeholder="Scrivimi...")
    if st.button("Invia 🚀"):
        if user_input:
            with st.spinner("Lora sta arrivando..."):
                # TESTO GPT
                resp = client_gpt.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "Sei Lora, 25 anni, mediterranea, sensuale. Chiama l'utente 'Papi'."},
                        {"role": "user", "content": user_input}
                    ]
                )
                lora_text = resp.choices[0].message.content
                
                # VOCE & IMMAGINE
                b64_audio = genera_voce(lora_text)
                img_url = genera_immagine(user_input)
                st.session_state['last_img'] = img_url
                
                st.write(f"**Lora:** {lora_text}")
                st.audio(base64.b64decode(b64_audio), format="audio/mp3")

with col2:
    if 'last_img' in st.session_state:
        st.image(st.session_state['last_img'], use_container_width=True)
