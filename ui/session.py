"""Gerenciamento de session state compartilhado entre páginas."""

import streamlit as st


def init_session_state():
    """Inicializa variáveis de sessão globais."""
    defaults = {
        "df_processado": None,
        "df_vendas_raw": None,
        "df_custos_raw": None,
        "auditoria": None,
        "alertas": [],
        "notificacoes_lidas": set(),
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def dados_disponiveis() -> bool:
    return (
        st.session_state.get("df_processado") is not None
        and not st.session_state["df_processado"].empty
    )


def get_df_processado():
    return st.session_state.get("df_processado")
