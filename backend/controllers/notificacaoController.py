from flask import Blueprint, jsonify, request
from extensions import db
from models.notificacao import Notificacao
from services.acesso import usuario_atual

notificacao_bp = Blueprint('notificacoes', __name__)


@notificacao_bp.get('/api/notificacoes')
def listar():
    usuario = usuario_atual()
    consulta = db.select(Notificacao)
    if usuario.perfil == 'CLIENTE':
        consulta = consulta.where(Notificacao.cliente_id == usuario.id_cliente)
    else:
        cliente_id = request.args.get('clienteId', type=int)
        if cliente_id:
            consulta = consulta.where(Notificacao.cliente_id == cliente_id)
    notificacoes = db.session.execute(consulta.order_by(Notificacao.id.desc()).limit(50)).scalars().all()
    return jsonify([{'id': n.id, 'clienteId': n.cliente_id, 'mensagem': n.mensagem,
                     'criadoEm': n.criado_em.isoformat()} for n in notificacoes]), 200
