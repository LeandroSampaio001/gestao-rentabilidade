# 🚀 Sistema de Gestão de Rentabilidade v2.0

Aplicação web em **Python (Streamlit)** para lojistas de e-commerce e marketplaces analisarem rentabilidade, simularem cenários estratégicos e exportarem relatórios profissionais.

## 🛠️ Tecnologias

- **Python** — Lógica central e processamento
- **Pandas** — Manipulação de datasets e métricas
- **Streamlit** — Interface web multipágina
- **FPDF2** — Geração de relatórios PDF

## 📈 Funcionalidades

### Núcleo de Processamento e Auditoria
- Importação dupla e independente de CSV (Vendas e Custos)
- Validação estrutural automática de colunas obrigatórias
- Auditoria linha a linha de células corrompidas/vazias (SKU + coluna exata)
- Detecção de divergência de lotes/períodos entre planilhas
- Modo tolerante a falhas com opção interativa do usuário

### Relatórios e Exportação
- Motor de status dinâmico: Lucrativo, Pouco Lucrativo, Prejuízo, ERRO DE DADOS
- PDF profissional com cabeçalho corporativo, paginação, zebrado e cores por status

### Módulos Estratégicos
- **Buy Box Simulator** — Impacto de variações de preço da concorrência
- **Ponto de Equilíbrio** — Custos fixos, meta de faturamento e break-even
- **Campanhas e Descontos** — Teste de promoções com bloqueio de campanhas inviáveis
- **Giro de Estoque** — Matriz de desempenho (estrelas vs peso-morto)

### Operacional
- Coluna `URL_ANUNCIO` para links diretos (Mercado Livre, Shopee, etc.)
- Atalhos de campanhas de tráfego pago por SKU
- Alertas visuais e base de notificações para mobile/PWA

## 🚀 Como executar

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 📄 Esquema das Planilhas

**Vendas (obrigatório):** `SKU`, `VALOR_VENDA_BRUTO`

**Vendas (opcional):** `URL_ANUNCIO`, `QTD_VENDIDA`

**Custos (obrigatório):** `SKU`, `PRECO_CUSTO`, `TAXA_PLATAFORMA`, `VALOR_FRETE`, `CUSTO_EMBALAGEM`

**Custos (opcional):** `URL_ANUNCIO`, `ESTOQUE_ATUAL`

## 📁 Estrutura do Projeto

```
projeto_web/
├── app.py                    # Página inicial (dashboard)
├── pages/                    # Módulos Streamlit multipágina
├── config/constants.py       # Esquemas e limiares
├── core/                     # Validação, processamento, status
├── business/                 # Buy Box, Break-Even, Campanhas, Giro
├── reports/pdf_generator.py  # Exportação PDF
└── ui/                       # Componentes, alertas, sessão
```

## 🧪 Dados de Teste

```bash
python gerar_testes.py
```

Gera `vendas_teste.csv` e `custos_teste.csv` com 50 SKUs, URLs e dados de giro.

## 🌐 Deploy

Hospedado em: https://gestao-rentabilidade-lpntcrvsqjiv8qvsydgugy.streamlit.app/

---
*Desenvolvido por Leandro Sampaio*
