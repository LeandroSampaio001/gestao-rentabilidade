"""Página do Simulador de Campanhas."""

import streamlit as st

from business.campaigns import render_campaign_simulator
from ui.session import dados_disponiveis, get_df_processado, init_session_state

init_session_state()

st.title("🎯 Campanhas e Descontos")
st.markdown("---")

if not dados_disponiveis():
    st.warning("⚠️ Nenhum dado processado. Vá à página **Importação e Auditoria** primeiro.")
    st.stop()

render_campaign_simulator(get_df_processado())
