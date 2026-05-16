# Relatório de Refatoração — EletroService

**Data:** 2026-05-16  
**Versão anterior:** pré-refatoração (124 testes, 94% cobertura)  
**Versão atual:** pós-refatoração (132 testes, 96% cobertura)  
**Guia:** `docs/03-specs.md`

---

## Resumo das Mudanças

### Etapa 1 — Modularização dos Modelos

#### `app/models/history_order.py`
- **Adicionado:** método estático `HistoryOrder.save_transition(work_order_id, old_status, new_status, description)`.
- **Motivo:** A criação de entradas no histórico estava duplicada inline em `work_order_controller.create()` e `work_order_controller.edit()`. Centralizar em um método estático elimina a duplicidade e torna o contrato explícito conforme a spec.
- **Regra de transação:** o método adiciona à sessão (`db.session.add`) mas **não faz commit** — a responsabilidade de commit permanece no caller (controller) para manter atomicidade.

#### `app/models/work_order.py`
- **Adicionado:** método de instância `generate_public_id()`.
- **Motivo:** A spec define este método explicitamente. A geração do `public_id` continuou com `default=lambda: str(uuid.uuid4())` no campo para retrocompatibilidade, e o método serve como ponto de chamada explícita e documentada na criação (UC1).

---

### Etapa 2 — Deduplicação e Cache em `report_controller.py`

#### Deduplicação
- **Removido:** bloco idêntico de parse de datas (`start_date` / `end_date`) que existia duplicado nas funções `entrada_saida()` e `dashboard()` (~20 linhas x 2).
- **Adicionado:** função interna `_parse_date_range(req)` que encapsula o parse, validação e normalização (`end_date` incluindo 23:59:59).

#### Cache das APIs de Gráficos
- **Adicionado:** `Flask-Caching==2.3.0` ao `requirements.txt`.
- **Adicionado:** `cache = Cache()` em `app/extensions.py`.
- **Configurado:** `CACHE_TYPE = 'SimpleCache'` (in-memory, sem servidor) em `Config` base; `CACHE_TYPE = 'NullCache'` em `TestingConfig` para manter testes determinísticos.
- **Aplicado:** `@cache.cached(timeout=300)` nas rotas `api_status_data` e `api_daily_data` — queries de gráficos com TTL de 5 minutos, evitando recálculo em cada clique do Dashboard (UC7).
- **Inicializado:** `cache.init_app(app)` no factory `create_app()`.

---

### Etapa 3 — Refatoração de `work_order_controller.py`

- **Substituído:** criações inline de `HistoryOrder(...)` + `db.session.add(history)` por chamadas a `HistoryOrder.save_transition(...)` em `create()` e `edit()`.
- **Removida:** rota `track()` com `@login_required` — violava UC9 (acesso público) e foi substituída pelo novo `tracking_controller.py`.
- **Corrigido:** fluxo de transação — `save_transition()` adiciona à sessão, o `db.session.commit()` é feito após, garantindo atomicidade com a WorkOrder.
- **Atualizado:** `app/templates/work_orders/list.html` — referência `url_for('work_orders.track', ...)` migrada para `url_for('tracking.search', code=...)`.

---

### Etapa 4 — Novo `tracking_controller.py` (Acesso Público)

#### `app/controllers/tracking_controller.py` (**NOVO**)
- Endpoint `GET /rastreio/search?code=<public_id>` **sem `@login_required`**.
- Comportamento conforme spec (UC9/UC10):
  - Sem `code` ou `code` vazio → exibe formulário de busca.
  - Código não encontrado → exibe mensagem de erro na mesma página (sem 404).
  - Código válido → exibe status atual + linha do tempo ordenada decrescentemente.

#### Templates Novos
| Arquivo | Descrição |
|---|---|
| `app/templates/base_public.html` | Layout base público (Bootstrap 5, sem navbar de admin) |
| `app/templates/tracking/index.html` | Formulário GET de entrada do código (UC9) |
| `app/templates/tracking/result.html` | Status atual com badge colorido + linha do tempo (UC9 + UC10) |

#### `app/controllers/__init__.py` / `app/__init__.py`
- Registrado `tracking_bp` na factory de forma idêntica aos outros blueprints.

---

### Etapa 5 — Testes, Requirements e Docs

#### `tests/test_tracking_controller.py` (**NOVO** — 8 testes)
- Cobre UC9 e UC10 com acesso **sem autenticação**.
- Casos: código válido, código inexistente, código vazio, múltiplas OS com IDs únicos, linha do tempo presente.

#### `tests/test_work_order_controller.py`
- Classe `TestRastreio` atualizada para usar o novo endpoint público `/rastreio/search`.

---

## Métricas

| Métrica | Antes | Depois |
|---|---|---|
| Testes | 124 | 132 (+8) |
| Cobertura | 94% | **96%** |
| Linhas duplicadas (report) | ~40 | 0 |
| Linhas duplicadas (history inline) | ~12 | 0 |
| UC9 acessível sem login | ❌ | ✅ |
| Cache nas APIs de gráficos | ❌ | ✅ (TTL 300s) |
| `tracking_controller.py` isolado | ❌ | ✅ |

---

## Arquivos Modificados

| Arquivo | Ação |
|---|---|
| `app/models/history_order.py` | MODIFICADO — `save_transition()` adicionado |
| `app/models/work_order.py` | MODIFICADO — `generate_public_id()` adicionado |
| `app/controllers/report_controller.py` | MODIFICADO — `_parse_date_range()` + `@cache.cached()` |
| `app/controllers/work_order_controller.py` | MODIFICADO — usa `save_transition()`, removeu `track()` |
| `app/controllers/tracking_controller.py` | **CRIADO** |
| `app/extensions.py` | MODIFICADO — `cache = Cache()` |
| `app/config.py` | MODIFICADO — `CACHE_TYPE` por ambiente |
| `app/__init__.py` | MODIFICADO — `cache.init_app()` + `tracking_bp` |
| `app/templates/base_public.html` | **CRIADO** |
| `app/templates/tracking/index.html` | **CRIADO** |
| `app/templates/tracking/result.html` | **CRIADO** |
| `app/templates/work_orders/list.html` | MODIFICADO — URL de rastreio atualizada |
| `tests/test_tracking_controller.py` | **CRIADO** |
| `tests/test_work_order_controller.py` | MODIFICADO — `TestRastreio` atualizada |
| `requirements.txt` | MODIFICADO — `Flask-Caching==2.3.0` |
| `docs/03-specs.md` | ATUALIZADO |
| `docs/testing.md` | ATUALIZADO |
| `README.md` | ATUALIZADO |

---

### Etapa 6 — Design System e Acessibilidade (Frontend Refactor)

#### `app/static/css/style.css`
- **Novo Esquema de Cores:** `primary` alterado para `#0a58ca` (Azul escuro/forte), e adicionado `accent` `#fd7e14` (Laranja) para botões de destaque, timeline e alertas.
- **Novas Classes de Acessibilidade/Loading:** Implementadas `.btn-loading` e `.skeleton` para carregamentos responsivos de estado.
- **Empty States:** Estilo aprimorado `.empty-state`, `.empty-state-icon` com bordas tracejadas e cores consistentes.

#### `app/static/js/app.js`
- **Manipulador Universal de Formulários:** Adicionado interceptador em submissões `setupFormLoading()` para aplicar estado de loading universal em botões e desabilitar multi-clicks acidentais.

#### Templates Modificados
- `app/templates/base.html` & `app/templates/base_public.html`: Adicionado identificadores e papéis (`role="main"`, `aria-label`, `id="main-content"`) e inclusão do `style.css` global.
- `app/templates/work_orders/list.html` & `app/templates/users/list.html`: Implementado o fallback amigável `.empty-state`.
- `app/templates/work_orders/create.html` & `app/templates/work_orders/edit.html`: Adicionados atributos `data_validate` para validação client-side via WTForms.
- `app/templates/tracking/result.html`: Cores de `Aguardando Retirada` e Timeline (`border-accent`) refatoradas para usar o Laranja (accent color).

#### Modelagem de Regras de Negócio
- **Campos Financeiros Restritos:** A edição do Custo de Mão de Obra e Preço Final foi limitada estritamente aos status `Em Orçamento` e `Em Manutenção`, garantindo que os valores não sejam alterados acidentalmente após o fechamento do acordo (Aguardando Pagamento, Retirada ou Finalizado).
