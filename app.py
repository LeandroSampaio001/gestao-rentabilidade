import streamlit as st
import pandas as pd

# Configuração da página para um visual profissional
st.set_page_config(page_title="Gestão de Rentabilidade", layout="wide")

st.title("🚀 Sistema de Gestão de Rentabilidade")
st.markdown("---")

def validar_arquivo(df, colunas_esperadas, nome_arquivo):
    """Verifica se as colunas necessárias estão presentes no CSV."""
    colunas_faltantes = [col for col in colunas_esperadas if col not in df.columns]
    if colunas_faltantes:
        return False, f"O arquivo '{nome_arquivo}' está faltando as colunas: {', '.join(colunas_faltantes)}"
    return True, "Validado"

# Definição das colunas esperadas para cada arquivo
colunas_vendas = ['SKU', 'VALOR_VENDA_BRUTO']
colunas_custos = ['SKU', 'PRECO_CUSTO', 'TAXA_PLATAFORMA', 'VALOR_FRETE', 'CUSTO_EMBALAGEM']

# Upload dos arquivos
col1, col2 = st.columns(2)
with col1:
    file_vendas = st.file_uploader("Carregue o CSV de Vendas", type="csv")
with col2:
    file_custos = st.file_uploader("Carregue o CSV de Custos", type="csv")

if file_vendas and file_custos:
    try:
        # Carregamento
        df_vendas = pd.read_csv(file_vendas)
        df_custos = pd.read_csv(file_custos)

        # Validação
        valido_vendas, msg_vendas = validar_arquivo(df_vendas, colunas_vendas, "Vendas")
        valido_custos, msg_custos = validar_arquivo(df_custos, colunas_custos, "Custos")

        if not valido_vendas:
            st.error(msg_vendas)
        elif not valido_custos:
            st.error(msg_custos)
        else:
            # Processamento
            # Limpeza de dados de forma segura
            df_vendas['VALOR_VENDA_BRUTO'] = pd.to_numeric(df_vendas['VALOR_VENDA_BRUTO'].astype(str).str.replace(';', '').str.replace(',', '.'), errors='coerce')
            
            # Merge
            df_final = pd.merge(df_vendas, df_custos, on='SKU')
            
            # Cálculo de métricas
            df_final['CUSTO_TOTAL'] = df_final[['PRECO_CUSTO', 'TAXA_PLATAFORMA', 'VALOR_FRETE', 'CUSTO_EMBALAGEM']].sum(axis=1)
            df_final['LUCRO_LIQUIDO'] = df_final['VALOR_VENDA_BRUTO'] - df_final['CUSTO_TOTAL']

            st.success("✅ Dados processados com sucesso!")
            st.subheader("📊 Resultado da Análise")
            st.dataframe(df_final[['SKU', 'LUCRO_LIQUIDO']])

            if st.button("Gerar Relatório PDF"):
                st.info("Funcionalidade de exportação em desenvolvimento.")

    except Exception as e:
        st.error(f"Ocorreu um erro inesperado ao processar os arquivos: {e}")
        st.warning("Verifique se o formato dos seus arquivos CSV está correto.")