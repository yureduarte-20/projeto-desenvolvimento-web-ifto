# Especificações do Sistema (03-Specs)

## 1. Resumo dos Documentos Anteriores

### Documento de Visão
O sistema **EletroService** é uma plataforma web para gestão do ciclo de vida de Ordens de Serviço (OS), desde a triagem até a entrega. O grande diferencial é o **Módulo de Transparência ao Cliente**, permitindo que clientes não autenticados acompanhem o status da sua manutenção em tempo real por meio de um código de rastreamento. Os atores principais são o Administrador (parametrização e gestão) e o Usuário Comum/Cliente (consulta de rastreio).

### Requisitos Funcionais
As necessidades do sistema estão divididas em:
- **Manutenção das OS (Crítico):** Abertura, edição, atualização de status, consulta/listagem e exclusão/cancelamento de OS pelo Administrador.
- **Relatórios (Importante):** Relatórios detalhados de entrada/saída e Dashboard com gráficos de produtividade.
- **Transparência ao Cliente (Crítico):** Geração automática de código de rastreio único na abertura da OS, consulta do status atual e visualização da linha do tempo da manutenção pelo cliente sem necessidade de autenticação.

### Casos de Uso
11 Casos de Uso (UC) principais divididos em duas áreas de acesso:
- **Administrativa (Autenticada):** Cadastrar OS, Editar OS, Atualizar Status da OS, Consultar/Listar OS, Cancelar OS, Gerar Relatórios, Visualizar Dashboard e Fazer Login. Ações de cadastro (UC1) e atualização de status (UC3) incluem a funcionalidade automatizada do sistema de gerar código e registrar histórico (UC8).
- **Transparência (Pública):** Consultar Status por Código de Rastreamento (UC9) com a extensão opcional para Visualizar a Linha do Tempo (UC10).

### Diagrama de Entidade-Relacionamento (DER)
As principais entidades estruturais mapeadas são:
- `users`: Usuários administrativos do sistema (id, nome, email, senha).
- `requesters`: Clientes/solicitantes dos reparos (id, nome, email, telefone, documento, atrelados ao user_id).
- `work_orders`: Ordens de serviço propriamente ditas, com informações financeiras e técnicas da OS, e contendo o campo vital `public_id` (código de rastreio).
- `history_orders`: Tabela dependente vinculada a `work_orders` que consolida o histórico de transições de status da OS, armazenando o status antigo, novo status, datas e descrições.

### Fluxo de Status
O ciclo de vida da Ordem de Serviço na máquina de estados compreende o seguinte fluxo lógico e restritivo: 
`Em Orçamento` -> `Em Manutenção` -> `Aguardando Pagamento` -> `Aguardando Retirada` -> `Finalizado`. 
O encerramento prematuro para o estado `Cancelado` pode ser acionado a partir das etapas "Em Orçamento" ou "Em Manutenção".

---

## 2. Estrutura de Pastas e Tecnologias

### Tecnologias
De acordo com o `README.md` oficial do projeto, o stack atual baseia-se em:
- **Linguagem:** Python 3.12
- **Framework Web:** Flask
- **Padrão de Arquitetura:** MVC (Model-View-Controller)
- **Banco de Dados Relacional:** SQLite (com ORM Flask-SQLAlchemy)
- **Migrações:** Flask-Migrate (Alembic)
- **Front-end / Views:** Jinja2 Template Engine e Bootstrap 5 (via CDN)
- **Ambiente de Execução:** Suporte nativo ao Docker & Docker Compose, além de otimizações para Replit (`replit.nix`).
- **Testes:** Pytest (com cobertura implementada).

### Estrutura de Pastas
```text
projeto-desen-web/
├── app/                  # Aplicação base - Módulo principal
│   ├── models/           # MODEL: Definição de tabelas com SQLAlchemy
│   ├── controllers/      # CONTROLLER: Regras de negócio e Blueprints do Flask
│   ├── templates/        # VIEW: Arquivos e layouts HTML renderizados via Jinja2
│   ├── static/           # Arquivos estáticos puros (CSS custom, JS, Imagens)
│   ├── config.py         # Módulo de parametrizações e variáveis
│   ├── extensions.py     # Inicializadores em container de injeção (db, migrate)
│   └── __init__.py       # Factory pattern do Flask
├── migrations/           # Histórico transacional do schema de banco
├── tests/                # Suíte de testes automatizados unitários/integração
├── docs/                 # Documentação (Requisitos, UML, Specs)
├── requirements.txt      # Mapeamento de dependências Python
├── docker-compose.yml    # Manifesto de orquestração local (Docker)
├── Dockerfile            # Configuração de imagem container
├── .env.example          # Modelo de environment local
└── run.py                # Ponto de entrada de execução web (WSGI)
```

---

## 3. Especificação (Spec)

Abaixo estão detalhadas as especificações com base na arquitetura descrita e nos artefatos da engenharia de requisitos.

    /app/models/work_order.py
    - ação: modificar
    - descrição: Definição da tabela WorkOrder para o banco de dados via SQLAlchemy e incorporação do gerador de rastreamento.
    - pseudocódigo:
        Declarar Classe WorkOrder herdando de db.Model:
            Definir colunas da entidade 'work_orders' (id PK, date, status, requester_id FK, public_id, etc.) conforme DER
            
            Criar método de instância generate_public_id():
                Se o atributo public_id atual for nulo ou string vazia:
                    Gerar string aleatória segura em formato alfanumérico com prefixo (ex: 'ELE-' + uuid curto)
                    Atribuir a string gerada ao atributo public_id
                    Retornar a string gerada

    /app/models/history_order.py
    - ação: criar
    - descrição: Definição da tabela para armazenar de forma imutável a linha do tempo técnica.
    - pseudocódigo:
        Declarar Classe HistoryOrder herdando de db.Model:
            Definir colunas da entidade 'history_orders' (id PK, old_status, new_status, description, changed_at, work_order_id FK) conforme DER
            
            Criar método estático save_transition(work_order_id, old_status, new_status, description):
                Instanciar objeto HistoryOrder
                Atribuir os parâmetros aos atributos do objeto
                Definir changed_at como o timestamp em UTC corrente
                Adicionar objeto na sessão do banco (db.session.add)
                Efetivar persistência (db.session.commit)

    /app/controllers/work_order_controller.py
    - ação: modificar
    - descrição: Cadastro de OS (UC1). Cria Requester se não existir, instancia WorkOrder,
      chama generate_public_id() e registra histórico via save_transition(). Commit único e atômico.
    - pseudocódigo:
        @work_order_bp.route('/nova', methods=['GET', 'POST'])
        @login_required
        Função create():
            Validar formulário (WorkOrderForm)
            requester = Buscar por email; criar se não existir
            db.session.flush()  # gera requester.id sem commit

            work_order = WorkOrder(requester_id, description, status='Em Orçamento')
            work_order.generate_public_id()
            db.session.add(work_order)
            db.session.flush()  # gera work_order.id

            HistoryOrder.save_transition(work_order.id, None, 'Em Orçamento', 'Abertura da Ordem de Serviço')
            db.session.commit()  # commit único e atômico

    /app/controllers/work_order_controller.py
    - ação: modificar
    - descrição: Edição e transição de status (UC2, UC3, UC5). STATUS_TRANSITIONS define
      as transições válidas. save_transition() registra historico; commit único no final.
    - pseudocódigo:
        @work_order_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
        @login_required
        Função edit(id):
            order = WorkOrder.query.get_or_404(id)
            config = STATUS_TRANSITIONS[order.status]
            is_terminal = config.next is None and not config.can_cancel

            Se form.validate_on_submit() e não is_terminal:
                action = request.form.get('action')  # 'save' | 'advance' | 'cancel'
                old_status = order.status

                Se action == 'advance' e config.next:
                    order.status = config.next
                    Se novo status == 'Finalizado': order.delivered_at = now()

                Se action == 'cancel' e config.can_cancel:
                    order.status = 'Cancelado'
                    order.is_canceled = True
                    order.cancelation_reason = form.cancelation_reason.data

                Se houve mudança de status ou nota:
                    HistoryOrder.save_transition(order.id, old_status, new_status, desc)

                db.session.commit()  # commit único e atômico

    /app/controllers/report_controller.py
    - ação: modificar
    - descrição: Helper _parse_date_range() elimina duplicação. @cache.cached(timeout=300)
      nas APIs de gráficos evita recálculo por 5 minutos (SimpleCache in-memory).
    - pseudocódigo:
        def _parse_date_range(req):
            Ler 'start_date' e 'end_date' dos query params
            Aplicar padrão de 30 dias se ausentes ou inválidos
            end_date.replace(hour=23, minute=59, second=59)
            Retornar (start_date, end_date)

        @bp.route('/api/status-data')
        @login_required
        @cache.cached(timeout=300, key_prefix='api_status_data')
        Função api_status_data():
            Consultar WorkOrder agrupado por status
            Retornar JSON para gráfico de pizza (Chart.js)

        @bp.route('/api/daily-data')
        @login_required
        @cache.cached(timeout=300, key_prefix='api_daily_data')
        Função api_daily_data():
            Consultar WorkOrder agrupado por dia (últimos 7 dias)
            Preencher dias sem OS com count=0
            Retornar JSON para gráfico de linha (Chart.js)

    /app/controllers/tracking_controller.py
    - ação: criar
    - descrição: Endpoint público UC9/UC10. Sem @login_required. Código via query param.
      Retorna index.html (formulário) ou result.html (status + timeline).
    - pseudocódigo:
        Blueprint tracking, url_prefix='/rastreio'

        @tracking_bp.route('/search')  # GET, sem @login_required
        Função search():
            code = request.args.get('code', '').strip()

            Se code vazio:
                Renderizar tracking/index.html (formulário)

            work_order = WorkOrder.query.filter_by(public_id=code).first()

            Se work_order é None:
                Renderizar tracking/index.html com mensagem de erro

            history = sorted(work_order.history, key=changed_at, reverse=True)
            Renderizar tracking/result.html com work_order e history

    /app/templates/base_public.html
    - ação: criar
    - descrição: Layout base para área pública (Bootstrap 5, navbar mínima, sem sidebar admin).

    /app/templates/tracking/index.html
    - ação: criar
    - descrição: Formulário GET com campo 'code' (UC9). Exibe alerta de erro se código inválido.
    - pseudocódigo:
        Estender base_public.html
        <form method="GET" action="/rastreio/search">
            <input type="text" name="code" required>
            <button type="submit">Rastrear Minha OS</button>

    /app/templates/tracking/result.html
    - ação: criar
    - descrição: Exibe status atual com badge colorido (UC9) e linha do tempo (UC10).
    - pseudocódigo:
        Estender base_public.html
        Exibir work_order.number e work_order.public_id
        Badge colorido conforme work_order.status (if/elif/else Jinja2)
        Para cada item em history (decrescente):
            Exibir item.changed_at formatado
            Exibir "Alterado para: item.new_status"
            Se item.description não vazio: exibir observação

## 4. Especificações de Frontend

### 4.1 Comportamento Visual e Cores
O design system deve garantir a consistência de cores usando o "teorema das cores", com foco no contraste:
- **Cor Primária:** Azul (ex: `#0a58ca`) para identificar ações principais.
- **Cor de Destaque (Accent):** Laranja (ex: `#fd7e14`) para alertas, chamadas secundárias e indicações de atenção na timeline.
- **Contraste:** Garantir que textos sobre fundos coloridos sejam legíveis, preferencialmente `text-white` ou escuro onde for claro.

### 4.2 Componentes de Interface e Estados
- **Loading / Skeleton:** Durante requisições pesadas ou submissões de formulário, botões devem ser desabilitados (`disabled`) e exibir um *spinner* ou classe `.btn-loading`. Se necessário (via manipulação DOM posterior), usar `.skeleton` para carregamento de listas.
- **Empty States (Estados Vazios):** Listagens (Ordens de Serviço, Usuários) que retornarem vazias devem mostrar um *Empty State* claro, com um ícone, texto descritivo e, preferencialmente, um call-to-action (ex: botão "Nova OS").
- **Validações Visuais e Feedback:** Formulários devem usar classes do Bootstrap (`.is-invalid`, `.is-valid`) combinadas com mensagens `<div class="invalid-feedback">`.

### 4.3 Responsividade e Acessibilidade
- **Responsividade:** Layout deve se adaptar perfeitamente em: Desktop (`>992px`), Tablet (`768px-991px`) e Mobile (`<768px`). Tabelas devem possuir scroll horizontal em telas pequenas.
- **Acessibilidade Básica:**
  - Presença de *Skip Link* (`#skip-link`) nos templates base para navegação por teclado.
  - Campos de input com labels explícitas (`for` attribute) ou `aria-label`.
  - Controle de foco visível (já mapeado no `style.css` via `:focus-visible`).
  - Uso de atributos `aria-invalid` e `aria-describedby` para erros em formulários.

### 4.4 Tratamento de Falhas (Fallback)
- **Mensagens de Erro:** Em caso de inputs incorretos ou código de rastreamento inexistente (UC9), a interface não deve redirecionar para uma página genérica 404/500 se o usuário puder corrigir. Exibir a mensagem na própria view de busca ou via `flash` messages em telas autenticadas.
