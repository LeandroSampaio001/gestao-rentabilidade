"""Simulador de Margem por Concorrência (Buy Box Simulator) com Configuração Intuitiva."""

import pandas as pd
import streamlit as st

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
    """Interface Streamlit do simulador Buy Box com configuração guiada de concorrentes."""
    st.subheader("🎯 Simulador de Concorrência e Buy Box")
    st.markdown(
        "Acompanhe os preços e anúncios dos concorrentes para proteger sua margem de lucro."
    )

    if df.empty:
        st.warning("Carregue e processe os dados na página de Início primeiro.")
        return

    # Garante colunas de apoio na sessão para concorrentes
    if "df_concorrentes_info" not in st.session_state:
        st.session_state["df_concorrentes_info"] = pd.DataFrame({
            "SKU": df["SKU"].astype(str),
            "PRECO_CONCORRENTE": df["VALOR_VENDA_BRUTO_NUM"] * 0.95,
            "LINK_CONCORRENTE": ""
        })

    # Bloco Intuitivo: Configurar Loja Concorrente
    with st.expander("🌐 Configurar Loja Concorrente (Global ou Individual)", expanded=True):
        st.markdown(
            "Escolha abaixo como deseja mapear os concorrentes. "
            "*(Nota: O link serve de atalho para abrir o anúncio; o preço numérico é usado para o cálculo matemático da margem).* "
            "Não se esqueça de clicar em **Salvar Alterações** após preencher."
        )
        
        tab_global, tab_individual = st.tabs(["🌍 Opção 1: Concorrente Global (Loja Inteira)", "🎯 Opção 2: Concorrente Individual (Por Produto)"])
        
        with tab_global:
            st.markdown("**Como usar:** Insira o link da página principal da loja do concorrente. O sistema criará o atalho estruturado para os SKUs.")
            url_global = st.text_input(
                "URL da Loja do Concorrente (Ex: https://perfil.mercadolivre.com.br/SUA-LOJA)",
                value=st.session_state.get("url_loja_global_concorrente", ""),
                key="input_url_global_master"
            )
            col_g1, col_g2 = st.columns([2, 5])
            with col_g1:
                if st.button("🚀 Aplicar Loja Global"):
                    st.session_state["url_loja_global_concorrente"] = url_global
                    if url_global:
                        df_temp = st.session_state["df_concorrentes_info"]
                        for idx, row in df_temp.iterrows():
                            sku_val = row["SKU"]
                            if not row["LINK_CONCORRENTE"] or row["LINK_CONCORRENTE"].strip() == "":
                                df_temp.at[idx, "LINK_CONCORRENTE"] = f"{url_global.rstrip('/')}/p/{sku_val}"
                        st.session_state["df_concorrentes_info"] = df_temp
                        st.success("✅ Links gerados com base na loja global!")
                    else:
                        st.warning("Informe uma URL válida.")

        with tab_individual:
            st.markdown("**Como usar:** Selecione o produto desejado na tabela abaixo, digite o preço praticado pelo concorrente e cole o link exato daquele anúncio.")
            
            df_base_edit = df[["SKU"]].copy()
            if "NOME_PRODUTO" in df.columns:
                df_base_edit["PRODUTO"] = df["NOME_PRODUTO"]
            df_base_edit["PREÇO_ATUAL"] = df["VALOR_VENDA_BRUTO_NUM"]
            
            df_editavel = pd.merge(df_base_edit, st.session_state["df_concorrentes_info"], on="SKU", how="left")
            
            df_resultado_edit = st.data_editor(
                df_editavel,
                num_rows="fixed",
                use_container_width=True,
                key="tabela_concorrentes_config",
                column_config={
                    "LINK_CONCORRENTE": st.column_config.LinkColumn("Link Anúncio Concorrente", display_text="Abrir Anúncio")
                }
            )

            if st.button("💾 Salvar Alterações de Concorrentes"):
                st.session_state["df_concorrentes_info"] = df_resultado_edit[["SKU", "PRECO_CONCORRENTE", "LINK_CONCORRENTE"]]
                st.success("✅ Alterações salvas com sucesso!")

    # Sincroniza dados de trabalho
    df_trab = df.copy()
    df_trab["SKU"] = df_trab["SKU"].astype(str)

    st.markdown("---")
    tab1, tab3 = st.tabs(["🔍 Simulação Detalhada por SKU", "📊 Simulação Global em Lote (%)"])

    with tab1:
        skus = df_trab["SKU"].tolist()
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            sku_sel = st.selectbox("Selecione o SKU para analisar", skus, key="sku_simulador_individual")
        with col_s2:
            row = df_trab[df_trab["SKU"] == sku_sel].iloc[0]
            preco_atual = float(row["VALOR_VENDA_BRUTO_NUM"])
            
            df_conc_sessao = st.session_state["df_concorrentes_info"]
            val_salvo = df_conc_sessao.loc[df_conc_sessao["SKU"] == sku_sel, "PRECO_CONCORRENTE"]
            default_val = float(val_salvo.values[0]) if not val_salvo.empty else round(preco_atual * 0.95, 2)

            preco_conc = st.number_input(
                "Preço do concorrente para este SKU (R$)",
                min_value=0.0,
                value=default_val,
                step=1.0,
                key=f"preco_conc_{sku_sel}"
            )

        # Exibe atalho para o link do anúncio do concorrente se houver
        link_sku_row = df_conc_sessao.loc[df_conc_sessao["SKU"] == sku_sel, "LINK_CONCORRENTE"]
        link_sku = str(link_sku_row.values[0]) if not link_sku_row.empty else ""
        if link_sku and link_sku.startswith("http"):
            st.markdown(f"🔗 **Atalho:** [Abrir Anúncio do Concorrente deste SKU]({link_sku})")

        sim = simular_preco_concorrente(df_trab, sku_sel, preco_conc)
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
                    f"⚠️ **ALERTA DE RISCO:** Com o preço de R$ {preco_conc:.2f}, "
                    f"o SKU **{sku_sel}** entraria em **{STATUS_PREJUIZO}**!"
                )
            elif sim["status_simulado"] == "Pouco Lucrativo":
                st.warning(
                    f"⚡ Atenção: margem reduzida. Status simulado: **{sim['status_simulado']}**"
                )
            else:
                st.success(f"✅ Status simulado: **{sim['status_simulado']}**")

    with tab3:
        variacao = st.slider(
            "Variação global de preço de mercado (%)",
            min_value=-50.0,
            max_value=50.0,
            value=-10.0,
            step=1.0,
            help="Negativo = queda de preço da concorrência. Positivo = aumento.",
        )
        df_sim = simular_lote_concorrencia(df_trab, variacao)
        em_prejuizo = df_sim[df_sim["STATUS_SIMULADO"] == STATUS_PREJUIZO]

        st.metric(
            "SKUs em risco de prejuízo com esta variação em lote",
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