import secrets
from datetime import datetime, timedelta, timezone
from functools import wraps
from flask import g, jsonify, request, session
from werkzeug.security import check_password_hash, generate_password_hash
from extensions import db
from models.usuario import Usuario


PAPEIS = {'ADMIN', 'FUNCIONARIO', 'CLIENTE'}
HASH_FICTICIO = generate_password_hash('senha-que-nao-existe')


def usuario_atual():
    return getattr(g, 'usuario', None)


def dados_usuario(usuario):
    if usuario.perfil == 'CLIENTE':
        from models.cliente import Cliente
        pessoa = db.session.get(Cliente, usuario.id_cliente)
    elif usuario.perfil == 'FUNCIONARIO':
        from models.funcionario import Funcionario
        pessoa = db.session.get(Funcionario, usuario.id_funcionario)
    else:
        pessoa = None
    return {
        'id': usuario.id,
        'email': usuario.email,
        'nome': pessoa.nome if pessoa is not None else 'Administrador',
        'perfil': usuario.perfil,
        'id_cliente': usuario.id_cliente,
        'id_funcionario': usuario.id_funcionario,
        'ativo': usuario.ativo
    }


def procurar_email(email):
    if not isinstance(email, str):
        return None
    return db.session.execute(
        db.select(Usuario).where(db.func.lower(Usuario.email) == email.strip().lower())
    ).scalar_one_or_none()


def email_normalizado(email):
    import re
    if not isinstance(email, str):
        raise ValueError('Informe um e-mail válido.')
    email = email.strip().lower()
    if len(email) > 80 or not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', email):
        raise ValueError('Informe um e-mail válido, com até 80 caracteres.')
    return email


def senha_validada(senha):
    if not isinstance(senha, str) or not 10 <= len(senha) <= 128:
        raise ValueError('A senha deve ter entre 10 e 128 caracteres.')
    return generate_password_hash(senha)


def autenticar(email, senha):
    usuario = procurar_email(email)
    if usuario is None:
        check_password_hash(HASH_FICTICIO, str(senha))
        return None
    agora = datetime.now(timezone.utc)
    if not usuario.ativo or (usuario.bloqueado_ate and usuario.bloqueado_ate > agora):
        return None
    if not isinstance(senha, str) or not check_password_hash(usuario.senha_hash, senha):
        usuario.tentativas_falhas += 1
        if usuario.tentativas_falhas >= 5:
            usuario.bloqueado_ate = agora + timedelta(minutes=15)
            usuario.tentativas_falhas = 0
        db.session.commit()
        return None
    usuario.tentativas_falhas = 0
    usuario.bloqueado_ate = None
    db.session.commit()
    return usuario


def iniciar_sessao(usuario):
    session.clear()
    session['uid'] = usuario.id
    session['csrf'] = secrets.token_urlsafe(32)
    session.permanent = True


def papeis_permitidos(*papeis):
    def decorador(funcao):
        @wraps(funcao)
        def protegida(*args, **kwargs):
            usuario = usuario_atual()
            if usuario is None:
                return jsonify({'erro': 'Faça login para continuar.'}), 401
            if usuario.perfil not in papeis:
                return jsonify({'erro': 'Você não tem permissão para realizar esta operação.'}), 403
            return funcao(*args, **kwargs)
        return protegida
    return decorador


def controlar_acesso():
    if not request.path.startswith('/api/'):
        return None
    if request.path == '/api/docs' or request.path.startswith('/api/docs/'):
        return None
    if request.path in ('/api/health', '/api/auth/login', '/api/auth/cadastro', '/api/openapi.json'):
        return None
    uid = session.get('uid')
    usuario = db.session.get(Usuario, uid) if type(uid) is int else None
    if usuario is None or not usuario.ativo:
        session.clear()
        return jsonify({'erro': 'Sessão expirada. Faça login novamente.'}), 401
    if usuario.perfil == 'CLIENTE' and usuario.id_cliente is None:
        session.clear()
        return jsonify({'erro': 'Conta sem vínculo válido.'}), 401
    if usuario.perfil == 'FUNCIONARIO' and usuario.id_funcionario is None:
        session.clear()
        return jsonify({'erro': 'Conta sem vínculo válido.'}), 401
    g.usuario = usuario
    if request.method not in ('GET', 'HEAD', 'OPTIONS'):
        token = request.headers.get('X-CSRF-Token')
        if not token or not secrets.compare_digest(str(token), str(session.get('csrf', ''))):
            return jsonify({'erro': 'Token de segurança inválido. Recarregue a página.'}), 403
    return None
