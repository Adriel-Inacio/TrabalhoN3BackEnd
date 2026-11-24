from sqlalchemy import or_
from extensions import db
from models.cliente import Cliente


ORDENACOES = {'id': Cliente.id, 'nome': Cliente.nome, 'email': Cliente.email}


def listar_clientes(page=1, per_page=10, q='', sort='id', ordem='asc'):
    consulta = db.select(Cliente)
    if q:
        termo = f'%{q}%'
        consulta = consulta.where(or_(Cliente.nome.ilike(termo), Cliente.email.ilike(termo)))
    coluna = ORDENACOES[sort]
    consulta = consulta.order_by(coluna.desc() if ordem == 'desc' else coluna.asc(), Cliente.id.asc())
    return db.paginate(consulta, page=page, per_page=per_page, error_out=False)


def buscar_cliente(id):
    return db.session.get(Cliente, id)


def salvar_cliente(cliente):
    db.session.add(cliente)
    db.session.flush()
    return cliente


def excluir_cliente(cliente):
    db.session.delete(cliente)
    db.session.flush()
