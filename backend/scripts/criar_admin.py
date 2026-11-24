import getpass
from app import app
from extensions import db
from models.usuario import Usuario
from services.acesso import email_normalizado, procurar_email, senha_validada


def main():
    email = email_normalizado(input('E-mail do administrador: '))
    senha = getpass.getpass('Senha (mínimo de 10 caracteres): ')
    confirmacao = getpass.getpass('Repita a senha: ')
    if senha != confirmacao:
        raise SystemExit('As senhas não coincidem.')
    senha_hash = senha_validada(senha)
    with app.app_context():
        if procurar_email(email) is not None:
            raise SystemExit('Este e-mail já possui uma conta.')
        db.session.add(Usuario(email=email, senha_hash=senha_hash, perfil='ADMIN', ativo=True))
        db.session.commit()
    print('Administrador criado diretamente no banco de dados.')


if __name__ == '__main__':
    main()
