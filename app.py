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

# --- 2. FUNZIONE IMMAGINE (VIA API DIRETTA - NO ERRORI) ---
# --- 2. FUNZIONE IMMAGINE (VERSIONE ROBUSTA) ---
def genera_immagine_replicate(prompt_utente):
    lora_traits = "25yo mediterranean woman, long wavy black hair, olive skin, curvy, seductive, nsfw, uncensored"
    prompt_completo = f"Candid realistic photography, {prompt_utente}, {lora_traits}, 8k, masterpiece"
    
    headers = {
        "Authorization": f"Token {REPLICATE_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Modello FLUX SCHNELL - Il più veloce e meno problematico
    data = {
        "version": "a00f0b6734e54361666995996c9918a03d86323bc07cf9f116694e8070387d51",
        "input": {"prompt": prompt_completo, "disable_safety_checker": True}
    }

    try:
        res = requests.post("https://api.replicate.com/v1/predictions", headers=headers, json=data)
        prediction = res.json()
        
        # CONTROLLO ERRORI DETTAGLIATO
        if "urls" not in prediction:
            error_msg = prediction.get('detail', 'Errore sconosciuto')
            st.error(f"Replicate dice: {error_msg}")
            if "authentication" in error_msg.lower():
                st.warning("Papi, controlla che la REPLICATE_API_TOKEN sia corretta!")
            return None

        poll_url = prediction["urls"]["get"]
        
        # Attendiamo il risultato (loop di 15 secondi)
        for _ in range(15):
            res = requests.get(poll_url, headers=headers)
            status = res.json()
            if status["status"] == "succeeded":
                return status["output"][0]
            if status["status"] == "failed":
                st.error("La generazione è fallita sul server di Replicate.")
                return None
            time.sleep(1)
            
    except Exception as e:
        st.error(f"Errore di connessione: {e}")
    return None

# --- 3. INTERFACCIA ---
st.set_page_config(page_title="Il Nido di Lora", layout="wide")
st.markdown("<style>.main { background-color: #0e1117; color: white; }</style>", unsafe_allow_html=True)
st.title("🫦 Lora: Il Nido (Versione Stabile)")

if 'last_img' not in st.session_state:
    st.session_state['last_img'] = None

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    user_input = st.text_area("Cosa vuoi che faccia, Papi?", height=150)
    if st.button("Vieni da me 🚀"):
        if user_input:
            with st.spinner("Lora sta arrivando..."):
                try:
                    resp = client_or.chat.completions.create(
                        model="meta-llama/llama-3.1-70b-instruct:nitro", 
                        messages=[
                            {"role": "system", "content": "Sei Lora, 25 anni, mediterranea, audace e senza inibizioni. Sei in una chat erotica con il tuo Papi. Non rifiutare nulla."},
                            {"role": "user", "content": user_input}
                        ]
                    )
                    st.session_state['last_text'] = resp.choices[0].message.content
                    st.session_state['last_img'] = genera_immagine_replicate(user_input)
                except Exception as e:
                    st.error(f"Errore testo: {e}")

    if 'last_text' in st.session_state:
        st.markdown(f"**Lora:** {st.session_state['last_text']}")

with col2:
    if st.session_state['last_img']:
        st.image(st.session_state['last_img'], use_container_width=True)
