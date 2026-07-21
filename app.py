import streamlit as st
import pandas as pd
from fpdf import FPDF
import io

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

def gerar_pdf(df):
    """Gera um PDF em memória com os resultados da análise."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    
    # Cabeçalho do Relatório
    pdf.cell(200, 10, txt="Relatorio de Gestao de Rentabilidade", ln=True, align="C")
    pdf.ln(10)
    
    pdf.set_font("Arial", "B", 12)
    pdf.cell(100, 10, "SKU", 1)
    pdf.cell(90, 10, "Lucro Liquido", 1)
    pdf.ln()
    
    pdf.set_font("Arial", "", 12)
    for index, row in df.iterrows():
        pdf.cell(100, 10, str(row['SKU']), 1)
        pdf.cell(90, 10, str(row['LUCRO_LIQUIDO']), 1)
        pdf.ln()
        
    # Retorna o PDF como bytes para o botão de download
    return pdf.output(dest='S').encode('latin1')

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
            df_vendas['VALOR_VENDA_BRUTO'] = pd.to_numeric(df_vendas['VALOR_VENDA_BRUTO'].astype(str).str.replace(';', '').str.replace(',', '.'), errors='coerce')
            
            # Merge
            df_final = pd.merge(df_vendas, df_custos, on='SKU')
            
            # Cálculo de métricas
            df_final['CUSTO_TOTAL'] = df_final[['PRECO_CUSTO', 'TAXA_PLATAFORMA', 'VALOR_FRETE', 'CUSTO_EMBALAGEM']].sum(axis=1)
            df_final['LUCRO_LIQUIDO'] = df_final['VALOR_VENDA_BRUTO'] - df_final['CUSTO_TOTAL']

            st.success("✅ Dados processados com sucesso!")
            st.subheader("📊 Resultado da Análise")
            st.dataframe(df_final[['SKU', 'LUCRO_LIQUIDO']])

            # Botão de Download do PDF funcional
            pdf_bytes = gerar_pdf(df_final)
            st.download_button(
                label="📥 Baixar Relatório em PDF",
                data=pdf_bytes,
                file_name="relatorio_rentabilidade.pdf",
                mime="application/pdf"
            )

    except Exception as e:
        st.error(f"Ocorreu um erro inesperado ao processar os arquivos: {e}")
        st.warning("Verifique se o formato dos seus arquivos CSV está correto.")