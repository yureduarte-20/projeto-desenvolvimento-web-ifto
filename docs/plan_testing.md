# Plano de Testes — EletroService

**Versão:** 1.0
**Data:** 15/05/2026
**Autor:** Yure Samarone Gomes Duarte
**Referência:** `docs/testing.md`, `docs/Casos de Uso.md`, `docs/Requisitos Funcionais e Não funcionais.md`

---

## 1. Introdução

### 1.1 Propósito

Este documento define o **Plano de Testes** do sistema **EletroService**, uma aplicação web Flask para gestão do ciclo de vida de Ordens de Serviço (OS) em assistências técnicas. O plano consolida o que foi implementado, o que está pendente e como executar cada categoria de teste.

### 1.2 Escopo

O sistema é composto por:

- **Backend (Flask/Python):** 4 modelos, 5 controllers, 5 formulários, CLI
- **Frontend (Jinja2/Bootstrap 5):** Templates responsivos com Bootstrap
- **Banco de dados:** SQLite (dev) / PostgreSQL (prod)
- **Infraestrutura:** Docker + Docker Compose

### 1.3 Resultado da Última Execução

> Executado em: 15/05/2026 via `docker compose exec web python -m pytest tests/ -v --cov=app --cov-report=term-missing`

| Métrica | Valor |
|---|---|
| Total de testes | **124 passou** |
| Falhas | **0** |
| Avisos | 48 (LegacyAPIWarning — `Query.get()`) |
| Cobertura global | **94%** |
| Tempo de execução | 26,02s |

---

## 2. Documentos de Referência

| Documento | Conteúdo |
|---|---|
| `docs/Casos de Uso.md` | 11 casos de uso (UC1–UC11), diagrama, fluxos |
| `docs/Requisitos Funcionais e Não funcionais.md` | 10 requisitos (F1.1–F3.3) |
| `docs/DER.mermaid` | Diagrama Entidade-Relacionamento (4 entidades) |
| `docs/Fluxo de Status.mermaid` | Máquina de estados da OS (6 status, 7 transições) |
| `docs/testing.md` | Estratégia de testes, specs E2E, checklists |
| `docs/03-specs.md` | Especificações de frontend e design system |

---

## 3. Arquitetura de Testes

### 3.1 Pirâmide de Testes

```
        /\
       /  \     E2E / Frontend (Playwright) — ⬜ PENDENTE
      /----\
     /      \   Integração / Controller — ✅ 49 testes
    /--------\
   /          \ Unitários (Models + Forms) — ✅ 75 testes
  /____________\
```

### 3.2 Stack Atual

| Ferramenta | Versão | Finalidade | Status |
|---|---|---|---|
| pytest | 8.3.4 | Framework principal | ✅ Ativo |
| pytest-cov | 6.0.0 | Cobertura de código | ✅ Ativo |
| pytest-flask | 1.3.0 | Integração com Flask | ✅ Ativo |
| factory-boy | 3.3.1 | Fábricas de dados | ✅ Ativo |
| faker | 33.3.1 | Dados falsos | ✅ Ativo |
| Playwright | 1.40+ | Testes E2E | ⬜ Pendente |
| axe-playwright-python | 4.8+ | Acessibilidade | ⬜ Pendente |

### 3.3 Configuração de Isolamento

```python
class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # banco em memória
    WTF_CSRF_ENABLED = False                         # CSRF desabilitado
    SERVER_NAME = 'localhost'
```

- Cada teste usa banco limpo (`create_all` / `drop_all` por função)
- Fixtures reutilizáveis em `tests/conftest.py`
- Autenticação via fixture `authenticated_client`

---

## 4. Casos de Teste por Módulo

### 4.1 Modelos (tests/test_models.py) — 36 testes ✅

#### 4.1.1 TestUserModel (5 testes)

| ID | Nome do Teste | Pré-condição | Resultado Esperado | Status |
|---|---|---|---|---|
| TM-U01 | `test_criar_usuario` | Banco vazio | Usuário criado com `id`, `name`, `email`, `created_at` | ✅ |
| TM-U02 | `test_set_password_gera_hash` | Banco vazio | `password_hash` diferente da senha em texto | ✅ |
| TM-U03 | `test_check_password_valida_corretamente` | Usuário com senha | `True` para senha correta, `False` para errada | ✅ |
| TM-U04 | `test_repr_usuario` | Usuário criado | `<User email@teste.com>` | ✅ |
| TM-U05 | `test_user_mixin_is_authenticated` | `sample_user` fixture | `is_authenticated == True` | ✅ |

#### 4.1.2 TestRequesterModel (5 testes)

| ID | Nome do Teste | Resultado Esperado | Status |
|---|---|---|---|
| TM-R01 | `test_criar_requester` | Requester criado com todos os campos | ✅ |
| TM-R02 | `test_requester_user_opcional` | `user_id` e `user` são `None` | ✅ |
| TM-R03 | `test_requester_relacionamento_user` | Relação com User válida | ✅ |
| TM-R04 | `test_requester_relacionamento_work_orders` | Lista de `work_orders` acessível | ✅ |
| TM-R05 | `test_repr_requester` | `<Requester email>` | ✅ |

#### 4.1.3 TestWorkOrderModel (10 testes) — UC8

| ID | Nome do Teste | Requisito | Status |
|---|---|---|---|
| TM-WO01 | `test_criar_ordem_status_padrao` | F1.1 | ✅ |
| TM-WO02 | `test_geracao_automatica_number` | F3.1 — formato `OS-YYYYMMDD-XXXX` | ✅ |
| TM-WO03 | `test_geracao_automatica_public_id` | F3.1 — UUID 36 chars | ✅ |
| TM-WO04 | `test_unicidade_number` | F3.1 | ✅ |
| TM-WO05 | `test_unicidade_public_id` | F3.1 | ✅ |
| TM-WO06 | `test_relacionamento_requester` | DER | ✅ |
| TM-WO07 | `test_relacionamento_history` | UC10 | ✅ |
| TM-WO08 | `test_cascade_delete_history` | Integridade referencial | ✅ |
| TM-WO09 | `test_campos_financeiros_opcionais` | UC2 | ✅ |
| TM-WO10 | `test_campos_cancelamento_padrao` | UC5 | ✅ |

#### 4.1.4 TestHistoryOrderModel (4 testes) — UC10

| ID | Nome do Teste | Resultado Esperado | Status |
|---|---|---|---|
| TM-H01 | `test_criar_historico_inicial` | `old_status=None`, `new_status='Em Orçamento'` | ✅ |
| TM-H02 | `test_historico_registra_timestamp` | `changed_at` preenchido | ✅ |
| TM-H03 | `test_criar_historico_com_transicao` | `old_status` e `new_status` corretos | ✅ |
| TM-H04 | `test_repr_historico` | `<HistoryOrder id (OS id)>` | ✅ |

#### 4.1.5 TestStatusTransitions (12 testes) — UC3/UC5

| ID | Transição | Regra | Status |
|---|---|---|---|
| TM-ST01 | Contém todos os 6 status | `STATUS_TRANSITIONS.keys()` | ✅ |
| TM-ST02 | Em Orçamento → Em Manutenção (T2) | `next == 'Em Manutenção'` | ✅ |
| TM-ST03 | Em Orçamento permite cancelar (T3) | `can_cancel == True` | ✅ |
| TM-ST04 | Em Manutenção → Aguardando Pagamento (T4) | `next == 'Aguardando Pagamento'` | ✅ |
| TM-ST05 | Em Manutenção permite cancelar (T5) | `can_cancel == True` | ✅ |
| TM-ST06 | Aguardando Pagamento → Aguardando Retirada (T6) | `next == 'Aguardando Retirada'` | ✅ |
| TM-ST07 | Aguardando Pagamento NÃO cancela | `can_cancel == False` | ✅ |
| TM-ST08 | Aguardando Retirada → Finalizado (T7) | `next == 'Finalizado'` | ✅ |
| TM-ST09 | Aguardando Retirada NÃO cancela | `can_cancel == False` | ✅ |
| TM-ST10 | Finalizado sem próximo (terminal) | `next == None` | ✅ |
| TM-ST11 | Finalizado NÃO cancela | `can_cancel == False` | ✅ |
| TM-ST12 | Cancelado sem próximo (terminal) | `next == None`, `can_cancel == False` | ✅ |

---

### 4.2 Formulários (tests/test_forms.py) — 21 testes ✅

| ID | Classe | Teste | Status |
|---|---|---|---|
| TF-L01–04 | `TestLoginForm` | Email obrigatório, senha obrigatória, email inválido, form válido | ✅ |
| TF-W01–08 | `TestWorkOrderForm` | Todos campos obrigatórios (nome, email, telefone, doc, descrição), mínimo 10 chars, data opcional | ✅ |
| TF-WE01–04 | `TestWorkOrderEditForm` | Campos financeiros opcionais, motivo cancelamento opcional, nota histórico opcional | ✅ |
| TF-UC01–03 | `TestUserCreateForm` | Form válido, senha mínimo 6 chars, email inválido | ✅ |
| TF-UE01–02 | `TestUserEditForm` | Senha opcional na edição, senha curta com Optional() | ✅ |

---

### 4.3 Autenticação (tests/test_auth_controller.py) — 9 testes ✅ — UC11

| ID | Classe | Cenário | Status |
|---|---|---|---|
| TA-L01 | `TestLogin` | GET `/auth/login` retorna 200 | ✅ |
| TA-L02 | `TestLogin` | POST com credenciais válidas → 302 redirect | ✅ |
| TA-L03 | `TestLogin` | POST válido com `follow_redirects` → 200 | ✅ |
| TA-L04 | `TestLogin` | Email inexistente → flash "Email ou senha incorretos" | ✅ |
| TA-L05 | `TestLogin` | Senha errada → flash "Email ou senha incorretos" | ✅ |
| TA-L06 | `TestLogin` | Usuário já logado em `/auth/login` → 302 | ✅ |
| TA-LO01 | `TestLogout` | GET `/auth/logout` → 302 | ✅ |
| TA-LO02 | `TestLogout` | Logout com `follow_redirects` → flash "saiu do sistema" | ✅ |
| TA-PR01–04 | `TestProtecaoDeRotas` | `/`, `/ordens/`, `/relatorios/`, `/users/` sem auth → 302 + `/auth/login` | ✅ |

---

### 4.4 Ordens de Serviço (tests/test_work_order_controller.py) — 20 testes ✅

#### UC1 — Cadastrar OS (TestCadastrarOS)

| ID | Cenário | Requisito | Status |
|---|---|---|---|
| TWO-C01 | GET `/ordens/nova` → 200 | UC1 | ✅ |
| TWO-C02 | POST com dados válidos → OS criada com status "Em Orçamento" e código gerado | F1.1 + F3.1 | ✅ |
| TWO-C03 | POST com email novo → Requester criado automaticamente | UC1 | ✅ |
| TWO-C04 | POST com email existente → Requester reutilizado | UC1 | ✅ |
| TWO-C05 | Criação gera entrada no histórico com `new_status='Em Orçamento'` | UC8/UC10 | ✅ |

#### UC4 — Listar OS (TestListarOS)

| ID | Cenário | Status |
|---|---|---|
| TWO-L01 | GET `/ordens/` sem dados → 200 | ✅ |
| TWO-L02 | GET `/ordens/` com OS → exibe número da OS | ✅ |

#### UC2 — Editar OS (TestEditarOS)

| ID | Cenário | Status |
|---|---|---|
| TWO-E01 | GET `/ordens/<id>/editar` → 200 | ✅ |
| TWO-E02 | POST descrição atualizada → banco reflete mudança | ✅ |
| TWO-E03 | GET `/ordens/99999/editar` → 404 | ✅ |

#### UC3 — Atualizar Status (TestAtualizarStatus) — Máquina de Estados

| ID | Transição | Verificação Adicional | Status |
|---|---|---|---|
| TWO-S01 | T2: Em Orçamento → Em Manutenção | Status no banco | ✅ |
| TWO-S02 | T4: Em Manutenção → Aguardando Pagamento | Status no banco | ✅ |
| TWO-S03 | T6: Aguardando Pagamento → Aguardando Retirada | Status no banco | ✅ |
| TWO-S04 | T7: Aguardando Retirada → Finalizado | `delivered_at` preenchido | ✅ |
| TWO-S05 | Finalizado é terminal — avançar não muda status | Idempotência | ✅ |
| TWO-S06 | Cancelado é terminal — avançar não muda status | Idempotência | ✅ |
| TWO-S07 | Transição cria entrada no histórico | `len(history) >= 2` | ✅ |
| TWO-S08 | **Ciclo completo T1→T2→T4→T6→T7** | 5 entradas no histórico, `delivered_at` preenchido | ✅ |

#### UC5 — Cancelar OS (TestCancelarOS)

| ID | Cenário | Status |
|---|---|---|
| TWO-K01 | T3: Cancelar a partir de "Em Orçamento" | ✅ |
| TWO-K02 | T5: Cancelar a partir de "Em Manutenção" | ✅ |
| TWO-K03 | NÃO cancelar a partir de "Aguardando Pagamento" | ✅ |
| TWO-K04 | NÃO cancelar a partir de "Aguardando Retirada" | ✅ |
| TWO-K05 | Cancelamento registra histórico com `new_status='Cancelado'` | ✅ |

#### Excluir OS / UC9 / UC10

| ID | Cenário | Status |
|---|---|---|
| TWO-D01 | POST `/ordens/<id>/delete` → OS e históricos excluídos | ✅ |
| TWO-D02 | POST `/ordens/99999/delete` → 404 | ✅ |
| TWO-R01 | GET `/ordens/rastreio/<public_id>` válido → 200 (UC9/F3.2) | ✅ |
| TWO-R02 | GET `/ordens/rastreio/uuid-invalido` → 404 | ✅ |
| TWO-R03 | Página de rastreio contém dados do histórico (UC10/F3.3) | ✅ |

---

### 4.5 Relatórios e Dashboard (tests/test_report_controller.py) — 10 testes ✅

| ID | Cenário | Requisito | Status |
|---|---|---|---|
| TR-01 | GET `/relatorios/` → 200 | UC6 | ✅ |
| TR-02 | GET `/relatorios/entrada-saida` sem datas → 200 (usa padrão 30 dias) | F2.1 | ✅ |
| TR-03 | GET `/relatorios/entrada-saida?start_date=&end_date=` → 200 | F2.1 | ✅ |
| TR-04 | Relatório com OS no período → 200 com dados | F2.1 | ✅ |
| TR-05 | Datas inválidas → fallback para padrão | F2.1 | ✅ |
| TR-06 | GET `/relatorios/dashboard` → 200 | UC7/F2.2 | ✅ |
| TR-07 | Dashboard com filtro de datas → 200 | F2.2 | ✅ |
| TR-08 | Dashboard sem dados → 200 sem erros | F2.2 | ✅ |
| TR-09 | GET `/relatorios/api/status-data` → JSON com `labels` e `datasets` | UC7 | ✅ |
| TR-10 | GET `/relatorios/api/daily-data` → JSON com >= 7 labels de datas | UC7 | ✅ |

---

### 4.6 Usuários (tests/test_user_controller.py) — 9 testes ✅

| ID | Cenário | Status |
|---|---|---|
| TU-01 | GET `/users/` → 200 | ✅ |
| TU-02 | Listagem exibe `admin@teste.com` | ✅ |
| TU-03 | GET `/users/create` → 200 | ✅ |
| TU-04 | POST criar usuário válido → flash "criado com sucesso" | ✅ |
| TU-05 | POST email duplicado → flash "já está em uso" | ✅ |
| TU-06 | GET `/users/<id>/edit` → 200 | ✅ |
| TU-07 | POST editar nome → banco atualizado + flash "atualizado com sucesso" | ✅ |
| TU-08 | POST email duplicado na edição → flash "já está em uso" | ✅ |
| TU-09 | GET `/users/99999/edit` → 404 | ✅ |
| TU-10 | POST excluir usuário → removido do banco + flash "removido com sucesso" | ✅ |
| TU-11 | POST `/users/99999/delete` → 404 | ✅ |

---

### 4.7 CLI (tests/test_cli.py) — 2 testes ✅

| ID | Cenário | Status |
|---|---|---|
| TC-01 | `flask create-user "Nome" "email" "senha"` → usuário criado com hash correto | ✅ |
| TC-02 | Criar usuário com email duplicado → mensagem "já existe" | ✅ |

---

## 5. Cobertura de Código

Resultado da última execução completa:

| Módulo | Linhas | Miss | Cobertura |
|---|---|---|---|
| `app/__init__.py` | 31 | 1 | 97% |
| `app/cli.py` | 25 | 3 | 88% |
| `app/config.py` | 18 | 0 | **100%** |
| `app/controllers/auth_controller.py` | 29 | 0 | **100%** |
| `app/controllers/main_controller.py` | 7 | 0 | **100%** |
| `app/controllers/report_controller.py` | 99 | 13 | 87% |
| `app/controllers/user_controller.py` | 52 | 1 | 98% |
| `app/controllers/work_order_controller.py` | 102 | 12 | 88% |
| `app/forms/` (todos) | — | 0 | **100%** |
| `app/models/` (todos) | — | 0 | **100%** |
| **TOTAL** | **496** | **30** | **94%** |

### 5.1 Lacunas de Cobertura Identificadas

| Módulo | Linhas Não Cobertas | Ação Recomendada |
|---|---|---|
| `app/cli.py` | 25–27 | Testar caminho de erro do CLI (exceção inesperada) |
| `app/controllers/report_controller.py` | 72–77, 105–112, 241–243 | Testar exportação/impressão de relatório |
| `app/controllers/work_order_controller.py` | 64–67, 138–141, 159–162 | Testar erros de validação de formulário no controller |

---

## 6. Avisos e Débito Técnico

### 6.1 LegacyAPIWarning — `Query.get()`

**Impacto:** Baixo (funciona, mas deprecated no SQLAlchemy 2.x)
**Total:** 48 avisos em `test_work_order_controller.py`

**Correção recomendada:** Substituir `Model.query.get(id)` por `db.session.get(Model, id)` nos testes.

```python
# Antes (deprecated)
order = WorkOrder.query.get(sample_work_order.id)

# Depois (moderno)
order = db.session.get(WorkOrder, sample_work_order.id)
```

---

## 7. Testes Pendentes

### 7.1 E2E com Playwright (⬜ Não Implementado)

Spec completa disponível em `docs/testing.md` nas seções 3.3.1 a 3.6.

| Módulo | Arquivo Alvo | Prioridade |
|---|---|---|
| Autenticação E2E | `tests/e2e/test_auth.py` | 🔴 Alta |
| Ordens de Serviço E2E | `tests/e2e/test_work_orders.py` | 🔴 Alta |
| Dashboard E2E | `tests/e2e/test_dashboard.py` | 🟡 Média |
| Componentes UI (modais, toasts) | `tests/e2e/test_components.py` | 🟡 Média |
| Responsividade | `tests/e2e/test_responsive.py` | 🟢 Baixa |
| Regressão Visual | `tests/e2e/test_visual_regression.py` | 🟢 Baixa |

**Instalação:**
```bash
pip install pytest-playwright axe-playwright-python
playwright install
```

### 7.2 Acessibilidade (⬜ Não Implementado)

| Teste | Ferramenta | Prioridade |
|---|---|---|
| Auditoria axe em todas as páginas | axe-playwright | 🔴 Alta |
| Navegação por teclado | Playwright | 🟡 Média |
| Contraste WCAG AA | axe-playwright | 🟡 Média |
| Estrutura de headings (h1→h2→h3) | axe-playwright | 🟡 Média |

### 7.3 Performance (⬜ Não Implementado)

| Métrica | Meta | Ferramenta |
|---|---|---|
| Lighthouse Performance | ≥ 80 | Lighthouse CI |
| Lighthouse Acessibilidade | ≥ 90 | Lighthouse CI |
| TTFB | < 600ms | Lighthouse CI |
| LCP | < 2.5s | Lighthouse CI |
| CLS | < 0.1 | Lighthouse CI |

---

## 8. Como Executar os Testes

### 8.1 Via Docker (Recomendado)

```bash
# Subir o container
docker compose up -d --build

# Executar todos os testes backend
docker compose exec web python -m pytest tests/ -v --tb=short

# Com relatório de cobertura
docker compose exec web python -m pytest tests/ --cov=app --cov-report=term-missing

# Módulo específico
docker compose exec web python -m pytest tests/test_models.py -v
docker compose exec web python -m pytest tests/test_work_order_controller.py -v

# Teste específico
docker compose exec web python -m pytest tests/test_models.py::TestStatusTransitions -v
```

### 8.2 Via Ambiente Virtual Local

```bash
source venv/bin/activate
pip install -r requirements.txt
pytest tests/ -v --tb=short
```

### 8.3 Relatório HTML

```bash
docker compose exec web python -m pytest tests/ --cov=app --cov-report=html
# Relatório disponível em: htmlcov/index.html
```

---

## 9. Matriz de Rastreabilidade Completa

| Requisito | Caso de Uso | Testes Backend | Status Backend | Status E2E |
|---|---|---|---|---|
| F1.1 | UC1 — Cadastrar OS | `TestCadastrarOS` (5 testes) | ✅ | ⬜ |
| F1.2 | UC2 — Editar OS | `TestEditarOS` (3 testes) | ✅ | ⬜ |
| F1.3 | UC3 — Atualizar Status | `TestAtualizarStatus` (8 testes) | ✅ | ⬜ |
| F1.4 | UC4 — Listar OS | `TestListarOS` (2 testes) | ✅ | ⬜ |
| F1.5 | UC5 — Cancelar OS | `TestCancelarOS` (5 testes) | ✅ | ⬜ |
| F2.1 | UC6 — Relatórios | `TestRelatorioEntradaSaida` (5 testes) | ✅ | ⬜ |
| F2.2 | UC7 — Dashboard | `TestDashboard` + `TestAPIsRelatorios` (7 testes) | ✅ | ⬜ |
| F3.1 | UC8 — Código Rastreio | `TestWorkOrderModel` (geração de `number`/`public_id`) | ✅ | — |
| F3.2 | UC9 — Rastreio Público | `TestRastreio` (3 testes) | ✅ | — |
| F3.3 | UC10 — Linha do Tempo | `TestHistoryOrderModel` + transições | ✅ | — |
| — | UC11 — Autenticação | `TestLogin`, `TestLogout`, `TestProtecaoDeRotas` (9 testes) | ✅ | ⬜ |

**Cobertura de requisitos funcionais: 11/11 (100%) no backend.**

---

## 10. Critérios de Aceite

### 10.1 Fase Atual (Backend)

- [x] 124 testes passando (0 falhas)
- [x] Cobertura ≥ 90% (resultado: 94%)
- [x] Todos os UC1–UC11 cobertos por testes backend
- [x] Ciclo completo de OS testado (T1→T7)
- [x] Máquina de estados com 100% de transições testadas

### 10.2 Próxima Fase (E2E)

- [ ] Instalar e configurar Playwright
- [ ] Implementar `tests/e2e/conftest.py` com login automático
- [ ] Mínimo de 15 testes E2E cobrindo fluxos críticos
- [ ] Testes de acessibilidade passando (axe — 0 violações críticas)
- [ ] Testes responsivos em 3 breakpoints (mobile 375px, tablet 768px, desktop 1440px)

---

*Última atualização: 15/05/2026 — v1.0*
*Autor: Yure Samarone Gomes Duarte*
