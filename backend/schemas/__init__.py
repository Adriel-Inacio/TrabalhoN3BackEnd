from marshmallow import Schema, fields, validate


class EventoEntradaSchema(Schema):
    nome = fields.String(required=True, validate=validate.Length(min=1, max=120))
    descricao = fields.String(required=True, validate=validate.Length(min=1, max=1000))
    local = fields.String(required=True, validate=validate.Length(min=1, max=200))
    dataHora = fields.String(required=True)
    capacidadeMaxima = fields.Integer(required=True, strict=True, validate=validate.Range(min=1))


class EventoSaidaSchema(Schema):
    id = fields.Integer()
    nome = fields.String()
    descricao = fields.String()
    local = fields.String()
    dataHora = fields.String()
    capacidadeMaxima = fields.Integer()
    ingressosVendidos = fields.Integer()
    ingressosDisponiveis = fields.Integer()


class IngressoEntradaSchema(Schema):
    eventoId = fields.Integer(required=True, strict=True, validate=validate.Range(min=1))
    clienteId = fields.Integer(required=False, allow_none=True, strict=True, validate=validate.Range(min=1))


class IngressoStatusSchema(Schema):
    status = fields.String(required=True, validate=validate.OneOf(['ATIVO', 'CANCELADO']))


class IngressoSaidaSchema(Schema):
    id = fields.Integer()
    eventoId = fields.Integer()
    clienteId = fields.Integer()
    eventoNome = fields.String()
    status = fields.String()
    adquiridoEm = fields.String()


class PaginaEventoSchema(Schema):
    items = fields.List(fields.Nested(EventoSaidaSchema))
    page = fields.Integer()
    perPage = fields.Integer()
    total = fields.Integer()
    pages = fields.Integer()


class PaginaIngressoSchema(Schema):
    items = fields.List(fields.Nested(IngressoSaidaSchema))
    page = fields.Integer()
    perPage = fields.Integer()
    total = fields.Integer()
    pages = fields.Integer()


class FiltroEventoSchema(Schema):
    page = fields.Integer(load_default=1)
    perPage = fields.Integer(load_default=10)
    q = fields.String(load_default='')
    sort = fields.String(load_default='id')
    ordem = fields.String(load_default='asc')


class FiltroIngressoSchema(FiltroEventoSchema):
    clienteId = fields.Integer(load_default=None)
    eventoId = fields.Integer(load_default=None)
    status = fields.String(load_default=None)


class ClienteEntradaSchema(Schema):
    nome = fields.String(required=True, validate=validate.Length(min=1, max=80))
    email = fields.Email(required=True, validate=validate.Length(max=80))
    telefone = fields.String(required=True)
    senha = fields.String(required=False, allow_none=True, validate=validate.Length(min=10, max=128))


class ClienteSaidaSchema(Schema):
    id = fields.Integer()
    nome = fields.String()
    email = fields.String()
    telefone = fields.String()


class PaginaClienteSchema(Schema):
    items = fields.List(fields.Nested(ClienteSaidaSchema))
    page = fields.Integer()
    perPage = fields.Integer()
    total = fields.Integer()
    pages = fields.Integer()
