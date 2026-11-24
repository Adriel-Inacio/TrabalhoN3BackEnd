from flask.views import MethodView
from flask_smorest import Blueprint
from services.acesso import papeis_permitidos
from services import ingressoService
from schemas import IngressoEntradaSchema, IngressoSaidaSchema, IngressoStatusSchema, FiltroIngressoSchema, PaginaIngressoSchema

blp = Blueprint('ingressos', __name__, description='Compra simulada de ingressos com regras R1 R2 R3')


@blp.route('/api/ingressos')
class Ingressos(MethodView):
    @blp.arguments(FiltroIngressoSchema, location='query')
    @blp.response(200, PaginaIngressoSchema)
    def get(self, filtros):
        return ingressoService.listar(filtros)

    @blp.arguments(IngressoEntradaSchema)
    @blp.response(201, IngressoSaidaSchema)
    def post(self, dados):
        return ingressoService.criar(dados)


@blp.route('/api/ingressos/<int:id>')
class IngressoDetalhe(MethodView):
    @blp.response(200, IngressoSaidaSchema)
    def get(self, id):
        return ingressoService.consultar(id)

    @papeis_permitidos('ADMIN')
    @blp.arguments(IngressoStatusSchema)
    @blp.response(200, IngressoSaidaSchema)
    def put(self, dados, id):
        return ingressoService.atualizar(id, dados)

    @papeis_permitidos('ADMIN')
    @blp.response(204)
    def delete(self, id):
        ingressoService.excluir(id)
        return ''


@blp.route('/api/clientes/<int:id>/ingressos')
class IngressosCliente(MethodView):
    @blp.arguments(FiltroIngressoSchema, location='query')
    @blp.response(200, PaginaIngressoSchema)
    def get(self, filtros, id):
        filtros['clienteId'] = id
        return ingressoService.listar(filtros)
