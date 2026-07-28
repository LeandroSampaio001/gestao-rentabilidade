"""Página do Simulador Buy Box."""

import streamlit as st

from business.buy_box import render_buy_box_simulator
from ui.session import dados_disponiveis, get_df_processado, init_session_state

init_session_state()

st.title("⚔️ Simulador de Concorrência")
st.markdown("---")

if not dados_disponiveis():
    st.warning("⚠️ Nenhum dado processado. Vá à página **Importação e Auditoria** primeiro.")
    st.stop()

render_buy_box_simulator(get_df_processado())
