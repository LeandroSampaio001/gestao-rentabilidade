"""Página de Alertas e Notificações."""

import streamlit as st
from ui.alerts import gerar_alertas_automaticos, render_notificacoes_mobile, render_painel_alertas
from ui.session import dados_disponiveis, get_df_processado, init_session_state
from ui.email_modal import modal_autorizacao_email

init_session_state()

st.title("🔔 Alertas e Notificações")
st.markdown("---")

# Seção para gerenciar o recebimento por e-mail
col_aviso, col_botao = st.columns([3, 1])
with col_aviso:
    status_email = "Ativado" if st.session_state.get("alertas_email_ativados") else "Desativado"
    email_atual = st.session_state.get("email_alerta", "Leosampaio1990@gmail.com")
    st.markdown(f"**Status de Alertas por E-mail:** {status_email} *(para: {email_atual})*")

with col_botao:
    if st.button("⚙️ Configurar E-mail", use_container_width=True):
        modal_autorizacao_email()

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
