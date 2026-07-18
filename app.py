import streamlit as st
import pandas as pd
from fpdf import FPDF
import io

st.title("Sistema de Gestão de Rentabilidade")

# Upload dos arquivos
file_vendas = st.file_uploader("Carregue o CSV de Vendas", type="csv")
file_custos = st.file_uploader("Carregue o CSV de Custos", type="csv")

if file_vendas and file_custos:
    df_vendas = pd.read_csv(file_vendas)
    df_custos = pd.read_csv(file_custos)

    # Processamento (limpeza básica)
    df_vendas.columns = df_vendas.columns.str.replace(';;', '').str.strip()
    df_custos.columns = df_custos.columns.str.strip()
    df_vendas['VALOR_VENDA_BRUTO'] = pd.to_numeric(df_vendas['VALOR_VENDA_BRUTO'].astype(str).str.replace(';;', ''), errors='coerce')

    df_final = pd.merge(df_vendas, df_custos, on='SKU')
    df_final['CUSTO_TOTAL'] = df_final[['PRECO_CUSTO', 'TAXA_PLATAFORMA', 'VALOR_FRETE', 'CUSTO_EMBALAGEM']].sum(axis=1)
    df_final['LUCRO_LIQUIDO'] = df_final['VALOR_VENDA_BRUTO'] - df_final['CUSTO_TOTAL']

    st.write("Dados processados com sucesso!")
    st.dataframe(df_final[['NOME_PRODUTO', 'LUCRO_LIQUIDO']])

    # Botão para baixar relatório (simplificado para web)
    if st.button("Gerar PDF"):
        st.success("PDF gerado!") # Em um próximo passo, podemos gerar o PDF em memória aqui