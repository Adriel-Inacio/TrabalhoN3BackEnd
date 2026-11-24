# CulturaPass — Projeto Final N3 · SATC Backend 2026.2

Sistema completo de gestão de eventos culturais e aquisição simulada de ingressos, evoluído a partir do sistema React/Flask desenvolvido durante a disciplina, com o **domínio do projeto original da N2** ([TrabalhoN2BackEnd](https://github.com/Adriel-Inacio/TrabalhoN2BackEnd)).

O projeto preserva a organização **Controller → Service → Repository → PostgreSQL**, conta com autenticação por perfil, DTOs e validações com Marshmallow, paginação, documentação Swagger/OpenAPI, migração do banco, frontend React, containerização integral **C5 — Arca** e mensageria real via RabbitMQ **Carta Secreta — Mensageiro Interestelar**.


> **Primeira instalação em uma máquina nova?** Comece pela seção **[7. Instalação passo a passo — recomendada com Docker](#7-instalação-passo-a-passo--recomendada-com-docker)**. Você não precisa instalar Python, Node.js, criar `.venv` ou executar SQL manualmente para utilizar o sistema com Docker.
>
> **Quer desenvolver e depurar o código no VS Code?** Depois de entender a instalação principal, consulte a **[seção 8 — execução local](#8-execução-local-alternativa-para-desenvolvimento)**. São **dois modos de execução alternativos**, não etapas para executar em sequência.

### Navegação rápida

| Quero... | Vá para... |
|---|---|
| Instalar tudo em um computador novo | [Seção 7](#7-instalação-passo-a-passo--recomendada-com-docker) |
| Saber qual senha usar no primeiro login | [Passo 7.7](#77-primeiro-login-e-criação-de-usuários) |
| Saber como ligar e desligar diariamente | [Seção 7.9](#79-como-ligar-e-desligar-nos-próximos-dias) |
| Executar Flask e Vite pelo VS Code | [Seção 8](#8-execução-local-alternativa-para-desenvolvimento) |
| Resolver erros de primeira instalação | [Seção 7.11](#711-solução-de-problemas-comuns) |
| Entender regras de eventos e ingressos | [Seção 3](#3-regras-de-negócio-preservadas-da-n2) |
| Conhecer rotas e exemplos da API | [Seção 10](#10-endpoints-e-contratos-json) |
| Demonstrar Docker e mensageria na N3 | [Seções 11 e 12](#11-c5--arca-implementação-e-demonstração) |

---

## 1. Equipe

| Integrante | GitHub |
|---|---|
| Adriel Inacio Cardoso | [Adriel-Inacio](https://github.com/Adriel-Inacio) |
| Bruno da Silva Martins | [Br-Silva1](https://github.com/Br-Silva1) |
| Pedro Bellarmino Cardoso | [pedrobellarminocardoso](https://github.com/pedrobellarminocardoso) |

**Disciplina:** Backend — Engenharia de Software · **Professor:** Daniel Plácido · **Avaliação:** N3.

## 2. Problema, tema e aplicação prática

**Tema:** Entretenimento e Cultura. Eventos podem ser vendidos acima da capacidade quando os registros não são centralizados; compradores podem adquirir ingressos após o início ou acima do limite individual. O CulturaPass concentra eventos, clientes e ingressos no PostgreSQL e executa regras na transação.

**Aplicação prática:** processamento assíncrono e persistente de eventos de ingressos. Cada emissão, cancelamento ou reativação registra um evento no *transactional outbox*. Um processo publica no RabbitMQ e um consumidor separado materializa uma notificação. O HTTP da compra é independente da disponibilidade do broker.

As aquisições são **simuladas**: não há gateway de pagamento, cobrança real, QR Code nem envio de e-mails.

## 3. Regras de negócio preservadas da N2

| Regra | Especificação | Implementação |
|---|---|---|
| R1 — Capacidade | Não exceder a capacidade máxima do evento | Bloqueio pessimista `FOR UPDATE` em `eventos` e contagem de ingressos `ATIVO` |
| R2 — Prazo | Não adquirir ingresso após o início do evento | Compara data local do evento com o horário atual de `America/Sao_Paulo` |
| R3 — Limite individual | Máximo de 4 ingressos por cliente/evento | Contagem de aquisições do cliente para o evento; inclui canceladas para preservar o limite histórico |

Cada `POST /api/ingressos` registra **um ingresso**; não aceita múltiplos ingressos por requisição. O cadastro de evento não precisa informar preço. Não há pagamento real.

## 4. Tecnologias

| Camada | Tecnologia |
|---|---|
| Frontend | React 19, React Router 7, Vite 6, CSS Modules |
| Backend/API | Python 3.12, Flask 3, Flask-SQLAlchemy 3, SQLAlchemy 2 |
| Contratos de entrada/saída | Marshmallow e Flask-Smorest (DTOs + OpenAPI 3) |
| Banco | PostgreSQL 15 no Docker |
| Autenticação | Sessão em cookie HttpOnly + token CSRF + hash de senha Werkzeug |
| Mensageria | RabbitMQ 3.13, Pika, transactional outbox |
| Servidor HTTP | Gunicorn e Nginx |
| Testes automatizados | Pytest |
| Infraestrutura | Dockerfiles e Docker Compose |

O professor autorizou Python/Flask no lugar de Java/Spring Boot. SQLAlchemy atende conceitualmente ao papel de JPA; Marshmallow ao de Bean Validation/DTO; Pytest ao de JUnit; Flask-Smorest ao de springdoc-openapi. **Não há código Spring Boot/JPA nesta adaptação.**

## 5. Entidades e relacionamentos

| Entidade | Campos principais | Relações |
|---|---|---|
| `Evento` | `id`, `nome`, `descricao`, `local`, `data_hora`, `capacidade_maxima` | 1:N com Ingresso |
| `Cliente` | `id`, `nome`, `email`, `telefone`, `senha_hash` | 1:N com Ingresso, 1:1 com Usuario |
| `Ingresso` | `id`, `evento_id`, `cliente_id`, `adquirido_em`, `status` | N:1 com Evento e Cliente |
| `Usuario` | `email`, `senha_hash`, `perfil`, `ativo` e controle de login | Perfis ADMIN, FUNCIONARIO, CLIENTE |
| `Funcionario` | `nome`, `email`, `telefone`, `cpf` | Conta de acesso FUNCIONARIO |
| `Outbox` | `chave`, `tipo`, `payload`, `estado`, `tentativas` | Eventos confiáveis de domínio |
| `Notificacao` | `chave_evento` única, `cliente_id`, `mensagem` | Processamento idempotente do consumer |

`Cliente` mantém os campos auxiliares da arquitetura de autenticação do SysStock, por compatibilidade com o modelo anterior. O hash duplicado em `cliente` é uma limitação legada; a autenticação consulta `usuario.senha_hash`.

**Relação principal:** `Cliente 1:N Ingresso N:1 Evento`. A disponibilidade é calculada de ingressos ativos e não armazenada de forma redundante.

## 6. Organização

```text
CulturaPass_N3/
├── .env
├── .env.example
├── .gitignore
├── docker-compose.yml
├── README.md
├── docs/
│   ├── MATRIZ_CONFORMIDADE.md
│   ├── PLANO_CARTA.md
│   ├── C5_ARCA.md
│   ├── CARTA_SECRETA.md
│   ├── RELATORIO_TESTES.md
│   └── ADAPTACAO_E_MIGRACAO.md
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app.py
│   ├── config.py
│   ├── models/
│   ├── schemas/
│   ├── controllers/
│   ├── services/
│   ├── repositories/
│   ├── migrations/
│   ├── scripts/
│   ├── workers/
│   └── tests/
└── frontend/
    ├── Dockerfile
    ├── nginx.conf
    ├── package.json
    ├── vite.config.js
    └── src/
```

## 7. Instalação passo a passo — recomendada com Docker

> **Este é o caminho principal para instalar o CulturaPass do zero em um computador novo.** Siga os passos **7.1 até 7.8, nesta ordem**. Não execute os comandos da seção 8 junto com estes: a seção 8 é outro modo de rodar o projeto, destinado a quem vai modificar o código.

### O que será instalado automaticamente?

O comando principal do Docker baixa e prepara o ambiente isolado da aplicação. Ele inicia os seguintes serviços:

| Serviço | Para que serve | Precisa instalar manualmente? |
|---|---|---|
| PostgreSQL | Salva usuários, eventos, ingressos e notificações | Não |
| RabbitMQ | Recebe mensagens de eventos de ingresso | Não |
| Migração (`migrate`) | Cria/atualiza tabelas e prepara o administrador inicial | Não |
| API Flask (`api`) | Fornece endpoints e regras de negócio | Não |
| Publicador e consumidor | Processam mensagens em segundo plano | Não |
| React + Nginx (`frontend`) | Disponibiliza a interface web | Não |

**No modo Docker você não precisa instalar Python 3.12, Node.js ou PostgreSQL no Windows.** A versão Python 3.12 está definida na imagem `backend/Dockerfile`; as dependências são instaladas dentro dos containers.

### 7.1. Instale os pré-requisitos uma vez

No **Windows 10/11**, instale e configure:

1. **Docker Desktop**, pelo site oficial: https://www.docker.com/products/docker-desktop/.
2. **WSL 2**, caso o Docker Desktop solicite, seguindo as orientações mostradas durante a instalação. Reinicie o computador se necessário.
3. **Git**, necessário para baixar o código-fonte do repositório: https://git-scm.com/downloads.
4. **VS Code** (opcional, apenas para editar os arquivos): https://code.visualstudio.com/.

Abra o **Docker Desktop** e aguarde até indicar que o mecanismo Docker está em execução. Mantenha o aplicativo aberto durante os próximos passos.

Abra o **PowerShell** e execute, um comando por vez:

```powershell
git --version
docker --version
docker compose version
docker info
```

**Como conferir:** `git --version` deve mostrar a versão do Git; os comandos `docker --version` e `docker compose version` mostram as versões do Docker. `docker info` precisa obter informações do servidor, sem o erro *Cannot connect to the Docker daemon*. Se aparecer um erro de Docker, abra/reinicie o Docker Desktop antes de continuar.

### 7.2. Clone o projeto pelo GitHub

O código-fonte é distribuído **pelo repositório GitHub da equipe**. Não é necessário receber um arquivo compactado nem copiar arquivos individualmente.

Abra o **PowerShell** em uma pasta onde deseja guardar o projeto (por exemplo, `Documentos`) e execute:

```powershell
git clone https://github.com/Adriel-Inacio/TrabalhoN3BackEnd.git CulturaPass_N3
cd CulturaPass_N3
```

O primeiro comando baixa os arquivos do GitHub para uma nova pasta `CulturaPass_N3`; o segundo entra nessa pasta.

Abra a pasta clonada no VS Code ou no Explorador de Arquivos. Na raiz, confira os itens:

```text
CulturaPass_N3/
├── docker-compose.yml
├── .env
├── .env.example
├── README.md
├── backend/
├── frontend/
└── docs/
```

**Importante:** o `docker-compose.yml` fica na **raiz**, e é nessa pasta que você executará os comandos Docker. Não entre em `backend` ou `frontend` para realizar a instalação principal.

**Como abrir o terminal no local certo no Windows:** no Explorador de Arquivos, abra `CulturaPass_N3`, clique na barra de endereços, digite `powershell` e pressione Enter. Ou, no VS Code, escolha **Terminal → Novo Terminal**.

Confira a pasta atual:

```powershell
Get-Location
Test-Path .\docker-compose.yml
Test-Path .\backend\Dockerfile
Test-Path .\frontend\Dockerfile
```

Os três últimos comandos devem retornar `True`. Se retornarem `False`, você está na pasta incorreta ou o repositório/branch clonado não contém o projeto CulturaPass N3 completo. Confira `git branch --show-current` e `git status`.

### 7.3. Confira as configurações iniciais

Na raiz existe o arquivo **`.env`**, utilizado pelo Compose para configurar banco, broker, chave do Flask e administrador inicial. O arquivo **`.env.example`** mostra as variáveis esperadas.

No PowerShell, verifique apenas se o arquivo está presente:

```powershell
Test-Path .\.env
```

Se retornar `False`, crie-o a partir do modelo:

```powershell
Copy-Item .\.env.example .\.env
```

**Não rode `Copy-Item` se o `.env` já existir**, pois você pode sobrescrever suas configurações. Abra-o no editor e verifique se estão preenchidas as variáveis:

```dotenv
DB_NAME=...
DB_USER=...
DB_PASSWORD=...
RABBIT_USER=...
RABBIT_PASSWORD=...
FLASK_SECRET_KEY=...
ADMIN_BOOTSTRAP_EMAIL=...
ADMIN_BOOTSTRAP_PASSWORD=...
```

O repositório da N3 deve disponibilizar as **variáveis de configuração necessárias**. O arquivo `.env.example` documenta valores de demonstração para uso **exclusivamente local**, conforme a proposta acadêmica. Se `.env` não estiver versionado, crie-o a partir do exemplo usando o comando acima. **Nunca publique senhas reais nem segredos de produção no GitHub.**

Atenção a três diferenças:

- **`.env` da raiz**: utilizado pelos serviços em Docker.
- **`backend/.env.example`**: modelo para a execução **manual** da seção 8; não precisa ser copiado no modo Docker.
- **`frontend`**: não precisa de `.env` para funcionar na instalação Docker deste pacote.

### 7.4. Verifique a configuração do Docker Compose

Ainda na raiz, execute:

```powershell
docker compose config --quiet
```

**Como conferir:** o comando deverá terminar sem mensagem de erro. Caso reclame de variável não definida, confira o `.env` da raiz e o nome das variáveis. Caso reclame de YAML, confirme que está utilizando o `docker-compose.yml` do CulturaPass N3.

As portas publicadas no computador são:

| Porta | Uso |
|---|---|
| `8080` | Interface web e API pelo Nginx |
| `5000` | API Flask para diagnóstico local |
| `5438` | PostgreSQL, para acesso local opcional |
| `5672` | RabbitMQ (protocolo AMQP) |
| `15672` | Painel de gerenciamento do RabbitMQ |

As portas foram vinculadas a `127.0.0.1` no Compose, para limitar o acesso ao próprio computador. Se alguma estiver ocupada, consulte a seção 7.11 antes de alterar as configurações.

### 7.5. Inicie todo o sistema pela primeira vez

Execute **um único comando**, na raiz:

```powershell
docker compose up --build -d
```

Na primeira execução, o Docker precisará baixar imagens e construir as imagens do backend/frontend. Isso depende da conexão com a internet. O modo `-d` deixa os serviços em execução sem prender o terminal.

Depois, consulte o estado dos serviços:

```powershell
docker compose ps -a
```

**O que esperar:**

- `db` e `rabbitmq`: em execução e, após a inicialização, `healthy`.
- `migrate`: pode aparecer como **`Exited (0)`**. Isso é **normal**: é um serviço de execução única que cria/prepara o banco e termina com sucesso.
- `api`: em execução, idealmente `healthy`.
- `publicador` e `consumidor`: em execução.
- `frontend`: em execução.

**Não execute migrações ou `criar_admin.py` manualmente nesse modo.** O serviço `migrate` já chama `python -m scripts.migrar`, executa `db.create_all()`, aplica os índices e tenta criar a conta ADMIN inicial definida no `.env`.

### 7.6. Confirme que o banco e a API foram inicializados

Ainda na raiz, execute:

```powershell
docker compose logs --tail 80 migrate
docker compose logs --tail 80 api
```

Na saída de `migrate`, procure a confirmação:

```text
Migração concluída sem apagar registros existentes.
```

Confira a API pelo PowerShell:

```powershell
Invoke-RestMethod http://localhost:8080/api/health
```

A resposta prevista é:

```json
{
  "status": "ok",
  "service": "culturapass"
}
```

Também é possível verificar se o banco possui a tabela `eventos`:

```powershell
docker compose exec db psql -U culturapass -d culturapass -c "SELECT COUNT(*) FROM eventos;"
```

O usuário e banco acima correspondem aos **valores padrão de demonstração**. Se você alterou `DB_USER` ou `DB_NAME`, substitua-os no comando. Uma contagem de `0` é normal em um banco recém-criado.

### 7.7. Primeiro login e criação de usuários

Abra o navegador e acesse:

**http://localhost:8080/login**

Acesse como administrador utilizando os valores de `ADMIN_BOOTSTRAP_EMAIL` e `ADMIN_BOOTSTRAP_PASSWORD` definidos no `.env` da raiz. **Na configuração de demonstração**, esses valores são:

| Campo | Valor de demonstração |
|---|---|
| E-mail | `admin@culturapass.local` |
| Senha | `SomenteParaDesenvolvimento2026!` |

Esses valores servem apenas para testes locais e **não são credenciais seguras para publicação**. O usuário ADMIN é criado pelo serviço de migração, não pela tela de cadastro público.

Depois do login:

1. **Administrador:** pode cadastrar funcionários e gerenciar os eventos e demais cadastros.
2. **Funcionário:** deve receber seu cadastro e senha inicial do administrador; não possui cadastro público.
3. **Cliente:** utiliza a página **http://localhost:8080/cadastro** para criar uma conta; depois faz login normalmente.

**Se o login falhar**, consulte `docker compose logs --tail 80 migrate` e confira o e-mail/senha de bootstrap. Se você reutilizou um banco já inicializado, alterar a senha de bootstrap no `.env` **não redefine automaticamente** a senha de uma conta ADMIN existente.

### 7.8. Faça um teste simples de ponta a ponta

Com o sistema aberto:

1. Entre como **ADMIN**.
2. Cadastre um **evento com data/hora futura** e capacidade, por exemplo, de 5 ingressos. Preencha nome, descrição e local.
3. Faça logout.
4. Crie um **cliente de teste** na página `/cadastro`.
5. Entre com a conta do cliente e acesse os eventos disponíveis.
6. Adquira **um ingresso** para o evento criado.
7. Abra **Meus ingressos** e confirme que a compra aparece com status `ATIVO`.
8. Abra **Notificações**. O processamento é assíncrono, portanto a notificação poderá aparecer após a publicação/consumo no RabbitMQ.
9. Faça logout e entre novamente com o administrador, conferindo o registro do ingresso no painel.

Para consultar o broker, abra **http://localhost:15672** e utilize `RABBIT_USER` / `RABBIT_PASSWORD` do `.env` da raiz. O painel é opcional para uso normal; ele ajuda a demonstrar a **Carta Secreta**.

**Pronto:** se esses passos funcionarem, você terá validado um fluxo básico em sua máquina, incluindo autenticação, persistência e integração. Para a prova completa das três regras de negócio, da mensageria e das permissões, utilize `docs/RELATORIO_TESTES.md` e `docs/CARTA_SECRETA.md`.

### 7.9. Como ligar e desligar nos próximos dias

Depois de realizar a primeira instalação **não é necessário repetir `--build` sempre**. Basta abrir o Docker Desktop e executar, na raiz do projeto:

```powershell
docker compose up -d
```

Para encerrar os serviços sem apagar os dados:

```powershell
docker compose stop
```

Para acompanhar o estado e os erros:

```powershell
docker compose ps -a
docker compose logs --tail 100 api
docker compose logs --tail 100 publicador consumidor
```

Use `docker compose up --build -d` novamente **quando você modificar o código ou as imagens precisarem ser reconstruídas**.

**Nunca use `docker compose down -v` para o encerramento diário:** `-v` remove os volumes do PostgreSQL e do RabbitMQ, com risco de perda dos dados de teste. O CulturaPass possui volumes próprios, separados do SysStock anterior.

### 7.10. Como conferir o funcionamento dos containers e da mensageria

Os serviços implementam o fluxo **API → Outbox no PostgreSQL → Publicador → RabbitMQ → Consumidor → Notificação**. A compra do ingresso não espera a resposta do RabbitMQ.

Para inspecionar mensagens e erros:

```powershell
docker compose logs --tail 100 publicador
docker compose logs --tail 100 consumidor
docker compose logs --tail 100 rabbitmq
```

**Teste acadêmico da Carta Secreta (somente em ambiente de testes):** pare o broker, realize a compra de um ingresso, e inicie o broker novamente. As mensagens pendentes deverão ser processadas quando ele voltar:

```powershell
docker compose stop rabbitmq
```

Faça **uma compra válida** pela interface e confira seu ingresso. Depois:

```powershell
docker compose start rabbitmq
docker compose logs --tail 100 publicador consumidor
```

Veja os critérios de evidência e os detalhes técnicos em `docs/CARTA_SECRETA.md`. O comportamento real precisa ser demonstrado no seu Docker; a existência dos arquivos por si só não comprova a carta.

### 7.11. Solução de problemas comuns

| Problema | O que significa | Como resolver |
|---|---|---|
| `docker` não reconhecido | Docker não instalado ou não encontrado no terminal | Instale/abra o Docker Desktop e reabra o PowerShell |
| `Cannot connect to the Docker daemon` | O mecanismo Docker não está ativo | Inicie o Docker Desktop e verifique `docker info` |
| `no configuration file provided` | Terminal aberto na pasta errada | Abra a raiz `CulturaPass_N3`, onde existe `docker-compose.yml` |
| Variável `DB_NAME`/`DB_PASSWORD` não definida | `.env` da raiz ausente ou incompleto | Confira a seção 7.3 e execute `docker compose config --quiet` |
| Porta `8080` ou `5438` ocupada | Outro programa usa a porta | Identifique o processo com `Get-NetTCPConnection -LocalPort 8080 -ErrorAction SilentlyContinue`, ou pare a aplicação conflitante |
| `migrate` terminou com erro | Falha na conexão ou migração do PostgreSQL | `docker compose logs --tail 150 migrate` e `docker compose logs --tail 100 db` |
| `relation "usuario" does not exist` | Esquema de autenticação não foi criado | Confirme que `migrate` terminou com código `0`; não apague as tabelas |
| `401` em `/api/auth/me` antes de logar | O navegador verificou sessão sem autenticação | Normal antes do primeiro login |
| Admin não consegue entrar | Credenciais diferentes ou usuário já criado | Confira variáveis de bootstrap, status de `migrate` e a conta existente |
| `http://localhost:8080` não abre | Frontend/API não inicializados ou porta em conflito | `docker compose ps -a` e `docker compose logs --tail 100 frontend api` |
| Notificações não aparecem imediatamente | Mensageria assíncrona | Confira `publicador`, `consumidor` e `rabbitmq`; atualize a página depois do processamento |
| Swagger abre sem interface visual | Recursos Swagger UI do CDN exigem internet | Use `/api/openapi.json` ou conecte à internet |

Se um comando falhar, **não execute os próximos passos às cegas**. Primeiro corrija a etapa atual, verificando os logs. Evite apagar volumes ou recriar o banco como primeira tentativa.

---

## 8. Execução local — alternativa para desenvolvimento

> **Opcional.** Use este modo apenas se quiser rodar Flask e Vite diretamente no VS Code para alterar/depurar o código. **Não é necessário depois de concluir a seção 7**. Caso tenha iniciado o Compose completo anteriormente, pare `api`, `frontend`, `publicador` e `consumidor` antes de iniciar equivalentes no Windows, evitando conflito de portas:
>
> `docker compose stop api frontend publicador consumidor`

### 8.1. Instale os pré-requisitos locais

Nesse modo, você precisa de **Python**, **Node.js com npm** e **Docker Desktop** (apenas para PostgreSQL e RabbitMQ).

No PowerShell, verifique:

```powershell
py --list-paths
node --version
npm --version
docker compose version
```

**Python 3.12 é a versão-alvo do backend no Docker.** Se ela não estiver instalada no Windows, o comando `py -3.12` falhará com `No suitable Python runtime found`. Para instalar a versão, use https://www.python.org/downloads/; ou utilize uma versão Python instalada e compatível, como 3.13, validando as dependências e os testes.

**Para não depender de uma versão específica**, os próximos comandos utilizam `py -m venv .venv`, que escolhe o Python padrão disponível no launcher. Confira o resultado de `py --list-paths` antes de seguir.

### 8.2. Inicie somente banco e RabbitMQ no Docker

Abra o PowerShell na **raiz** `CulturaPass_N3` e execute:

```powershell
docker compose up -d db rabbitmq
docker compose ps
```

**Não use `docker compose up -d` sem especificar os serviços neste modo**, pois ele também iniciaria o backend e o frontend containerizados.

### 8.3. Prepare o backend Python

Abra um **segundo terminal** na pasta `CulturaPass_N3\backend` e execute **um comando por vez**:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
```

**Por que não há `Activate.ps1`?** Invocar `.\.venv\Scripts\python.exe` diretamente dispensa a ativação do ambiente virtual e evita problemas com a política de execução do PowerShell. Todas as dependências serão instaladas no `.venv`, e não no Python global.

Confira que o interpretador está correto:

```powershell
.\.venv\Scripts\python.exe -c "import sys; print(sys.executable)"
```

O caminho exibido deve terminar em `backend\.venv\Scripts\python.exe`.

### 8.4. Configure o ambiente do backend

Ainda dentro de `backend`, verifique se o `.env` existe:

```powershell
Test-Path .\.env
```

Se o resultado for `False`, crie-o com:

```powershell
Copy-Item .\.env.example .\.env
```

Agora abra o arquivo **`backend/.env`** e confira:

```dotenv
DATABASE_URL=postgresql+psycopg://culturapass:culturapass_apenas_ambiente_local@localhost:5438/culturapass
SECRET_KEY=substituir-por-uma-chave-local-aleatoria
SESSION_COOKIE_SECURE=false
RABBITMQ_URL=amqp://culturapass:rabbit_dev_local@localhost:5672/%2F
```

Os valores de usuário/senha no exemplo correspondem **somente** ao `.env` de demonstração do pacote. Se mudou o `.env` da raiz antes de inicializar os containers, ajuste o `backend/.env` para usar as mesmas credenciais. `localhost:5438` é o acesso ao PostgreSQL **a partir do Windows**, diferente do endereço interno `db:5432` utilizado pelos containers. O RabbitMQ local fica em `localhost:5672`.

Gere uma chave local aleatória para `SECRET_KEY`, se necessário:

```powershell
.\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_hex(32))"
```

Copie o resultado para `backend/.env`; não coloque a chave no repositório público.

### 8.5. Crie as tabelas e o administrador (uma vez)

Com o banco Docker funcionando e o `.env` configurado, execute no terminal de `backend`:

```powershell
.\.venv\Scripts\python.exe -m scripts.migrar
```

O resultado esperado inclui `Migração concluída sem apagar registros existentes.`. Esse comando cria as tabelas e aplica os índices necessários.

**Se ainda não existir um administrador nesse banco**, execute:

```powershell
.\.venv\Scripts\python.exe -m scripts.criar_admin
```

O script solicita e-mail e senha no terminal. **Não execute novamente para a mesma conta.** Se você já iniciou o Compose completo no mesmo banco, o bootstrap administrativo pode ter criado a conta automaticamente.

### 8.6. Inicie o backend

No mesmo terminal de `backend`:

```powershell
.\.venv\Scripts\python.exe app.py
```

Ele deverá iniciar em **http://127.0.0.1:5000**. Mantenha esse terminal aberto enquanto utilizar o sistema.

Confirme a saúde em outro terminal:

```powershell
Invoke-RestMethod http://127.0.0.1:5000/api/health
```

### 8.7. Inicie os workers em terminais separados

Abra **dois outros terminais**, ambos na pasta `backend`:

**Terminal do publicador:**

```powershell
.\.venv\Scripts\python.exe -m workers.publicador
```

**Terminal do consumidor:**

```powershell
.\.venv\Scripts\python.exe -m workers.consumidor
```

Mantenha ambos abertos. Eles usam `RABBITMQ_URL` configurada no `backend/.env`.

### 8.8. Inicie o frontend

Abra mais um terminal na pasta `CulturaPass_N3\frontend`:

```powershell
npm install
npm run dev
```

O terminal informará a URL de desenvolvimento do Vite, normalmente **http://localhost:5173**. O proxy do `frontend/vite.config.js` encaminha `/api` para o Flask em `http://127.0.0.1:5000`.

**Resultado:** o frontend e o Flask estão rodando no Windows, enquanto PostgreSQL e RabbitMQ estão no Docker. Esse modo serve para desenvolvimento, mas **não substitui a demonstração de `docker compose up --build -d` exigida pela carta C5**.

### 8.9. Como encerrar o modo local

Pressione `Ctrl+C` nos terminais do Flask, publicador, consumidor e Vite. Para parar banco e RabbitMQ, na raiz do projeto:

```powershell
docker compose stop
```

Não é necessário recriar o ambiente virtual, instalar dependências nem executar migração a cada inicialização. Nas próximas vezes, basta ligar banco/broker e executar os programas já instalados.

---

## 9. Login e papéis

| Perfil | Permissões |
|---|---|
| ADMIN | CRUD de eventos, clientes, funcionários e ingressos, além de consulta de notificações |
| FUNCIONARIO | Consultar clientes, criar/editar eventos, comprar ingresso para cliente existente, consultar ingressos |
| CLIENTE | Cadastro público, consulta de eventos, compra própria, consulta exclusiva de seus ingressos/notificações |

O backend usa `session` + CSRF para escritas autenticadas. O frontend obtém o token em login ou `/api/auth/me` e envia o cabeçalho `X-CSRF-Token`. APIs protegidas retornam 401 sem login e 403 com papel inadequado. Cookies são HttpOnly e SameSite=Lax. Nginx usa o mesmo domínio da interface para `/api`, não sendo necessário CORS aberto.

## 10. Endpoints e contratos JSON

Base via Nginx: `http://localhost:8080`. Endpoints estruturais das entidades possuem descrição, schemas e exemplos no Swagger/OpenAPI gerado automaticamente por Flask-Smorest.

| Método | Rota | Perfis autorizados | Função |
|---|---|---|---|
| POST | `/api/auth/cadastro` | Público | Criar cliente e conta CLIENTE |
| POST | `/api/auth/login` | Público | Autenticar e obter sessão/CSRF |
| GET | `/api/auth/me` | Logado | Identidade e token CSRF |
| POST | `/api/auth/logout` | Logado | Encerrar sessão |
| GET | `/api/eventos` | Logado | Listar com filtros/paginação |
| GET | `/api/eventos/{id}` | Logado | Detalhes e vagas |
| POST | `/api/eventos` | ADMIN/FUNCIONARIO | Cadastrar evento |
| PUT | `/api/eventos/{id}` | ADMIN/FUNCIONARIO | Editar evento |
| DELETE | `/api/eventos/{id}` | ADMIN | Excluir evento sem histórico |
| GET | `/api/clientes` | ADMIN/FUNCIONARIO | Listar com filtros/paginação |
| GET | `/api/clientes/{id}` | ADMIN/FUNCIONARIO | Consultar cliente |
| POST | `/api/clientes` | ADMIN | Cadastrar cliente com acesso |
| PUT | `/api/clientes/{id}` | ADMIN | Editar cliente |
| DELETE | `/api/clientes/{id}` | ADMIN | Excluir cliente sem ingressos/notificações |
| GET | `/api/ingressos` | Logado | Listar; CLIENTE vê apenas os próprios |
| GET | `/api/ingressos/{id}` | Logado | Detalhe; CLIENTE vê apenas o próprio |
| GET | `/api/clientes/{id}/ingressos` | Logado | Lista do cliente, restrita por papel |
| POST | `/api/ingressos` | Logado | Emitir 1 ingresso com R1/R2/R3 e outbox |
| PUT | `/api/ingressos/{id}` | ADMIN | Cancelar/reativar ingresso |
| DELETE | `/api/ingressos/{id}` | ADMIN | Excluir ingresso já cancelado |
| GET | `/api/notificacoes` | Logado | Últimos 50 eventos processados; cliente vê só os seus |
| GET | `/api/dados` | ADMIN | Listar funcionários |
| POST | `/api/funcionarios/novo` | ADMIN | Criar funcionário e credenciais |
| PUT | `/api/funcionarios/{id}` | ADMIN | Atualizar funcionário |
| PUT | `/api/funcionarios/{id}/acesso` | ADMIN | Trocar senha, ativar/desativar |
| DELETE | `/api/funcionarios/{id}` | ADMIN | Excluir funcionário |
| GET | `/api/health` | Público | Saúde básica da API |
| GET | `/api/openapi.json` | Público | OpenAPI gerada por schemas |
| GET | `/api/docs` | Público | Swagger UI |

### 10.1. Filtros e ordenação

`GET /api/eventos?page=1&perPage=10&q=festival&sort=dataHora&ordem=asc`

`GET /api/clientes?page=1&perPage=10&q=ana&sort=nome&ordem=asc`

`GET /api/ingressos?page=1&perPage=10&status=ATIVO&eventoId=1&sort=adquiridoEm&ordem=desc`

Padrão de saída paginada: `{"items": [...], "page": 1, "perPage": 10, "total": 3, "pages": 1}`. `page` deve ser >=1, `perPage` entre 1 e 100, e `sort` é validado em lista de campos permitidos.

### 10.2. Exemplos de requisição/resposta

**Criar conta pública:**

```http
POST /api/auth/cadastro
Content-Type: application/json

{"nome":"Ana Lima","email":"ana@example.com","telefone":"48999999999","senha":"SenhaSegura2026!"}
```

**Login:**

```http
POST /api/auth/login
Content-Type: application/json

{"email":"ana@example.com","senha":"SenhaSegura2026!"}
```

Resposta ilustrativa: `{"usuario":{"id":1,"nome":"Ana Lima","email":"ana@example.com","perfil":"CLIENTE","id_cliente":1,"id_funcionario":null,"ativo":true},"csrf_token":"TOKEN_GERADO_PELO_SERVIDOR"}`. Envie o cookie de sessão recebido e o token CSRF em toda operação POST/PUT/DELETE autenticada.

**Criar evento** (requer ADMIN ou FUNCIONARIO):

```http
POST /api/eventos
Content-Type: application/json
X-CSRF-Token: TOKEN_GERADO_PELO_SERVIDOR

{"nome":"Festival Cultural SATC","descricao":"Música e teatro","local":"Auditório SATC","dataHora":"2028-12-20T19:00:00","capacidadeMaxima":30}
```

Resposta `201` ilustrativa: `{"id":1,"nome":"Festival Cultural SATC","descricao":"Música e teatro","local":"Auditório SATC","dataHora":"2028-12-20T19:00:00","capacidadeMaxima":30,"ingressosVendidos":0,"ingressosDisponiveis":30}`.

**Adquirir um ingresso** (cliente autenticado, servidor preenche seu `clienteId`):

```http
POST /api/ingressos
Content-Type: application/json
X-CSRF-Token: TOKEN_GERADO_PELO_SERVIDOR

{"eventoId":1}
```

Resposta `201` ilustrativa: `{"id":1,"eventoId":1,"clienteId":1,"eventoNome":"Festival Cultural SATC","status":"ATIVO","adquiridoEm":"2026-11-24T12:00:00+00:00"}`. O evento `ingresso.emitido` é persistido no outbox na mesma transação da compra, e a notificação é criada **depois**, assincronamente.

**Atualizar ingresso** (ADMIN):

```http
PUT /api/ingressos/1
Content-Type: application/json
X-CSRF-Token: TOKEN_GERADO_PELO_SERVIDOR

{"status":"CANCELADO"}
```

**Atualizar evento** usa o mesmo JSON do POST em `PUT /api/eventos/1`. Para `DELETE` de eventos com ingressos, o backend devolve conflito, preservando o histórico.

### 10.3. Erros HTTP

| Status | Exemplo |
|---|---|
| 400 | `{"erro":"R1: ingressos esgotados para este evento."}` |
| 400 | `{"erro":"R2: não é possível comprar ingressos após o início do evento."}` |
| 400 | `{"erro":"R3: o cliente já possui 4 ingressos para este evento."}` |
| 400 | `{"erro":"Dados inválidos.","detalhes":{...}}` |
| 401 | `{"erro":"Sessão expirada. Faça login novamente."}` |
| 403 | `{"erro":"Você não tem permissão para realizar esta operação."}` |
| 404 | `{"erro":"Evento não encontrado."}` |
| 409 | `{"erro":"Evento com histórico de ingressos não pode ser excluído."}` |
| 500 | `{"erro":"Erro interno do servidor."}` — informação interna somente nos logs |

## 11. C5 — Arca: implementação e demonstração

`backend/Dockerfile` cria a imagem Flask e executa com Gunicorn. `frontend/Dockerfile` compila o React e serve com Nginx. `docker-compose.yml` sobe **aplicação inteira**, PostgreSQL, RabbitMQ, jobs de migração e os dois workers. Um comando `docker compose up --build -d` inicializa a aplicação de um banco vazio sem criação manual de tabelas ou execução extra de scripts.

Evidências de demonstração:

```powershell
docker compose ps
docker compose logs migrate
docker compose exec api python -c "import urllib.request; print(urllib.request.urlopen('http://localhost:5000/api/health').read())"
```

Detalhamento dos três critérios e o teste de uma instalação vazia: [C5_ARCA.md](docs/C5_ARCA.md).

## 12. Carta Secreta — Mensageiro Interestelar

**Fluxo técnico:** API grava `Ingresso` e `Outbox` no mesmo commit → publicador separado lê pendências → RabbitMQ recebe mensagem persistente com publisher confirms → consumidor separado materializa `Notificacao` e confirma com `ACK` → cliente consulta `/api/notificacoes`.

O produtor não é executado na requisição: mesmo se o RabbitMQ cair, a API segue recebendo compras, limitadas apenas pela saúde do PostgreSQL. Mensagens pendentes ficam no outbox e são publicadas após o retorno do broker. O consumidor rejeita falhas (`NACK`) para nova tentativa, e uma `chave_evento` única evita duplicidade.

Para demonstrar a independência:

```powershell
docker compose stop rabbitmq
docker compose ps
```

Faça uma compra pelo navegador enquanto o broker estiver parado: o ticket deve retornar `201` e o outbox manter `PENDENTE`. Depois:

```powershell
docker compose start rabbitmq
docker compose logs -f publicador consumidor
```

Atualize a tela **Notificações** para verificar a mensagem após o processamento. Veja [CARTA_SECRETA.md](docs/CARTA_SECRETA.md) para consultas SQL e critérios de aceite.

## 13. Testes automatizados

Com as dependências de `backend/requirements-dev.txt` instaladas:

```powershell
cd backend
python -m pytest -q
```

Cobertura planejada: login e CSRF, autorização por perfil, regras R1/R2/R3, contagem de vagas ao cancelar, DTOs, filtros/paginação, criação de outbox sem broker e idempotência do consumidor. A suíte usa SQLite isolado para fluxos funcionais; **não substitui o teste de concorrência PostgreSQL** nem a homologação de RabbitMQ real.

No frontend, execute `npm install` e `npm run build`. **Consulte `docs/RELATORIO_TESTES.md` para distinguir testes executados de testes pendentes.**

## 14. Limitações e observações de segurança

- A compra é simulada: não cobra dinheiro, não emite QR Code, não reserva assentos numerados e não envia e-mail.
- Os hashes do cliente permanecem duplicados em `cliente` e `usuario` por compatibilidade de migração; a verificação de login usa `usuario`.
- Não há CAPTCHA nem limitação distribuída de tentativas por IP no cadastro público. Login possui bloqueio temporário por conta após falhas.
- O controle R1 é protegido com `FOR UPDATE` no PostgreSQL; SQLite usado nos testes automatizados não oferece o mesmo bloqueio, de modo que um teste de concorrência real deve ser feito no Docker.
- Em caso de falha permanente de uma mensagem inválida, o consumidor reenvia para a fila; para produção recomenda-se fila de mensagens mortas (DLQ) e monitoramento.
- A interface Swagger utiliza assets do CDN configurado no Flask-Smorest e pode precisar de internet para a visualização, mas o JSON OpenAPI é servido pela API.
- Valores em `.env` são **exclusivamente locais e públicos por exigência acadêmica**; substitua senha e segredo antes de qualquer uso em rede ou produção. Para HTTPS, configure `SESSION_COOKIE_SECURE=true`, TLS e gestão de segredos externa.
- O banco antigo de estoque permanece preservado no volume antigo. A nova solução cria um **novo banco CulturaPass**, não converte produtos/pedidos antigos em eventos/ingressos fictícios.

## 15. Entrega e apresentação

Na apresentação (15 minutos), sugere-se: explicar o problema e as regras R1/R2/R3, mostrar entidades/relações e DTOs, executar a compra do cliente, provar as permissões com dois perfis, demonstrar a carta C5 com `docker compose ps`, parar o RabbitMQ para demonstrar a Carta Secreta, mostrar o OpenAPI e a matriz de conformidade.

Documentos de suporte: [Matriz de Conformidade](docs/MATRIZ_CONFORMIDADE.md), [Plano da Carta](docs/PLANO_CARTA.md), [C5](docs/C5_ARCA.md), [Carta Secreta](docs/CARTA_SECRETA.md), [Adaptação e migração](docs/ADAPTACAO_E_MIGRACAO.md) e [Relatório de testes](docs/RELATORIO_TESTES.md).

## Referências

- [Projeto N2: CulturaPass](https://github.com/Adriel-Inacio/TrabalhoN2BackEnd)
- [Flask-Smorest — OpenAPI](https://flask-smorest.readthedocs.io/en/latest/openapi.html)
- [Pika — Publisher Confirms](https://pika.github.io/pika/latest/examples/blocking_delivery_confirmations/)
