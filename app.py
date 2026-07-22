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

class PDFRelatorio(FPDF):
    def header(self):
        # Cabeçalho decorativo profissional
        self.set_fill_color(30, 41, 59) # Azul escuro corporativo
        self.rect(0, 0, 210, 25, 'F')
        self.set_font('Arial', 'B', 14)
        self.set_text_color(255, 255, 255)
        self.set_xy(10, 8)
        self.cell(0, 10, 'RELATORIO DE GESTAO DE RENTABILIDADE', 0, 0, 'L')
        self.ln(25)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Pagina {self.page_no()}', 0, 0, 'C')

def gerar_pdf(df):
    """Gera um PDF formatado com linhas zebradas e coluna de status colorida."""
    pdf = PDFRelatorio()
    pdf.add_page()
    
    # Cabeçalho da Tabela
    pdf.set_font("Arial", "B", 10)
    pdf.set_fill_color(241, 245, 249)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(60, 8, "SKU", 1, 0, 'C', True)
    pdf.cell(65, 8, "LUCRO LIQUIDO (R$)", 1, 0, 'C', True)
    pdf.cell(65, 8, "STATUS", 1, 1, 'C', True)
    
    pdf.set_font("Arial", "", 10)
    
    for index, row in df.iterrows():
        sku = str(row['SKU'])
        lucro = float(row['LUCRO_LIQUIDO'])
        
        # Cores de fundo alternadas (Zebra: Branco e Cinza claro)
        if index % 2 == 0:
            pdf.set_fill_color(255, 255, 255)
        else:
            pdf.set_fill_color(248, 250, 252)
            
        pdf.set_text_color(30, 41, 59)
        pdf.cell(60, 8, sku, 1, 0, 'C', True)
        pdf.cell(65, 8, f"R$ {lucro:.2f}", 1, 0, 'C', True)
        
        if lucro > 20:
            status = "Lucrativo"
            pdf.set_text_color(22, 101, 52)
        elif lucro >= 0:
            status = "Pouco Lucrativo"
            pdf.set_text_color(161, 98, 7)
        else:
            status = "Prejuizo"
            pdf.set_text_color(185, 28, 28)
            
        pdf.cell(65, 8, status, 1, 1, 'C', True)
        
    return pdf.output(dest='S').encode('latin1')

# Definição das colunas esperadas
colunas_vendas = ['SKU', 'VALOR_VENDA_BRUTO']
colunas_custos = ['SKU', 'PRECO_CUSTO', 'TAXA_PLATAFORMA', 'VALOR_FRETE', 'CUSTO_EMBALAGEM']

# Layout de Upload
col1, col2 = st.columns(2)
with col1:
    file_vendas = st.file_uploader("1️⃣ Carregar Planilha de Vendas (CSV)", type="csv")
with col2:
    file_custos = st.file_uploader("2️⃣ Carregar Planilha de Custos (CSV)", type="csv")

if file_vendas or file_custos:
    try:
        if not file_vendas:
            st.warning("⚠️ Aguardando o carregamento da **Planilha de Vendas** (primeiro arquivo).")
        elif not file_custos:
            st.warning("⚠️ Aguardando o carregamento da **Planilha de Custos** (segundo arquivo).")
        else:
            df_vendas = pd.read_csv(file_vendas)
            df_custos = pd.read_csv(file_custos)

            # Validar estrutura de colunas
            valido_vendas, msg_vendas = validar_arquivo(df_vendas, colunas_vendas, "Planilha de Vendas")
            valido_custos, msg_custos = validar_arquivo(df_custos, colunas_custos, "Planilha de Custos")

            if not valido_vendas:
                st.error(f"❌ **Erro estrutural na primeira planilha:** {msg_vendas}")
                st.warning("💡 **O que fazer:** Clique no **'X'** ao lado do arquivo de Vendas para removê-lo e envie um arquivo com as colunas corretas.")
            elif not valido_custos:
                st.error(f"❌ **Erro estrutural na segunda planilha:** {msg_custos}")
                st.warning("💡 **O que fazer:** Clique no **'X'** ao lado do arquivo de Custos para removê-lo e envie um arquivo com as colunas corretas.")
            else:
                # Tratamento e limpeza rigorosa de conversão numérica por célula
                df_vendas['VALOR_VENDA_BRUTO'] = pd.to_numeric(
                    df_vendas['VALOR_VENDA_BRUTO'].astype(str).str.replace(';', '').str.replace(',', '.'), 
                    errors='coerce'
                )

                colunas_custos_numericas = ['PRECO_CUSTO', 'TAXA_PLATAFORMA', 'VALOR_FRETE', 'CUSTO_EMBALAGEM']
                for col in colunas_custos_numericas:
                    df_custos[col] = pd.to_numeric(
                        df_custos[col].astype(str).str.replace(';', '').str.replace(',', '.'), 
                        errors='coerce'
                    )

                # Verificar se há valores nulos (células com erros, textos inválidos ou em branco) após a conversão
                erros_vendas = df_vendas['VALOR_VENDA_BRUTO'].isna().any()
                erros_custos = df_custos[colunas_custos_numericas].isna().any().any()

                if erros_vendas:
                    st.error("❌ **Erro de dados na Planilha de Vendas:** Encontramos células com valores inválidos, letras ou vazios na coluna `VALOR_VENDA_BRUTO`.")
                    st.warning("💡 **O que fazer:** Abra a sua planilha de Vendas, verifique se todas as linhas da coluna de valores possuem apenas números válidos, corrija-as, salve o arquivo e faça o upload novamente clicando no 'X'.")
                elif erros_custos:
                    st.error("❌ **Erro de dados na Planilha de Custos:** Encontramos células com valores inválidos, letras ou vazios nas colunas de custos.")
                    st.warning("💡 **O que fazer:** Abra a sua planilha de Custos, verifique se há letras, caracteres especiais ou células vazias nas colunas numéricas, corrija o arquivo e envie-o novamente.")
                else:
                    # Merge dos dados
                    df_final = pd.merge(df_vendas, df_custos, on='SKU')
                    
                    if df_final.empty:
                        st.error("❌ **Erro de cruzamento:** Nenhum SKU em comum foi encontrado entre a planilha de Vendas e a de Custos.")
                        st.warning("💡 **O que fazer:** Certifique-se de que os códigos dos produtos (SKUs) na planilha de Vendas são idênticos aos cadastrados na planilha de Custos.")
                    else:
                        # Cálculos
                        df_final['CUSTO_TOTAL'] = df_final[colunas_custos_numericas].sum(axis=1)
                        df_final['LUCRO_LIQUIDO'] = df_final['VALOR_VENDA_BRUTO'] - df_final['CUSTO_TOTAL']

                        st.success("✅ Dados processados com sucesso!")
                        st.subheader("📊 Resultado da Análise de Rentabilidade")
                        st.dataframe(df_final[['SKU', 'LUCRO_LIQUIDO']])

                        # Botão de Download do PDF customizado
                        pdf_bytes = gerar_pdf(df_final)
                        st.download_button(
                            label="📥 Baixar Relatório em PDF com Status",
                            data=pdf_bytes,
                            file_name="relatorio_rentabilidade.pdf",
                            mime="application/pdf"
                        )

    except Exception as e:
        st.error(f"❌ Ocorreu um erro técnico inesperado ao processar os arquivos: {e}")
        st.warning("Verifique se os arquivos enviados estão corrompidos ou se utilizam codificações incompatíveis.")