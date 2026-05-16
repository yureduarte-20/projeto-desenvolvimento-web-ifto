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
    - descrição: Criação de endpoint para receber requisição de cadastro da OS, efetivar a persistência e engatilhar primeiro histórico.
    - pseudocódigo:
        Declarar Blueprint work_order_bp
        
        @work_order_bp.route('/create', methods=['POST'])
        @login_required
        Função create_work_order():
            Ler carga útil do formulário enviado no request
            Validar dados obrigatórios (requester_id, description)
            
            Instanciar WorkOrder com status forçado para 'Em Orçamento' e atributos fornecidos
            Chamar método work_order.generate_public_id()
            Salvar WorkOrder no banco de dados e dar commit
            
            Recuperar o work_order.id recém inserido
            Chamar HistoryOrder.save_transition(work_order.id, Null, 'Em Orçamento', 'Ordem de serviço aberta na triagem')
            
            Disparar flash message visual de sucesso
            Redirecionar HTTP para a rota de visualização/listagem de OS

    /app/controllers/work_order_controller.py
    - ação: modificar
    - descrição: Manipulador para atualização de status, com forte validação na máquina de estados antes da persistência.
    - pseudocódigo:
        @work_order_bp.route('/<id>/update-status', methods=['POST'])
        @login_required
        Função update_work_order_status(id):
            Extrair 'novo_status' e opcional 'observacao' do request
            Buscar WorkOrder no banco utilizando id
            Abortar com erro 404 se não existir
            
            estado_atual = work_order.status
            Definir dicionário com transições válidas:
                'Em Orçamento': ['Em Manutenção', 'Cancelado']
                'Em Manutenção': ['Aguardando Pagamento', 'Cancelado']
                'Aguardando Pagamento': ['Aguardando Retirada']
                'Aguardando Retirada': ['Finalizado']
            
            Se 'novo_status' não existir na lista de transições permitidas para estado_atual:
                Retornar erro de validação ("Transição de status não permitida")
                
            work_order.status = novo_status
            Se novo_status for igual a 'Cancelado':
                work_order.is_canceled = True
                work_order.cancelation_reason = observacao
                
            Persistir alterações em work_order (db.session.commit())
            Chamar HistoryOrder.save_transition(work_order.id, estado_atual, novo_status, observacao)
            
            Disparar flash message visual informando mudança de status
            Redirecionar HTTP para página de detalhes da Ordem de Serviço atualizada

    /app/controllers/tracking_controller.py
    - ação: criar
    - descrição: Implementação do endpoint de transparência pública. Não requer autenticação de login.
    - pseudocódigo:
        Declarar Blueprint tracking_bp
        
        @tracking_bp.route('/search', methods=['GET'])
        Função search_tracking():
            Ler query parameter 'code' do request (GET)
            
            Se 'code' for vazio:
                Renderizar template 'tracking/index.html' com mensagem de erro "Insira o código."
                
            work_order = Buscar objeto da tabela WorkOrder com filtro (public_id == 'code')
            
            Se work_order não for encontrado:
                Renderizar template 'tracking/index.html' com mensagem "OS não encontrada."
                
            history = Buscar objetos da tabela HistoryOrder vinculados a work_order.id, com ordenação descending por changed_at
            
            Retornar render_template apontando para 'tracking/result.html', repassando os objetos work_order e history no contexto.

    /app/templates/tracking/index.html
    - ação: criar
    - descrição: Página de entrada do tracking (landing page do cliente), onde digita o código único que recebeu.
    - pseudocódigo:
        Estender estrutura de "base_public.html"
        Construir contêiner centralizado Bootstrap na view
        Inserir bloco HTML <form> com método GET apontando action para '/tracking/search'
        Adicionar <input type="text" name="code" required> estilizado
        Adicionar <button type="submit"> contendo o texto "Rastrear Minha OS"

    /app/templates/tracking/result.html
    - ação: criar
    - descrição: Página final que o cliente consome para ver situação (UC9) e linha do tempo (UC10) agregada.
    - pseudocódigo:
        Estender estrutura de "base_public.html"
        Montar cabeçalho exibindo variável "work_order.public_id"
        Aplicar lógica de if/else Jinja2 para atribuir badge Bootstrap de cor específica baseado em "work_order.status"
        
        Criar div de visualização da Linha do Tempo:
            Aplicar bloco for do Jinja2: "for item in history"
                Dentro do loop, renderizar item visual para cada evento
                Exibir data com formatação local: "item.changed_at|datetimeformat"
                Exibir "Alterado para: item.new_status"
                Se "item.description" for diferente de nulo e não for vazio:
                    Renderizar parágrafo exibindo "Observação: item.description"
            Finalizar bloco for
