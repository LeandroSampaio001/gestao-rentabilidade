"""Componentes reutilizáveis de exibição de auditoria."""

import streamlit as st

from core.validation import ErroCelula, ResultadoAuditoria


def render_erros_celulas(auditoria: ResultadoAuditoria):
    """Exibe erros de células com SKU, linha e coluna exata."""
    if not auditoria.tem_erros_celulas:
        return

    st.warning(
        "⚠️ **Atenção: Encontramos células com dados inválidos ou vazios nas suas planilhas!**"
    )
    for erro in auditoria.erros_vendas + auditoria.erros_custos:
        st.markdown(
            f"- **{erro.planilha}** (Linha {erro.linha}): "
            f"O produto **{erro.sku}** apresenta dado inválido/vazio "
            f"na coluna `{erro.coluna}`."
        )


def render_divergencia_skus(auditoria: ResultadoAuditoria):
    """Exibe alertas de divergência de lotes/períodos."""
    if not auditoria.tem_divergencia_lote:
        return

    st.warning(
        "📅 **Atenção: As planilhas parecem ser de períodos ou lotes diferentes!**"
    )
    if auditoria.skus_apenas_vendas:
        exemplos = list(auditoria.skus_apenas_vendas)[:3]
        st.markdown(
            f"- Há **{len(auditoria.skus_apenas_vendas)} produto(s)** presentes nas "
            f"**Vendas**, mas sem cadastro de custos (Ex: `{exemplos}...`)."
        )
    if auditoria.skus_apenas_custos:
        exemplos = list(auditoria.skus_apenas_custos)[:3]
        st.markdown(
            f"- Há **{len(auditoria.skus_apenas_custos)} produto(s)** com custos "
            f"cadastrados, mas sem vendas neste arquivo (Ex: `{exemplos}...`)."
        )


def render_opcao_prosseguir(auditoria: ResultadoAuditoria) -> bool:
    """Retorna True se o usuário optou por prosseguir no modo tolerante."""
    if not auditoria.tem_inconsistencias:
        return True

    st.markdown("---")
    st.info("💡 **Como você deseja proceder?**")
    opcao = st.radio(
        "Escolha uma opção:",
        (
            "Revisar e corrigir os arquivos",
            "Prosseguir mesmo assim (processar apenas os itens válidos/compatíveis)",
        ),
        key="opcao_prosseguir",
    )
    return opcao == "Prosseguir mesmo assim (processar apenas os itens válidos/compatíveis)"
