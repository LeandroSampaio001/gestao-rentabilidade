"""Página de Ponto de Equilíbrio."""

import streamlit as st

from business.break_even import render_break_even
from ui.session import dados_disponiveis, get_df_processado, init_session_state

init_session_state()

st.title("⚖️ Ponto de Equilíbrio")
st.markdown("---")

if not dados_disponiveis():
    st.warning("⚠️ Nenhum dado processado. Vá à página **Importação e Auditoria** primeiro.")
    st.stop()

render_break_even(get_df_processado())
