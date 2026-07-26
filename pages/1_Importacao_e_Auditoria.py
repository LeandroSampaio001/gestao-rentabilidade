"""Página principal — Importação, validação e auditoria de dados."""

import pandas as pd
import streamlit as st

from config.constants import COLUNAS_CUSTOS_OPCIONAIS, COLUNAS_VENDAS_OPCIONAIS
from core.processing import processar_rentabilidade
from core.validation import validar_planilhas_completas
from ui.alerts import gerar_alertas_automaticos
from ui.audit_display import (
    render_divergencia_skus,
    render_erros_celulas,
    render_opcao_prosseguir,
)
from ui.components import render_coluna_links, render_tabela_com_links
from ui.session import dados_disponiveis, init_session_state

init_session_state()

st.title("📋 Importação e Auditoria de Dados")
st.markdown("---")

st.markdown("### Instruções de Uso")
st.info(
    "1. **Primeiro arquivo:** Carregue a **planilha de vendas** (CSV).\n"
    "2. **Segundo arquivo:** Carregue a **planilha de custos** (CSV).\n"
    "3. Colunas opcionais: `URL_ANUNCIO`, `QTD_VENDIDA`, `ESTOQUE_ATUAL`."
)

with st.expander("📄 Esquema esperado das planilhas"):
    st.markdown(
        "**Vendas (obrigatório):** `SKU`, `VALOR_VENDA_BRUTO`\n\n"
        "**Vendas (opcional):** `URL_ANUNCIO`, `QTD_VENDIDA`\n\n"
        "**Custos (obrigatório):** `SKU`, `PRECO_CUSTO`, `TAXA_PLATAFORMA`, "
        "`VALOR_FRETE`, `CUSTO_EMBALAGEM`\n\n"
        "**Custos (opcional):** `URL_ANUNCIO`, `ESTOQUE_ATUAL`"
    )

col1, col2 = st.columns(2)
with col1:
    file_vendas = st.file_uploader("1️⃣ Planilha de Vendas (CSV)", type="csv")
with col2:
    file_custos = st.file_uploader("2️⃣ Planilha de Custos (CSV)", type="csv")

if file_vendas or file_custos:
    try:
        if not file_vendas:
            st.warning("⚠️ Aguardando o carregamento da **Planilha de Vendas**.")
        elif not file_custos:
            st.warning("⚠️ Aguardando o carregamento da **Planilha de Custos**.")
        else:
            df_vendas = pd.read_csv(file_vendas)
            df_custos = pd.read_csv(file_custos)

            st.session_state["df_vendas_raw"] = df_vendas
            st.session_state["df_custos_raw"] = df_custos

            ok, msg, auditoria = validar_planilhas_completas(df_vendas, df_custos)

            if not ok:
                st.error(f"❌ {msg}")
                st.warning(
                    "💡 Clique no **'X'** do arquivo com erro para reenviá-lo corrigido."
                )
            else:
                st.session_state["auditoria"] = auditoria
                render_erros_celulas(auditoria)
                render_divergencia_skus(auditoria)

                processar = render_opcao_prosseguir(auditoria)

                if processar:
                    df_final = processar_rentabilidade(
                        df_vendas, df_custos, auditoria, modo_tolerante=True
                    )

                    if df_final.empty:
                        st.error(
                            "❌ Nenhum SKU em comum foi encontrado entre as planilhas."
                        )
                    else:
                        st.session_state["df_processado"] = df_final
                        st.session_state["alertas"] = gerar_alertas_automaticos(
                            df_final
                        )

                        st.success("✅ Processamento concluído!")
                        st.subheader("📊 Resultado da Análise de Rentabilidade")
                        render_tabela_com_links(df_final)
                        render_coluna_links(df_final)

                        resumo = df_final["STATUS"].value_counts()
                        cols = st.columns(len(resumo))
                        for i, (status, qtd) in enumerate(resumo.items()):
                            cols[i].metric(status, qtd)

    except Exception as e:
        st.error(f"❌ Ocorreu um erro técnico inesperado: {e}")

elif dados_disponiveis():
    st.info("Dados já processados nesta sessão. Veja os resultados abaixo ou recarregue novos arquivos.")
    df = st.session_state["df_processado"]
    render_tabela_com_links(df)
