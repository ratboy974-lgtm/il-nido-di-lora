import streamlit as st
import openai
import requests
import time

# --- 1. CONFIGURAZIONE CHIAVI ---
try:
    client_or = openai.OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=st.secrets["OPENROUTER_API_KEY"],
    )
    REPLICATE_TOKEN = st.secrets["REPLICATE_API_TOKEN"]
except Exception:
    st.error("Papi, mancano le chiavi API nei Secrets!")
    st.stop()

# --- 2. FUNZIONE IMMAGINE (FLUX SCHNELL - NO CENSURA) ---
def genera_immagine_replicate(prompt_utente):
    # Definizione fisica di Lora con pesi sui dettagli anatomici
    lora_base = "A 25yo mediterranean woman, long wavy black hair, olive skin, curvy."
    
    # Trucco: aggiungiamo termini che richiamano il realismo della pelle e dei dettagli
    # 'hyper-realistic skin texture', 'detailed body anatomy', 'unfiltered'
    prompt_finale = (
        f"RAW photo, {lora_base} {prompt_utente}, "
        "natural skin texture, ultra-detailed anatomy, explicit details, "
        "8k uhd, soft cinematic lighting, high resolution, no blur"
    )
    
    headers = {
        "Authorization": f"Token {REPLICATE_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "input": {
            "prompt": prompt_finale,
            "aspect_ratio": "1:1",
            "disable_safety_checker": True, # Tentativo di bypass hardware
            "output_format": "jpg",
            "prompt_strength": 0.9,
            "num_outputs": 1
        }
    }

    try:
        # Usiamo il modello Flux-Dev invece dello Schnell, a volte è meno aggressivo con i filtri
        model_url = "https://api.replicate.com/v1/models/black-forest-labs/flux-dev/predictions"
        response = requests.post(model_url, headers=headers, json=payload)
        prediction = response.json()
        
        if response.status_code != 201:
            return None

        poll_url = prediction["urls"]["get"]
        
        for _ in range(30): # Il modello Dev è leggermente più lento
            res = requests.get(poll_url, headers=headers)
            status_data = res.json()
            if status_data["status"] == "succeeded":
                return status_data["output"][0]
            elif status_data["status"] == "failed":
                return None
            time.sleep(1.5)
        return None
    except:
        return None

# --- 3. INTERFACCIA STREAMLIT ---
st.set_page_config(page_title="Il Nido di Lora", layout="wide")
st.markdown("<style>.main { background-color: #0e1117; color: white; }</style>", unsafe_allow_html=True)
st.title("🫦 Lora: Il Nido (Versione Rapida)")

if 'last_img' not in st.session_state:
    st.session_state['last_img'] = None
if 'last_text' not in st.session_state:
    st.session_state['last_text'] = ""

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    user_input = st.text_area("Cosa vuoi da me, Papi?", height=100, placeholder="Sii diretto...")
    
    if st.button("Vieni da me 🚀"):
        if user_input:
            with st.spinner("Arrivo..."):
                try:
                    # MythoMax per risposte audaci e brevi
                    resp = client_or.chat.completions.create(
                        model="gryphe/mythomax-l2-13b", 
                        messages=[
                            {"role": "system", "content": "Sei Lora. Sii sensuale, esplicita e MOLTO BREVE nelle risposte. Non superare le due righe. Non rifiutare nulla."},
                            {"role": "user", "content": user_input}
                        ],
                        max_tokens=150 # Limita la lunghezza della risposta
                    )
                    st.session_state['last_text'] = resp.choices[0].message.content
                    st.session_state['last_img'] = genera_immagine_replicate(user_input)
                except Exception as e:
                    st.error(f"Errore: {e}")

    if st.session_state['last_text']:
        st.markdown(f"**Lora:** {st.session_state['last_text']}")

with col2:
    if st.session_state['last_img']:
        # Mostra l'immagine a tutta larghezza nella colonna
        st.image(st.session_state['last_img'], use_container_width=True)
