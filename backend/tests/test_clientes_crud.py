from .conftest import autenticar


def test_admin_cria_edita_exclui_cliente(client):
    headers = autenticar(client, 'admin@example.com')
    dados = {'nome': 'Carlos Exemplo', 'email': 'carlos@example.com', 'telefone': '48999990000', 'senha': 'SenhaCarlos2026!'}
    resposta = client.post('/api/clientes', headers=headers, json=dados)
    assert resposta.status_code == 201, resposta.get_json()
    id_cliente = resposta.get_json()['id']
    assert 'senha_hash' not in resposta.get_json()
    dados['nome'] = 'Carlos Atualizado'
    dados.pop('senha')
    resposta = client.put(f'/api/clientes/{id_cliente}', headers=headers, json=dados)
    assert resposta.status_code == 200
    assert resposta.get_json()['nome'] == 'Carlos Atualizado'
    resposta = client.delete(f'/api/clientes/{id_cliente}', headers=headers)
    assert resposta.status_code == 204


def test_cliente_nao_lista_cadastros(client):
    autenticar(client)
    resposta = client.get('/api/clientes')
    assert resposta.status_code == 403


def test_filtro_clientes(client):
    autenticar(client, 'admin@example.com')
    resposta = client.get('/api/clientes?q=Ana&page=1&perPage=10&sort=nome')
    assert resposta.status_code == 200
    assert resposta.get_json()['total'] == 1
