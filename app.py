import streamlit as st
import pandas as pd
from fpdf import FPDF
import io

# Configuração da página para um visual profissional
st.set_page_config(page_title="Gestão de Rentabilidade", layout="wide")

st.title("🚀 Sistema de Gestão de Rentabilidade")
st.markdown("---")

st.markdown("### 📋 Instruções de Uso")
st.info(
    "1. **Primeiro arquivo:** Carregue abaixo a sua **planilha de vendas**.\n"
    "2. **Segundo arquivo:** Carregue abaixo a sua **planilha de custos**."
)

def validar_estrutura(df, colunas_esperadas, nome_planilha):
    """Verifica se as colunas obrigatórias estão presentes no CSV."""
    colunas_faltantes = [col for col in colunas_esperadas if col not in df.columns]
    if colunas_faltantes:
        return False, f"Na **{nome_planilha}**, está faltando a(s) coluna(s): {', '.join(colunas_faltantes)}."
    return True, "Validado"

class PDFRelatorio(FPDF):
    def header(self):
        self.set_fill_color(30, 41, 59)
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
    """Gera um PDF formatado com cores dinâmicas para os status."""
    pdf = PDFRelatorio()
    pdf.add_page()
    
    pdf.set_font("Arial", "B", 10)
    pdf.set_fill_color(241, 245, 249)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(50, 8, "SKU", 1, 0, 'C', True)
    pdf.cell(50, 8, "LUCRO LIQUIDO (R$)", 1, 0, 'C', True)
    pdf.cell(90, 8, "STATUS", 1, 1, 'C', True)
    
    pdf.set_font("Arial", "", 10)
    
    for index, row in df.iterrows():
        sku = str(row['SKU'])
        status = str(row['STATUS'])
        lucro = row['LUCRO_LIQUIDO']
        
        if index % 2 == 0:
            pdf.set_fill_color(255, 255, 255)
        else:
            pdf.set_fill_color(248, 250, 252)
            
        pdf.set_text_color(30, 41, 59)
        pdf.cell(50, 8, sku, 1, 0, 'C', True)
        
        if pd.isna(lucro):
            lucro_str = "N/D"
        else:
            lucro_str = f"R$ {float(lucro):.2f}"
            
        pdf.cell(50, 8, lucro_str, 1, 0, 'C', True)
        
        if status == "Lucrativo":
            pdf.set_text_color(22, 101, 52)
        elif status == "Pouco Lucrativo":
            pdf.set_text_color(161, 98, 7)
        elif status == "Prejuizo":
            pdf.set_text_color(185, 28, 28)
        else:
            pdf.set_text_color(128, 128, 128)
            
        pdf.cell(90, 8, status, 1, 1, 'C', True)
        
    return pdf.output(dest='S').encode('latin1')

colunas_vendas = ['SKU', 'VALOR_VENDA_BRUTO']
colunas_custos = ['SKU', 'PRECO_CUSTO', 'TAXA_PLATAFORMA', 'VALOR_FRETE', 'CUSTO_EMBALAGEM']

col1, col2 = st.columns(2)
with col1:
    file_vendas = st.file_uploader("1️⃣ Carregar Planilha de Vendas (CSV)", type="csv")
with col2:
    file_custos = st.file_uploader("2️⃣ Carregar Planilha de Custos (CSV)", type="csv")

if file_vendas or file_custos:
    try:
        if not file_vendas:
            st.warning("⚠️ Aguardando o carregamento da **Planilha de Vendas**.")
        elif not file_custos:
            st.warning("⚠️ Aguardando o carregamento da **Planilha de Custos**.")
        else:
            df_vendas = pd.read_csv(file_vendas)
            df_custos = pd.read_csv(file_custos)

            # Validação estrutural de colunas
            ok_v, msg_v = validar_estrutura(df_vendas, colunas_vendas, "Planilha de Vendas")
            ok_c, msg_c = validar_estrutura(df_custos, colunas_custos, "Planilha de Custos")

            if not ok_v:
                st.error(f"❌ {msg_v}")
                st.warning("💡 Clique no **'X'** do arquivo de Vendas para reenviá-lo corrigido.")
            elif not ok_c:
                st.error(f"❌ {msg_c}")
                st.warning("💡 Clique no **'X'** do arquivo de Custos para reenviá-lo corrigido.")
            else:
                # Auditoria de células numéricas
                venda_numerica = pd.to_numeric(
                    df_vendas['VALOR_VENDA_BRUTO'].astype(str).str.replace(';', '').str.replace(',', '.'), 
                    errors='coerce'
                )
                erros_vendas_idx = df_vendas[venda_numerica.isna()].index.tolist()

                colunas_custos_num = ['PRECO_CUSTO', 'TAXA_PLATAFORMA', 'VALOR_FRETE', 'CUSTO_EMBALAGEM']
                erros_custos_detalhes = {}
                for col in colunas_custos_num:
                    temp_num = pd.to_numeric(
                        df_custos[col].astype(str).str.replace(';', '').str.replace(',', '.'), 
                        errors='coerce'
                    )
                    linhas_com_erro = df_custos[temp_num.isna()].index.tolist()
                    for idx in linhas_com_erro:
                        if idx not in erros_custos_detalhes:
                            erros_custos_detalhes[idx] = []
                        erros_custos_detalhes[idx].append(col)

                # Auditoria de SKUs (Divergência entre lotes/semanas)
                skus_vendas = set(df_vendas['SKU'].astype(str))
                skus_custos = set(df_custos['SKU'].astype(str))
                
                skus_apenas_vendas = skus_vendas - skus_custos
                skus_apenas_custos = skus_custos - skus_vendas
                tem_divergencia_lote = len(skus_apenas_vendas) > 0 or len(skus_apenas_custos) > 0

                # Tratamento de Erros de Células
                if erros_vendas_idx or erros_custos_detalhes:
                    st.warning("⚠️ **Atenção: Encontramos células com dados inválidos ou vazios nas suas planilhas!**")
                    if erros_vendas_idx:
                        for idx in erros_vendas_idx:
                            sku_afetado = df_vendas.loc[idx, 'SKU'] if 'SKU' in df_vendas.columns else f"Linha {idx+1}"
                            st.markdown(f"- **Planilha de Vendas:** O produto **{sku_afetado}** está com valor inválido em `VALOR_VENDA_BRUTO`.")
                    if erros_custos_detalhes:
                        for idx, colunas_afetadas in erros_custos_detalhes.items():
                            sku_afetado = df_custos.loc[idx, 'SKU'] if 'SKU' in df_custos.columns else f"Linha {idx+1}"
                            st.markdown(f"- **Planilha de Custos:** O produto **{sku_afetado}** apresenta dados vazios/corrompidos nas colunas: `{', '.join(colunas_afetadas)}`.")

                # Tratamento de Divergência de Lotes/Semanas (Diferença de SKUs)
                if tem_divergencia_lote:
                    st.warning("📅 **Atenção: As planilhas parecem ser de períodos ou lotes diferentes!**")
                    if skus_apenas_vendas:
                        st.markdown(f"- Há **{len(skus_apenas_vendas)} produto(s)** presentes nas **Vendas**, mas que **não possuem cadastro de custos** (Ex: `{list(skus_apenas_vendas)[:3]}...`).")
                    if skus_apenas_custos:
                        st.markdown(f"- Há **{len(skus_apenas_custos)} produto(s)** com custos cadastrados, mas que **não registraram vendas** neste arquivo (Ex: `{list(skus_apenas_custos)[:3]}...`).")

                # Se houver qualquer inconsistência (células erradas ou divergência de lotes), damos opção de controle
                if erros_vendas_idx or erros_custos_detalhes or tem_divergencia_lote:
                    st.markdown("---")
                    st.info("💡 **Como você deseja proceder?**")
                    opcao_usuario = st.radio(
                        "Escolha uma opção:",
                        ("Revisar e corrigir os arquivos", "Prosseguir mesmo assim (processar apenas os itens válidos/compatíveis)")
                    )

                    if opcao_usuario == "Prosseguir mesmo assim (processar apenas os itens válidos/compatíveis)":
                        processar_dados = True
                    else:
                        processar_dados = False
                else:
                    processar_dados = True

                if processar_dados:
                    # Execução do processamento
                    df_vendas['VALOR_VENDA_BRUTO_NUM'] = venda_numerica
                    for col in colunas_custos_num:
                        df_custos[f"{col}_NUM"] = pd.to_numeric(
                            df_custos[col].astype(str).str.replace(';', '').str.replace(',', '.'), 
                            errors='coerce'
                        )
                    
                    # Merge (mantendo alerta transparente)
                    df_final = pd.merge(df_vendas, df_custos, on='SKU', how='inner')
                    
                    if df_final.empty:
                        st.error("❌ Nenhum SKU em comum foi encontrado entre as planilhas para realizar o cruzamento.")
                    else:
                        custos_tratados = [f"{col}_NUM" for col in colunas_custos_num]
                        df_final['CUSTO_TOTAL'] = df_final[custos_tratados].sum(axis=1)
                        df_final['LUCRO_LIQUIDO'] = df_final['VALOR_VENDA_BRUTO_NUM'] - df_final['CUSTO_TOTAL']
                        
                        def definir_status(row):
                            if pd.isna(row['VALOR_VENDA_BRUTO_NUM']) or row[custos_tratados].isna().any():
                                return "ERRO DE DADOS"
                            lucro = row['LUCRO_LIQUIDO']
                            if lucro > 20:
                                return "Lucrativo"
                            elif lucro >= 0:
                                return "Pouco Lucrativo"
                            else:
                                return "Prejuizo"

                        df_final['STATUS'] = df_final.apply(definir_status, axis=1)

                        st.success("✅ Processamento concluído com base nos itens compatíveis!")
                        st.subheader("📊 Resultado da Análise de Rentabilidade")
                        st.dataframe(df_final[['SKU', 'LUCRO_LIQUIDO', 'STATUS']])

                        pdf_bytes = gerar_pdf(df_final)
                        st.download_button(
                            label="📥 Baixar Relatório em PDF",
                            data=pdf_bytes,
                            file_name="relatorio_rentabilidade.pdf",
                            mime="application/pdf"
                        )

    except Exception as e:
        st.error(f"❌ Ocorreu um erro técnico inesperado: {e}")