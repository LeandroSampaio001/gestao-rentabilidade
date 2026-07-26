"""Motor de classificação dinâmica de status por SKU."""

import pandas as pd

from config.constants import (
    LIMIAR_LUCRATIVO,
    LIMIAR_POUCO_LUCRATIVO,
    STATUS_ERRO,
    STATUS_LUCRATIVO,
    STATUS_POUCO_LUCRATIVO,
    STATUS_PREJUIZO,
)


def definir_status(lucro: float, tem_erro: bool = False) -> str:
    """Classifica um SKU com base no lucro líquido."""
    if tem_erro or pd.isna(lucro):
        return STATUS_ERRO
    if lucro > LIMIAR_LUCRATIVO:
        return STATUS_LUCRATIVO
    if lucro >= LIMIAR_POUCO_LUCRATIVO:
        return STATUS_POUCO_LUCRATIVO
    return STATUS_PREJUIZO


def aplicar_status(df: pd.DataFrame, colunas_custos_num: list[str]) -> pd.DataFrame:
    """Aplica classificação de status a todo o DataFrame processado."""
    df = df.copy()

    def _status_row(row):
        tem_erro = pd.isna(row.get("VALOR_VENDA_BRUTO_NUM"))
        if not tem_erro:
            for col in colunas_custos_num:
                if pd.isna(row.get(col)):
                    tem_erro = True
                    break
        return definir_status(row.get("LUCRO_LIQUIDO"), tem_erro)

    df["STATUS"] = df.apply(_status_row, axis=1)
    df["MARGEM_PCT"] = df.apply(
        lambda r: (
            (r["LUCRO_LIQUIDO"] / r["VALOR_VENDA_BRUTO_NUM"] * 100)
            if pd.notna(r["LUCRO_LIQUIDO"])
            and pd.notna(r["VALOR_VENDA_BRUTO_NUM"])
            and r["VALOR_VENDA_BRUTO_NUM"] != 0
            else None
        ),
        axis=1,
    )
    return df


def resumo_por_status(df: pd.DataFrame) -> dict[str, int]:
    """Retorna contagem de SKUs por status."""
    if df.empty or "STATUS" not in df.columns:
        return {}
    return df["STATUS"].value_counts().to_dict()
