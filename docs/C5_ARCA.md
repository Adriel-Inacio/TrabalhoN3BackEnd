# C5 — Arca: Containerização total

## Critérios da carta

1. **Dockerfile para construir e executar a aplicação.** `backend/Dockerfile` prepara Python 3.12 e inicia Gunicorn; `frontend/Dockerfile` prepara React/Vite e executa Nginx. Ao contrário do SysStock anterior, o Compose não executa somente o PostgreSQL.
2. **Compose sobe aplicação junto do banco.** Serviços `db`, `migrate`, `api`, `frontend`, `rabbitmq`, `publicador`, `consumidor` em `docker-compose.yml`.
3. **Compose up inicia sem passos manuais extras.** `migrate` depende de `db:healthy`, executa SQLAlchemy `create_all` e a migração de índices versionada; a API espera sua conclusão; o frontend espera a API saudável; o admin local de demonstração é criado no primeiro boot pela variável `ADMIN_BOOTSTRAP_*`.

## Demonstração obrigatória na apresentação

```powershell
docker compose up --build -d
docker compose ps
docker compose logs migrate
docker compose exec api python -c "import urllib.request; print(urllib.request.urlopen('http://localhost:5000/api/health').read())"
```

Acesse `http://localhost:8080`, faça login com a conta local de demonstração e cadastre um evento. O fluxo comprova que o frontend, o backend e o banco estão integrados. O banco usa volume dedicado para persistência e a API não publica a senha do banco em respostas.

### Caso banco novo

O Compose usa volumes `culturapass_pgdata` e `culturapass_rabbitdata`, separados do projeto antigo. Na primeira inicialização, `migrate` cria `cliente`, `funcionario`, `usuario`, `eventos`, `ingressos`, `outbox_eventos`, `notificacoes` e registra `schema_migrations`. Inícios posteriores preservam os dados e não repetem as migrações já registradas.

### Não fazer

Nunca utilize `docker compose down -v` em banco com dados a preservar. Em ambiente público, não usar as credenciais de desenvolvimento do `.env` e configurar TLS e cookies `Secure`.

### Pendência de validação

O código dos Dockerfiles e Compose está presente. **O build de imagens e o boot real dependem do Docker no ambiente do grupo**, não disponível na execução desta entrega.
