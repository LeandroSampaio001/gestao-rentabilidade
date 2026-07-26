"""Página de Giro de Estoque."""

import streamlit as st

from business.inventory_matrix import render_inventory_matrix
from ui.session import dados_disponiveis, get_df_processado, init_session_state

init_session_state()

st.title("📦 Giro de Estoque")
st.markdown("---")

if not dados_disponiveis():
    st.warning("⚠️ Nenhum dado processado. Vá à página **Importação e Auditoria** primeiro.")
    st.stop()

render_inventory_matrix(get_df_processado())
