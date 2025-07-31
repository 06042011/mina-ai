import streamlit as st
import json
import os
from datetime import datetime
import requests

# Configurazione pagina
st.set_page_config(
    page_title="MINA - Il Mio Assistente AI", 
    page_icon="💎",
    layout="wide"
)

# Stile personalizzato
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    .assistant-message {
        background-color: #f3e5f5;
        border-left: 4px solid #9c27b0;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">💎 MINA - Il Tuo Assistente Personale</h1>', unsafe_allow_html=True)

# Funzione per chiamare Groq API
def call_groq_api(messages, temperature=0.7):
    """Chiama l'API di Groq per ottenere una risposta"""
    
    # Controlla se l'API key è configurata
    api_key = st.secrets.get("GROQ_API_KEY", "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")
    if not api_key:
        return "❌ Errore: API Key non configurata. Controlla le impostazioni su Streamlit Cloud."
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "llama3-8b-8192",  # Modello gratuito di Groq
        "messages": messages,
        "temperature": temperature,
        "max_tokens": 1000
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        return result["choices"][0]["message"]["content"]
        
    except requests.exceptions.Timeout:
        return "❌ Errore: Timeout nella richiesta. Riprova."
    except requests.exceptions.RequestException as e:
        return f"❌ Errore di connessione: {str(e)}"
    except Exception as e:
        return f"❌ Errore imprevisto: {str(e)}"

# Knowledge Base personalizzabile
KNOWLEDGE_BASE = {
    "chi sei": "Sono MINA, il tuo assistente personale AI! Sono stata creata per aiutarti con qualsiasi domanda tu abbia. Il mio nome significa 'intelligenza' e sono qui per essere la tua compagna digitale.",
    "cosa sai fare": "Sono MINA e posso chattare, rispondere a domande, aiutarti con problemi, scrivere testi, spiegare concetti, fare calcoli e molto altro! Sono la tua assistente personale sempre disponibile.",
    "mina": "MINA è il mio nome! Significa 'intelligenza' e rappresenta la mia missione: essere la tua assistente AI più utile e affidabile.",
    "come funzioni": "Sono MINA e ora funziono nel cloud usando Groq API con il modello Llama3. Sono sempre disponibile online!",
    "il mio progetto": "Puoi aggiungere informazioni sui tuoi progetti qui!",
    "contatti": "Aggiungi qui i tuoi contatti o informazioni personali",
}

# Sidebar per impostazioni
with st.sidebar:
    st.header("⚙️ Impostazioni")
    
    # Selezione temperatura (creatività)
    temperature = st.slider(
        "🌡️ Creatività (Temperature)", 
        min_value=0.1, 
        max_value=2.0, 
        value=0.7, 
        step=0.1,
        help="Valori bassi = risposte più precise. Valori alti = risposte più creative"
    )
    
    # Personalità del chatbot
    personality = st.selectbox(
        "🎭 Personalità", 
        ["Amichevole", "Professionale", "Creativo", "Tecnico", "Divertente"],
        help="Cambia il modo in cui il chatbot risponde"
    )
    
    # Pulsanti controllo
    st.markdown("---")
    if st.button("🗑️ Cancella Cronologia"):
        st.session_state.messages = []
        st.success("Cronologia cancellata!")
        st.rerun()
    
    # Info modello
    st.markdown("---")
    st.markdown("**🤖 Assistente:** MINA")
    st.markdown("**🧠 Modello:** Llama3 via Groq")
    st.markdown("**☁️ Hosting:** Streamlit Cloud")
    st.markdown("**💰 Costo:** Gratuito")

# Inizializza cronologia chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Crea il prompt di sistema basato sulla personalità
personality_prompts = {
    "Amichevole": "Sei MINA, un'assistente amichevole e calorosa. Rispondi sempre in italiano con un tono cordiale e disponibile.",
    "Professionale": "Sei MINA, un'assistente professionale ed efficiente. Fornisci risposte precise e ben strutturate in italiano.",
    "Creativo": "Sei MINA, un'assistente creativa e fantasiosa. Usa metafore, esempi coloriti e approcci originali nelle tue risposte in italiano.",
    "Tecnico": "Sei MINA, un'assistente tecnica specializzata. Fornisci spiegazioni dettagliate e precise con terminologia appropriata in italiano.",
    "Divertente": "Sei MINA, un'assistente spiritosa e divertente. Usa humor appropriato e mantieni un tono leggero nelle tue risposte in italiano."
}

system_prompt = personality_prompts[personality]

# Mostra cronologia
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input utente principale
if prompt := st.chat_input("💬 Scrivi qui la tua domanda..."):
    # Aggiungi messaggio utente
    st.session_state.messages.append({
        "role": "user", 
        "content": prompt,
        "timestamp": datetime.now().isoformat()
    })
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Controlla knowledge base prima
    response_from_kb = None
    for key in KNOWLEDGE_BASE:
        if key.lower() in prompt.lower():
            response_from_kb = KNOWLEDGE_BASE[key]
            break
    
    # Genera risposta
    with st.chat_message("assistant"):
        if response_from_kb:
            # Risposta dalla knowledge base
            st.markdown(f"📚 **Dalla mia base di conoscenze:**\n\n{response_from_kb}")
            answer = response_from_kb
        else:
            # Risposta da Groq API
            with st.spinner("💎 MINA sta pensando..."):
                # Prepara il contesto della conversazione
                conversation_context = []
                
                # Aggiungi gli ultimi 10 messaggi per contesto
                recent_messages = st.session_state.messages[-20:] if len(st.session_state.messages) > 20 else st.session_state.messages
                
                for msg in recent_messages[:-1]:  # Escludi l'ultimo messaggio dell'utente
                    conversation_context.append({
                        'role': msg['role'],
                        'content': msg['content']
                    })
                
                # Aggiungi il prompt di sistema e il messaggio corrente
                messages_for_api = [
                    {'role': 'system', 'content': system_prompt}
                ] + conversation_context + [
                    {'role': 'user', 'content': prompt}
                ]
                
                # Chiama Groq API
                answer = call_groq_api(messages_for_api, temperature)
                st.markdown(answer)
        
        # Salva risposta
        st.session_state.messages.append({
            "role": "assistant", 
            "content": answer,
            "timestamp": datetime.now().isoformat()
        })

# Footer con statistiche
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("💬 Messaggi Totali", len(st.session_state.messages))
with col2:
    st.metric("🤖 Assistente", "MINA")
with col3:
    st.metric("🌡️ Temperatura", f"{temperature}")

# Istruzioni per l'utente
with st.expander("ℹ️ Come usare MINA"):
    st.markdown("""
    **Comandi speciali che puoi provare:**
    - "chi sei" - Informazioni su MINA
    - "cosa sai fare" - Capacità di MINA
    - "mina" - Informazioni sul nome
    
    **Suggerimenti:**
    - Usa la sidebar per cambiare personalità e creatività
    - Puoi fare domande su qualsiasi argomento
    - MINA ricorda la conversazione corrente
    
    **Personalizzazione:**
    - Modifica il `KNOWLEDGE_BASE` nel codice per aggiungere tue conoscenze
    - Cambia i prompt di personalità per adattare il comportamento
    """)

# Debug info (solo se necessario)
if st.checkbox("🔍 Modalità Debug"):
    st.json({
        "Messaggi in memoria": len(st.session_state.messages),
        "Personalità": personality,
        "Temperatura": temperature,
        "API Key configurata": bool(st.secrets.get("GROQ_API_KEY", ""))
    })