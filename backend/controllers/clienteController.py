from flask.views import MethodView
from flask_smorest import Blueprint
from services.acesso import papeis_permitidos
from services import clienteService
from schemas import ClienteEntradaSchema, ClienteSaidaSchema, PaginaClienteSchema, FiltroEventoSchema

blp = Blueprint('clientes', __name__, description='Cadastro e consulta de clientes')


@blp.route('/api/clientes')
class Clientes(MethodView):
    @papeis_permitidos('ADMIN', 'FUNCIONARIO')
    @blp.arguments(FiltroEventoSchema, location='query')
    @blp.response(200, PaginaClienteSchema)
    def get(self, filtros):
        return clienteService.listar(filtros)

    @papeis_permitidos('ADMIN')
    @blp.arguments(ClienteEntradaSchema)
    @blp.response(201, ClienteSaidaSchema)
    def post(self, dados):
        return clienteService.criar(dados)


@blp.route('/api/clientes/<int:id>')
class ClienteDetalhe(MethodView):
    @papeis_permitidos('ADMIN', 'FUNCIONARIO')
    @blp.response(200, ClienteSaidaSchema)
    def get(self, id):
        return clienteService.consultar(id)

    @papeis_permitidos('ADMIN')
    @blp.arguments(ClienteEntradaSchema)
    @blp.response(200, ClienteSaidaSchema)
    def put(self, dados, id):
        return clienteService.atualizar(id, dados)

    @papeis_permitidos('ADMIN')
    @blp.response(204)
    def delete(self, id):
        clienteService.excluir(id)
        return ''
