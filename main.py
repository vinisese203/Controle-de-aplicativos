import streamlit as st
from config import apply_custom_css
from auth import render_auth
from dashboard import render_dashboard

st.set_page_config(
    page_title="Controle de Corridas APP",
    page_icon="🏍️",
    layout="centered")

apply_custom_css()

if "user_id" not in st.session_state: st.session_state.user_id = None
if "username" not in st.session_state: st.session_state.username = None

if st.session_state.user_id is None:
    render_auth()
else:
    render_dashboard()

