"""Simulador de Campanhas e Descontos."""

import pandas as pd

from config.constants import STATUS_PREJUIZO
from core.status import definir_status


def simular_desconto(df: pd.DataFrame, desconto_pct: float) -> pd.DataFrame:
    """Testa impacto de desconto promocional cruzado com estrutura de custos."""
    resultado = df.copy()
    resultado["PRECO_PROMOCIONAL"] = resultado["VALOR_VENDA_BRUTO_NUM"] * (
        1 - desconto_pct / 100
    )
    resultado["LUCRO_PROMOCIONAL"] = (
        resultado["PRECO_PROMOCIONAL"] - resultado["CUSTO_TOTAL"]
    )
    resultado["MARGEM_PROMOCIONAL"] = (
        resultado["LUCRO_PROMOCIONAL"] / resultado["PRECO_PROMOCIONAL"] * 100
    ).where(resultado["PRECO_PROMOCIONAL"] > 0)
    resultado["STATUS_PROMOCIONAL"] = resultado["LUCRO_PROMOCIONAL"].apply(
        definir_status
    )
    resultado["VIAVEL"] = resultado["STATUS_PROMOCIONAL"] != STATUS_PREJUIZO
    return resultado


def simular_campanha_lote(
    df: pd.DataFrame, descontos: list[float]
) -> pd.DataFrame:
    """Simula múltiplos percentuais promocionais em lote."""
    linhas = []
    for desc in descontos:
        sim = simular_desconto(df, desc)
        viaveis = sim["VIAVEL"].sum()
        inviaveis = len(sim) - viaveis
        linhas.append(
            {
                "Desconto (%)": desc,
                "SKUs Viáveis": viaveis,
                "SKUs Inviáveis": inviaveis,
                "Lucro Total Estimado": sim["LUCRO_PROMOCIONAL"].sum(),
            }
        )
    return pd.DataFrame(linhas)


def render_campaign_simulator(df: pd.DataFrame):
    """Interface Streamlit do simulador de campanhas e descontos."""
    import streamlit as st

    st.subheader("🎉 Promoções e Descontos")
    st.markdown(
        "Planeje percentuais promocionais (Black Friday, cupons, queima de estoque) "
        "cruzados com a estrutura de custos para bloquear campanhas inviáveis."
    )

    if df.empty:
        st.warning("Carregue e processe os dados na página de Importação primeiro.")
        return

    tab1, tab2 = st.tabs(["📊 Simulação Individual", "📈 Comparativo em Lote"])

    with tab1:
        desconto = st.slider(
            "Desconto promocional (%)",
            min_value=0.0,
            max_value=70.0,
            value=20.0,
            step=5.0,
        )
        df_sim = simular_desconto(df, desconto)
        inviaveis = df_sim[~df_sim["VIAVEL"]]
        viaveis = df_sim[df_sim["VIAVEL"]]

        c1, c2, c3 = st.columns(3)
        c1.metric("SKUs Viáveis", len(viaveis))
        c2.metric("SKUs Bloqueados", len(inviaveis), delta=f"-{len(inviaveis)}")
        c3.metric(
            "Lucro Total Estimado",
            f"R$ {df_sim['LUCRO_PROMOCIONAL'].sum():,.2f}",
        )

        if not inviaveis.empty:
            st.error(
                f"🚫 **{len(inviaveis)} SKU(s) inviável(is)** com {desconto}% de desconto:"
            )
            st.dataframe(
                inviaveis[
                    [
                        "SKU",
                        "VALOR_VENDA_BRUTO_NUM",
                        "PRECO_PROMOCIONAL",
                        "CUSTO_TOTAL",
                        "LUCRO_PROMOCIONAL",
                        "STATUS_PROMOCIONAL",
                    ]
                ],
                use_container_width=True,
            )
        else:
            st.success(f"✅ Todos os SKUs são viáveis com {desconto}% de desconto!")

    with tab2:
        st.markdown("**Comparativo de cenários promocionais:**")
        descontos_teste = [5, 10, 15, 20, 25, 30, 40, 50]
        comparativo = simular_campanha_lote(df, descontos_teste)
        st.dataframe(comparativo, use_container_width=True)

        st.bar_chart(
            comparativo.set_index("Desconto (%)")[["SKUs Viáveis", "SKUs Inviáveis"]]
        )
