from sqlalchemy.exc import IntegrityError
from extensions import db
from models.cliente import Cliente
from models.usuario import Usuario
from models.ingresso import Ingresso
from models.notificacao import Notificacao
from repositories.clienteRepository import listar_clientes, buscar_cliente, salvar_cliente, excluir_cliente, ORDENACOES
from services.erros import ErroDominio
from services.validacao import parametros_pagina
from services.acesso import email_normalizado, procurar_email, senha_validada


class ClienteInvalidError(ValueError):
    pass


def validar_dados_cliente(nome, email, telefone):
    if not isinstance(nome, str) or not nome.strip() or len(nome.strip()) > 80:
        raise ClienteInvalidError('O nome deve possuir entre 1 e 80 caracteres.')
    try:
        email = email_normalizado(email)
    except ValueError as erro:
        raise ClienteInvalidError(str(erro)) from erro
    if not isinstance(telefone, str):
        raise ClienteInvalidError('Informe telefone com DDD.')
    telefone = ''.join(d for d in telefone if d.isdigit())
    if len(telefone) not in (10, 11):
        raise ClienteInvalidError('O telefone deve conter 10 ou 11 dígitos.')
    return {'nome': nome.strip(), 'email': email, 'telefone': telefone}


def serializar_cliente(cliente):
    return {'id': cliente.id, 'nome': cliente.nome, 'email': cliente.email, 'telefone': cliente.telefone}


def listar(dados):
    page, size, sort, ordem = parametros_pagina(dados, ORDENACOES)
    pagina = listar_clientes(page, size, str(dados.get('q', '')).strip()[:120], sort, ordem)
    return {'items': [serializar_cliente(c) for c in pagina.items],
            'page': page, 'perPage': size, 'total': pagina.total, 'pages': pagina.pages}


def consultar(id):
    cliente = buscar_cliente(id)
    if cliente is None:
        raise ErroDominio('Cliente não encontrado.', 404)
    return serializar_cliente(cliente)


def criar(dados):
    validos = validar_dados_cliente(dados.get('nome'), dados.get('email'), dados.get('telefone'))
    senha = dados.get('senha')
    try:
        if procurar_email(validos['email']):
            raise ErroDominio('E-mail já cadastrado.', 409)
        if not senha:
            raise ErroDominio('Informe uma senha com pelo menos 10 caracteres.')
        try:
            hash_senha = senha_validada(senha)
        except ValueError as erro:
            raise ErroDominio(str(erro), 400) from erro
        cliente = salvar_cliente(Cliente(**validos, senha_hash=hash_senha))
        db.session.add(Usuario(email=validos['email'], senha_hash=hash_senha,
                               perfil='CLIENTE', ativo=True, id_cliente=cliente.id))
        db.session.commit()
        return serializar_cliente(cliente)
    except IntegrityError:
        db.session.rollback()
        raise ErroDominio('Cliente ou e-mail já cadastrado.', 409)
    except Exception:
        db.session.rollback()
        raise


def atualizar(id, dados):
    validos = validar_dados_cliente(dados.get('nome'), dados.get('email'), dados.get('telefone'))
    try:
        cliente = buscar_cliente(id)
        if cliente is None:
            raise ErroDominio('Cliente não encontrado.', 404)
        usuario = db.session.scalar(db.select(Usuario).where(Usuario.id_cliente == id))
        outro = procurar_email(validos['email'])
        if outro and outro != usuario:
            raise ErroDominio('E-mail já utilizado.', 409)
        for campo, valor in validos.items():
            setattr(cliente, campo, valor)
        if usuario:
            usuario.email = validos['email']
        senha = dados.get('senha')
        if senha:
            try:
                novo_hash = senha_validada(senha)
            except ValueError as erro:
                raise ErroDominio(str(erro), 400) from erro
            cliente.senha_hash = novo_hash
            if usuario:
                usuario.senha_hash = novo_hash
        db.session.commit()
        return serializar_cliente(cliente)
    except IntegrityError:
        db.session.rollback()
        raise ErroDominio('Dados duplicados ou inválidos.', 409)
    except Exception:
        db.session.rollback()
        raise


def excluir(id):
    try:
        cliente = buscar_cliente(id)
        if cliente is None:
            raise ErroDominio('Cliente não encontrado.', 404)
        if db.session.scalar(db.select(Ingresso.id).where(Ingresso.cliente_id == id).limit(1)) is not None:
            raise ErroDominio('Cliente com ingressos não pode ser excluído.', 409)
        if db.session.scalar(db.select(Notificacao.id).where(Notificacao.cliente_id == id).limit(1)) is not None:
            raise ErroDominio('Cliente com notificações não pode ser excluído.', 409)
        conta = db.session.scalar(db.select(Usuario).where(Usuario.id_cliente == id))
        if conta:
            db.session.delete(conta)
            db.session.flush()
        excluir_cliente(cliente)
        db.session.commit()
        return True
    except Exception:
        db.session.rollback()
        raise
