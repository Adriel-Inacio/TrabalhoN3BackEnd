# Relatório de testes e limitações — CulturaPass N3

**Data da preparação:** 24/11/2026. **Escopo:** cópia do código-fonte final entregue no ZIP. Os comandos e resultados abaixo correspondem apenas às verificações realmente executadas no ambiente de preparação; não representam homologação no ambiente Docker do grupo.

## Verificações realizadas

| Verificação | Comando ou método | Resultado | Limitações |
|---|---|---|---|
| Sintaxe de módulos Python | `python -m compileall backend` | **Passou:** arquivos compilados sem erro de sintaxe | Não importa bibliotecas ou executa a API |
| Sintaxe dos componentes JavaScript/JSX | Parser TypeScript, AST para arquivos `.js`/`.jsx` do frontend | **Passou:** 22 arquivos interpretados sem erros de parsing | Não substitui Vite/React build |
| Imports relativos do frontend | Inspeção dos caminhos importados por arquivos `.js` e `.jsx` | **Passou:** nenhum import local ausente encontrado | Não executa componentes |
| YAML do Docker Compose | `yaml.safe_load` via PyYAML | **Passou:** YAML válido com 7 serviços (`db`, `rabbitmq`, `migrate`, `api`, `publicador`, `consumidor`, `frontend`) | Não valida o runtime Docker nem a semântica completa do Compose |
| Validação isolada de domínio | Importação de `services.validacao` e chamadas com dados válidos e inválidos | **Passou:** rejeição de capacidade e data inadequadas | Sem banco; não testa chamadas HTTP |
| Estrutura de entrega | Conferência de arquivos, documentação e ZIP | **Passou** | Não assegura funcionamento integrado |

## Tentativas não executadas com sucesso por restrições do ambiente

| Verificação | Resultado real |
|---|---|
| Pytest HTTP e banco | **Não executado:** tentativa de iniciar Pytest falhou na coleta/importação por `ModuleNotFoundError: No module named 'flask'` |
| Instalação das dependências Python | **Não concluída:** tentativa de `pip install` bloqueada por indisponibilidade de acesso aos índices de pacotes (DNS/rede) |
| `npm run build` com Vite | **Não executado com sucesso:** não há `vite`/`node_modules` instalados no ambiente de preparação |
| `docker compose config`, `docker compose up --build` | **Não executados:** CLI do Docker ausente |
| Testes reais do PostgreSQL, locks concorrentes e migrations | **Pendentes:** banco Docker não iniciado neste ambiente |
| RabbitMQ com producer, consumer, reinício do broker e recuperação outbox | **Pendentes:** broker real não disponível |
| Testes ponta a ponta do navegador e perfis | **Pendentes:** execução conjunta do backend e frontend não ocorreu |
| Scan independente de vulnerabilidades/dependências | **Não executado** |

**Conclusão:** existe uma implementação entregue e verificações estáticas positivas, mas **não é legítimo declarar aprovação dos critérios de aceite C5/C★ sem executar Docker e os testes de integração na máquina da equipe**.

## Roteiro de homologação obrigatório

1. Com Docker Desktop instalado e a raiz do projeto aberta: `docker compose config` e `docker compose up --build -d`; verificar `docker compose ps`, migrator `Exited (0)` e os serviços saudáveis.
2. `docker compose exec api python -m pytest -q` não inclui Pytest na imagem de produção; use `cd backend; python -m pip install -r requirements-dev.txt; python -m pytest -q` com Python local e `DATABASE_URL` de teste, ou execute os testes com um contêiner de teste temporário conforme a documentação. **Não use banco com dados de produção**.
3. Abrir `http://localhost:8080` e `/api/docs`; testar ADMIN, funcionário e cliente, incluindo respostas HTTP 401/403 quando necessário.
4. Criar evento com capacidade 1, fazer uma compra `201`; tentar segunda compra e confirmar R1 (400).
5. Tentar comprar evento já iniciado e verificar R2 (400).
6. Criar evento com capacidade 10, fazer 4 compras pelo mesmo cliente e verificar que a quinta falha com R3 (400).
7. Acessar ingresso de outro cliente como CLIENTE e verificar 403; enviar `POST` sem `X-CSRF-Token` e verificar 403.
8. Parar RabbitMQ: `docker compose stop rabbitmq`; fazer compra válida. Confirmar 201 e `outbox_eventos.estado = PENDENTE` (ou tentativa com reenvio programado).
9. Restaurar RabbitMQ: `docker compose start rabbitmq`; verificar logs `docker compose logs -f publicador consumidor`, registro de notificação e ausência de duplicação após eventual reenvio.
10. Reiniciar serviços com `docker compose restart`; confirmar que dados persistem nos volumes.
11. Validar filtros, paginação, ordenação, DTOs, edição, exclusão e constraints com banco PostgreSQL em execução.
12. Confirmar que `docker compose up --build` inicia a aplicação com banco vazio. **Use ambiente/volume descartável separado; não execute `docker compose down -v` em dados que deseja preservar.**

## Critérios de avaliação — situação factual

- **C5 — Arca:** Dockerfiles, healthchecks, dependências, etapa de migração e Compose constam no código; confirmação de build e subida com um comando ainda pendente.
- **Carta Secreta:** implementação de RabbitMQ real, Outbox transacional, publicador em processo separado e consumidor idempotente com ACK/NACK; prova de mensagens reais ainda pendente.
- **R1/R2/R3:** código e testes de Pytest incluídos; suíte não pôde ser executada no ambiente de preparação.
- **Segurança:** controles de sessão, CSRF, autorização, hashes e DTOs presentes no código, mas sem pentest e sem validação integrada completa.
- **Frontend:** componentes React e caminhos relativos validados estaticamente; build e navegador aguardam instalação real.

## Próxima ação da equipe

Execute primeiro `docker compose up --build -d` e registre `docker compose ps`, `docker compose logs migrate` e `docker compose logs api`; então execute a suíte de testes e registre o resultado. Apenas depois substitua os status pendentes da matriz por “homologado”.
