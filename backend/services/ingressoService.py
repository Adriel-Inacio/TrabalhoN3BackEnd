from datetime import datetime, timezone
from extensions import db
from models.cliente import Cliente
from models.ingresso import Ingresso
from models.outbox import Outbox
from repositories.eventoRepository import obter_evento
from repositories.ingressoRepository import (
    listar_ingressos, buscar_ingresso, bloquear_ingresso, contar_ativos_evento,
    contar_ingressos_cliente, salvar_ingresso, ORDENACOES
)
from services.acesso import usuario_atual
from services.erros import ErroDominio
from services.validacao import data_local_agora, validar_id, parametros_pagina

LIMITE_INGRESSOS = 4


def serializar_ingresso(ingresso):
    return {'id': ingresso.id, 'eventoId': ingresso.evento_id,
            'clienteId': ingresso.cliente_id,
            'eventoNome': ingresso.evento.nome,
            'status': ingresso.status, 'adquiridoEm': ingresso.adquirido_em.isoformat()}


def cliente_permitido(cliente_id):
    usuario = usuario_atual()
    if usuario.perfil == 'CLIENTE':
        if cliente_id is not None and cliente_id != usuario.id_cliente:
            raise ErroDominio('Você não pode acessar ingressos de outro cliente.', 403)
        return usuario.id_cliente
    return cliente_id


def listar(dados):
    page, size, sort, ordem = parametros_pagina(dados, ORDENACOES)
    usuario = usuario_atual()
    cliente_id = cliente_permitido(dados.get('clienteId'))
    evento_id = dados.get('eventoId')
    if cliente_id is not None:
        validar_id(cliente_id, 'clienteId')
    if evento_id is not None:
        validar_id(evento_id, 'eventoId')
    status = dados.get('status')
    if status and status not in ('ATIVO', 'CANCELADO'):
        raise ErroDominio('Status inválido.')
    q = str(dados.get('q', '')).strip()[:120]
    resultado = listar_ingressos(page, size, sort, ordem, cliente_id, evento_id, status, q)
    return {'items': [serializar_ingresso(i) for i in resultado.items],
            'page': page, 'perPage': size, 'total': resultado.total, 'pages': resultado.pages}


def consultar(id):
    ingresso = buscar_ingresso(id)
    if ingresso is None:
        raise ErroDominio('Ingresso não encontrado.', 404)
    cliente_permitido(ingresso.cliente_id)
    return serializar_ingresso(ingresso)


def publicar_evento(tipo, ingresso):
    db.session.add(Outbox(tipo=tipo, payload={
        'ingressoId': ingresso.id,
        'eventoId': ingresso.evento_id,
        'clienteId': ingresso.cliente_id,
        'eventoNome': ingresso.evento.nome,
        'status': ingresso.status
    }))


def verificar_regras(evento, cliente_id, verificar_limite=True):
    if data_local_agora() >= evento.data_hora:
        raise ErroDominio('R2: não é possível comprar ingressos após o início do evento.', 400)
    if contar_ativos_evento(evento.id) >= evento.capacidade_maxima:
        raise ErroDominio('R1: ingressos esgotados para este evento.', 400)
    if verificar_limite and contar_ingressos_cliente(evento.id, cliente_id) >= LIMITE_INGRESSOS:
        raise ErroDominio('R3: o cliente já possui 4 ingressos para este evento.', 400)


def criar(dados):
    evento_id = validar_id(dados.get('eventoId'), 'eventoId')
    cliente_id = cliente_permitido(dados.get('clienteId'))
    validar_id(cliente_id, 'clienteId')
    try:
        evento = obter_evento(evento_id, bloquear=True)
        if evento is None:
            raise ErroDominio('Evento não encontrado.', 404)
        if db.session.get(Cliente, cliente_id) is None:
            raise ErroDominio('Cliente não encontrado.', 404)
        verificar_regras(evento, cliente_id)
        ingresso = salvar_ingresso(Ingresso(evento_id=evento_id, cliente_id=cliente_id,
                                           adquirido_em=datetime.now(timezone.utc), status='ATIVO'))
        ingresso.evento = evento
        publicar_evento('ingresso.emitido', ingresso)
        db.session.commit()
        return serializar_ingresso(ingresso)
    except Exception:
        db.session.rollback()
        raise


def atualizar(id, dados):
    novo_status = dados.get('status')
    if novo_status not in ('ATIVO', 'CANCELADO'):
        raise ErroDominio('Informe status ATIVO ou CANCELADO.')
    try:
        atual = buscar_ingresso(id)
        if atual is None:
            raise ErroDominio('Ingresso não encontrado.', 404)
        evento = obter_evento(atual.evento_id, bloquear=True)
        ingresso = bloquear_ingresso(id)
        if ingresso.status != novo_status:
            if novo_status == 'ATIVO':
                verificar_regras(evento, ingresso.cliente_id, verificar_limite=False)
            ingresso.status = novo_status
            ingresso.evento = evento
            publicar_evento('ingresso.reativado' if novo_status == 'ATIVO' else 'ingresso.cancelado', ingresso)
        db.session.commit()
        return serializar_ingresso(ingresso)
    except Exception:
        db.session.rollback()
        raise


def excluir(id):
    try:
        atual = buscar_ingresso(id)
        if atual is None:
            raise ErroDominio('Ingresso não encontrado.', 404)
        evento = obter_evento(atual.evento_id, bloquear=True)
        ingresso = bloquear_ingresso(id)
        if ingresso.status != 'CANCELADO':
            raise ErroDominio('Cancele o ingresso antes de excluí-lo.', 409)
        db.session.delete(ingresso)
        db.session.commit()
        return True
    except Exception:
        db.session.rollback()
        raise
