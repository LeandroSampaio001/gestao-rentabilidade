import pandas as pd

# Dados de Vendas
vendas_data = {
    'SKU': ['PROD001', 'PROD002', 'PROD003'],
    'VALOR_VENDA_BRUTO': [150.00, 200.00, 50.00]
}

# Dados de Custos
custos_data = {
    'SKU': ['PROD001', 'PROD002', 'PROD003'],
    'PRECO_CUSTO': [80.00, 120.00, 30.00],
    'TAXA_PLATAFORMA': [10.00, 20.00, 5.00],
    'VALOR_FRETE': [15.00, 20.00, 10.00],
    'CUSTO_EMBALAGEM': [5.00, 5.00, 2.00]
}

# Gerar arquivos CSV
pd.DataFrame(vendas_data).to_csv('vendas_teste.csv', index=False)
pd.DataFrame(custos_data).to_csv('custos_teste.csv', index=False)

print("Arquivos 'vendas_teste.csv' e 'custos_teste.csv' gerados com sucesso!")