"""Gestão de Ponto de Equilíbrio (Break-Even)."""

import pandas as pd

from config.constants import STATUS_PREJUIZO


def calcular_break_even(
    df: pd.DataFrame, custos_fixos_mensais: float
) -> dict:
    """Calcula meta de faturamento e ponto de virada para lucro."""
    if df.empty:
        return {"erro": "Nenhum dado disponível."}

    lucro_por_sku = df["LUCRO_LIQUIDO"].fillna(0)
    faturamento_por_sku = df["VALOR_VENDA_BRUTO_NUM"].fillna(0)

    lucro_total = lucro_por_sku.sum()
    faturamento_total = faturamento_por_sku.sum()
    qtd_skus = len(df)

    margem_media = (
        (lucro_total / faturamento_total * 100) if faturamento_total > 0 else 0
    )

    lucro_medio_por_sku = lucro_total / qtd_skus if qtd_skus > 0 else 0
    faturamento_medio_por_sku = faturamento_total / qtd_skus if qtd_skus > 0 else 0

    if margem_media > 0:
        faturamento_break_even = custos_fixos_mensais / (margem_media / 100)
        skus_necessarios = (
            faturamento_break_even / faturamento_medio_por_sku
            if faturamento_medio_por_sku > 0
            else 0
        )
    else:
        faturamento_break_even = float("inf")
        skus_necessarios = float("inf")

    falta_para_break_even = max(0, faturamento_break_even - faturamento_total)
    lucro_liquido_real = lucro_total - custos_fixos_mensais

    return {
        "custos_fixos": custos_fixos_mensais,
        "faturamento_atual": faturamento_total,
        "lucro_bruto_skus": lucro_total,
        "lucro_liquido_real": lucro_liquido_real,
        "margem_media_pct": margem_media,
        "faturamento_break_even": faturamento_break_even,
        "falta_para_break_even": falta_para_break_even,
        "skus_necessarios": skus_necessarios,
        "atingiu_break_even": lucro_liquido_real >= 0,
        "qtd_skus_prejuizo": len(df[df["STATUS"] == STATUS_PREJUIZO]),
    }


def render_break_even(df: pd.DataFrame):
    """Interface Streamlit de ponto de equilíbrio."""
    import streamlit as st

    st.subheader("⚖️ Gestão de Ponto de Equilíbrio")
    st.markdown(
        "Insira seus custos fixos mensais para rastrear a meta de faturamento "
        "e o ponto de virada para lucro."
    )

    if df.empty:
        st.warning("Carregue e processe os dados na página de Importação primeiro.")
        return

    custos_fixos = st.number_input(
        "Custos fixos mensais (R$)",
        min_value=0.0,
        value=5000.0,
        step=100.0,
        help="Aluguel, salários, ferramentas, assinaturas, etc.",
    )

    resultado = calcular_break_even(df, custos_fixos)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Faturamento Atual", f"R$ {resultado['faturamento_atual']:,.2f}")
    c2.metric("Margem Média", f"{resultado['margem_media_pct']:.1f}%")
    c3.metric(
        "Meta Break-Even",
        f"R$ {resultado['faturamento_break_even']:,.2f}"
        if resultado["faturamento_break_even"] != float("inf")
        else "N/A",
    )
    c4.metric("Lucro Líquido Real", f"R$ {resultado['lucro_liquido_real']:,.2f}")

    if resultado["atingiu_break_even"]:
        st.success(
            "✅ **Ponto de equilíbrio atingido!** "
            f"Lucro líquido após custos fixos: R$ {resultado['lucro_liquido_real']:,.2f}"
        )
    else:
        st.warning(
            f"📊 Faltam **R$ {resultado['falta_para_break_even']:,.2f}** "
            f"em faturamento para atingir o break-even."
        )

    st.progress(
        min(
            1.0,
            resultado["faturamento_atual"] / resultado["faturamento_break_even"]
            if resultado["faturamento_break_even"] not in (0, float("inf"))
            else 0,
        )
    )

    st.info(
        f"💡 Com margem média de **{resultado['margem_media_pct']:.1f}%**, "
        f"você precisa faturar **R$ {resultado['faturamento_break_even']:,.2f}** "
        f"para cobrir custos fixos de R$ {custos_fixos:,.2f}."
    )

    if resultado["qtd_skus_prejuizo"] > 0:
        st.error(
            f"⚠️ {resultado['qtd_skus_prejuizo']} SKU(s) em prejuízo "
            "estão puxando sua margem para baixo."
        )
