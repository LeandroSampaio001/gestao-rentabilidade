import streamlit as st
import pandas as pd
from fpdf import FPDF
import io

# Configuração da página para um visual profissional
st.set_page_config(page_title="Gestão de Rentabilidade", layout="wide")

st.title("🚀 Sistema de Gestão de Rentabilidade")
st.markdown("---")

# Instruções claras para guiar o usuário iterativamente
st.markdown("### 📋 Instruções de Uso")
st.info(
    "1. **Primeiro arquivo:** Carregue abaixo a sua **planilha de vendas**.\n"
    "2. **Segundo arquivo:** Carregue abaixo a sua **planilha de custos**."
)

def validar_arquivo(df, colunas_esperadas, nome_planilha):
    """Verifica se as colunas necessárias estão presentes no CSV especificado."""
    colunas_faltantes = [col for col in colunas_esperadas if col not in df.columns]
    if colunas_faltantes:
        return False, f"Erro na coluna: Na **{nome_planilha}**, está faltando a(s) seguinte(s) coluna(s) obrigatória(s): {', '.join(colunas_faltantes)}."
    return True, "Validado com sucesso!"

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
        
    return pdf.output(dest='S').encode('latin1')

# Definição rigorosa das colunas esperadas para cada tipo de planilha
colunas_vendas = ['SKU', 'VALOR_VENDA_BRUTO']
colunas_custos = ['SKU', 'PRECO_CUSTO', 'TAXA_PLATAFORMA', 'VALOR_FRETE', 'CUSTO_EMBALAGEM']

# Layout de Upload dividido em colunas na tela
col1, col2 = st.columns(2)
with col1:
    file_vendas = st.file_uploader("1️⃣ Carregar Planilha de Vendas (CSV)", type="csv")
with col2:
    file_custos = st.file_uploader("2️⃣ Carregar Planilha de Custos (CSV)", type="csv")

# Validação individual para dar feedback preciso caso o usuário inverta os arquivos
if file_vendas or file_custos:
    try:
        # Se faltou um dos arquivos
        if not file_vendas:
            st.warning("⚠️ Aguardando o carregamento da **Planilha de Vendas** (primeiro arquivo).")
        elif not file_custos:
            st.warning("⚠️ Aguardando o carregamento da **Planilha de Custos** (segundo arquivo).")
        else:
            # Ambos carregados, hora de processar com segurança
            df_vendas = pd.read_csv(file_vendas)
            df_custos = pd.read_csv(file_custos)

            # Validar separadamente para mensurar o erro exato
            valido_vendas, msg_vendas = validar_arquivo(df_vendas, colunas_vendas, "Planilha de Vendas")
            valido_custos, msg_custos = validar_arquivo(df_custos, colunas_custos, "Planilha de Custos")

            if not valido_vendas:
                st.error(f"❌ **Erro no carregamento da primeira planilha:** {msg_vendas}")
                st.warning("💡 **O que fazer:** Clique no **'X'** ao lado do arquivo carregado incorretamente acima para removê-lo e, em seguida, carregue a planilha correta no lugar certo.")
            elif not valido_custos:
                st.error(f"❌ **Erro no carregamento da segunda planilha:** {msg_custos}")
                st.warning("💡 **O que fazer:** Clique no **'X'** ao lado do arquivo carregado incorretamente acima para removê-lo e, em seguida, carregue a planilha correta no lugar certo.")
            else:
                # Processamento limpo e seguro
                df_vendas['VALOR_VENDA_BRUTO'] = pd.to_numeric(df_vendas['VALOR_VENDA_BRUTO'].astype(str).str.replace(';', '').str.replace(',', '.'), errors='coerce')
                
                # Merge dos dados
                df_final = pd.merge(df_vendas, df_custos, on='SKU')
                
                # Cálculos
                df_final['CUSTO_TOTAL'] = df_final[['PRECO_CUSTO', 'TAXA_PLATAFORMA', 'VALOR_FRETE', 'CUSTO_EMBALAGEM']].sum(axis=1)
                df_final['LUCRO_LIQUIDO'] = df_final['VALOR_VENDA_BRUTO'] - df_final['CUSTO_TOTAL']

                st.success("✅ Dados processados com sucesso!")
                st.subheader("📊 Resultado da Análise de Rentabilidade")
                st.dataframe(df_final[['SKU', 'LUCRO_LIQUIDO']])

                # Botão de Download do PDF
                pdf_bytes = gerar_pdf(df_final)
                st.download_button(
                    label="📥 Baixar Relatório em PDF",
                    data=pdf_bytes,
                    file_name="relatorio_rentabilidade.pdf",
                    mime="application/pdf"
                )

    except Exception as e:
        st.error(f"❌ Ocorreu um erro técnico inesperado ao processar os arquivos: {e}")
        st.warning("Verifique se os arquivos enviados estão corrompidos ou se utilizam separadores inválidos.")