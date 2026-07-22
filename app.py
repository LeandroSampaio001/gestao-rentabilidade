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
        
        # Cores condicionais do status no PDF
        if status == "Lucrativo":
            pdf.set_text_color(22, 101, 52)
        elif status == "Pouco Lucrativo":
            pdf.set_text_color(161, 98, 7)
        elif status == "Prejuizo":
            pdf.set_text_color(185, 28, 28)
        else:  # Erro
            pdf.set_text_color(128, 128, 128) # Cinza escuro ou tom de alerta para erro
            
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
                # Mapeamento cirúrgico de erros por linha e célula
                # Vamos converter e identificar quais linhas possuem falhas numéricas
                
                # Cópia temporária para checagem de conversão
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

                # Se houveram erros nas células, informamos detalhadamente e damos a escolha
                if erros_vendas_idx or erros_custos_detalhes:
                    st.warning("⚠️ **Atenção: Encontramos células com dados inválidos ou vazios nas suas planilhas!**")
                    
                    if erros_vendas_idx:
                        for idx in erros_vendas_idx:
                            sku_afetado = df_vendas.loc[idx, 'SKU'] if 'SKU' in df_vendas.columns else f"Linha {idx+1}"
                            st.markdown(f"- **Planilha de Vendas:** O produto **{sku_afetado}** (Linha {idx+2} do arquivo) está com valor inválido na coluna `VALOR_VENDA_BRUTO`.")
                    
                    if erros_custos_detalhes:
                        for idx, colunas_afetadas in erros_custos_detalhes.items():
                            sku_afetado = df_custos.loc[idx, 'SKU'] if 'SKU' in df_custos.columns else f"Linha {idx+1}"
                            cols_str = ', '.join(colunas_afetadas)
                            st.markdown(f"- **Planilha de Custos:** O produto **{sku_afetado}** (Linha {idx+2} do arquivo) apresenta dados corrompidos/vazios na(s) coluna(s): `{cols_str}`.")

                    st.markdown("---")
                    st.info("💡 **O que você deseja fazer?**")
                    
                    # Decisão interativa do usuário via checkbox ou selectbox/botão
                    opcao_usuario = st.radio(
                        "Escolha uma opção para continuar:",
                        ("Quero corrigir os arquivos e fazer upload novamente", "Gerar relatório mesmo assim (marcar os afetados com STATUS DE ERRO)")
                    )

                    if opcao_usuario == "Gerar relatório mesmo assim (marcar os afetados com STATUS DE ERRO)":
                        # Processamento tolerante a falhas marcando com ERRO
                        df_vendas['VALOR_VENDA_BRUTO_NUM'] = venda_numerica
                        
                        for col in colunas_custos_num:
                            df_custos[f"{col}_NUM"] = pd.to_numeric(
                                df_custos[col].astype(str).str.replace(';', '').str.replace(',', '.'), 
                                errors='coerce'
                            )
                        
                        df_final = pd.merge(df_vendas, df_custos, on='SKU', how='inner')
                        
                        # Definir custo total somando as colunas numéricas tratadas
                        custos_tratados = [f"{col}_NUM" for col in colunas_custos_num]
                        df_final['CUSTO_TOTAL'] = df_final[custos_tratados].sum(axis=1)
                        df_final['LUCRO_LIQUIDO'] = df_final['VALOR_VENDA_BRUTO_NUM'] - df_final['CUSTO_TOTAL']
                        
                        # Atribuir status dinâmico incluindo a condição de Erro
                        def definir_status(row):
                            if pd.isna(row['VALOR_VENDA_BRUTO_NUM']) or row[[f"{c}_NUM" for c in colunas_custos_num]].isna().any():
                                return "ERRO DE DADOS"
                            lucro = row['LUCRO_LIQUIDO']
                            if lucro > 20:
                                return "Lucrativo"
                            elif lucro >= 0:
                                return "Pouco Lucrativo"
                            else:
                                return "Prejuizo"

                        df_final['STATUS'] = df_final.apply(definir_status, axis=1)

                        st.success("✅ Relatório gerado com itens sinalizados!")
                        st.subheader("📊 Resultado da Análise com Itens com Erro")
                        st.dataframe(df_final[['SKU', 'LUCRO_LIQUIDO', 'STATUS']])

                        pdf_bytes = gerar_pdf(df_final)
                        st.download_button(
                            label="📥 Baixar Relatório em PDF com Itens de Erro",
                            data=pdf_bytes,
                            file_name="relatorio_rentabilidade_erros.pdf",
                            mime="application/pdf"
                        )
                else:
                    # Caminho feliz: Sem nenhum erro nas células
                    df_vendas['VALOR_VENDA_BRUTO'] = pd.to_numeric(
                        df_vendas['VALOR_VENDA_BRUTO'].astype(str).str.replace(';', '').str.replace(',', '.'), 
                        errors='coerce'
                    )
                    for col in colunas_custos_num:
                        df_custos[col] = pd.to_numeric(
                            df_custos[col].astype(str).str.replace(';', '').str.replace(',', '.'), 
                            errors='coerce'
                        )

                    df_final = pd.merge(df_vendas, df_custos, on='SKU')
                    
                    if df_final.empty:
                        st.error("❌ Nenhum SKU em comum foi encontrado entre as planilhas.")
                    else:
                        df_final['CUSTO_TOTAL'] = df_final[colunas_custos_num].sum(axis=1)
                        df_final['LUCRO_LIQUIDO'] = df_final['VALOR_VENDA_BRUTO'] - df_final['CUSTO_TOTAL']
                        
                        def definir_status_limpo(lucro):
                            if lucro > 20:
                                return "Lucrativo"
                            elif lucro >= 0:
                                return "Pouco Lucrativo"
                            else:
                                return "Prejuizo"

                        df_final['STATUS'] = df_final['LUCRO_LIQUIDO'].apply(definir_status_limpo)

                        st.success("✅ Dados processados com sucesso!")
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