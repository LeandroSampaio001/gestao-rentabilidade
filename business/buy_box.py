"""Simulador de Margem por Concorrência (Buy Box Simulator)."""

import pandas as pd

from config.constants import STATUS_PREJUIZO
from core.status import definir_status


def simular_preco_concorrente(
    df: pd.DataFrame, sku: str, preco_concorrente: float
) -> dict:
    """Calcula impacto de um preço de concorrente na margem líquida."""
    row = df[df["SKU"].astype(str) == str(sku)]
    if row.empty:
        return {"erro": f"SKU {sku} não encontrado."}

    r = row.iloc[0]
    custo_total = r.get("CUSTO_TOTAL", 0)
    if pd.isna(custo_total):
        return {"erro": "Custo total indisponível para este SKU."}

    lucro_atual = r.get("LUCRO_LIQUIDO", 0)
    preco_atual = r.get("VALOR_VENDA_BRUTO_NUM", 0)
    lucro_simulado = preco_concorrente - custo_total
    margem_simulada = (
        (lucro_simulado / preco_concorrente * 100) if preco_concorrente > 0 else 0
    )
    diferenca = lucro_simulado - lucro_atual
    status_simulado = definir_status(lucro_simulado)

    return {
        "sku": sku,
        "preco_atual": preco_atual,
        "preco_concorrente": preco_concorrente,
        "custo_total": custo_total,
        "lucro_atual": lucro_atual,
        "lucro_simulado": lucro_simulado,
        "margem_simulada": margem_simulada,
        "diferenca_lucro": diferenca,
        "status_simulado": status_simulado,
        "risco_prejuizo": status_simulado == STATUS_PREJUIZO,
    }


def simular_lote_concorrencia(
    df: pd.DataFrame, variacao_pct: float
) -> pd.DataFrame:
    """Simula impacto de redução/aumento de preço em lote (%)."""
    resultado = df.copy()
    resultado["PRECO_SIMULADO"] = resultado["VALOR_VENDA_BRUTO_NUM"] * (
        1 + variacao_pct / 100
    )
    resultado["LUCRO_SIMULADO"] = (
        resultado["PRECO_SIMULADO"] - resultado["CUSTO_TOTAL"]
    )
    resultado["MARGEM_SIMULADA"] = (
        resultado["LUCRO_SIMULADO"] / resultado["PRECO_SIMULADO"] * 100
    ).where(resultado["PRECO_SIMULADO"] > 0)
    resultado["STATUS_SIMULADO"] = resultado["LUCRO_SIMULADO"].apply(definir_status)
    resultado["VARIACAO_LUCRO"] = (
        resultado["LUCRO_SIMULADO"] - resultado["LUCRO_LIQUIDO"]
    )
    return resultado


def render_buy_box_simulator(df: pd.DataFrame):
    """Interface Streamlit do simulador Buy Box."""
    import streamlit as st

    st.subheader("🏷️ Simulador de Margem por Concorrência (Buy Box)")
    st.markdown(
        "Simule o impacto de variações de preço de mercado ou do concorrente "
        "na margem líquida de cada SKU."
    )

    if df.empty:
        st.warning("Carregue e processe os dados na página de Importação primeiro.")
        return

    tab1, tab2 = st.tabs(["Simulação por SKU", "Simulação em Lote"])

    with tab1:
        skus = df["SKU"].astype(str).tolist()
        col1, col2 = st.columns(2)
        with col1:
            sku_sel = st.selectbox("Selecione o SKU", skus)
        with col2:
            row = df[df["SKU"].astype(str) == sku_sel].iloc[0]
            preco_atual = float(row["VALOR_VENDA_BRUTO_NUM"])
            preco_conc = st.number_input(
                "Preço do concorrente (R$)",
                min_value=0.0,
                value=round(preco_atual * 0.95, 2),
                step=1.0,
            )

        sim = simular_preco_concorrente(df, sku_sel, preco_conc)
        if "erro" in sim:
            st.error(sim["erro"])
        else:
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Preço Atual", f"R$ {sim['preco_atual']:.2f}")
            c2.metric("Lucro Atual", f"R$ {sim['lucro_atual']:.2f}")
            c3.metric("Lucro Simulado", f"R$ {sim['lucro_simulado']:.2f}")
            c4.metric("Margem Simulada", f"{sim['margem_simulada']:.1f}%")

            if sim["risco_prejuizo"]:
                st.error(
                    f"⚠️ **ALERTA DE RISCO:** Com preço de R$ {preco_conc:.2f}, "
                    f"o SKU **{sku_sel}** entraria em **{STATUS_PREJUIZO}**!"
                )
            elif sim["status_simulado"] == "Pouco Lucrativo":
                st.warning(
                    f"⚡ Atenção: margem reduzida. Status simulado: **{sim['status_simulado']}**"
                )
            else:
                st.success(f"✅ Status simulado: **{sim['status_simulado']}**")

    with tab2:
        variacao = st.slider(
            "Variação de preço de mercado (%)",
            min_value=-50.0,
            max_value=50.0,
            value=-10.0,
            step=1.0,
            help="Negativo = queda de preço (concorrência). Positivo = aumento.",
        )
        df_sim = simular_lote_concorrencia(df, variacao)
        em_prejuizo = df_sim[df_sim["STATUS_SIMULADO"] == STATUS_PREJUIZO]

        st.metric(
            "SKUs em risco de prejuízo",
            len(em_prejuizo),
            delta=f"{len(em_prejuizo) - len(df_sim[df_sim['STATUS'] == STATUS_PREJUIZO])}",
        )

        if not em_prejuizo.empty:
            st.error("SKUs que entrariam em prejuízo com esta variação:")
            st.dataframe(
                em_prejuizo[
                    ["SKU", "LUCRO_LIQUIDO", "LUCRO_SIMULADO", "STATUS", "STATUS_SIMULADO"]
                ],
                use_container_width=True,
            )

        st.dataframe(
            df_sim[
                [
                    "SKU",
                    "VALOR_VENDA_BRUTO_NUM",
                    "PRECO_SIMULADO",
                    "LUCRO_LIQUIDO",
                    "LUCRO_SIMULADO",
                    "STATUS_SIMULADO",
                ]
            ],
            use_container_width=True,
        )
