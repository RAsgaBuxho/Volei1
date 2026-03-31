from supabase import create_client
import streamlit as st
import os

# Tenta st.secrets primeiro (Streamlit Cloud), depois env vars
def get_secret(key):
    try:
        return st.secrets[key]
    except KeyError:
        return os.getenv(key)

SUPABASE_URL = get_secret("SUPABASE_URL")
SUPABASE_KEY = get_secret("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("❌ Secrets não configuradas!")
    st.info("""
    📋 Configure no Streamlit Cloud:
    1. Vá para App settings → Secrets
    2. Adicione:
    ```
    SUPABASE_URL = "sua_url"
    SUPABASE_KEY = "sua_chave"
    ```
    """)
    st.stop()

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)