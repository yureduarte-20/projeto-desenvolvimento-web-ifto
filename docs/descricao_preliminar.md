# Descrição Preliminar do Projeto

## 1. Visão Geral
Este projeto consiste em uma aplicação web estruturada sob o padrão de arquitetura **MVC** (Model-View-Controller). O sistema foi concebido para possuir uma base sólida e escalável, contando com gerenciamento de usuários, sistema de testes com alta cobertura e fácil configuração de ambiente através de contêineres.

## 2. Equipe
*As definições de equipe podem ser ajustadas conforme o andamento do projeto.*
- **Desenvolvedor / Líder Técnico:** Yure (conforme identificação do ambiente de trabalho)

## 3. Estrutura Lógica
A aplicação adota uma organização em módulos e blueprints baseada em MVC, encapsulada no diretório principal `app/`:
- **Model (`app/models/`):** Camada de dados que mapeia objetos de negócio para tabelas relacionais utilizando o ORM SQLAlchemy (ex: Entidade `User`, ordens de serviço, etc).
- **View (`app/templates/` & `app/static/`):** Interface com o usuário renderizada no lado do servidor utilizando o motor de templates **Jinja2** e estilização via **Bootstrap 5** carregado por CDN.
- **Controller (`app/controllers/`):** Concentra a lógica de negócios e o roteamento das requisições web utilizando Flask Blueprints. Responsável por conectar as Views aos Models.

## 4. Tecnologias
As tecnologias selecionadas visam produtividade e estabilidade, formando uma stack moderna baseada em Python:
- **Linguagem Principal:** Python 3.12
- **Microframework:** Flask 3.1.0
- **Segurança e Autenticação:** Flask-Login, Flask-Bcrypt, Flask-WTF (para validação de formulários).
- **Persistência de Dados:** SQLite (para facilidade no desenvolvimento local) e compatibilidade com PostgreSQL (via `psycopg2-binary`).
- **ORM e Migrações:** Flask-SQLAlchemy (ORM) e Flask-Migrate (Alembic) para versionamento do esquema de banco de dados.
- **Garantia de Qualidade:** Ampla suíte de testes (124 testes) rodando via Pytest, com suporte de Faker e Factory-Boy.

## 5. Infraestrutura
O projeto conta com múltiplas estratégias para deploy e execução em ambientes distintos:
- **Local (Bare-metal):** Uso de ambientes virtuais (`venv`) para instalação e execução local isolada.
- **Containerização:** Uso de **Docker** e **Docker Compose** (`Dockerfile` e `docker-compose.yml` / `docker-compose.prod.yml`) para garantir que a aplicação rode de maneira uniforme em qualquer ambiente de hospedagem.
- **Cloud IDE:** Integração nativa com a plataforma **Replit** (via configurações `.replit` e `replit.nix`).
- **Automação:** Presença de scripts utilitários (`deploy.sh`, `trigger.sh`) que facilitam processos de deploy e CI/CD.
