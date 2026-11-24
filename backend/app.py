import logging
from flask import Flask, jsonify, request
from flask_smorest import Api
from werkzeug.exceptions import HTTPException
from config import Config
from extensions import db
import models
from controllers.authController import auth_bp
from controllers.clienteController import blp as cliente_blp
from controllers.funcionarioController import funcionario_bp
from controllers.eventoController import blp as evento_blp
from controllers.ingressoController import blp as ingresso_blp
from controllers.notificacaoController import notificacao_bp
from services.acesso import controlar_acesso
from services.erros import ErroDominio
from services.clienteService import ClienteInvalidError


def create_app(configuracao=None):
    aplicacao = Flask(__name__)
    aplicacao.config.from_object(Config)
    if configuracao:
        aplicacao.config.update(configuracao)
    db.init_app(aplicacao)
    aplicacao.before_request(controlar_acesso)
    api = Api(aplicacao)
    aplicacao.register_blueprint(auth_bp)
    api.register_blueprint(cliente_blp)
    aplicacao.register_blueprint(funcionario_bp)
    aplicacao.register_blueprint(notificacao_bp)
    api.register_blueprint(evento_blp)
    api.register_blueprint(ingresso_blp)

    @aplicacao.get('/api/health')
    def health():
        return jsonify({'status': 'ok', 'service': 'culturapass'})

    @aplicacao.after_request
    def proteger_resposta(resposta):
        if request.path.startswith('/api/'):
            resposta.headers['Cache-Control'] = 'no-store'
            resposta.headers['X-Content-Type-Options'] = 'nosniff'
            resposta.headers['X-Frame-Options'] = 'DENY'
            resposta.headers['Referrer-Policy'] = 'no-referrer'
        return resposta

    @aplicacao.errorhandler(ClienteInvalidError)
    def erro_cliente(erro):
        return jsonify({'erro': str(erro)}), 400

    @aplicacao.errorhandler(422)
    def erro_validacao(erro):
        return jsonify({'erro': 'Dados inválidos.', 'detalhes': getattr(erro, 'data', {})}), 400

    @aplicacao.errorhandler(ErroDominio)
    def erro_dominio(erro):
        return jsonify({'erro': str(erro)}), erro.status

    @aplicacao.errorhandler(HTTPException)
    def erro_http(erro):
        if request.path.startswith('/api/'):
            return jsonify({'erro': erro.description}), erro.code
        return erro

    @aplicacao.errorhandler(Exception)
    def erro_interno(erro):
        aplicacao.logger.exception('Falha inesperada em %s %s', request.method, request.path)
        return jsonify({'erro': 'Erro interno do servidor.'}), 500

    return aplicacao


app = create_app()


if __name__ == '__main__':
    app.run(debug=False)
