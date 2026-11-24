from sqlalchemy import func, or_
from extensions import db
from models.evento import Evento
from models.ingresso import Ingresso


ORDENACOES = {
    'id': Evento.id,
    'nome': Evento.nome,
    'dataHora': Evento.data_hora,
    'local': Evento.local,
    'capacidadeMaxima': Evento.capacidade_maxima
}


def listar_eventos(page, per_page, q, sort, ordem):
    consulta = db.select(Evento)
    if q:
        termo = f'%{q}%'
        consulta = consulta.where(or_(Evento.nome.ilike(termo), Evento.local.ilike(termo)))
    coluna = ORDENACOES[sort]
    consulta = consulta.order_by(coluna.desc() if ordem == 'desc' else coluna.asc(), Evento.id.asc())
    return db.paginate(consulta, page=page, per_page=per_page, error_out=False)


def obter_evento(id, bloquear=False):
    consulta = db.select(Evento).where(Evento.id == id)
    if bloquear:
        consulta = consulta.with_for_update()
    return db.session.execute(consulta).scalar_one_or_none()


def ingressos_ativos(evento_id):
    return db.session.scalar(db.select(func.count(Ingresso.id)).where(
        Ingresso.evento_id == evento_id, Ingresso.status == 'ATIVO')) or 0


def salvar_evento(evento):
    db.session.add(evento)
    db.session.flush()
    return evento


def possui_ingressos(evento_id):
    return bool(db.session.scalar(db.select(func.count(Ingresso.id)).where(Ingresso.evento_id == evento_id)))
