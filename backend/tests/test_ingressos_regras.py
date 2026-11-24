from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from .conftest import autenticar
from extensions import db
from models.evento import Evento
from models.ingresso import Ingresso
from models.outbox import Outbox


def adquirir(client, headers, evento=1, cliente=None):
    body = {'eventoId': evento}
    if cliente is not None:
        body['clienteId'] = cliente
    return client.post('/api/ingressos', json=body, headers=headers)


def test_r1_capacidade_nao_excede(client, app):
    with app.app_context():
        evento = db.session.get(Evento, 1)
        evento.capacidade_maxima = 1
        db.session.commit()
    headers = autenticar(client)
    assert adquirir(client, headers).status_code == 201
    segunda = adquirir(client, headers)
    assert segunda.status_code == 400
    assert 'R1' in segunda.get_json()['erro']


def test_r2_evento_iniciado(client):
    headers = autenticar(client)
    resposta = adquirir(client, headers, evento=2)
    assert resposta.status_code == 400
    assert 'R2' in resposta.get_json()['erro']


def test_r3_maximo_quatro_por_cliente(client):
    headers = autenticar(client)
    for _ in range(4):
        assert adquirir(client, headers).status_code == 201
    quinta = adquirir(client, headers)
    assert quinta.status_code == 400
    assert 'R3' in quinta.get_json()['erro']


def test_cliente_nao_compra_para_outro(client):
    headers = autenticar(client)
    resposta = adquirir(client, headers, cliente=2)
    assert resposta.status_code == 403


def test_cliente_nao_consulta_ingresso_alheio(client):
    headers_admin = autenticar(client, 'admin@example.com')
    ingresso = adquirir(client, headers_admin, cliente=2).get_json()
    autenticar(client, 'ana@example.com')
    resposta = client.get(f"/api/ingressos/{ingresso['id']}")
    assert resposta.status_code == 403
    resposta_lista = client.get('/api/clientes/2/ingressos')
    assert resposta_lista.status_code == 403


def test_cada_compra_gera_evento_outbox_sem_acessar_broker(client, app):
    headers = autenticar(client)
    resposta = adquirir(client, headers)
    assert resposta.status_code == 201
    with app.app_context():
        ingressos = db.session.execute(db.select(Ingresso)).scalars().all()
        pendentes = db.session.execute(db.select(Outbox)).scalars().all()
        assert len(ingressos) == 1
        assert len(pendentes) == 1
        assert pendentes[0].estado == 'PENDENTE'
        assert pendentes[0].payload['ingressoId'] == ingressos[0].id


def test_cancelamento_devolve_vaga(client):
    headers = autenticar(client, 'admin@example.com')
    ingresso = adquirir(client, headers, cliente=1).get_json()
    resposta = client.put(f"/api/ingressos/{ingresso['id']}", json={'status': 'CANCELADO'}, headers=headers)
    assert resposta.status_code == 200
    evento = client.get('/api/eventos/1').get_json()
    assert evento['ingressosDisponiveis'] == 5


def test_csrf_requerido(client):
    autenticar(client, 'admin@example.com')
    resposta = client.post('/api/eventos', json={})
    assert resposta.status_code == 403
