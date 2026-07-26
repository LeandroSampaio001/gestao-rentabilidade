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


def render_atalhos_campanhas(df: pd.DataFrame):
    """Atalhos rápidos para gerenciamento de campanhas de tráfego pago."""
    st.markdown("**📢 Atalhos de Campanhas de Tráfego Pago**")

    skus = df["SKU"].astype(str).tolist()
    sku_sel = st.selectbox("Selecione o SKU para gerenciar campanha", skus, key="camp_sku")

    col1, col2, col3 = st.columns(3)

    plataformas = {
        "Google Ads": f"https://ads.google.com/aw/campaigns",
        "Meta Ads": f"https://www.facebook.com/adsmanager",
        "Mercado Ads": f"https://www.mercadolivre.com.br/publicidade",
    }

    with col1:
        if st.button("🔍 Google Ads", use_container_width=True):
            st.session_state["campanha_url"] = plataformas["Google Ads"]
            st.info(f"Abra o Google Ads e busque campanhas do SKU **{sku_sel}**")

    with col2:
        if st.button("📱 Meta Ads", use_container_width=True):
            st.session_state["campanha_url"] = plataformas["Meta Ads"]
            st.info(f"Abra o Meta Ads Manager para o SKU **{sku_sel}**")

    with col3:
        if st.button("🛒 Mercado Ads", use_container_width=True):
            st.session_state["campanha_url"] = plataformas["Mercado Ads"]
            st.info(f"Abra o Mercado Ads para o SKU **{sku_sel}**")

    row = df[df["SKU"].astype(str) == sku_sel]
    if not row.empty:
        r = row.iloc[0]
        st.markdown(
            f"**Resumo do SKU {sku_sel}:** "
            f"Lucro R$ {r.get('LUCRO_LIQUIDO', 0):.2f} | "
            f"Margem {r.get('MARGEM_PCT', 0):.1f}% | "
            f"Status: {r.get('STATUS', 'N/D')}"
        )


def render_tabela_com_links(df: pd.DataFrame):
    """Exibe tabela com coluna de links clicáveis."""
    cols_exibir = ["SKU", "LUCRO_LIQUIDO", "MARGEM_PCT", "STATUS"]
    if "URL_ANUNCIO" in df.columns:
        cols_exibir.append("URL_ANUNCIO")
    if "QTD_VENDIDA" in df.columns:
        cols_exibir.append("QTD_VENDIDA")

    st.dataframe(
        df[[c for c in cols_exibir if c in df.columns]],
        use_container_width=True,
        column_config={
            "URL_ANUNCIO": st.column_config.LinkColumn("Anúncio", display_text="Abrir"),
            "LUCRO_LIQUIDO": st.column_config.NumberColumn("Lucro (R$)", format="R$ %.2f"),
            "MARGEM_PCT": st.column_config.NumberColumn("Margem %", format="%.1f%%"),
        },
    )
