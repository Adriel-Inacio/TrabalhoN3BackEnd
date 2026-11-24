from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError
from extensions import db
from models.funcionario import Funcionario
from models.usuario import Usuario
from services.acesso import papeis_permitidos, email_normalizado, procurar_email, senha_validada
from services.funcionarioService import validar_dados_funcionario, FuncionarioInvalidError

funcionario_bp = Blueprint('funcionarios', __name__)


def serializar(f):
    conta = db.session.execute(db.select(Usuario).where(Usuario.id_funcionario == f.id)).scalar_one_or_none()
    return {'id': f.id, 'nome': f.nome, 'email': f.email, 'telefone': f.telefone,
            'cpf': f.cpf, 'ativo': conta.ativo if conta else False, 'possui_acesso': bool(conta)}


@funcionario_bp.get('/api/dados')
@papeis_permitidos('ADMIN')
def listar():
    return jsonify([serializar(f) for f in db.session.execute(db.select(Funcionario).order_by(Funcionario.id)).scalars()]), 200


@funcionario_bp.post('/api/funcionarios/novo')
@papeis_permitidos('ADMIN')
def cadastrar():
    dados = request.get_json(silent=True)
    if not isinstance(dados, dict):
        return jsonify({'erro': 'Envie um JSON válido.'}), 400
    try:
        validos = validar_dados_funcionario(dados.get('nome'), dados.get('email'), dados.get('telefone'), dados.get('cpf'))
        validos['email'] = email_normalizado(validos['email'])
        senha_hash = senha_validada(dados.get('senha'))
        if procurar_email(validos['email']):
            return jsonify({'erro': 'Este e-mail já possui acesso ao sistema.'}), 409
        funcionario = Funcionario(**validos)
        db.session.add(funcionario)
        db.session.flush()
        db.session.add(Usuario(email=validos['email'], senha_hash=senha_hash, perfil='FUNCIONARIO',
                               ativo=True, id_funcionario=funcionario.id))
        db.session.commit()
        return jsonify({'message': 'Funcionário cadastrado com acesso habilitado!', 'id': funcionario.id}), 201
    except (FuncionarioInvalidError, ValueError) as erro:
        db.session.rollback()
        return jsonify({'erro': str(erro)}), 400
    except IntegrityError:
        db.session.rollback()
        return jsonify({'erro': 'CPF ou e-mail já cadastrado ou restrição do banco.'}), 409


@funcionario_bp.put('/api/funcionarios/<int:id>')
@papeis_permitidos('ADMIN')
def atualizar(id):
    dados = request.get_json(silent=True)
    if not isinstance(dados, dict):
        return jsonify({'erro': 'Envie um JSON válido.'}), 400
    try:
        validos = validar_dados_funcionario(dados.get('nome'), dados.get('email'), dados.get('telefone'), dados.get('cpf'))
        validos['email'] = email_normalizado(validos['email'])
        funcionario = db.session.get(Funcionario, id)
        if not funcionario:
            return jsonify({'erro': 'Funcionário não encontrado.'}), 404
        outro = procurar_email(validos['email'])
        conta = db.session.execute(db.select(Usuario).where(Usuario.id_funcionario == id)).scalar_one_or_none()
        if outro is not None and outro != conta:
            return jsonify({'erro': 'Este e-mail já possui acesso ao sistema.'}), 409
        for chave, valor in validos.items():
            setattr(funcionario, chave, valor)
        if conta:
            conta.email = validos['email']
        db.session.commit()
        return jsonify({'message': 'Funcionário atualizado!', 'funcionario': serializar(funcionario)}), 200
    except (FuncionarioInvalidError, ValueError) as erro:
        db.session.rollback()
        return jsonify({'erro': str(erro)}), 400
    except IntegrityError:
        db.session.rollback()
        return jsonify({'erro': 'CPF ou e-mail já utilizado.'}), 409


@funcionario_bp.put('/api/funcionarios/<int:id>/acesso')
@papeis_permitidos('ADMIN')
def acesso(id):
    dados = request.get_json(silent=True)
    if not isinstance(dados, dict):
        return jsonify({'erro': 'Envie um JSON válido.'}), 400
    funcionario = db.session.get(Funcionario, id)
    if not funcionario:
        return jsonify({'erro': 'Funcionário não encontrado.'}), 404
    try:
        conta = db.session.execute(db.select(Usuario).where(Usuario.id_funcionario == id)).scalar_one_or_none()
        senha = dados.get('senha')
        senha_hash = senha_validada(senha) if senha else None
        if conta is None:
            if not senha_hash:
                return jsonify({'erro': 'Defina uma senha para habilitar o acesso deste funcionário.'}), 400
            email = email_normalizado(funcionario.email)
            if procurar_email(email):
                return jsonify({'erro': 'E-mail já associado a outra conta.'}), 409
            conta = Usuario(email=email, senha_hash=senha_hash, perfil='FUNCIONARIO', ativo=dados.get('ativo', True), id_funcionario=id)
            db.session.add(conta)
        else:
            if senha_hash:
                conta.senha_hash = senha_hash
                conta.tentativas_falhas = 0
                conta.bloqueado_ate = None
            if 'ativo' in dados:
                if type(dados['ativo']) is not bool:
                    return jsonify({'erro': 'O estado ativo deve ser verdadeiro ou falso.'}), 400
                if dados['ativo'] and conta.senha_hash == '!SEM_SENHA!':
                    return jsonify({'erro': 'Defina uma senha antes de ativar a conta.'}), 400
                conta.ativo = dados['ativo']
        db.session.commit()
        return jsonify({'message': 'Acesso atualizado.', 'funcionario': serializar(funcionario)}), 200
    except ValueError as erro:
        db.session.rollback()
        return jsonify({'erro': str(erro)}), 400
    except IntegrityError:
        db.session.rollback()
        return jsonify({'erro': 'E-mail já associado a outra conta.'}), 409


@funcionario_bp.delete('/api/funcionarios/<int:id>')
@papeis_permitidos('ADMIN')
def excluir(id):
    funcionario = db.session.get(Funcionario, id)
    if not funcionario:
        return jsonify({'erro': 'Funcionário não encontrado.'}), 404
    try:
        conta = db.session.execute(db.select(Usuario).where(Usuario.id_funcionario == id)).scalar_one_or_none()
        if conta:
            db.session.delete(conta)
            db.session.flush()
        db.session.delete(funcionario)
        db.session.commit()
        return jsonify({'message': 'Funcionário excluído.'}), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({'erro': 'Existem registros vinculados a este funcionário. Desative seu acesso em vez de excluí-lo.'}), 409
