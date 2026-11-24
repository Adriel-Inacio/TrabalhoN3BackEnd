from datetime import datetime
from zoneinfo import ZoneInfo
from services.erros import ErroDominio


def data_local_agora():
    return datetime.now(ZoneInfo('America/Sao_Paulo')).replace(tzinfo=None)


def campos_evento(dados):
    nome = dados.get('nome')
    descricao = dados.get('descricao')
    local = dados.get('local')
    data_hora = dados.get('dataHora')
    capacidade = dados.get('capacidadeMaxima')
    for rotulo, valor, limite in (('nome', nome, 120), ('descricao', descricao, 1000), ('local', local, 200)):
        if not isinstance(valor, str) or not valor.strip() or len(valor.strip()) > limite:
            raise ErroDominio(f'O campo {rotulo} é obrigatório e deve ter até {limite} caracteres.')
    if isinstance(data_hora, str):
        try:
            data_hora = datetime.fromisoformat(data_hora)
        except ValueError:
            raise ErroDominio('Informe uma data e hora ISO-8601 válida.')
    if not isinstance(data_hora, datetime) or data_hora.tzinfo is not None:
        raise ErroDominio('Informe dataHora no horário local, sem fuso (ISO-8601).')
    if type(capacidade) is not int or capacidade < 1 or capacidade > 2147483647:
        raise ErroDominio('A capacidade máxima deve ser um inteiro positivo.')
    return {'nome': nome.strip(), 'descricao': descricao.strip(), 'local': local.strip(),
            'data_hora': data_hora, 'capacidade_maxima': capacidade}


def validar_id(valor, nome):
    if type(valor) is not int or valor <= 0:
        raise ErroDominio(f'O campo {nome} deve ser um ID inteiro positivo.')
    return valor


def parametros_pagina(dados, ordenacoes):
    page = dados.get('page', 1)
    per_page = dados.get('perPage', 10)
    sort = dados.get('sort', 'id')
    ordem = dados.get('ordem', 'asc')
    if type(page) is not int or page < 1 or type(per_page) is not int or not 1 <= per_page <= 100:
        raise ErroDominio('Paginação inválida: page >= 1 e perPage entre 1 e 100.')
    if sort not in ordenacoes or ordem not in ('asc', 'desc'):
        raise ErroDominio('Ordenação inválida.')
    return page, per_page, sort, ordem
