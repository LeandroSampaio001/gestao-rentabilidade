import random

import pandas as pd

print("Gerando arquivos de teste avançados...")

# ==========================================
# 1. CENÁRIO CORRETO (50 PRODUTOS)
# ==========================================
skus = [f"PROD{i:03d}" for i in range(1, 51)]
vendas_correto = []
custos_correto = []

urls_base = {
    "mercadolivre": "https://produto.mercadolivre.com.br/MLB-",
    "shopee": "https://shopee.com.br/product/",
}

for sku in skus:
    venda_bruta = round(random.uniform(30.0, 250.0), 2)
    preco_custo = round(venda_bruta * random.uniform(0.3, 0.8), 2)
    taxa_plat = round(venda_bruta * 0.1, 2)
    frete = round(random.uniform(10.0, 30.0), 2)
    embalagem = round(random.uniform(2.0, 8.0), 2)
    qtd_vendida = random.randint(1, 60)
    estoque = random.randint(0, 100)

    if sku in ["PROD003", "PROD015", "PROD027"]:
        preco_custo = venda_bruta * 1.1
    elif sku in ["PROD005", "PROD012"]:
        preco_custo = venda_bruta - taxa_plat - frete - embalagem + 2

    plataforma = random.choice(["mercadolivre", "shopee"])
    url = f"{urls_base[plataforma]}{sku}"

    vendas_correto.append(
        {
            "SKU": sku,
            "VALOR_VENDA_BRUTO": venda_bruta,
            "URL_ANUNCIO": url,
            "QTD_VENDIDA": qtd_vendida,
        }
    )
    custos_correto.append(
        {
            "SKU": sku,
            "PRECO_CUSTO": preco_custo,
            "TAXA_PLATAFORMA": taxa_plat,
            "VALOR_FRETE": frete,
            "CUSTO_EMBALAGEM": embalagem,
            "ESTOQUE_ATUAL": estoque,
        }
    )

pd.DataFrame(vendas_correto).to_csv("vendas_teste.csv", index=False)
pd.DataFrame(custos_correto).to_csv("custos_teste.csv", index=False)

# ==========================================
# 2. CENÁRIO DE CÉLULAS CORROMPIDAS
# ==========================================
vendas_celula_erro = {
    "SKU": ["PROD001", "PROD002", "PROD003"],
    "VALOR_VENDA_BRUTO": [150.00, "200,00x", 50.00],
}
pd.DataFrame(vendas_celula_erro).to_csv("vendas_celula_erro.csv", index=False)

custos_celula_erro = {
    "SKU": ["PROD001", "PROD002", "PROD003"],
    "PRECO_CUSTO": [80.00, 120.00, ""],
    "TAXA_PLATAFORMA": [10.00, 20.00, 5.00],
    "VALOR_FRETE": [15.00, 20.00, 10.00],
    "CUSTO_EMBALAGEM": [5.00, 5.00, 2.00],
}
pd.DataFrame(custos_celula_erro).to_csv("custos_celula_erro.csv", index=False)

print("\n[SUCESSO] Arquivos de teste gerados!")
print("- vendas_teste.csv / custos_teste.csv (50 SKUs com URLs e giro)")
print("- vendas_celula_erro.csv (erro no PROD002)")
print("- custos_celula_erro.csv (célula vazia no PROD003)")
