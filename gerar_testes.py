import pandas as pd
import random

print("Gerando arquivos de teste avançados para auditoria de células...")

# ==========================================
# 1. CENÁRIO CORRETO (50 PRODUTOS)
# ==========================================
skus = [f"PROD{i:03d}" for i in range(1, 51)]
vendas_correto = []
custos_correto = []

for sku in skus:
    venda_bruta = round(random.uniform(30.0, 250.0), 2)
    preco_custo = round(venda_bruta * random.uniform(0.3, 0.8), 2)
    taxa_plat = round(venda_bruta * 0.1, 2)
    frete = round(random.uniform(10.0, 30.0), 2)
    embalagem = round(random.uniform(2.0, 8.0), 2)
    
    if sku in ['PROD003', 'PROD015', 'PROD027']:
        preco_custo = venda_bruta * 1.1 # Prejuízo
    elif sku in ['PROD005', 'PROD012']:
        preco_custo = venda_bruta - taxa_plat - frete - embalagem + 2 # Lucro baixo

    vendas_correto.append({'SKU': sku, 'VALOR_VENDA_BRUTO': venda_bruta})
    custos_correto.append({
        'SKU': sku, 
        'PRECO_CUSTO': preco_custo, 
        'TAXA_PLATAFORMA': taxa_plat, 
        'VALOR_FRETE': frete, 
        'CUSTO_EMBALAGEM': embalagem
    })

pd.DataFrame(vendas_correto).to_csv('vendas_teste.csv', index=False)
pd.DataFrame(custos_correto).to_csv('custos_teste.csv', index=False)


# ==========================================
# 2. CENÁRIO DE CÉLULAS CORROMPIDAS / COM ERROS
# ==========================================

# Vendas com erro pontual em uma célula (ex: inserção de letra '150,00a' ou valor vazio)
vendas_celula_erro = {
    'SKU': ['PROD001', 'PROD002', 'PROD003'],
    'VALOR_VENDA_BRUTO': [150.00, '200,00x', 50.00] # Erro na linha do PROD002
}
pd.DataFrame(vendas_celula_erro).to_csv('vendas_celula_erro.csv', index=False)

# Custos com erro pontual em célula (ex: célula vazia ou texto na coluna de custo)
custos_celula_erro = {
    'SKU': ['PROD001', 'PROD002', 'PROD003'],
    'PRECO_CUSTO': [80.00, 120.00, ''], # Vazio no PROD003
    'TAXA_PLATAFORMA': [10.00, 20.00, 5.00],
    'VALOR_FRETE': [15.00, 20.00, 10.00],
    'CUSTO_EMBALAGEM': [5.00, 5.00, 2.00]
}
pd.DataFrame(custos_celula_erro).to_csv('custos_celula_erro.csv', index=False)

print("\n[SUCESSO] Arquivos de teste de células gerados com sucesso!")
print("- vendas_celula_erro.csv (Contém erro no PROD002)")
print("- custos_celula_erro.csv (Contém célula vazia no PROD003)")
