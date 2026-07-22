import pandas as pd
import random

print("Gerando arquivos de teste avançados...")

# ==========================================
# 1. CENÁRIO CORRETO (50 PRODUTOS COM VARIADOS LUCROS)
# ==========================================
skus = [f"PROD{i:03d}" for i in range(1, 51)]
vendas_correto = []
custos_correto = []

for sku in skus:
    venda_bruta = round(random.uniform(30.0, 250.0), 2)
    # Definimos custos para gerar propositalmente lucros positivos, baixos e negativos
    preco_custo = round(venda_bruta * random.uniform(0.3, 0.8), 2)
    taxa_plat = round(venda_bruta * 0.1, 2)
    frete = round(random.uniform(10.0, 30.0), 2)
    embalagem = round(random.uniform(2.0, 8.0), 2)
    
    # Forçamos alguns prejuízos e lucros baixos propositalmente para testar cores
    if sku in ['PROD003', 'PROD015', 'PROD027', 'PROD042']:
        preco_custo = venda_bruta * 1.1 # Prejuízo
    elif sku in ['PROD005', 'PROD012', 'PROD033']:
        preco_custo = venda_bruta - taxa_plat - frete - embalagem + 5 # Lucro baixo (amarelo)

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
# 2. CENÁRIOS DE ERRO PARA TESTE DE UX
# ==========================================

# Erro na Planilha de Vendas (Falta a coluna VALOR_VENDA_BRUTO)
vendas_erro = {'SKU': ['PROD001', 'PROD002'], 'PRECO_ERRADO': [100, 200]}
pd.DataFrame(vendas_erro).to_csv('vendas_erro.csv', index=False)

# Erro na Planilha de Custos (Falta a coluna PRECO_CUSTO)
custos_erro = {'SKU': ['PROD001', 'PROD002'], 'OUTRA_COLUNA': [10, 20]}
pd.DataFrame(custos_erro).to_csv('custos_erro.csv', index=False)

print("\n[SUCESSO] Todos os arquivos de teste foram gerados na raiz do projeto!")
print("- vendas_teste.csv / custos_teste.csv (Cenário principal com 50 itens)")
print("- vendas_erro.csv (Para testar erro na primeira planilha)")
print("- custos_erro.csv (Para testar erro na segunda planilha)")
