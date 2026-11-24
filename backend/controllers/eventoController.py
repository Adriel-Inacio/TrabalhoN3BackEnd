from flask.views import MethodView
from flask_smorest import Blueprint
from services.acesso import papeis_permitidos
from services import eventoService
from schemas import EventoEntradaSchema, EventoSaidaSchema, FiltroEventoSchema, PaginaEventoSchema

blp = Blueprint('eventos', __name__, description='CRUD de eventos culturais, vagas e filtros')


@blp.route('/api/eventos')
class Eventos(MethodView):
    @blp.arguments(FiltroEventoSchema, location='query')
    @blp.response(200, PaginaEventoSchema)
    def get(self, filtros):
        return eventoService.listar(filtros)

    @papeis_permitidos('ADMIN', 'FUNCIONARIO')
    @blp.arguments(EventoEntradaSchema)
    @blp.response(201, EventoSaidaSchema)
    def post(self, dados):
        return eventoService.criar(dados)


@blp.route('/api/eventos/<int:id>')
class EventoDetalhe(MethodView):
    @blp.response(200, EventoSaidaSchema)
    def get(self, id):
        return eventoService.consultar(id)

    @papeis_permitidos('ADMIN', 'FUNCIONARIO')
    @blp.arguments(EventoEntradaSchema)
    @blp.response(200, EventoSaidaSchema)
    def put(self, dados, id):
        return eventoService.atualizar(id, dados)

    @papeis_permitidos('ADMIN')
    @blp.response(204)
    def delete(self, id):
        eventoService.excluir(id)
        return ''
