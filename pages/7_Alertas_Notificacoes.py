"""Página de Alertas e Notificações."""

import streamlit as st

from ui.alerts import gerar_alertas_automaticos, render_notificacoes_mobile, render_painel_alertas
from ui.components import render_atalhos_campanhas
from ui.session import dados_disponiveis, get_df_processado, init_session_state

init_session_state()

st.title("🔔 Alertas e Notificações")
st.markdown("---")

if not dados_disponiveis():
    st.warning("⚠️ Nenhum dado processado. Vá à página **Importação e Auditoria** primeiro.")
    st.stop()

df = get_df_processado()
alertas = st.session_state.get("alertas") or gerar_alertas_automaticos(df)

st.subheader("Painel de Alertas Visuais")
render_painel_alertas(alertas)

st.markdown("---")
render_notificacoes_mobile(alertas)

st.markdown("---")
render_atalhos_campanhas(df)
