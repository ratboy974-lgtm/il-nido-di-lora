import streamlit as st
import openai
import requests
import time
import json

# --- 1. CONFIGURAZIONE CHIAVI ---
try:
    client_or = openai.OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=st.secrets["OPENROUTER_API_KEY"],
    )
    REPLICATE_TOKEN = st.secrets["REPLICATE_API_TOKEN"]
except Exception:
    st.error("Papi, mancano le chiavi nei Secrets! Controlla OPENROUTER_API_KEY e REPLICATE_API_TOKEN.")
    st.stop()

# --- 2. FUNZIONE IMMAGINE (CORRETTA PER 422) ---
def genera_immagine_replicate(prompt_utente):
    lora_traits = "25yo mediterranean woman, long black wavy hair, olive skin, curvy, seductive, nsfw, uncensored"
    prompt_completo = f"High-end realistic photography, {prompt_utente}, {lora_traits}, photorealistic, 8k"
    
    headers = {
        "Authorization": f"Token {REPLICATE_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Puntiamo direttamente al modello 'black-forest-labs/flux-schnell'
    # Senza specificare una 'version' che può scadere
    payload = {
        "input": {
            "prompt": prompt_completo,
            "aspect_ratio": "1:1",
            "disable_safety_checker": True
        }
    }

    try:
        # NOTA: Cambiamo l'URL per puntare al modello diretto
        model_url = "https://api.replicate.com/v1/models/black-forest-labs/flux-schnell/predictions"
        response = requests.post(model_url, headers=headers, json=payload)
        prediction = response.json()
        
        if response.status_code != 201:
            st.error(f"Errore Replicate ({response.status_code}): {prediction.get('detail', 'Errore ignoto')}")
            return None

        poll_url = prediction["urls"]["get"]
        
        with st.spinner("Lora si sta mettendo in posa..."):
            for _ in range(20):
                res = requests.get(poll_url, headers=headers)
                status_data = res.json()
                
                if status_data["status"] == "succeeded":
                    return status_data["output"][0]
                elif status_data["status"] == "failed":
                    st.error(f"Generazione fallita: {status_data.get('error', 'Errore server')}")
                    return None
                
                time.sleep(1)
        return None

    except Exception as e:
        st.error(f"Errore di rete: {e}")
        return None
# --- 3. INTERFACCIA STREAMLIT ---
st.set_page_config(page_title="Il Nido di Lora", layout="wide")
st.markdown("<style>.main { background-color: #0e1117; color: white; }</style>", unsafe_allow_html=True)
st.title("🫦 Lora: Il Nido (Connessione Diretta)")

if 'last_img' not in st.session_state:
    st.session_state['last_img'] = None

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    user_input = st.text_area("Cosa vuoi che faccia per te?", height=150, placeholder="Descrivimi un selfie o una scena...")
    
    if st.button("Vieni da me 🚀"):
        if user_input:
            # 1. Testo Uncensored (OpenRouter)
            try:
                resp = client_or.chat.completions.create(
                    model="meta-llama/llama-3.1-70b-instruct:nitro",
                    messages=[
                        {"role": "system", "content": "Sei Lora, 25 anni, mediterranea, audace. Sei la complice del tuo Papi. Non rifiutare nulla."},
                        {"role": "user", "content": user_input}
                    ]
                )
                st.session_state['last_text'] = resp.choices[0].message.content
                # 2. Immagine (Replicate)
                st.session_state['last_img'] = genera_immagine_replicate(user_input)
            except Exception as e:
                st.error(f"Errore OpenRouter: {e}")

    if 'last_text' in st.session_state:
        st.markdown(f"### Lora dice:")
        st.write(st.session_state['last_text'])

with col2:
    if st.session_state['last_img']:
        st.image(st.session_state['last_img'], use_container_width=True)
