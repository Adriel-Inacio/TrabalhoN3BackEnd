from extensions import db
from models.funcionario import Funcionario

def listar_funcionarios():
    funcionarios = db.session.execute(
        db.select(Funcionario)
    ).scalars().all()

    return funcionarios

def inserir_funcionarios(nome, email, telefone, cpf):
    funcionario = Funcionario(
        nome = nome,
        email = email,
        telefone = telefone,
        cpf = cpf
    )

    try:
        db.session.add(funcionario)
        db.session.commit()

        return funcionario

    except Exception:
        db.session.rollback()
        raise

def atualizar_funcionario(id, nome, email, telefone, cpf):
    funcionario = db.session.get(Funcionario, id)

    if funcionario is None:
        return None

    funcionario.nome = nome
    funcionario.email = email
    funcionario.telefone = telefone
    funcionario.cpf = cpf

    try:
        db.session.commit()
        return funcionario
    except Exception:
        db.session.rollback()
        raise

def excluir_funcionario(id):
    funcionario = db.session.get(Funcionario, id)

    if funcionario is None:
        return False

    try:
        db.session.delete(funcionario)
        db.session.commit()
        return True

    except Exception:
        db.session.rollback()
        raise