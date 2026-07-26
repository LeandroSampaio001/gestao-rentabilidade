"""Validação estrutural e auditoria linha a linha de planilhas CSV."""

from dataclasses import dataclass, field

import pandas as pd

from config.constants import (
    COLUNAS_CUSTOS_NUMERICAS,
    COLUNAS_CUSTOS_OBRIGATORIAS,
    COLUNAS_VENDAS_NUMERICAS,
    COLUNAS_VENDAS_OBRIGATORIAS,
)


@dataclass
class ErroCelula:
    planilha: str
    sku: str
    linha: int
    coluna: str
    motivo: str = "valor inválido ou vazio"


@dataclass
class ResultadoAuditoria:
    erros_vendas: list[ErroCelula] = field(default_factory=list)
    erros_custos: list[ErroCelula] = field(default_factory=list)
    skus_apenas_vendas: set = field(default_factory=set)
    skus_apenas_custos: set = field(default_factory=set)
    venda_numerica: pd.Series | None = None
    custos_numericos: dict[str, pd.Series] = field(default_factory=dict)

    @property
    def tem_erros_celulas(self) -> bool:
        return bool(self.erros_vendas or self.erros_custos)

    @property
    def tem_divergencia_lote(self) -> bool:
        return bool(self.skus_apenas_vendas or self.skus_apenas_custos)

    @property
    def tem_inconsistencias(self) -> bool:
        return self.tem_erros_celulas or self.tem_divergencia_lote


def validar_estrutura(
    df: pd.DataFrame, colunas_esperadas: list[str], nome_planilha: str
) -> tuple[bool, str]:
    """Verifica se as colunas obrigatórias estão presentes no CSV."""
    colunas_faltantes = [col for col in colunas_esperadas if col not in df.columns]
    if colunas_faltantes:
        return (
            False,
            f"Na **{nome_planilha}**, está faltando a(s) coluna(s): "
            f"{', '.join(colunas_faltantes)}.",
        )
    return True, "Validado"


def coercer_numerico(serie: pd.Series) -> pd.Series:
    """Converte strings com formato brasileiro para numérico."""
    return pd.to_numeric(
        serie.astype(str).str.replace(";", "").str.replace(",", "."),
        errors="coerce",
    )


def _sku_da_linha(df: pd.DataFrame, idx: int) -> str:
    if "SKU" in df.columns and pd.notna(df.loc[idx, "SKU"]):
        return str(df.loc[idx, "SKU"])
    return f"Linha {idx + 2}"


def auditar_celulas(
    df_vendas: pd.DataFrame, df_custos: pd.DataFrame
) -> ResultadoAuditoria:
    """Auditoria cirúrgica de células corrompidas, vazias ou com tipos incorretos."""
    resultado = ResultadoAuditoria()

    venda_numerica = coercer_numerico(df_vendas["VALOR_VENDA_BRUTO"])
    resultado.venda_numerica = venda_numerica

    for idx in df_vendas[venda_numerica.isna()].index.tolist():
        resultado.erros_vendas.append(
            ErroCelula(
                planilha="Planilha de Vendas",
                sku=_sku_da_linha(df_vendas, idx),
                linha=idx + 2,
                coluna="VALOR_VENDA_BRUTO",
            )
        )

    for col in COLUNAS_CUSTOS_NUMERICAS:
        temp_num = coercer_numerico(df_custos[col])
        resultado.custos_numericos[col] = temp_num
        for idx in df_custos[temp_num.isna()].index.tolist():
            resultado.erros_custos.append(
                ErroCelula(
                    planilha="Planilha de Custos",
                    sku=_sku_da_linha(df_custos, idx),
                    linha=idx + 2,
                    coluna=col,
                )
            )

    return resultado


def auditar_divergencia_skus(
    df_vendas: pd.DataFrame, df_custos: pd.DataFrame, resultado: ResultadoAuditoria
) -> ResultadoAuditoria:
    """Detecta divergência de lotes/períodos entre planilhas."""
    skus_vendas = set(df_vendas["SKU"].astype(str))
    skus_custos = set(df_custos["SKU"].astype(str))
    resultado.skus_apenas_vendas = skus_vendas - skus_custos
    resultado.skus_apenas_custos = skus_custos - skus_vendas
    return resultado


def validar_planilhas_completas(
    df_vendas: pd.DataFrame, df_custos: pd.DataFrame
) -> tuple[bool, str, ResultadoAuditoria | None]:
    """Pipeline completo de validação estrutural + auditoria."""
    ok_v, msg_v = validar_estrutura(
        df_vendas, COLUNAS_VENDAS_OBRIGATORIAS, "Planilha de Vendas"
    )
    if not ok_v:
        return False, msg_v, None

    ok_c, msg_c = validar_estrutura(
        df_custos, COLUNAS_CUSTOS_OBRIGATORIAS, "Planilha de Custos"
    )
    if not ok_c:
        return False, msg_c, None

    resultado = auditar_celulas(df_vendas, df_custos)
    auditar_divergencia_skus(df_vendas, df_custos, resultado)
    return True, "Validado", resultado
