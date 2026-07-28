"""Componentes de links operacionais e atalhos por SKU."""

import streamlit as st
import pandas as pd


def render_coluna_links(df: pd.DataFrame):
    """Renderiza coluna de URLs de anúncios com acesso direto."""
    if "URL_ANUNCIO" not in df.columns:
        st.info(
            "💡 Adicione a coluna opcional `URL_ANUNCIO` nas planilhas para "
            "acesso direto aos anúncios (Mercado Livre, Shopee, etc.)."
        )
        return

    df_links = df[df["URL_ANUNCIO"].notna() & (df["URL_ANUNCIO"] != "")]
    if df_links.empty:
        st.warning("Nenhum SKU possui URL de anúncio cadastrada.")
        return

    st.markdown("**🔗 Links diretos dos anúncios:**")
    for _, row in df_links.iterrows():
        url = str(row["URL_ANUNCIO"]).strip()
        if url and url.startswith("http"):
            st.markdown(f"- **{row['SKU']}**: [{url[:60]}...]({url})")


def render_tabela_com_links(df: pd.DataFrame):
    """Exibe tabela com coluna de links clicáveis apenas para URLs válidas."""
    df_exibicao = df.copy()
    
    # Valida se a URL é real antes de renderizar o link na coluna
    if "URL_ANUNCIO" in df_exibicao.columns:
        df_exibicao["URL_ANUNCIO"] = df_exibicao["URL_ANUNCIO"].apply(
            lambda x: x if pd.notna(x) and str(x).strip().startswith("http") else None
        )

    cols_exibir = ["SKU", "LUCRO_LIQUIDO", "MARGEM_PCT", "STATUS"]
    if "URL_ANUNCIO" in df_exibicao.columns:
        cols_exibir.append("URL_ANUNCIO")
    if "QTD_VENDIDA" in df_exibicao.columns:
        cols_exibir.append("QTD_VENDIDA")

    st.dataframe(
        df_exibicao[[c for c in cols_exibir if c in df_exibicao.columns]],
        use_container_width=True,
        column_config={
            "URL_ANUNCIO": st.column_config.LinkColumn("Anúncio", display_text="Abrir"),
            "LUCRO_LIQUIDO": st.column_config.NumberColumn("Lucro (R$)", format="R$ %.2f"),
            "MARGEM_PCT": st.column_config.NumberColumn("Margem %", format="%.1f%%"),
        },
    )