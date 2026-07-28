"""Página de Diagnóstico e Correção de Erros nas Planilhas."""

import pandas as pd
import streamlit as st

from core.processing import processar_rentabilidade
from core.validation import validar_planilhas_completas
from ui.alerts import gerar_alertas_automaticos
from ui.audit_display import (
    render_divergencia_skus,
    render_erros_celulas,
    render_opcao_prosseguir,
)
from ui.components import render_tabela_com_links
from ui.session import dados_disponiveis, init_session_state

init_session_state()

st.title("🛠️ Correção e Diagnóstico de Erros")
st.markdown("---")

st.markdown(
    """
    Este painel monitora a integridade das suas planilhas. Caso o sistema tenha apontado 
    alguma divergência ou erro célula a célula, você poderá analisar e decidir como prosseguir abaixo.
    """
)

# Captura os dados da sessão (se já carregados na tela Início)
df_vendas = st.session_state.get("df_vendas_raw", None)
df_custos = st.session_state.get("df_custos_raw", None)

if df_vendas is not None and df_custos is not None:
    st.info("📂 Utilizando as planilhas carregadas na sessão atual.")
    
    try:
        ok, msg, auditoria = validar_planilhas_completas(df_vendas, df_custos)

        if not ok:
            st.warning("⚠️ **Atenção: Problema estrutural detectado nas planilhas**")
            st.error(f"**O que aconteceu:** {msg}")
            st.info(
                "📌 **O que fazer:** Corrija o arquivo no seu Excel com base no erro acima "
                "ou reenvie planilhas ajustadas."
            )
        else:
            st.session_state["auditoria"] = auditoria
            render_erros_celulas(auditoria)
            render_divergencia_skus(auditoria)

            processar = render_opcao_prosseguir(auditoria)

            if processar:
                df_final = process_final = processar_rentabilidade(
                    df_vendas, df_custos, auditoria, modo_tolerante=True
                )

                if df_final.empty:
                    st.error("❌ Nenhum SKU em comum encontrado entre as planilhas.")
                else:
                    st.session_state["df_processado"] = df_final
                    st.session_state["alertas"] = gerar_alertas_automaticos(df_final)
                    st.success("✅ Correções aplicadas e dados reprocessados com sucesso!")
                    
                    st.subheader("📊 Prévia dos Dados Atualizados")
                    render_tabela_com_links(df_final)
    except Exception as e:
        st.error(f"❌ Erro técnico ao processar a auditoria: {e}")
elif dados_disponiveis():
    st.success("✅ Seus dados atuais já estão íntegros e processados.")
else:
    st.warning(
        "⚠️ Nenhuma planilha encontrada na sessão. "
        "Por favor, volte à página **Início** e faça o upload dos arquivos de Vendas e Custos."
    )

st.markdown("---")
st.caption("Gestão de Rentabilidade v2.0")
