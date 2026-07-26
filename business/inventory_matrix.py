"""Análise de Giro de Estoque — Matriz de Desempenho."""

import pandas as pd

from config.constants import GIRO_ALTO, GIRO_BAIXO, STATUS_PREJUIZO


def classificar_matriz_desempenho(df: pd.DataFrame) -> pd.DataFrame:
    """
    Categoriza SKUs em matriz rentabilidade x giro:
    - Estrela: alta rentabilidade + alto giro
    - Vaca Leiteira: rentabilidade ok + alto giro
    - Peso Morto: baixo giro + baixa rentabilidade
    - Oportunidade: alta rentabilidade + baixo giro
    - Alerta: prejuízo
    """
    resultado = df.copy()

    def _categoria(row):
        if row.get("STATUS") == STATUS_PREJUIZO:
            return "🔴 Alerta (Prejuízo)"
        qtd = row.get("QTD_VENDIDA", 1)
        lucro = row.get("LUCRO_LIQUIDO", 0)
        margem = row.get("MARGEM_PCT", 0)

        alto_giro = qtd >= GIRO_ALTO
        baixo_giro = qtd <= GIRO_BAIXO
        alta_rent = lucro > 20 and (pd.isna(margem) or margem > 15)
        baixa_rent = lucro <= 5

        if alto_giro and alta_rent:
            return "⭐ Estrela"
        if alto_giro and not baixa_rent:
            return "🐄 Vaca Leiteira"
        if baixo_giro and (baixa_rent or row.get("STATUS") == "Pouco Lucrativo"):
            return "⚓ Peso Morto"
        if baixo_giro and alta_rent:
            return "💎 Oportunidade (Investir em Tráfego)"
        return "📊 Monitorar"

    resultado["CATEGORIA_GIRO"] = resultado.apply(_categoria, axis=1)
    return resultado


def render_inventory_matrix(df: pd.DataFrame):
    """Interface Streamlit da matriz de giro de estoque."""
    import streamlit as st

    st.subheader("📦 Análise de Giro de Estoque (Matriz de Desempenho)")
    st.markdown(
        "Categorização automática entre produtos de alta rentabilidade "
        "e itens 'peso-morto' que travam capital de giro."
    )

    if df.empty:
        st.warning("Carregue e processe os dados na página de Importação primeiro.")
        return

    df_matriz = classificar_matriz_desempenho(df)

    categorias = df_matriz["CATEGORIA_GIRO"].value_counts()
    cols = st.columns(len(categorias) if len(categorias) <= 5 else 5)
    for i, (cat, qtd) in enumerate(categorias.items()):
        if i < len(cols):
            cols[i].metric(cat, qtd)

    peso_morto = df_matriz[df_matriz["CATEGORIA_GIRO"].str.contains("Peso Morto")]
    if not peso_morto.empty:
        st.error(
            f"⚓ **{len(peso_morto)} produto(s) peso-morto** travando capital de giro:"
        )
        st.dataframe(
            peso_morto[
                ["SKU", "LUCRO_LIQUIDO", "MARGEM_PCT", "QTD_VENDIDA", "ESTOQUE_ATUAL"]
            ],
            use_container_width=True,
        )

    estrelas = df_matriz[df_matriz["CATEGORIA_GIRO"].str.contains("Estrela")]
    if not estrelas.empty:
        st.success(f"⭐ **{len(estrelas)} produto(s) estrela** — priorize estoque e tráfego:")
        st.dataframe(
            estrelas[
                ["SKU", "LUCRO_LIQUIDO", "MARGEM_PCT", "QTD_VENDIDA"]
            ],
            use_container_width=True,
        )

    st.markdown("---")
    st.markdown("**Matriz completa:**")
    st.dataframe(
        df_matriz[
            [
                "SKU",
                "LUCRO_LIQUIDO",
                "MARGEM_PCT",
                "QTD_VENDIDA",
                "ESTOQUE_ATUAL",
                "STATUS",
                "CATEGORIA_GIRO",
            ]
        ],
        use_container_width=True,
    )

    st.info(
        "💡 **Dica:** Produtos 'Peso Morto' com estoque alto representam capital "
        "parado. Considere liquidação ou descontinuação."
    )
