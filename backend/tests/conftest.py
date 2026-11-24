import os
import pytest
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

os.environ['DATABASE_URL'] = 'sqlite://'
os.environ['SECRET_KEY'] = 'testing-local-very-long-secret-key'

from app import create_app
from extensions import db
from models.cliente import Cliente
from models.usuario import Usuario
from models.evento import Evento
from werkzeug.security import generate_password_hash


@pytest.fixture
def app():
    aplicacao = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite://', 'SECRET_KEY': 'tests-secret'})
    with aplicacao.app_context():
        db.create_all()
        senha = generate_password_hash('SenhaSegura123!')
        cliente = Cliente(nome='Ana Teste', email='ana@example.com', telefone='48999999999', senha_hash=senha)
        outro = Cliente(nome='Bia Teste', email='bia@example.com', telefone='48988888888', senha_hash=senha)
        db.session.add_all([cliente, outro])
        db.session.flush()
        db.session.add_all([
            Usuario(email='ana@example.com', senha_hash=senha, perfil='CLIENTE', ativo=True, id_cliente=cliente.id),
            Usuario(email='bia@example.com', senha_hash=senha, perfil='CLIENTE', ativo=True, id_cliente=outro.id),
            Usuario(email='admin@example.com', senha_hash=senha, perfil='ADMIN', ativo=True)
        ])
        futuro = datetime.now(ZoneInfo('America/Sao_Paulo')).replace(tzinfo=None) + timedelta(days=10)
        passado = futuro - timedelta(days=20)
        db.session.add(Evento(nome='Festival SATC', descricao='Evento musical', local='Criciúma', data_hora=futuro, capacidade_maxima=5))
        db.session.add(Evento(nome='Evento passado', descricao='Evento encerrado', local='Criciúma', data_hora=passado, capacidade_maxima=2))
        db.session.commit()
        yield aplicacao
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def autenticar(client, email='ana@example.com'):
    resposta = client.post('/api/auth/login', json={'email': email, 'senha': 'SenhaSegura123!'})
    assert resposta.status_code == 200
    return {'X-CSRF-Token': resposta.get_json()['csrf_token']}
