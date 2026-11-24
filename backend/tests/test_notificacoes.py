from .conftest import autenticar
from extensions import db
from models.notificacao import Notificacao
from models.outbox import Outbox


def test_notificacao_restrita_por_cliente(client, app):
    headers = autenticar(client)
    with app.app_context():
        db.session.add_all([
            Notificacao(chave_evento='id-1', cliente_id=1, mensagem='Ingresso criado'),
            Notificacao(chave_evento='id-2', cliente_id=2, mensagem='Ingresso de outro cliente')
        ])
        db.session.commit()
    resposta = client.get('/api/notificacoes')
    assert resposta.status_code == 200
    assert len(resposta.get_json()) == 1
    assert resposta.get_json()[0]['clienteId'] == 1


def test_consumidor_processa_uma_vez_mesmo_com_reenvio(client, app, monkeypatch):
    import workers.consumidor as consumidor
    monkeypatch.setattr(consumidor, 'app', app)
    mensagem = {
        'chave': 'evento-duplicado-1',
        'tipo': 'ingresso.emitido',
        'payload': {'ingressoId': 123, 'clienteId': 1, 'eventoId': 1, 'eventoNome': 'Festival SATC'}
    }
    consumidor.processar(mensagem)
    consumidor.processar(mensagem)
    with app.app_context():
        assert db.session.scalar(db.select(db.func.count(Notificacao.id))) == 1
