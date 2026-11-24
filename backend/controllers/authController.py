from flask import Blueprint, jsonify, request, session
from sqlalchemy.exc import IntegrityError
from extensions import db
from models.cliente import Cliente
from models.usuario import Usuario
from services.acesso import (
    autenticar, iniciar_sessao, dados_usuario, usuario_atual,
    email_normalizado, procurar_email, senha_validada
)
from services.clienteService import validar_dados_cliente, ClienteInvalidError


auth_bp = Blueprint('auth', __name__)


@auth_bp.post('/api/auth/login')
def login():
    dados = request.get_json(silent=True)
    if not isinstance(dados, dict):
        return jsonify({'erro': 'Envie um JSON válido.'}), 400
    usuario = autenticar(dados.get('email'), dados.get('senha'))
    if usuario is None:
        return jsonify({'erro': 'Credenciais inválidas ou acesso temporariamente indisponível.'}), 401
    iniciar_sessao(usuario)
    return jsonify({'usuario': dados_usuario(usuario), 'csrf_token': session['csrf']}), 200


@auth_bp.get('/api/auth/me')
def me():
    return jsonify({'usuario': dados_usuario(usuario_atual()), 'csrf_token': session['csrf']}), 200


@auth_bp.post('/api/auth/logout')
def logout():
    session.clear()
    return jsonify({'message': 'Sessão encerrada.'}), 200


@auth_bp.post('/api/auth/cadastro')
def cadastro():
    dados = request.get_json(silent=True)
    if not isinstance(dados, dict):
        return jsonify({'erro': 'Envie um JSON válido.'}), 400
    try:
        cliente_dados = validar_dados_cliente(dados.get('nome'), dados.get('email'), dados.get('telefone'))
        email = email_normalizado(cliente_dados['email'])
        senha_hash = senha_validada(dados.get('senha'))
        if procurar_email(email) is not None:
            return jsonify({'erro': 'Este e-mail já está em uso.'}), 409
        cliente = Cliente(**cliente_dados, senha_hash=senha_hash)
        db.session.add(cliente)
        db.session.flush()
        usuario = Usuario(email=email, senha_hash=senha_hash, perfil='CLIENTE', ativo=True, id_cliente=cliente.id)
        db.session.add(usuario)
        db.session.commit()
        return jsonify({'message': 'Conta criada com sucesso. Faça login.'}), 201
    except (ClienteInvalidError, ValueError) as erro:
        db.session.rollback()
        return jsonify({'erro': str(erro)}), 400
    except IntegrityError:
        db.session.rollback()
        return jsonify({'erro': 'Não foi possível concluir o cadastro. Verifique se o e-mail já está em uso.'}), 409
