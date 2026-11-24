from sqlalchemy import func, or_
from extensions import db
from models.ingresso import Ingresso
from models.evento import Evento
from models.cliente import Cliente


ORDENACOES = {'id': Ingresso.id, 'adquiridoEm': Ingresso.adquirido_em, 'status': Ingresso.status}


def listar_ingressos(page, per_page, sort, ordem, cliente_id=None, evento_id=None, status=None, q=None):
    consulta = db.select(Ingresso)
    if cliente_id is not None:
        consulta = consulta.where(Ingresso.cliente_id == cliente_id)
    if evento_id is not None:
        consulta = consulta.where(Ingresso.evento_id == evento_id)
    if status:
        consulta = consulta.where(Ingresso.status == status)
    if q:
        termo = f'%{q}%'
        consulta = consulta.join(Evento, Ingresso.evento_id == Evento.id).join(Cliente, Ingresso.cliente_id == Cliente.id).where(
            or_(Evento.nome.ilike(termo), Cliente.nome.ilike(termo)))
    coluna = ORDENACOES[sort]
    consulta = consulta.order_by(coluna.desc() if ordem == 'desc' else coluna.asc(), Ingresso.id.asc())
    return db.paginate(consulta, page=page, per_page=per_page, error_out=False)


def buscar_ingresso(id):
    return db.session.get(Ingresso, id)


def bloquear_ingresso(id):
    return db.session.execute(db.select(Ingresso).where(Ingresso.id == id).with_for_update()).scalar_one_or_none()


def contar_ativos_evento(evento_id):
    return db.session.scalar(db.select(func.count(Ingresso.id)).where(
        Ingresso.evento_id == evento_id, Ingresso.status == 'ATIVO')) or 0


def contar_ingressos_cliente(evento_id, cliente_id):
    return db.session.scalar(db.select(func.count(Ingresso.id)).where(
        Ingresso.evento_id == evento_id, Ingresso.cliente_id == cliente_id)) or 0


def salvar_ingresso(ingresso):
    db.session.add(ingresso)
    db.session.flush()
    return ingresso
