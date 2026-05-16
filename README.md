# Projeto Flask MVC

Este é um projeto base de uma aplicação web desenvolvida em Python e Flask, estruturada com o padrão de arquitetura **MVC** (Model-View-Controller).

## Tecnologias

- **Python 3.12**
- **Flask**: Microframework web
- **Flask-SQLAlchemy**: ORM (Object-Relational Mapping)
- **Flask-Migrate** (Alembic): Gerenciamento de migrações do banco de dados
- **Flask-Caching**: Cache in-memory (SimpleCache, TTL 5min) para APIs de gráficos
- **Jinja2**: Motor de templates nativo do Flask
- **Bootstrap 5**: Framework CSS para interface visual (carregado via CDN)
- **SQLite**: Banco de dados relacional padrão (fácil para desenvolvimento)
- **Docker & Docker Compose**: Para empacotamento e execução isolada
- **Replit**: Compatibilidade out-of-the-box (`.replit` e `replit.nix`)

## Estrutura de Pastas (MVC)

A aplicação está contida no pacote `app`:

```
projeto-desen-web/
├── app/                  # Diretório principal da aplicação
│   ├── models/           # MODEL: Classes de banco de dados (User, WorkOrder, ...)
│   ├── controllers/      # CONTROLLER: Lógica de negócio e rotas (Blueprints)
│   │   ├── work_order_controller.py  # UC1–UC5 (autenticado)
│   │   ├── tracking_controller.py    # UC9–UC10 (público, sem login)
│   │   ├── report_controller.py      # UC6–UC7 + cache de APIs
│   │   └── auth_controller.py        # UC11 — Login/Logout
│   ├── templates/        # VIEW: Arquivos HTML renderizados pelo Jinja2
│   │   ├── tracking/     # Módulo público de rastreamento (base_public.html)
│   │   └── ...           # Demais módulos
│   ├── static/           # Arquivos estáticos (CSS, JS, Imagens)
│   ├── config.py         # Configurações de ambiente (incl. CACHE_TYPE)
│   ├── extensions.py     # Inicialização das extensões (db, migrate, cache)
│   └── __init__.py       # Factory de criação do aplicativo
├── migrations/           # Histórico de migrações (Gerado pelo Flask-Migrate)
├── tests/                # Suíte de testes automatizados (132 testes, 96% cobertura)
├── docs/                 # Documentação (requisitos, specs, refactor.md)
├── requirements.txt      # Dependências Python
├── docker-compose.yml    # Orquestração Docker
├── Dockerfile            # Imagem Docker
├── .env.example          # Template de variáveis de ambiente
├── .gitignore            # Arquivos ignorados pelo Git
└── run.py                # Arquivo principal para inicializar o servidor
```

## Como Rodar Localmente

### 1. Criar o Ambiente Virtual

Abra um terminal na pasta raiz e instale as dependências:

```bash
python -m venv venv
source venv/bin/activate       # Linux/Mac
# ou venv\Scripts\activate     # Windows

pip install -r requirements.txt
```

### 2. Configurar Variáveis de Ambiente

Crie o arquivo `.env` copiando o de exemplo:

```bash
cp .env.example .env
```

### 3. Banco de Dados e Migrações (Flask-Migrate)

O Flask-Migrate gerencia as mudanças no banco.

```bash
# 1. Inicializar diretório de migrações (se /migrations ainda não existir)
flask db init

# 2. Criar a primeira migração (Gera o arquivo baseado em models/user.py)
flask db migrate -m "Criando tabela de usuários"

# 3. Aplicar a migração no banco de dados (Cria o app.db)
flask db upgrade
```

### 4. Gerenciamento de Usuários (CLI)

O projeto possui comandos de linha de comando para gerenciar o sistema. Você pode criar novos usuários diretamente pelo terminal:

```bash
flask create-user "Nome do Usuário" "email@exemplo.com" "senha123"
```

### 5. Executar Servidor

```bash
python run.py
```
Acesse: [http://localhost:5000](http://localhost:5000)

## Como Rodar com Docker

Para usar Docker, basta rodar o Docker Compose:

```bash
docker compose up -d --build
```
A aplicação estará disponível em `http://localhost:5000`.

> [!NOTE]
> **Permissões no Linux:** O `docker-compose.yml` está configurado para passar o seu UID e USER atuais para o container. Isso garante que os arquivos criados pelo banco de dados ou pela aplicação dentro do volume vinculado pertençam ao seu usuário no host, evitando problemas de permissão (arquivos pertencentes ao root).

**Atenção:** Se for a primeira vez, será necessário rodar as migrações dentro do container para criar o banco de dados.
```bash
docker compose exec web flask db upgrade
```

Para criar um usuário dentro do container:
```bash
docker compose exec web flask create-user "Nome" "email@exemplo.com" "senha"
```

## Como Executar os Testes

O projeto possui uma suíte de **132 testes automatizados** com cobertura de 96%. Para mais detalhes, consulte o [Plano de Testes](docs/testing.md).

### Via Docker Compose (Recomendado)

```bash
# Executar toda a suíte de testes
docker compose exec web python -m pytest tests/ -v --tb=short

# Executar com relatório de cobertura
docker compose exec web python -m pytest tests/ --cov=app --cov-report=term-missing

# Executar um módulo específico
docker compose exec web python -m pytest tests/test_work_order_controller.py -v

# Executar um teste específico
docker compose exec web python -m pytest tests/test_models.py::TestStatusTransitions -v
```

> [!NOTE]
> O container precisa estar em execução (`docker compose up -d`) antes de rodar os testes.

### Via Ambiente Virtual Local

```bash
source venv/bin/activate
pip install -r requirements.txt
pytest tests/ -v --tb=short
```

## Como Rodar no Replit

Ao importar este repositório no Replit:
1. O Replit detectará automaticamente o ambiente pelo `replit.nix` e `.replit`.
2. Acesse a aba **Shell** e rode o comando de migração: `flask db upgrade`
3. Clique no botão de "Run" na interface web.
