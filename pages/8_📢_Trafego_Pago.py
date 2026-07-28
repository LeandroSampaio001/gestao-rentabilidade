"""Página de Tráfego Pago."""

import streamlit as st
import pandas as pd
from ui.session import dados_disponiveis, get_df_processado, init_session_state

init_session_state()

st.title("📢 Tráfego Pago")
st.markdown("---")

if not dados_disponiveis():
    st.warning("⚠️ Nenhum dado processado. Vá à página **Importação e Auditoria** primeiro.")
    st.stop()

df = get_df_processado()

# Bloco de gerenciamento de tráfego pago
st.markdown("Gerencie o impulsionamento dos seus anúncios e configure os links das suas contas de anúncio.")

if "url_google_ads" not in st.session_state:
    st.session_state["url_google_ads"] = "https://ads.google.com/aw/campaigns"
if "url_meta_ads" not in st.session_state:
    st.session_state["url_meta_ads"] = "https://www.facebook.com/adsmanager"
if "url_mercado_ads" not in st.session_state:
    st.session_state["url_mercado_ads"] = "https://www.mercadolivre.com.br/publicidade"

with st.expander("⚙️ Configurar Links das Suas Contas de Anúncio"):
    st.markdown("Insira abaixo o link direto para o gerenciador de anúncios da sua empresa em cada plataforma:")
    
    st.session_state["url_google_ads"] = st.text_input(
        "Link do seu Google Ads", 
        value=st.session_state["url_google_ads"]
    )
    st.session_state["url_meta_ads"] = st.text_input(
        "Link do seu Meta Ads (Gerenciador de Anúncios)", 
        value=st.session_state["url_meta_ads"]
    )
    st.session_state["url_mercado_ads"] = st.text_input(
        "Link do seu Mercado Ads (Publicidade)", 
        value=st.session_state["url_mercado_ads"]
    )

st.markdown("---")

if df.empty:
    st.info("Nenhum SKU disponível para análise.")
else:
    skus = df["SKU"].astype(str).tolist()
    sku_sel = st.selectbox("Selecione o SKU para gerenciar campanha", skus, key="camp_sku")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**Google Ads**")
        st.link_button("🔍 Acessar Google Ads", st.session_state["url_google_ads"], use_container_width=True)

    with col2:
        st.markdown("**Meta Ads**")
        st.link_button("📱 Acessar Meta Ads", st.session_state["url_meta_ads"], use_container_width=True)

    with col3:
        st.markdown("**Mercado Ads**")
        st.link_button("🛒 Acessar Mercado Ads", st.session_state["url_mercado_ads"], use_container_width=True)

    st.markdown("")
    row = df[df["SKU"].astype(str) == sku_sel]
    if not row.empty:
        r = row.iloc[0]
        st.markdown(
            f"**Resumo do SKU {sku_sel}:** "
            f"Lucro R$ {r.get('LUCRO_LIQUIDO', 0):.2f} | "
            f"Margem {r.get('MARGEM_PCT', 0):.1f}% | "
            f"Status: {r.get('STATUS', 'N/D')}"
        )