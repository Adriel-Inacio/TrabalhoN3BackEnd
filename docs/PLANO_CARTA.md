# Entrega 01 — Plano da Carta C5 (Arca)

**Carta sorteada:** C5 — Arca (Aula 16, Infraestrutura). **Tema:** CulturaPass, Entretenimento e Cultura. **Aplicação prática adicional:** mensageria de ingressos com notificações assíncronas (Carta Secreta C★).

**Entidades/rotas afetadas:** `Evento`, `Cliente`, `Ingresso`, `Outbox`, `Notificacao`; endpoints `/api/eventos`, `/api/clientes`, `/api/ingressos`, `/api/notificacoes`, `/api/health`.

**Dependências adicionadas no ecossistema Python (equivalentes conceituais ao `pom.xml`):** `Flask-SQLAlchemy`, `Flask-Smorest`, `marshmallow`, `psycopg`, `pika`, `gunicorn`, `pytest`. A equipe foi autorizada a não utilizar Java/Spring Boot. No frontend, React/Vite é compilado para arquivos estáticos pelo Docker.

**Infraestrutura nova:** `backend/Dockerfile`, `frontend/Dockerfile`, `docker-compose.yml`, `frontend/nginx.conf` e job de migração idempotente. RabbitMQ é necessário para a Carta Secreta, mas não para aceitar a compra de ingressos.

**Maior risco:** evitar que o `docker compose up` dependa de ações manuais; garantir persistência e recuperação do broker; não reutilizar indevidamente o volume do sistema antigo e não permitir que compras paralelas ultrapassem a capacidade.

**Mitigações:** healthchecks, ordem de inicialização por `depends_on`, volumes dedicados, bloqueio pessimista em eventos e transactional outbox para mensageria desacoplada. Testes incluídos, pendentes de execução real no Docker para comprovação acadêmica.
