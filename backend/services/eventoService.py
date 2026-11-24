from extensions import db
from models.evento import Evento
from repositories.eventoRepository import (
    listar_eventos, obter_evento, ingressos_ativos, salvar_evento, possui_ingressos, ORDENACOES
)
from services.validacao import campos_evento, parametros_pagina
from services.erros import ErroDominio


def serializar_evento(evento):
    ocupados = ingressos_ativos(evento.id)
    return {'id': evento.id, 'nome': evento.nome, 'descricao': evento.descricao,
            'local': evento.local, 'dataHora': evento.data_hora.isoformat(),
            'capacidadeMaxima': evento.capacidade_maxima,
            'ingressosDisponiveis': max(evento.capacidade_maxima - ocupados, 0),
            'ingressosVendidos': ocupados}


def listar(dados):
    page, size, sort, ordem = parametros_pagina(dados, ORDENACOES)
    q = str(dados.get('q', '')).strip()[:120]
    resultado = listar_eventos(page, size, q, sort, ordem)
    return {'items': [serializar_evento(evento) for evento in resultado.items],
            'page': page, 'perPage': size, 'total': resultado.total, 'pages': resultado.pages}


def consultar(id):
    evento = obter_evento(id)
    if evento is None:
        raise ErroDominio('Evento não encontrado.', 404)
    return serializar_evento(evento)


def criar(dados):
    valores = campos_evento(dados)
    try:
        evento = salvar_evento(Evento(**valores))
        db.session.commit()
        return serializar_evento(evento)
    except Exception:
        db.session.rollback()
        raise


def atualizar(id, dados):
    valores = campos_evento(dados)
    try:
        evento = obter_evento(id, bloquear=True)
        if evento is None:
            raise ErroDominio('Evento não encontrado.', 404)
        ocupados = ingressos_ativos(id)
        if valores['capacidade_maxima'] < ocupados:
            raise ErroDominio('A capacidade não pode ser menor que os ingressos ativos.', 409)
        for campo, valor in valores.items():
            setattr(evento, campo, valor)
        db.session.commit()
        return serializar_evento(evento)
    except Exception:
        db.session.rollback()
        raise


def excluir(id):
    try:
        evento = obter_evento(id, bloquear=True)
        if evento is None:
            raise ErroDominio('Evento não encontrado.', 404)
        if possui_ingressos(id):
            raise ErroDominio('Evento com histórico de ingressos não pode ser excluído.', 409)
        db.session.delete(evento)
        db.session.commit()
        return True
    except Exception:
        db.session.rollback()
        raise
