"""Sistema de Gestão de Rentabilidade — Ponto de entrada Streamlit."""

import streamlit as st

from ui.session import dados_disponiveis, init_session_state

st.set_page_config(
    page_title="Gestão de Rentabilidade",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_session_state()

st.title("🚀 Sistema de Gestão de Rentabilidade")
st.markdown("---")

st.markdown(
    """
    Plataforma completa para **lojistas de e-commerce e marketplaces** analisarem
    rentabilidade, simularem cenários e tomarem decisões estratégicas.

    ### Módulos Disponíveis

    Use o menu lateral para navegar entre os módulos:

    | Módulo | Descrição |
    |--------|-----------|
    | **Importação e Auditoria** | Upload de CSV, validação e auditoria linha a linha |
    | **Relatórios** | Status dinâmico e exportação PDF profissional |
    | **Buy Box Simulator** | Simulação de impacto de preços da concorrência |
    | **Ponto de Equilíbrio** | Meta de faturamento e break-even |
    | **Campanhas e Descontos** | Teste de promoções e bloqueio de campanhas inviáveis |
    | **Giro de Estoque** | Matriz de desempenho (estrelas vs peso-morto) |
    | **Alertas e Notificações** | Alertas visuais e base para mobile/PWA |
    """
)

st.markdown("---")

if dados_disponiveis():
    df = st.session_state["df_processado"]
    st.success(f"✅ **{len(df)} SKU(s)** processados nesta sessão.")

    resumo = df["STATUS"].value_counts()
    cols = st.columns(len(resumo))
    for i, (status, qtd) in enumerate(resumo.items()):
        cols[i].metric(status, qtd)

    lucro_total = df["LUCRO_LIQUIDO"].sum(skipna=True)
    st.metric("Lucro Líquido Total", f"R$ {lucro_total:,.2f}")
else:
    st.info(
        "👈 Comece pela página **Importação e Auditoria** no menu lateral "
        "para carregar suas planilhas de vendas e custos."
    )

st.markdown("---")
st.caption("Desenvolvido por Leandro Sampaio | Gestão de Rentabilidade v2.0")
