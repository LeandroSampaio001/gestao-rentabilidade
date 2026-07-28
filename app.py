"""Página Inicial - Importação Rápida e Diagnóstico Direto."""

import pandas as pd
import streamlit as st

from ui.session import init_session_state

init_session_state()

st.title("📂 Início - Gestão de Rentabilidade")
st.markdown("---")

st.markdown("### 🚀 Importação Rápida de Dados")
st.markdown("Faça o upload das planilhas semanais abaixo para iniciar as análises:")

col1, col2 = st.columns(2)
with col1:
    file_vendas = st.file_uploader("Planilha de Vendas (CSV)", type="csv", key="main_vendas")
with col2:
    file_custos = st.file_uploader("Planilha de Custos (CSV)", type="csv", key="main_custos")

# Salva os arquivos na sessão de forma persistente
if file_vendas is not None:
    try:
        st.session_state["df_vendas_raw"] = pd.read_csv(file_vendas)
        st.session_state["nome_vendas"] = file_vendas.name
    except Exception as e:
        st.error(f"❌ Erro ao ler o CSV de Vendas: {e}")

if file_custos is not None:
    try:
        st.session_state["df_custos_raw"] = pd.read_csv(file_custos)
        st.session_state["nome_custos"] = file_custos.name
    except Exception as e:
        st.error(f"❌ Erro ao ler o CSV de Custos: {e}")

tem_vendas = "df_vendas_raw" in st.session_state and st.session_state["df_vendas_raw"] is not None
tem_custos = "df_custos_raw" in st.session_state and st.session_state["df_custos_raw"] is not None

if tem_vendas and tem_custos:
    df_v = st.session_state["df_vendas_raw"]
    df_c = st.session_state["df_custos_raw"]

    st.success(f"✅ Arquivos carregados: **{st.session_state.get('nome_vendas', 'Vendas')}** e **{st.session_state.get('nome_custos', 'Custos')}**")

    # Verificação direta e infalível de integridade (estrutura e dados corrompidos/nulos)
    tem_erro_conteudo = False
    motivo_erro = ""

    # Verifica colunas obrigatórias básicas
    cols_vendas_nec = {"SKU", "VALOR_VENDA_BRUTO"}
    cols_custos_nec = {"SKU", "PRECO_CUSTO"}

    if not cols_vendas_nec.issubset(df_v.columns) or not cols_custos_nec.issubset(df_c.columns):
        tem_erro_conteudo = True
        motivo_erro = "Colunas obrigatórias ausentes nas planilhas."
    else:
        # Verifica se há valores nulos/vazios em custos
        if df_c["PRECO_CUSTO"].isna().any():
            tem_erro_conteudo = True
            motivo_erro = "Existem preços de custo vazios na planilha de custos."
        
        # Verifica se há caracteres inválidos (letras misturadas em números) na venda bruta
        venda_str = df_v["VALOR_VENDA_BRUTO"].astype(str)
        # Tenta converter para float para ver se há letras (ex: '200,00x')
        for val in venda_str:
            val_limpo = val.replace("R$", "").strip().replace(".", "").replace(",", ".")
            try:
                float(val_limpo)
            except ValueError:
                tem_erro_conteudo = True
                motivo_erro = f"Valor de venda inválido detectado ('{val}')."
                break

    if tem_erro_conteudo:
        st.warning("⚠️ **Atenção: Foram encontrados erros ou inconsistências nas suas planilhas!**")
        st.error(f"**Detalhe:** {motivo_erro}")
        st.info(
            "👉 Vá para o módulo **Correcao de Erros Na Planilha** no menu lateral "
            "para inspecionar os detalhes e decidir como prosseguir."
        )
    else:
        st.success("✨ Planilhas validadas com sucesso e 100% íntegras! Você já pode navegar pelos módulos.")

elif tem_vendas or tem_custos:
    st.warning("⚠️ Aguardando o carregamento de ambas as planilhas (Vendas e Custos) para efetuar a validação.")
else:
    st.info("ℹ️ Faça o upload das planilhas de Vendas e Custos acima para começar.")

st.markdown("---")
st.caption("Gestão de Rentabilidade v2.0")