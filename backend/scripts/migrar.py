import os
from pathlib import Path
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from app import app
from extensions import db
from models.cliente import Cliente
from models.funcionario import Funcionario
from models.usuario import Usuario
from services.acesso import senha_validada


BASE_DIR = Path(__file__).resolve().parents[1]


def aplicar_migracoes():
    with app.app_context():
        db.create_all()
        with db.engine.begin() as conexao:
            conexao.exec_driver_sql('CREATE TABLE IF NOT EXISTS schema_migrations (versao VARCHAR(80) PRIMARY KEY, aplicado_em TIMESTAMPTZ NOT NULL DEFAULT NOW())')
            versao = '002_culturapass_indices'
            aplicado = conexao.execute(text('SELECT 1 FROM schema_migrations WHERE versao=:versao'), {'versao': versao}).scalar()
            if not aplicado:
                conteudo = (BASE_DIR / 'migrations' / '002_culturapass_indices.sql').read_text(encoding='utf-8')
                for instrucao in conteudo.split(';'):
                    if instrucao.strip():
                        conexao.exec_driver_sql(instrucao.strip())
                conexao.execute(text('INSERT INTO schema_migrations (versao) VALUES (:versao)'), {'versao': versao})
        clientes = db.session.execute(db.select(Cliente).order_by(Cliente.id)).scalars().all()
        existentes = set(db.session.execute(db.select(db.func.lower(Usuario.email))).scalars().all())
        for cliente in clientes:
            email = cliente.email.strip().lower()
            if email and cliente.senha_hash and email not in existentes:
                db.session.add(Usuario(email=email, senha_hash=cliente.senha_hash,
                                       perfil='CLIENTE', ativo=True, id_cliente=cliente.id))
                existentes.add(email)
        funcionarios = db.session.execute(db.select(Funcionario).order_by(Funcionario.id)).scalars().all()
        for funcionario in funcionarios:
            email = funcionario.email.strip().lower()
            if email and email not in existentes:
                db.session.add(Usuario(email=email, senha_hash='!SEM_SENHA!',
                                       perfil='FUNCIONARIO', ativo=False, id_funcionario=funcionario.id))
                existentes.add(email)
        email_admin = os.environ.get('ADMIN_BOOTSTRAP_EMAIL', '').strip().lower()
        senha_admin = os.environ.get('ADMIN_BOOTSTRAP_PASSWORD', '')
        if email_admin and senha_admin and email_admin not in existentes:
            db.session.add(Usuario(email=email_admin, senha_hash=senha_validada(senha_admin),
                                   perfil='ADMIN', ativo=True))
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            raise
        print('Migração concluída sem apagar registros existentes.')


if __name__ == '__main__':
    aplicar_migracoes()
