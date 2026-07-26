"""Processamento e cruzamento de dados de vendas e custos."""

import pandas as pd

from config.constants import COLUNAS_CUSTOS_NUMERICAS
from core.status import aplicar_status
from core.validation import coercer_numerico


def processar_rentabilidade(
    df_vendas: pd.DataFrame,
    df_custos: pd.DataFrame,
    auditoria=None,
    modo_tolerante: bool = True,
) -> pd.DataFrame:
    """
    Cruza vendas e custos, calcula lucro e aplica status.
    No modo tolerante, SKUs com erro recebem status ERRO DE DADOS.
    """
    df_v = df_vendas.copy()
    df_c = df_custos.copy()

    if auditoria and auditoria.venda_numerica is not None:
        df_v["VALOR_VENDA_BRUTO_NUM"] = auditoria.venda_numerica
        for col in COLUNAS_CUSTOS_NUMERICAS:
            if col in auditoria.custos_numericos:
                df_c[f"{col}_NUM"] = auditoria.custos_numericos[col]
    else:
        df_v["VALOR_VENDA_BRUTO_NUM"] = coercer_numerico(df_v["VALOR_VENDA_BRUTO"])
        for col in COLUNAS_CUSTOS_NUMERICAS:
            df_c[f"{col}_NUM"] = coercer_numerico(df_c[col])

    colunas_custos_num = [f"{col}_NUM" for col in COLUNAS_CUSTOS_NUMERICAS]

    if modo_tolerante:
        skus_com_erro = set()
        if auditoria:
            for erro in auditoria.erros_vendas + auditoria.erros_custos:
                skus_com_erro.add(erro.sku)
        df_final = pd.merge(df_v, df_c, on="SKU", how="outer", indicator=True)
    else:
        df_final = pd.merge(df_v, df_c, on="SKU", how="inner")

    if df_final.empty:
        return df_final

    df_final["CUSTO_TOTAL"] = df_final[colunas_custos_num].sum(axis=1, skipna=True)
    df_final["LUCRO_LIQUIDO"] = (
        df_final["VALOR_VENDA_BRUTO_NUM"] - df_final["CUSTO_TOTAL"]
    )

    if "QTD_VENDIDA" in df_final.columns:
        df_final["QTD_VENDIDA"] = coercer_numerico(df_final["QTD_VENDIDA"]).fillna(0)
    else:
        df_final["QTD_VENDIDA"] = 1

    if "ESTOQUE_ATUAL" in df_final.columns:
        df_final["ESTOQUE_ATUAL"] = coercer_numerico(
            df_final["ESTOQUE_ATUAL"]
        ).fillna(0)
    else:
        df_final["ESTOQUE_ATUAL"] = 0

    if "URL_ANUNCIO_x" in df_final.columns and "URL_ANUNCIO_y" in df_final.columns:
        df_final["URL_ANUNCIO"] = df_final["URL_ANUNCIO_x"].fillna(
            df_final["URL_ANUNCIO_y"]
        )
        df_final.drop(columns=["URL_ANUNCIO_x", "URL_ANUNCIO_y"], inplace=True)
    elif "URL_ANUNCIO_x" in df_final.columns:
        df_final.rename(columns={"URL_ANUNCIO_x": "URL_ANUNCIO"}, inplace=True)
    elif "URL_ANUNCIO_y" in df_final.columns:
        df_final.rename(columns={"URL_ANUNCIO_y": "URL_ANUNCIO"}, inplace=True)

    df_final = aplicar_status(df_final, colunas_custos_num)
    return df_final
