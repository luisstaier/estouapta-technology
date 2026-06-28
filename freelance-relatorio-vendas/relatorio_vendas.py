#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
relatorio_vendas.py - Script para gerar relatório resumido de vendas a partir de CSV.

Uso:
    python relatorio_vendas.py vendas.csv
    python relatorio_vendas.py vendas.csv --saida relatorio.txt

Características:
    - Aceita CSV com separador , ou ;
    - Aceita encoding UTF-8 com fallback Latin-1
    - Normaliza valores monetarios (R$, ponto de milhar, virgula decimal)
    - Aceita datas nos formatos DD/MM/AAAA ou AAAA-MM-DD
    - Ignora linhas invalidas e reporta a quantidade
    - Nao requer dependencias externas (apenas biblioteca padrao)
"""

import csv
import argparse
import sys
from datetime import datetime
from collections import defaultdict


def parse_args():
    """Interpreta argumentos da linha de comando."""
    parser = argparse.ArgumentParser(
        description='Gera relatorio resumido de vendas a partir de CSV.',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        'arquivo',
        help='Caminho para o arquivo CSV (colunas: data, regiao, produto, valor)'
    )
    parser.add_argument(
        '--saida', '-s',
        help='Caminho opcional para salvar o relatorio em arquivo .txt'
    )
    return parser.parse_args()


def ler_vendas(caminho):
    """Le o CSV, normaliza cada linha e retorna lista de vendas validas.

    Args:
        caminho: Caminho do arquivo CSV.

    Returns:
        tuple: (lista_de_vendas_validas, total_de_linhas_ignoradas)
            Cada venda e um dict com: data (date), regiao (str),
            produto (str), valor (float)
    """
    vendas = []
    ignoradas = 0
    linhas_total = 0

    # Tenta ler com UTF-8, se falhar tenta Latin-1
    encodings = ['utf-8', 'latin-1', 'iso-8859-1']
    arquivo = None
    for enc in encodings:
        try:
            arquivo = open(caminho, 'r', encoding=enc)
            break
        except UnicodeDecodeError:
            continue
        except FileNotFoundError:
            print(f'ERRO: Arquivo nao encontrado: {caminho}', file=sys.stderr)
            sys.exit(1)

    if arquivo is None:
        print(f'ERRO: Nao foi possivel ler o arquivo com os encodings testados.',
              file=sys.stderr)
        sys.exit(1)

    with arquivo:
        # Detecta separador: se tiver ; usa ; caso contrario ,
        primeira_linha = arquivo.readline()
        arquivo.seek(0)

        if ';' in primeira_linha:
            separador = ';'
        else:
            separador = ','

        leitor = csv.DictReader(arquivo, delimiter=separador)

        # Normaliza nomes das colunas (remove espacos, lower case)
        if hasattr(leitor, 'fieldnames') and leitor.fieldnames:
            leitor.fieldnames = [h.strip().lower() for h in leitor.fieldnames]

        for linha in leitor:
            linhas_total += 1
            try:
                # Normaliza chaves
                linha = {k.strip().lower(): v.strip() if v else ''
                         for k, v in linha.items()}

                data_str = linha.get('data', '')
                regiao = linha.get('regiao', '')
                produto = linha.get('produto', '')
                valor_str = linha.get('valor', '')

                if not all([data_str, regiao, produto, valor_str]):
                    ignoradas += 1
                    continue

                # Converte data: tenta DD/MM/AAAA, depois AAAA-MM-DD
                data = None
                for fmt in ('%d/%m/%Y', '%Y-%m-%d', '%d/%m/%y', '%Y/%m/%d'):
                    try:
                        data = datetime.strptime(data_str.strip(), fmt).date()
                        break
                    except ValueError:
                        continue

                if data is None:
                    ignoradas += 1
                    continue

                # Normaliza valor monetario
                valor_str = valor_str.replace('R$', '').replace('$', '').strip()

                # Detecta formato: se tem virgula como decimal ou separador
                if ',' in valor_str and '.' in valor_str:
                    # Caso 1.234,56 (ponto de milhar + virgula decimal)
                    if valor_str.rfind(',') > valor_str.rfind('.'):
                        valor_str = valor_str.replace('.', '').replace(',', '.')
                    else:
                        # Caso 1234.56 (ja esta no formato padrao)
                        valor_str = valor_str.replace(',', '')
                elif ',' in valor_str:
                    # Virgula como decimal: 1234,56 -> 1234.56
                    valor_str = valor_str.replace(',', '.')

                valor = float(valor_str)

                if valor < 0:
                    ignoradas += 1
                    continue

                vendas.append({
                    'data': data,
                    'regiao': regiao,
                    'produto': produto,
                    'valor': valor
                })

            except (ValueError, KeyError, AttributeError):
                ignoradas += 1
                continue

    return vendas, ignoradas


def total_por_regiao(vendas):
    """Agrega o valor total de vendas por regiao.

    Args:
        vendas: Lista de dicts de vendas.

    Returns:
        dict: {regiao: valor_total}
    """
    total = defaultdict(float)
    for v in vendas:
        total[v['regiao']] += v['valor']
    return dict(sorted(total.items(), key=lambda x: x[1], reverse=True))


def top_produtos(vendas, n=5):
    """Retorna os N produtos com maior valor total de vendas.

    Args:
        vendas: Lista de dicts de vendas.
        n: Quantidade de produtos no ranking (padrao 5).

    Returns:
        list: Tuplas (produto, valor_total) ordenadas do maior para o menor.
    """
    total = defaultdict(float)
    for v in vendas:
        total[v['produto']] += v['valor']
    ordenado = sorted(total.items(), key=lambda x: x[1], reverse=True)
    return ordenado[:n]


def media_diaria(vendas):
    """Calcula a media de vendas por dia.

    Considera apenas os dias distintos com registro no arquivo.

    Args:
        vendas: Lista de dicts de vendas.

    Returns:
        tuple: (media_diaria, quantidade_de_dias)
    """
    if not vendas:
        return 0.0, 0

    dias = set(v['data'] for v in vendas)
    total_valor = sum(v['valor'] for v in vendas)
    qtd_dias = len(dias)

    if qtd_dias == 0:
        return 0.0, 0

    return total_valor / qtd_dias, qtd_dias


def formatar_moeda(valor):
    """Formata valor float no padrao brasileiro R$ 1.234,56."""
    if valor is None:
        return 'R$ 0,00'
    inteiro = int(valor)
    centavos = int(round((valor - inteiro) * 100))
    if centavos < 0:
        centavos = 0
    # Formata parte inteira com separador de milhar
    inteiro_str = f'{inteiro:,}'.replace(',', '.')
    return f'R$ {inteiro_str},{centavos:02d}'


def gerar_relatorio(vendas, ignoradas):
    """Gera o texto completo do relatorio de vendas."""
    if not vendas:
        return 'Nenhum registro valido encontrado no arquivo CSV.'

    # Datas do periodo
    datas = sorted(set(v['data'] for v in vendas))
    data_inicio = datas[0].strftime('%d/%m/%Y')
    data_fim = datas[-1].strftime('%d/%m/%Y')

    # Agregacoes
    total_regioes = total_por_regiao(vendas)
    ranking = top_produtos(vendas)
    media, qtd_dias = media_diaria(vendas)

    linhas = []
    linhas.append('=== RELATORIO DE VENDAS ===')
    linhas.append(f'Periodo: {data_inicio} a {data_fim}')
    linhas.append(f'Registros validos: {len(vendas):,} | '
                  f'Linhas ignoradas: {ignoradas}')
    linhas.append('')

    # Total por regiao
    linhas.append('-- Total por Regiao --')
    maior_nome = max(len(r) for r in total_regioes.keys()) if total_regioes else 10
    for regiao, valor in total_regioes.items():
        pontos = '.' * (maior_nome - len(regiao) + 2)
        linhas.append(f'{regiao}{pontos}: {formatar_moeda(valor)}')
    linhas.append('')

    # Top 5 produtos
    linhas.append('-- Top 5 Produtos --')
    if ranking:
        maior_prod = max(len(p[0]) for p in ranking)
        for i, (produto, valor) in enumerate(ranking, 1):
            espacos = ' ' * (maior_prod - len(produto) + 2)
            linhas.append(f'{i}. {produto}{espacos}: {formatar_moeda(valor)}')
    else:
        linhas.append('Nenhum produto encontrado.')
    linhas.append('')

    # Media diaria
    linhas.append('-- Media Diaria --')
    linhas.append(f'{formatar_moeda(media)} (em {qtd_dias} dias com vendas)')
    linhas.append('')

    return '\n'.join(linhas)


def main():
    """Funcao principal: orquestra a leitura, processamento e saida."""
    args = parse_args()

    vendas, ignoradas = ler_vendas(args.arquivo)
    relatorio = gerar_relatorio(vendas, ignoradas)

    # Saida no terminal
    print(relatorio)

    # Saida opcional em arquivo
    if args.saida:
        with open(args.saida, 'w', encoding='utf-8') as f:
            f.write(relatorio)
        print(f'Relatorio salvo em: {args.saida}')


if __name__ == '__main__':
    main()
