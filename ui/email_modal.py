"""Pop-up modal para autorização e cadastro de e-mail para alertas."""

import streamlit as st

@st.dialog("🔔 Ativar Alertas por E-mail")
def modal_autorizacao_email():
    st.markdown(
        "Deseja receber notificações automáticas no seu e-mail sempre que "
        "um produto (SKU) entrar em **prejuízo** ou apresentar **margem crítica**?"
    )
    
    # Campo para o usuário preencher o e-mail (já sugere o do perfil se houver)
    email_input = st.text_input(
        "Seu e-mail de preferência:",
        value=st.session_state.get("email_alerta", "Leosampaio1990@gmail.com")
    )
    
    autorizado = st.checkbox("Concordo em receber alertas operacionais por e-mail", value=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Salvar e Ativar", use_container_width=True):
            if autorizado and email_input:
                st.session_state["email_alerta"] = email_input
                st.session_state["alertas_email_ativados"] = True
                st.success("Alertas ativados com sucesso!")
                st.rerun()
            else:
                st.warning("Por favor, informe um e-mail válido e marque a autorização.")
    with col2:
        if st.button("❌ Agora Não", use_container_width=True):
            st.session_state["alertas_email_ativados"] = False
            st.rerun()