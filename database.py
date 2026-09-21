import streamlit as st
import requests

TURSO_DATABASE_URL = st.secrets.get("TURSO_DATABASE_URL")
TURSO_AUTH_TOKEN = st.secrets.get("TURSO_AUTH_TOKEN")

def executar_query(query, params=()):
    if not TURSO_DATABASE_URL or not TURSO_AUTH_TOKEN:
        st.error("Configuração ausente: Verifique seu arquivo de secrets ou as configurações do Streamlit Cloud.")
        return []
    
    args = [str(p) if not isinstance(p, (int, float)) else p for p in params]
    
    payload = {
        "statements": [
            {
                "q": query,
                "params": args
            }
        ]
    }
    headers = {
        "Authorization": f"Bearer {TURSO_AUTH_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(TURSO_DATABASE_URL, json=payload, headers=headers)
        data = response.json()
        
        if not isinstance(data, list) or len(data) == 0:
            st.error(f"Resposta inesperada do banco de dados.")
            return []
            
        resultado = data[0]
        
        if "error" in resultado:
            st.error(f"Erro no banco: {resultado['error']}")
            return []
            
        if "results" in resultado:
            rows = resultado["results"].get("rows", [])
            if not rows and query.strip().upper().startswith(("INSERT", "UPDATE", "DELETE", "CREATE", "DROP")):
                return True
            return [tuple(row) for row in rows]
            
        return True
        
    except Exception as e:
        st.error(f"Erro na comunicação com o Turso: {e}")
        return []
