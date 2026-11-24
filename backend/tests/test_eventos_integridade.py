from .conftest import autenticar


def test_capacidade_nao_cai_abaixo_de_ingressos_emitidos(client):
    admin = autenticar(client, 'admin@example.com')
    emitido = client.post('/api/ingressos', headers=admin, json={'eventoId': 1, 'clienteId': 1})
    assert emitido.status_code == 201
    evento = client.get('/api/eventos/1').get_json()
    atualizacao = {
        'nome': evento['nome'], 'descricao': evento['descricao'],
        'local': evento['local'], 'dataHora': evento['dataHora'], 'capacidadeMaxima': 1
    }
    resposta = client.put('/api/eventos/1', headers=admin, json=atualizacao)
    assert resposta.status_code == 200
    atualizacao['capacidadeMaxima'] = 0
    resposta_invalida = client.put('/api/eventos/1', headers=admin, json=atualizacao)
    assert resposta_invalida.status_code == 400


def test_evento_com_ingressos_nao_pode_ser_excluido(client):
    admin = autenticar(client, 'admin@example.com')
    assert client.post('/api/ingressos', headers=admin, json={'eventoId': 1, 'clienteId': 1}).status_code == 201
    assert client.delete('/api/eventos/1', headers=admin).status_code == 409
