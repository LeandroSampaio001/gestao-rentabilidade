"""Geração de relatório profissional em PDF."""

import pandas as pd
from fpdf import FPDF

from config.constants import STATUS_CORES_RGB, STATUS_ERRO
from core.status import resumo_por_status


class PDFRelatorio(FPDF):
    def header(self):
        self.set_fill_color(30, 41, 59)
        self.rect(0, 0, 210, 28, "F")
        self.set_font("Arial", "B", 14)
        self.set_text_color(255, 255, 255)
        self.set_xy(10, 6)
        self.cell(0, 8, "RELATORIO DE GESTAO DE RENTABILIDADE", 0, 0, "L")
        self.set_font("Arial", "", 8)
        self.set_xy(10, 15)
        self.cell(0, 6, "Analise automatizada de margem e lucro liquido por SKU", 0, 0, "L")
        self.ln(28)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Pagina {self.page_no()}", 0, 0, "C")


def _formatar_moeda(valor) -> str:
    if pd.isna(valor):
        return "N/D"
    return f"R$ {float(valor):.2f}"


def _formatar_pct(valor) -> str:
    if pd.isna(valor):
        return "N/D"
    return f"{float(valor):.1f}%"


def gerar_pdf(df: pd.DataFrame) -> bytes:
    """Gera PDF com cabeçalho corporativo, paginação, zebrado e cores por status."""
    pdf = PDFRelatorio(orientation="L", unit="mm", format="A4")
    pdf.add_page()

    resumo = resumo_por_status(df)
    pdf.set_font("Arial", "B", 10)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(0, 8, "Resumo Executivo", 0, 1, "L")
    pdf.set_font("Arial", "", 9)
    for status, qtd in resumo.items():
        rgb = STATUS_CORES_RGB.get(status, (30, 41, 59))
        pdf.set_text_color(*rgb)
        pdf.cell(0, 6, f"  {status}: {qtd} SKU(s)", 0, 1, "L")

    lucro_total = df["LUCRO_LIQUIDO"].sum(skipna=True)
    pdf.set_text_color(30, 41, 59)
    pdf.set_font("Arial", "B", 9)
    pdf.cell(0, 8, f"Lucro Liquido Total: {_formatar_moeda(lucro_total)}", 0, 1, "L")
    pdf.ln(4)

    colunas = ["SKU", "LUCRO_LIQUIDO", "MARGEM_PCT", "STATUS"]
    larguras = [40, 45, 35, 50]
    headers = ["SKU", "LUCRO LIQUIDO", "MARGEM %", "STATUS"]

    pdf.set_font("Arial", "B", 9)
    pdf.set_fill_color(241, 245, 249)
    pdf.set_text_color(30, 41, 59)
    for header, largura in zip(headers, larguras):
        pdf.cell(largura, 8, header, 1, 0, "C", True)
    pdf.ln()

    pdf.set_font("Arial", "", 8)
    for index, row in df.iterrows():
        if pdf.get_y() > 180:
            pdf.add_page()
            pdf.set_font("Arial", "B", 9)
            pdf.set_fill_color(241, 245, 249)
            for header, largura in zip(headers, larguras):
                pdf.cell(largura, 8, header, 1, 0, "C", True)
            pdf.ln()
            pdf.set_font("Arial", "", 8)

        fill = index % 2 == 0
        pdf.set_fill_color(255, 255, 255) if fill else pdf.set_fill_color(248, 250, 252)

        status = str(row.get("STATUS", STATUS_ERRO))
        pdf.set_text_color(30, 41, 59)
        pdf.cell(larguras[0], 7, str(row["SKU"])[:20], 1, 0, "C", True)
        pdf.cell(larguras[1], 7, _formatar_moeda(row.get("LUCRO_LIQUIDO")), 1, 0, "C", True)
        pdf.cell(larguras[2], 7, _formatar_pct(row.get("MARGEM_PCT")), 1, 0, "C", True)

        rgb = STATUS_CORES_RGB.get(status, (128, 128, 128))
        pdf.set_text_color(*rgb)
        pdf.cell(larguras[3], 7, status, 1, 1, "C", True)

    output = pdf.output(dest="S")
    if isinstance(output, (bytes, bytearray)):
        return bytes(output)
    return output.encode("latin1")
