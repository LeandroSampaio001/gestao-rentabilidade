"""Camada de alertas e notificações (base para mobile/PWA)."""

from dataclasses import dataclass, field
from datetime import datetime

import pandas as pd
import streamlit as st

from config.constants import STATUS_POUCO_LUCRATIVO, STATUS_PREJUIZO


@dataclass
class Alerta:
    sku: str
    tipo: str
    mensagem: str
    severidade: str  # "critico", "aviso", "info"
    timestamp: str = field(default_factory=lambda: datetime.now().strftime("%d/%m/%Y %H:%M"))


def gerar_alertas_automaticos(df: pd.DataFrame) -> list[Alerta]:
    """Gera alertas automáticos com base no status e margem dos SKUs."""
    alertas = []
    if df is None or df.empty:
        return alertas

    for _, row in df.iterrows():
        sku = str(row["SKU"])
        status = row.get("STATUS", "")
        lucro = row.get("LUCRO_LIQUIDO", 0)
        margem = row.get("MARGEM_PCT", 0)

        if status == STATUS_PREJUIZO:
            alertas.append(
                Alerta(
                    sku=sku,
                    tipo="prejuizo",
                    mensagem=f"SKU {sku} em PREJUÍZO (R$ {lucro:.2f})",
                    severidade="critico",
                )
            )
        elif status == STATUS_POUCO_LUCRATIVO:
            alertas.append(
                Alerta(
                    sku=sku,
                    tipo="margem_baixa",
                    mensagem=f"SKU {sku} com margem baixa (R$ {lucro:.2f})",
                    severidade="aviso",
                )
            )
        elif pd.notna(margem) and margem < 5:
            alertas.append(
                Alerta(
                    sku=sku,
                    tipo="margem_critica",
                    mensagem=f"SKU {sku} com margem crítica ({margem:.1f}%)",
                    severidade="aviso",
                )
            )

    return alertas


def registrar_alerta_mudanca_margem(
    sku: str, lucro_anterior: float, lucro_novo: float
) -> Alerta | None:
    """Registra alerta quando SKU entra em zona de prejuízo por alteração de margem."""
    if lucro_anterior >= 0 and lucro_novo < 0:
        return Alerta(
            sku=sku,
            tipo="mudanca_margem",
            mensagem=(
                f"SKU {sku} entrou em PREJUÍZO! "
                f"Lucro caiu de R$ {lucro_anterior:.2f} para R$ {lucro_novo:.2f}"
            ),
            severidade="critico",
        )
    if lucro_anterior > 20 and lucro_novo <= 20:
        return Alerta(
            sku=sku,
            tipo="queda_margem",
            mensagem=f"SKU {sku} saiu da zona Lucrativa (R$ {lucro_novo:.2f})",
            severidade="aviso",
        )
    return None


def render_painel_alertas(alertas: list[Alerta]):
    """Renderiza painel visual de alertas."""
    if not alertas:
        st.success("✅ Nenhum alerta ativo. Todos os SKUs estão dentro dos parâmetros.")
        return

    criticos = [a for a in alertas if a.severidade == "critico"]
    avisos = [a for a in alertas if a.severidade == "aviso"]

    if criticos:
        st.error(f"🚨 **{len(criticos)} alerta(s) crítico(s)**")
        for a in criticos:
            st.markdown(f"- 🔴 **{a.sku}** — {a.mensagem} _({a.timestamp})_")

    if avisos:
        st.warning(f"⚡ **{len(avisos)} aviso(s)**")
        for a in avisos:
            st.markdown(f"- 🟡 **{a.sku}** — {a.mensagem} _({a.timestamp})_")


def render_notificacoes_mobile(alertas: list[Alerta]):
    """Base de notificações leves voltada para acompanhamento mobile/PWA."""
    st.markdown("### 📱 Central de Notificações (Mobile/PWA)")
    st.markdown(
        "Estrutura base para acompanhamento rápido no celular. "
        "Alertas são gerados automaticamente quando SKUs entram em zonas de risco."
    )

    if not alertas:
        st.info("Nenhuma notificação pendente.")
        return

    for i, alerta in enumerate(alertas):
        cor = {"critico": "🔴", "aviso": "🟡", "info": "🔵"}.get(
            alerta.severidade, "⚪"
        )
        with st.container(border=True):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"{cor} **{alerta.sku}** — {alerta.mensagem}")
                st.caption(f"{alerta.timestamp} | Tipo: {alerta.tipo}")
            with col2:
                if st.button("✓ Lido", key=f"lido_{i}"):
                    st.session_state["notificacoes_lidas"].add(alerta.sku)

    st.markdown("---")
    st.markdown(
        "**Integração PWA:** Esta camada pode ser conectada a "
        "Web Push Notifications via Service Worker para alertas em tempo real no celular."
    )
