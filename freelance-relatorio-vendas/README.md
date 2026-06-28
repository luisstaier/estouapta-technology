# 📊 Relatório de Vendas — Script Python

Script Python puro (sem dependências externas) para gerar relatórios resumidos de vendas a partir de arquivos CSV.

## 🚀 Como usar

```bash
python relatorio_vendas.py vendas.csv
```

Para salvar o relatório em arquivo:

```bash
python relatorio_vendas.py vendas.csv --saida relatorio.txt
```

## 📄 Formato esperado do CSV

O arquivo deve conter as colunas: **data, regiao, produto, valor**

Exemplo:

```
data,regiao,produto,valor
01/06/2026,Sudeste,Notebook ABC,4500.00
02/06/2026,Sul,Smartphone XYZ,2200.50
```

### Tolerância a variações

O script aceita automaticamente:

- **Separadores:** `,` ou `;`
- **Encoding:** UTF-8 com fallback para Latin-1 (ISO-8859-1)
- **Valor monetário:** com ou sem `R$`, ponto de milhar (`1.234,56`) ou ponto decimal (`1234.56`)
- **Data:** `DD/MM/AAAA` ou `AAAA-MM-DD`
- **Linhas inválidas:** são ignoradas e contabilizadas no relatório

## 📋 Exemplo de saída

```
=== RELATÓRIO DE VENDAS ===
Período: 01/06/2026 a 28/06/2026
Registros válidos: 1.240 | Linhas ignoradas: 3

-- Total por Região --
Sudeste......: R$ 45.300,00
Sul..........: R$ 22.150,50
Nordeste.....: R$ 18.720,30
Centro-Oeste.: R$ 12.400,00
Norte........: R$ 8.950,00

-- Top 5 Produtos --
1. Notebook ABC     : R$ 52.300,00
2. Smartphone XYZ   : R$ 38.150,50
3. Tablet Pro       : R$ 12.400,00
4. Fone Bluetooth   : R$ 4.520,00
5. Mouse Wireless   : R$ 3.200,00

-- Média Diária --
R$ 3.420,75 (em 28 dias úteis com vendas)
```

## 🧩 Estrutura do código

| Função | Responsabilidade |
|---|---|
| `parse_args()` | Interpreta argumentos da linha de comando |
| `ler_vendas(caminho)` | Lê e normaliza o CSV |
| `total_por_regiao(vendas)` | Agrega valor total por região |
| `top_produtos(vendas, n=5)` | Ranking dos produtos mais vendidos |
| `media_diaria(vendas)` | Média de vendas por dia |
| `gerar_relatorio(...)` | Formata o relatório em texto |
| `main()` | Orquestra a execução completa |

## ✅ Requisitos

- Python 3.6 ou superior
- Nenhuma biblioteca externa (usa apenas `csv`, `argparse`, `datetime`, `collections` da biblioteca padrão)
