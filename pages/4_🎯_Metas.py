"""Página de Meta de Lucratividade."""

import streamlit as st
import pandas as pd

from ui.session import dados_disponiveis, get_df_processado, init_session_state

init_session_state()

st.title("🎯 Meta de Lucratividade")
st.markdown("---")

if not dados_disponiveis():
    st.warning("⚠️ Nenhum dado processado. Vá à página **Importação e Auditoria** primeiro.")
    st.stop()

df = get_df_processado()

st.markdown("### 📊 Análise de Ponto de Equilíbrio e Início do Lucro")
st.markdown(
    "Aqui você acompanha o volume de vendas necessário para cobrir todos os custos operacionais "
    "e o exato momento em que a operação passa a gerar **lucro real**."
)

if df.empty:
    st.info("Nenhum dado disponível para cálculo.")
else:
    # Exemplo de exibição analítica para a meta de lucratividade
    df_metas = df[["SKU", "VALOR_VENDA_BRUTO_NUM", "CUSTO_TOTAL", "LUCRO_LIQUIDO"]].copy()
    
    # Cálculo simples de unidades para zerar o prejuízo (se houver custo fixo proporcional ou margem de contribuição)
    df_metas["MARGEM_CONTRIBUICAO"] = df_metas["VALOR_VENDA_BRUTO_NUM"] - df_metas["CUSTO_TOTAL"]
    
    st.dataframe(
        df_metas,
        use_container_width=True,
        column_config={
            "VALOR_VENDA_BRUTO_NUM": st.column_config.NumberColumn("Preço de Venda (R$)", format="R$ %.2f"),
            "CUSTO_TOTAL": st.column_config.NumberColumn("Custo Total (R$)", format="R$ %.2f"),
            "LUCRO_LIQUIDO": st.column_config.NumberColumn("Lucro Líquido (R$)", format="R$ %.2f"),
            "MARGEM_CONTRIBUICAO": st.column_config.NumberColumn("Margem de Contribuição (R$)", format="R$ %.2f"),
        }
    )
