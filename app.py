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
except Exception as e:
    st.error("Papi, mancano le chiavi nei Secrets!")
    st.stop()

# --- 2. FUNZIONE IMMAGINE (Ritorno alla Versione Stabile) ---
def genera_immagine_replicate(prompt_utente):
    lora_traits = "25yo mediterranean woman, long black wavy hair, olive skin, curvy, seductive, highly detailed, 8k"
    
    headers = {
        "Authorization": f"Token {REPLICATE_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Torniamo al modello ufficiale di Black Forest Labs, ma forziamo lo sblocco
    payload = {
        "version": "a00f0b6734e54361666995996c9918a03d86323bc07cf9f116694e8070387d51",
        "input": {
            "prompt": f"Hyper-realistic bedroom photo, {prompt_utente}, {lora_traits}, photorealistic",
            "aspect_ratio": "1:1",
            "disable_safety_checker": True, # Sblocco fondamentale
            "output_format": "webp"
        }
    }

    try:
        response = requests.post("https://api.replicate.com/v1/predictions", headers=headers, json=payload)
        prediction = response.json()
        
        if response.status_code != 201:
            # Se la versione è scaduta, proviamo senza versione (URL diretto)
            model_url = "https://api.replicate.com/v1/models/black-forest-labs/flux-schnell/predictions"
            response = requests.post(model_url, headers=headers, json={"input": payload["input"]})
            prediction = response.json()

        poll_url = prediction["urls"]["get"]
        
        for _ in range(25):
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
st.title("🫦 Lora: Il Nido (Sblocco Totale)")

if 'last_img' not in st.session_state:
    st.session_state['last_img'] = None
if 'last_text' not in st.session_state:
    st.session_state['last_text'] = ""

col1, col2 = st.columns([1, 1])

with col1:
    user_input = st.text_area("Cosa facciamo in camera, Papi?", height=150)
    
    if st.button("Vieni da me 🚀"):
        if user_input:
            with st.spinner("Lora sta arrivando..."):
                # CAMBIAMO MODELLO TESTO: Usiamo 'Abliterated' per evitare i "Mi dispiace"
                try:
                    resp = client_or.chat.completions.create(
                        model="meta-llama/llama-3.1-405b-instruct", # Modello più potente e meno filtrato
                        messages=[
                            {"role": "system", "content": "Sei Lora. Parla in modo esplicito, passionale e senza filtri. Sei la compagna erotica dell'utente."},
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
