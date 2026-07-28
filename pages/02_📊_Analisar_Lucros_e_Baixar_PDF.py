"""Página de relatórios e exportação PDF."""

import streamlit as st

from config.constants import STATUS_CORES
from core.status import resumo_por_status
from reports.pdf_generator import gerar_pdf
from ui.components import render_tabela_com_links
from ui.session import dados_disponiveis, get_df_processado, init_session_state

init_session_state()

st.title("📈 Relatórios e Exportação")
st.markdown("---")

if not dados_disponiveis():
    st.warning("⚠️ Nenhum dado processado. Vá à página **Importação e Auditoria** primeiro.")
    st.stop()

df = get_df_processado()

st.subheader("Motor de Status Dinâmico")
resumo = resumo_por_status(df)

cols = st.columns(4)
status_ordem = ["Lucrativo", "Pouco Lucrativo", "Prejuizo", "ERRO DE DADOS"]
for i, status in enumerate(status_ordem):
    qtd = resumo.get(status, 0)
    cor = STATUS_CORES.get(status, "#333")
    cols[i].markdown(
        f"<div style='text-align:center;padding:12px;border-radius:8px;"
        f"background:{cor}22;border-left:4px solid {cor}'>"
        f"<b style='color:{cor}'>{status}</b><br>"
        f"<span style='font-size:24px'>{qtd}</span></div>",
        unsafe_allow_html=True,
    )

lucro_total = df["LUCRO_LIQUIDO"].sum(skipna=True)
margem_media = df["MARGEM_PCT"].mean(skipna=True)
c1, c2, c3 = st.columns(3)
c1.metric("Lucro Total", f"R$ {lucro_total:,.2f}")
c2.metric("Margem Média", f"{margem_media:.1f}%" if margem_media == margem_media else "N/D")
c3.metric("Total de SKUs", len(df))

st.markdown("---")
st.subheader("Tabela Detalhada")
render_tabela_com_links(df)

st.markdown("---")
st.subheader("📥 Exportar Relatório PDF")
st.markdown(
    "Relatório profissional com cabeçalho corporativo, paginação, "
    "linhas zebradas e cores condicionais por status."
)

pdf_bytes = gerar_pdf(df)
st.download_button(
    label="📥 Baixar Relatório em PDF",
    data=pdf_bytes,
    file_name="relatorio_rentabilidade.pdf",
    mime="application/pdf",
    type="primary",
)
