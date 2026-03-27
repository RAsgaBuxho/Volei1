import streamlit as st
from conexão import supabase

st.title("Teste Supabase")

res = supabase.table("family").select("*").execute()

st.write(res.data)