# Matriz de conformidade — Projeto Final N3

**Fonte de requisitos:** `projeto-final.md`, fornecido para a N3. **Fonte de domínio:** repositório público `Adriel-Inacio/TrabalhoN2BackEnd` (CulturaPass). **Adaptação:** Python/Flask por autorização do docente informada pelo grupo. "Implementado" abaixo significa código disponibilizado; a confirmação em Docker deve ocorrer em máquina com runtime disponível.

| ID | Exigência | Implementação / evidência no pacote | Estado |
|---|---|---|---|
| N3-01 | Controller → Service → Repository | `backend/controllers/`, `services/`, `repositories/` de Cliente, Evento, Ingresso | Implementado |
| N3-02 | Pelo menos 3 entidades relacionadas | `models/cliente.py`, `models/evento.py`, `models/ingresso.py` e 2 FKs | Implementado |
| N3-03 | Service CRUD de cada entidade | `clienteService.py`, `eventoService.py`, `ingressoService.py` (status e exclusão de cancelados) | Implementado |
| N3-04 | DTO de entrada e saída | `backend/schemas/__init__.py`, schemas Marshmallow, serialização sem hashes | Implementado |
| N3-05 | Validação e erros tratados | `schemas/`, `services/validacao.py`, `services/erros.py`, `app.py` | Implementado |
| N3-06 | Paginação e ordenação | `repositorios/{cliente,evento,ingresso}Repository.py` + parâmetros `page`, `perPage`, `sort`, `ordem` | Implementado |
| N3-07 | Filtros de busca | `q`, `status`, `eventoId`, `clienteId` | Implementado |
| N3-08 | Persistência PostgreSQL via Compose | `docker-compose.yml`, SQLAlchemy e `scripts/migrar.py` | Implementado; Docker pendente de execução local |
| N3-09 | Swagger/OpenAPI automatizado | Flask-Smorest nos Controllers de Cliente, Evento e Ingresso; `/api/docs`, `/api/openapi.json` | Implementado; endpoint não executado neste ambiente |
| N3-10 | Variáveis de banco em `.env` local público | `.env` e `.env.example` somente com valores descartáveis de desenvolvimento | Implementado; não usar em produção |
| N3-11 | README completo | `README.md`: domínio, equipe, rotas, exemplos, respostas, erros, execução e carta | Implementado |
| N3-12 | Repositório público e publicação | ZIP preparado para commit no repositório do grupo | Pendente de `git push` pelo responsável |
| N3-13 | Uma aplicação prática além do domínio | Processamento assíncrono de eventos de ingresso para notificações | Implementado |
| C5-01 | Dockerfile que builda e roda aplicação | `backend/Dockerfile` (Flask/Gunicorn); `frontend/Dockerfile` (Vite/Nginx) | Implementado; build Docker não executado aqui |
| C5-02 | Compose sobe aplicativo + banco | `docker-compose.yml`: api, frontend, migrate, db, rabbitmq, publicador e consumidor | Implementado; integração pendente |
| C5-03 | Compose up inicializa sem passos extras | `migrate` executa `scripts/migrar.py`, cria tabelas e admin local; serviços dependem de healthcheck | Implementado; execução pendente |
| C★-01 | Producer real publicando em broker via Docker | `workers/publicador.py`, RabbitMQ e `Outbox` | Implementado; publicação real pendente |
| C★-02 | Consumer separado assíncrono | `workers/consumidor.py`, serviço próprio Compose, `Notificacao` idempotente | Implementado; consumo real pendente |
| C★-03 | HTTP não espera broker | `ingressoService.criar`: grava ingresso/outbox na mesma transação; publicação acontece em worker | Implementado; queda real pendente |
| SEC-01 | Login e hash de senhas | `authController.py`, `services/acesso.py`, Werkzeug | Implementado |
| SEC-02 | Autorização backend | `services/acesso.py`, decorators, isolamento por `id_cliente` em Ingresso e Notificacao | Implementado; teste automatizado incluído |
| SEC-03 | CSRF e cookies seguros | `services/acesso.py`, `config.py`, frontend `utils/api.js` | Implementado; TLS necessário em produção |
| SEC-04 | Prevenir SQLi e XSS | SQLAlchemy com parâmetros vinculados; React não interpola HTML inseguro; sorting whitelist | Implementado; sem pentest independente |
| SEC-05 | Tratamento de erro e dados sensíveis | `app.py`, DTOs, `.gitignore`, arquivos de ambiente de exemplo | Implementado |
| R1 | Capacidade | `ingressoService.verificar_regras`, bloqueio de evento e contagem ATIVO | Implementado; teste unitário incluído |
| R2 | Prazo | `services/validacao.py` e `ingressoService.verificar_regras` | Implementado; teste unitário incluído |
| R3 | Limite quatro por cliente/evento | `ingressoRepository.contar_ingressos_cliente`, `ingressoService` | Implementado; teste unitário incluído |
| DOC-01 | Plano da carta N3 | `docs/PLANO_CARTA.md` | Implementado |
| DOC-02 | Documento C5 | `docs/C5_ARCA.md` | Implementado |
| DOC-03 | Documento Carta Secreta | `docs/CARTA_SECRETA.md` | Implementado |
| DOC-04 | Resumo da adaptação/migração | `docs/ADAPTACAO_E_MIGRACAO.md` | Implementado |
| DOC-05 | Relatório de testes | `docs/RELATORIO_TESTES.md` | Implementado com limitações explícitas |
| PRE-01 | Apresentação 15 min e demonstração | Roteiro sugerido no README | Pendente de realização pela equipe |
| PRE-02 | Integração no repositório original N2 | ZIP preparado como nova base; GitHub do usuário não foi modificado | Pendente de publicação pela equipe |

## Distinção: conformidade de código x homologação

A implementação local do projeto **não comprova automaticamente** que o build Docker, a publicação RabbitMQ ou os testes de banco PostgreSQL foram executados com sucesso. Os critérios C5/C★ exigem demonstração prática via `docker compose up --build` e cenário com broker parado/restaurado. Use o relatório e a sequência do README para validar no ambiente da equipe antes da apresentação.

## Desvios conceituais autorizados

Spring Boot / JPA / Bean Validation / JUnit / Maven foram substituídos por Flask / SQLAlchemy / Marshmallow / Pytest / pip, mantendo as responsabilidades exigidas. A autorização para uso de outras tecnologias foi declarada pelo grupo e deve ser mencionada na apresentação.
