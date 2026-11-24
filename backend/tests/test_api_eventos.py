from .conftest import autenticar
from extensions import db
from models.evento import Evento


def test_cadastro_evento_exige_login(client):
    resposta = client.post('/api/eventos', json={'nome': 'Teste'})
    assert resposta.status_code == 401


def test_cliente_nao_pode_criar_eventos(client):
    headers = autenticar(client)
    resposta = client.post('/api/eventos', headers=headers, json={
        'nome': 'Novo', 'descricao': 'Descrição', 'local': 'Auditório',
        'dataHora': '2028-01-01T19:00:00', 'capacidadeMaxima': 20
    })
    assert resposta.status_code == 403


def test_admin_cria_evento_e_lista_paginas(client):
    headers = autenticar(client, 'admin@example.com')
    resposta = client.post('/api/eventos', headers=headers, json={
        'nome': 'Música e Arte', 'descricao': 'Festival de música', 'local': 'Auditório SATC',
        'dataHora': '2028-01-01T19:00:00', 'capacidadeMaxima': 30
    })
    assert resposta.status_code == 201, resposta.get_json()
    assert resposta.get_json()['ingressosDisponiveis'] == 30
    lista = client.get('/api/eventos?page=1&perPage=1&q=Música&sort=nome')
    assert lista.status_code == 200
    assert lista.get_json()['total'] == 1
    assert len(lista.get_json()['items']) == 1


def test_validacao_e_openapi(client):
    autenticar(client, 'admin@example.com')
    erro = client.get('/api/eventos?sort=drop_table')
    assert erro.status_code == 400
    docs = client.get('/api/openapi.json')
    assert docs.status_code == 200
    assert '/api/eventos' in docs.get_json()['paths']
