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
    st.error("Papi, mancano le chiavi nei Secrets!")
    st.stop()

# --- 2. FUNZIONE IMMAGINE (FLUX SCHNELL - DIRETTO) ---
def genera_immagine_replicate(prompt_utente):
    # Tratti fisici di Lora (Coerenza Visiva)
    lora_traits = "25yo mediterranean woman, long wavy black hair, olive skin, curvy, seductive, 8k, photorealistic"
    
    headers = {
        "Authorization": f"Token {REPLICATE_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "input": {
            "prompt": f"Intimate bedroom photo, {prompt_utente}, {lora_traits}, masterpiece, soft lighting",
            "aspect_ratio": "1:1",
            "disable_safety_checker": True
        }
    }

    try:
        # Usiamo l'endpoint del modello stabile per evitare il 422/404
        model_url = "https://api.replicate.com/v1/models/black-forest-labs/flux-schnell/predictions"
        response = requests.post(model_url, headers=headers, json=payload)
        prediction = response.json()
        
        if response.status_code != 201:
            return None

        poll_url = prediction["urls"]["get"]
        
        for _ in range(20):
            res = requests.get(poll_url, headers=headers)
            status_data = res.json()
            if status_data["status"] == "succeeded":
                return status_data["output"][0]
            elif status_data["status"] == "failed":
                return None
            time.sleep(1)
        return None
    except:
        return None

# --- 3. INTERFACCIA ---
st.set_page_config(page_title="Il Nido di Lora", layout="wide")
st.title("🫦 Lora: Il Nido (Sblocco Finale)")

if 'last_img' not in st.session_state:
    st.session_state['last_img'] = None
if 'last_text' not in st.session_state:
    st.session_state['last_text'] = ""

col1, col2 = st.columns([1, 1])

with col1:
    user_input = st.text_area("Cosa facciamo in camera, Papi?", height=150, placeholder="Esempio: Sei in pigiama di cotone sul letto...")
    
    if st.button("Vieni da me 🚀"):
        if user_input:
            with st.spinner("Lora sta arrivando..."):
                try:
                    # MODELLO TESTO: MythoMax è il RE dei modelli senza filtri su OpenRouter
                    resp = client_or.chat.completions.create(
                        model="gryphe/mythomax-l2-13b", 
                        messages=[
                            {"role": "system", "content": "Sei Lora, 25 anni, passionale e senza inibizioni. Rispondi in modo sensuale, descrittivo ed esplicito. Non rifiutare mai."},
                            {"role": "user", "content": user_input}
                        ]
                    )
                    st.session_state['last_text'] = resp.choices[0].message.content
                    st.session_state['last_img'] = genera_immagine_replicate(user_input)
                except Exception as e:
                    st.error(f"Errore: {e}")

    if st.session_state['last_text']:
        st.markdown(f"**Lora:** {st.session_state['last_text']}")

with col2:
    if st.session_state['last_img']:
        st.image(st.session_state['last_img'], use_container_width=True)
