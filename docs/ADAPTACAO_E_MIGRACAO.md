# Adaptação do SysStock ao CulturaPass e política de dados

## Fontes e decisão técnica

O projeto original da N2 é o CulturaPass, domínio **Entretenimento e Cultura**: `Evento`, `Cliente`, `Ingresso`, regras R1, R2 e R3. O sistema desenvolvido anteriormente, SysStock, possuía funcionários, clientes, produtos, pedidos, controle de pedidos e autenticação de três perfis. O novo projeto preserva o **framework e a arquitetura**, não as entidades que deixaram de fazer sentido.

| Origem SysStock | Destino CulturaPass | Justificativa |
|---|---|---|
| `Produto`, `estoque` | `Evento`, `capacidadeMaxima`, disponibilidade calculada | Eventos têm limite de ingressos, não estoque de mercadorias |
| `Pedido` / `ControlePedido` | `Ingresso` individual por compra | Projeto N2 exige uma aquisição por registro e compra de um ingresso por requisição |
| `Cliente` | `Cliente` + `Usuario` | Cadastro e login mantidos; cliente vinculado às aquisições |
| `Funcionario` | `Funcionario` organizador | Admin cadastra acesso, funcionário cria/edita eventos |
| Status de pedido | Status de ingresso (`ATIVO`, `CANCELADO`) | Cancela e devolve vaga sem perder histórico |
| Operação de pedido | Serviço de compra de ingresso com bloqueio de evento | Preserva atomicidade e evita vender acima da capacidade |
| Frontend de produtos/pedidos | Telas de Eventos/Ingressos | Formulários e listagens conectados ao domínio real |
| Nova infraestrutura | Dockerfiles, Compose, PostgreSQL, RabbitMQ | Atende C5 + C★ |

## Dados existentes

A distribuição Docker utiliza um volume **próprio**, identificado por `name: culturapass_n3`. Isso impede a substituição silenciosa dos volumes do SysStock. Portanto, clientes/funcionários da instalação antiga não migram automaticamente para o novo banco separado, e nenhum produto ou pedido antigo é convertido indevidamente em evento/ingresso.

Caso a equipe queira reutilizar os clientes/funcionários de uma instalação anterior **com esquema compatível**, configure o novo serviço para apontar ao banco já existente **após backup**; `python -m scripts.migrar` usa `db.create_all()` e cria as tabelas novas sem emitir `DROP`. O script também migra contas antigas sem criar perfis ADMIN automaticamente, exceto quando as variáveis de bootstrap estão presentes. A aplicação não transforma dados de estoque para ingressos porque não existe correspondência semântica segura.

## Banco novo e migração

`backend/scripts/migrar.py`: cria tabelas de modelos inexistentes; aplica `backend/migrations/002_culturapass_indices.sql` uma vez, com registro em `schema_migrations`; opcionalmente cria o administrador local. O job `migrate` é chamado automaticamente pelo Compose.

| Tabela nova | Responsabilidade |
|---|---|
| `eventos` | Programação cultural, capacidade |
| `ingressos` | Aquisição individual, cliente/evento, status |
| `outbox_eventos` | Eventos pendentes e status de publicação |
| `notificacoes` | Resultado processado por consumidor assíncrono |
| `schema_migrations` | Controle da migração aplicada |

A instalação não contém `DROP TABLE`, `TRUNCATE` nem limpeza do volume. Antes de apontar para um banco legado, verifique diferenças de colunas, faça backup e valide em ambiente de teste; `create_all` não converte automaticamente tabelas incompatíveis.

## Restrições específicas

- `ingressos.evento_id` referencia `eventos.id`.
- `ingressos.cliente_id` referencia `cliente.id`.
- Não é permitido excluir evento com histórico de ingressos, nem cliente com ingressos/notificações.
- A senha de login fica na tabela `usuario`. A duplicação do hash em `cliente` é uma herança do modelo de autenticação anterior, documentada como limitação.
- O limite R3 é histórico; ingressos cancelados também entram na contagem de quatro aquisições por evento/cliente.
