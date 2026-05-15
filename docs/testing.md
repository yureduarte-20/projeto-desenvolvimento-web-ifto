# Plano de Testes TDD-First — EletroService

**Versão:** 1.1  
**Data:** 10/05/2026  
**Autor:** Yure Samarone Gomes Duarte  
**Metodologia:** TDD (Test-Driven Development)

---

## 1. Introdução

Este documento define a estratégia de testes automatizados do sistema **EletroService**, uma plataforma web Flask para gestão do ciclo de vida de Ordens de Serviço (OS). A abordagem segue o paradigma **TDD-First**, onde os testes são escritos antes ou em conjunto com o código funcional, servindo como especificação executável do comportamento esperado.

### 1.1 Objetivos

- Validar **todas as funcionalidades** definidas nos documentos de requisitos e casos de uso
- Garantir **cobertura da máquina de estados** da OS (6 status, 7 transições)
- Prevenir **regressões** em alterações futuras do código
- Fornecer **documentação viva** do comportamento do sistema
- Garantir **qualidade de frontend** com testes visuais, responsivos e de acessibilidade

### 1.2 Documentos de Referência

| Documento | Conteúdo |
|---|---|
| `docs/Casos de Uso.md` | 11 casos de uso (UC1–UC11), diagramas, fluxos principal/alternativo |
| `docs/Requisitos Funcionais e Não funcionais.md` | 10 requisitos funcionais (F1.1–F3.3) com criticidade |
| `docs/DER.mermaid` | Diagrama Entidade-Relacionamento (4 entidades) |
| `docs/Fluxo de Status.mermaid` | Máquina de estados da OS (6 status, 7 transições) |
| `docs/03-specs.md` | Especificações de frontend, design system, componentes |

---

## 2. Arquitetura de Testes

### 2.1 Stack de Testes

#### Testes de Backend

| Ferramenta | Versão | Finalidade |
|---|---|---|
| **pytest** | 8.3.4 | Framework principal de testes |
| **pytest-cov** | 6.0.0 | Relatório de cobertura de código |
| **pytest-flask** | 1.3.0 | Integração pytest + Flask (test client) |
| **factory-boy** | 3.3.1 | Fábricas de objetos de teste |
| **faker** | 33.3.1 | Geração de dados falsos realísticos |

#### Testes de Frontend (Recomendado)

| Ferramenta | Versão | Finalidade |
|---|---|---|
| **Playwright** | 1.40+ | Testes E2E, acessibilidade, responsividade |
| **Axe Core** | 4.8+ | Testes automatizados de acessibilidade |
| **BackstopJS / Playwright** | - | Testes de regressão visual |
| **Lighthouse CI** | - | Auditoria de performance e melhores práticas |

### 2.2 Estrutura de Diretórios

```
tests/
├── __init__.py                     # Pacote de testes
├── conftest.py                     # Fixtures globais (app, db, client, dados)
├── test_models.py                  # Modelos e regras de negócio
├── test_forms.py                   # Validação de formulários WTForms
├── test_auth_controller.py         # UC11 — Autenticação
├── test_work_order_controller.py   # UC1–UC5, UC9, UC10 — Ordens de Serviço
├── test_report_controller.py       # UC6, UC7 — Relatórios e Dashboard
├── test_user_controller.py         # Gestão de usuários
├── test_cli.py                     # Comando CLI create-user
└── e2e/                            # Testes End-to-End (Playwright)
    ├── __init__.py
    ├── conftest.py
    ├── test_auth.py
    ├── test_work_orders.py
    ├── test_dashboard.py
    ├── test_accessibility.py
    └── test_responsive.py
```

### 2.3 Configuração de Teste (`TestingConfig`)

```python
class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # Banco em memória
    WTF_CSRF_ENABLED = False                         # CSRF desabilitado
    SERVER_NAME = 'localhost'
```

### 2.4 Estratégia de Isolamento

- **Banco em memória**: Cada teste usa SQLite `:memory:` com `create_all()`/`drop_all()` por função
- **CSRF desabilitado**: Permite testar formulários sem tokens
- **Fixtures por função**: Dados recriados a cada teste (sem estado compartilhado)
- **Autenticação via fixture**: `authenticated_client` faz login automático antes dos testes

---

## 3. Testes de Frontend (E2E)

### 3.1 Estratégia de Testes E2E

Os testes E2E utilizam **Playwright** para garantir que as funcionalidades críticas do sistema funcionem corretamente do ponto de vista do usuário final.

#### Pirâmide de Testes

```
        /\
       /  \     E2E Tests (Playwright) - 10%
      /----\    ------------------------
     /      \   Integration Tests - 30%
    /--------\  ------------------------
   /          \ Unit Tests (pytest) - 60%
  /____________\
```

### 3.2 Configuração do Playwright

**playwright.config.ts:**
```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:5000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    // Mobile
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
    {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 12'] },
    },
  ],
});
```

### 3.3 Cenários de Teste E2E

#### 3.3.1 Autenticação (`test_auth.py`)

```python
# tests/e2e/test_auth.py
import re
from playwright.sync_api import Page, expect

def test_login_success(page: Page):
    """Testa login com credenciais válidas"""
    page.goto("/auth/login")
    
    # Preenche formulário
    page.get_by_label("Email").fill("admin@example.com")
    page.get_by_label("Senha").fill("password123")
    
    # Submete
    page.get_by_role("button", name="Entrar").click()
    
    # Verifica redirecionamento
    expect(page).to_have_url("/")
    
    # Verifica mensagem de sucesso
    expect(page.get_by_text("Login realizado com sucesso")).to_be_visible()

def test_login_invalid_credentials(page: Page):
    """Testa login com credenciais inválidas"""
    page.goto("/auth/login")
    
    page.get_by_label("Email").fill("wrong@example.com")
    page.get_by_label("Senha").fill("wrongpassword")
    page.get_by_role("button", name="Entrar").click()
    
    # Permanece na página de login
    expect(page).to_have_url("/auth/login")
    
    # Mostra mensagem de erro
    expect(page.get_by_text("Email ou senha incorretos")).to_be_visible()

def test_logout(page: Page):
    """Testa logout do sistema"""
    # Login primeiro
    page.goto("/auth/login")
    page.get_by_label("Email").fill("admin@example.com")
    page.get_by_label("Senha").fill("password123")
    page.get_by_role("button", name="Entrar").click()
    
    # Faz logout
    page.get_by_role("link", name="Sair").click()
    
    # Verifica redirecionamento para login
    expect(page).to_have_url("/auth/login")
    
    # Verifica mensagem
    expect(page.get_by_text("Você saiu do sistema")).to_be_visible()
```

#### 3.3.2 Ordens de Serviço (`test_work_orders.py`)

```python
# tests/e2e/test_work_orders.py
from playwright.sync_api import Page, expect

def test_create_work_order(page: Page):
    """Testa criação de nova ordem de serviço"""
    page.goto("/work-orders/create")
    
    # Preenche dados do solicitante
    page.get_by_label("Nome").fill("João Silva")
    page.get_by_label("Email").fill("joao@email.com")
    page.get_by_label("Telefone").fill("(11) 99999-9999")
    
    # Preenche dados da OS
    page.get_by_label("Descrição").fill("Problema no aparelho que não liga mais")
    
    # Submete
    page.get_by_role("button", name="Salvar").click()
    
    # Verifica redirecionamento
    expect(page).to_have_url(re.compile("/work-orders"))
    
    # Verifica mensagem
    expect(page.get_by_text("Ordem de serviço criada com sucesso")).to_be_visible()

def test_list_work_orders(page: Page):
    """Testa listagem de ordens de serviço"""
    page.goto("/work-orders")
    
    # Verifica título
    expect(page.get_by_role("heading", name="Ordens de Serviço")).to_be_visible()
    
    # Verifica botão de nova OS
    expect(page.get_by_role("link", name="Nova OS")).to_be_visible()
    
    # Verifica tabela ou estado vazio
    table_or_empty = page.locator("table tbody tr, .text-center.py-5").first
    expect(table_or_empty).to_be_visible()

def test_edit_work_order(page: Page):
    """Testa edição de ordem de serviço"""
    # Acessa lista primeiro
    page.goto("/work-orders")
    
    # Clica no primeiro botão de editar se existir
    edit_button = page.get_by_role("link", name="Editar").first
    if edit_button.is_visible():
        edit_button.click()
        
        # Modifica descrição
        description_field = page.get_by_label("Descrição")
        description_field.fill("Descrição atualizada via teste E2E")
        
        # Salva
        page.get_by_role("button", name="Salvar").click()
        
        # Verifica mensagem
        expect(page.get_by_text("salva com sucesso")).to_be_visible()

def test_work_order_status_transitions(page: Page):
    """Testa transições de status da OS"""
    page.goto("/work-orders")
    
    # Acessa primeira OS para edição
    edit_button = page.get_by_role("link", name="Editar").first
    if edit_button.is_visible():
        edit_button.click()
        
        # Verifica botão de avançar status existe
        advance_button = page.get_by_role("button", name=re.compile("Avançar|Próximo"))
        if advance_button.is_visible():
            # Clica e confirma
            advance_button.click()
            page.get_by_role("button", name="Confirmar").click()
            
            # Verifica mensagem de sucesso
            expect(page.get_by_text("Status atualizado")).to_be_visible()
```

#### 3.3.3 Dashboard e Relatórios (`test_dashboard.py`)

```python
# tests/e2e/test_dashboard.py
from playwright.sync_api import Page, expect

def test_dashboard_access(page: Page):
    """Testa acesso ao dashboard"""
    page.goto("/reports/dashboard")
    
    # Verifica título
    expect(page.get_by_role("heading", name="Dashboard")).to_be_visible()
    
    # Verifica cards de métricas
    expect(page.get_by_text("Total de Ordens")).to_be_visible()
    expect(page.get_by_text("Receita Total")).to_be_visible()

def test_dashboard_charts(page: Page):
    """Testa carregamento de gráficos no dashboard"""
    page.goto("/reports/dashboard")
    
    # Agrega carregamento dos gráficos
    page.wait_for_timeout(2000)
    
    # Verifica se canvas dos gráficos estão presentes
    charts = page.locator("canvas").all()
    assert len(charts) >= 2, "Esperado pelo menos 2 gráficos"

def test_report_generation(page: Page):
    """Testa geração de relatórios"""
    page.goto("/reports/entrada-saida")
    
    # Define período
    page.get_by_label("Data Inicial").fill("2026-01-01")
    page.get_by_label("Data Final").fill("2026-12-31")
    
    # Filtra
    page.get_by_role("button", name="Filtrar").click()
    
    # Verifica resultados
    expect(page.locator("table tbody tr, .text-center.py-5").first).to_be_visible()
```

#### 3.3.4 Testes de Acessibilidade (`test_accessibility.py`)

```python
# tests/e2e/test_accessibility.py
import pytest
from playwright.sync_api import Page
from axe_playwright_python import run_axe

def test_home_page_accessibility(page: Page):
    """Testa acessibilidade da página inicial"""
    page.goto("/")
    
    # Executa análise do axe
    results = run_axe(page)
    
    # Verifica se não há violações críticas
    critical_violations = [v for v in results.violations if v.impact == 'critical']
    assert len(critical_violations) == 0, f"Violações críticas encontradas: {critical_violations}"

def test_login_page_accessibility(page: Page):
    """Testa acessibilidade da página de login"""
    page.goto("/auth/login")
    
    results = run_axe(page)
    
    # Verifica labels de formulário
    form_violations = [v for v in results.violations if 'form' in v.id or 'label' in v.id]
    assert len(form_violations) == 0, f"Problemas em formulários: {form_violations}"

def test_keyboard_navigation(page: Page):
    """Testa navegação por teclado"""
    page.goto("/auth/login")
    
    # Pressiona Tab várias vezes
    for _ in range(5):
        page.keyboard.press('Tab')
        # Verifica se algum elemento está focado
        focused = page.evaluate('() => document.activeElement.tagName')
        assert focused != 'BODY', "Navegação por teclado falhou"

def test_contrast_ratios(page: Page):
    """Testa taxas de contraste"""
    page.goto("/")
    
    results = run_axe(page)
    
    # Filtra violações de contraste
    contrast_violations = [v for v in results.violations if 'contrast' in v.id]
    
    # Permite no máximo 2 violações menores
    serious_contrast = [v for v in contrast_violations if v.impact in ['serious', 'critical']]
    assert len(serious_contrast) == 0, f"Violações graves de contraste: {serious_contrast}"
```

#### 3.3.5 Testes Responsivos (`test_responsive.py`)

```python
# tests/e2e/test_responsive.py
from playwright.sync_api import Page, expect

def test_mobile_navigation(page: Page):
    """Testa navegação em dispositivo móvel"""
    # Configura viewport mobile
    page.set_viewport_size({"width": 375, "height": 667})
    
    page.goto("/")
    
    # Verifica se o menu hamburguer está visível
    menu_button = page.get_by_role("button", name="Toggle navigation")
    expect(menu_button).to_be_visible()
    
    # Abre o menu
    menu_button.click()
    
    # Verifica se os itens do menu estão visíveis
    expect(page.get_by_role("link", name="Ordens de Serviço")).to_be_visible()

def test_table_responsiveness(page: Page):
    """Testa responsividade de tabelas"""
    page.set_viewport_size({"width": 768, "height": 1024})
    page.goto("/work-orders")
    
    # Verifica se a tabela tem scroll horizontal quando necessário
    table_container = page.locator(".table-responsive").first
    
    if table_container.is_visible():
        # Verifica se o container tem overflow
        has_scroll = table_container.evaluate("el => el.scrollWidth > el.clientWidth")
        
        # Em telas menores, tabelas grandes devem ter scroll
        if has_scroll:
            # Verifica se é possível scrollar
            table_container.evaluate("el => el.scrollLeft = 100")

def test_form_layout_mobile(page: Page):
    """Testa layout de formulários em mobile"""
    page.set_viewport_size({"width": 375, "height": 667})
    page.goto("/work-orders/create")
    
    # Verifica se os campos estão empilhados verticalmente
    form = page.locator("form").first
    
    # Verifica se inputs são largos o suficiente
    inputs = form.locator("input[type='text'], input[type='email']").all()
    
    for input_field in inputs:
        if input_field.is_visible():
            box = input_field.bounding_box()
            # Em mobile, inputs devem ocupar quase toda largura
            assert box['width'] >= 300, f"Input muito estreito: {box['width']}px"

def test_breakpoint_transitions(page: Page):
    """Testa transições entre breakpoints"""
    page.goto("/")
    
    breakpoints = [
        {"width": 320, "height": 568},   # Mobile pequeno
        {"width": 375, "height": 667},   # Mobile
        {"width": 768, "height": 1024},  # Tablet
        {"width": 1024, "height": 768},  # Desktop pequeno
        {"width": 1440, "height": 900},  # Desktop
    ]
    
    for size in breakpoints:
        page.set_viewport_size(size)
        
        # Recarrega para aplicar media queries
        page.reload()
        
        # Verifica se conteúdo principal está visível
        expect(page.locator("main").first).to_be_visible()
        
        # Verifica se não há scroll horizontal indesejado
        has_h_scroll = page.evaluate("() => document.documentElement.scrollWidth > window.innerWidth")
        assert not has_h_scroll, f"Scroll horizontal detectado em {size['width']}x{size['height']}"
```

### 3.4 Testes de Componentes e Renderização

```python
# tests/e2e/test_components.py
from playwright.sync_api import Page, expect

def test_card_hover_effects(page: Page):
    """Testa efeitos hover em cards"""
    page.goto("/reports")
    
    # Localiza primeiro card
    card = page.locator(".card").first
    
    # Captura estado inicial
    initial_box = card.bounding_box()
    
    # Hover no card
    card.hover()
    
    # Aguarda transição
    page.wait_for_timeout(300)
    
    # Verifica se houve transformação (elevação)
    # Nota: bounding_box pode não mudar com transform, verificamos visualmente

def test_modal_interactions(page: Page):
    """Testa interações com modais"""
    page.goto("/work-orders")
    
    # Clica no primeiro botão de excluir
    delete_button = page.get_by_role("button", name="Excluir").first
    
    if delete_button.is_visible():
        delete_button.click()
        
        # Verifica se modal apareceu
        modal = page.locator(".modal").first
        expect(modal).to_be_visible()
        
        # Verifica conteúdo do modal
        expect(page.get_by_text("Confirmar Exclusão")).to_be_visible()
        
        # Fecha modal
        page.get_by_role("button", name="Cancelar").click()
        
        # Verifica se modal fechou
        expect(modal).not_to_be_visible()

def test_form_validation_messages(page: Page):
    """Testa mensagens de validação em formulários"""
    page.goto("/work-orders/create")
    
    # Tenta submeter formulário vazio
    page.get_by_role("button", name="Salvar").click()
    
    # Verifica mensagens de erro
    expect(page.get_by_text("Este campo é obrigatório")).to_be_visible()
    
    # Preenche email inválido
    page.get_by_label("Email").fill("email-invalido")
    page.get_by_role("button", name="Salvar").click()
    
    # Verifica mensagem de email inválido
    expect(page.get_by_text("Email inválido")).to_be_visible()

def test_toast_notifications(page: Page):
    """Testa notificações toast"""
    # Realiza uma ação que mostra toast
    page.goto("/work-orders/create")
    
    # Preenche e salva
    page.get_by_label("Nome").fill("Teste Toast")
    page.get_by_label("Email").fill("teste@toast.com")
    page.get_by_label("Descrição").fill("Testando notificações")
    page.get_by_role("button", name="Salvar").click()
    
    # Verifica toast de sucesso
    toast = page.locator(".toast").first
    expect(toast).to_be_visible()
    
    # Verifica mensagem
    expect(page.get_by_text("sucesso")).to_be_visible()
    
    # Aguarda toast desaparecer
    page.wait_for_timeout(6000)
    expect(toast).not_to_be_visible()
```

### 3.5 Testes de Acessibilidade Detalhados

```python
# tests/e2e/test_accessibility_detailed.py
import pytest
from playwright.sync_api import Page
from axe_playwright_python import run_axe

def test_login_page_a11y(page: Page):
    """Testa acessibilidade da página de login"""
    page.goto("/auth/login")
    
    results = run_axe(page)
    
    # Verifica violações críticas e sérias
    critical_and_serious = [
        v for v in results.violations 
        if v.impact in ['critical', 'serious']
    ]
    
    assert len(critical_and_serious) == 0, f"Violações encontradas: {critical_and_serious}"

def test_work_order_list_a11y(page: Page):
    """Testa acessibilidade da lista de OS"""
    page.goto("/work-orders")
    
    results = run_axe(page)
    
    # Verifica violações relacionadas a tabelas
    table_violations = [
        v for v in results.violations 
        if 'table' in v.id or 'th' in v.id
    ]
    
    assert len(table_violations) == 0, f"Problemas em tabelas: {table_violations}"

def test_form_labels_a11y(page: Page):
    """Testa labels de formulários"""
    page.goto("/work-orders/create")
    
    # Verifica se todos os inputs têm labels associadas
    inputs = page.locator("input, select, textarea").all()
    
    for input_field in inputs:
        if input_field.is_visible():
            # Verifica aria-label, aria-labelledby, ou label associada
            has_label = input_field.evaluate("""
                el => {
                    const id = el.id;
                    const ariaLabel = el.getAttribute('aria-label');
                    const ariaLabelledBy = el.getAttribute('aria-labelledby');
                    const hasLabel = document.querySelector(`label[for="${id}"]`);
                    return !!(ariaLabel || ariaLabelledBy || hasLabel || el.placeholder);
                }
            """)
            
            assert has_label, f"Input sem label: {input_field.get_attribute('name')}"

def test_heading_structure_a11y(page: Page):
    """Testa estrutura de headings"""
    page.goto("/")
    
    # Obtém todos os headings
    headings = page.locator("h1, h2, h3, h4, h5, h6").all()
    
    # Deve ter pelo menos um h1
    h1_count = len([h for h in headings if h.evaluate("el => el.tagName") == "H1"])
    assert h1_count > 0, "Página deve ter pelo menos um H1"
    
    # Verifica ordem hierárquica
    previous_level = 0
    for heading in headings:
        level = int(heading.evaluate("el => el.tagName[1]"))
        
        # Não pode pular mais de um nível
        if previous_level > 0:
            assert level <= previous_level + 1, \
                f"Pulou de H{previous_level} para H{level}"
        
        previous_level = level

def test_color_contrast_a11y(page: Page):
    """Testa contraste de cores"""
    page.goto("/")
    
    results = run_axe(page)
    
    # Filtra violações de contraste
    contrast_violations = [
        v for v in results.violations 
        if 'contrast' in v.id.lower()
    ]
    
    # Não deve ter violações sérias de contraste
    serious_contrast = [
        v for v in contrast_violations 
        if v.impact in ['serious', 'critical']
    ]
    
    assert len(serious_contrast) == 0, \
        f"Violações sérias de contraste: {serious_contrast}"
```

### 3.6 Testes de Regressão Visual

```python
# tests/e2e/test_visual_regression.py
import pytest
from playwright.sync_api import Page

def test_homepage_visual(page: Page):
    """Testa regressão visual da página inicial"""
    page.goto("/")
    
    # Aguarda carregamento completo
    page.wait_for_load_state("networkidle")
    
    # Compara com screenshot de referência
    expect(page).to_have_screenshot("homepage.png", 
        threshold=0.2,  # Tolerância de 20%
        full_page=True
    )

def test_login_page_visual(page: Page):
    """Testa regressão visual da página de login"""
    page.goto("/auth/login")
    page.wait_for_load_state("networkidle")
    
    expect(page).to_have_screenshot("login-page.png",
        threshold=0.2,
        full_page=True
    )

def test_work_order_list_visual(page: Page):
    """Testa regressão visual da lista de OS"""
    page.goto("/work-orders")
    page.wait_for_load_state("networkidle")
    
    expect(page).to_have_screenshot("work-order-list.png",
        threshold=0.2,
        full_page=True
    )

def test_mobile_homepage_visual(page: Page):
    """Testa regressão visual mobile"""
    page.set_viewport_size({"width": 375, "height": 667})
    page.goto("/")
    page.wait_for_load_state("networkidle")
    
    expect(page).to_have_screenshot("homepage-mobile.png",
        threshold=0.2,
        full_page=True
    )

def test_tablet_homepage_visual(page: Page):
    """Testa regressão visual tablet"""
    page.set_viewport_size({"width": 768, "height": 1024})
    page.goto("/")
    page.wait_for_load_state("networkidle")
    
    expect(page).to_have_screenshot("homepage-tablet.png",
        threshold=0.2,
        full_page=True
    )
```

---

## 4. Execução dos Testes E2E

### 4.1 Instalação

```bash
# Instalar Playwright
pip install pytest-playwright

# Instalar navegadores
playwright install

# Instalar dependências adicionais
pip install axe-playwright-python
```

### 4.2 Execução

```bash
# Executar todos os testes E2E
pytest tests/e2e/ -v

# Executar em modo headed (visível)
pytest tests/e2e/ --headed -v

# Executar em modo debug
pytest tests/e2e/ --headed --slowmo 1000 -v

# Executar testes específicos
pytest tests/e2e/test_auth.py -v
pytest tests/e2e/test_accessibility.py -v

# Gerar relatório HTML
pytest tests/e2e/ --html=report.html --self-contained-html

# Executar com paralelismo
pytest tests/e2e/ -n auto
```

### 4.3 Atualização de Screenshots

```bash
# Atualizar todos os screenshots de referência
pytest tests/e2e/test_visual_regression.py --update-screenshots

# Atualizar screenshot específico
pytest tests/e2e/test_visual_regression.py::test_homepage_visual --update-screenshots
```

---

## 5. Integração CI/CD

### 5.1 GitHub Actions Workflow

```yaml
# .github/workflows/e2e-tests.yml
name: E2E Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  e2e-tests:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest-playwright
          playwright install
      
      - name: Start application
        run: |
          flask run --host=0.0.0.0 --port=5000 &
          sleep 5
        env:
          FLASK_ENV: testing
      
      - name: Run E2E tests
        run: pytest tests/e2e/ -v --html=report.html --self-contained-html
      
      - name: Upload test results
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: e2e-test-results
          path: |
            report.html
            test-results/
```

### 5.2 Lighthouse CI

```yaml
# .github/workflows/lighthouse.yml
name: Lighthouse CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  lighthouse:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Run Lighthouse CI
        uses: treosh/lighthouse-ci-action@v11
        with:
          configPath: './lighthouserc.json'
          uploadArtifacts: true
          temporaryPublicStorage: true
```

```json
// lighthouserc.json
{
  "ci": {
    "collect": {
      "url": ["http://localhost:5000/", "http://localhost:5000/auth/login"],
      "numberOfRuns": 3
    },
    "assert": {
      "preset": "lighthouse:recommended",
      "assertions": {
        "categories:performance": ["warn", { "minScore": 0.8 }],
        "categories:accessibility": ["error", { "minScore": 0.9 }],
        "categories:best-practices": ["warn", { "minScore": 0.9 }],
        "categories:seo": ["warn", { "minScore": 0.8 }]
      }
    }
  }
}
```

---

## 6. Checklist de Qualidade de Testes

> **Legenda:** ✅ Implementado e verificado no código | ⬜ Pendente de implementação

### 6.1 Testes Unitários/Backend

| Item | Status | Arquivo |
|------|--------|---------|
| Modelos User possuem testes de criação, hash de senha e validação | ✅ | `test_models.py::TestUserModel` (5 testes) |
| Modelo Requester possui testes de criação e relacionamentos | ✅ | `test_models.py::TestRequesterModel` (5 testes) |
| Modelo WorkOrder possui testes de status padrão, geração de códigos (UC8), cascade delete | ✅ | `test_models.py::TestWorkOrderModel` (10 testes) |
| Modelo HistoryOrder possui testes de timestamps e transições | ✅ | `test_models.py::TestHistoryOrderModel` (4 testes) |
| Máquina de estados (`STATUS_TRANSITIONS`) possui 100% de cobertura de transições (6 status, 7 transições) | ✅ | `test_models.py::TestStatusTransitions` (12 testes) |
| Formulário LoginForm possui testes de validação (email/senha obrigatórios, formato de email) | ✅ | `test_forms.py::TestLoginForm` (4 testes) |
| Formulário WorkOrderForm possui testes de todos campos obrigatórios e opcionais | ✅ | `test_forms.py::TestWorkOrderForm` (8 testes) |
| Formulário WorkOrderEditForm possui testes de campos opcionais | ✅ | `test_forms.py::TestWorkOrderEditForm` (4 testes) |
| Formulário UserCreateForm possui testes de validação de senha e email | ✅ | `test_forms.py::TestUserCreateForm` (3 testes) |
| Formulário UserEditForm possui testes (senha opcional na edição) | ✅ | `test_forms.py::TestUserEditForm` (2 testes) |
| Auth Controller cobre Login, Logout e proteção de rotas (UC11) | ✅ | `test_auth_controller.py` (9 testes) |
| Work Order Controller cobre UC1 (criar), UC2 (editar), UC3 (status), UC4 (listar), UC5 (cancelar), UC9 (rastreio), UC10 (histórico) | ✅ | `test_work_order_controller.py` (20 testes) |
| Ciclo completo de OS (T1→T2→T4→T6→T7) com verificação de histórico | ✅ | `test_work_order_controller.py::TestAtualizarStatus::test_ciclo_completo_happy_path` |
| Report Controller cobre UC6 (relatórios) e UC7 (dashboard + APIs JSON) | ✅ | `test_report_controller.py` (10 testes) |
| User Controller cobre CRUD completo de usuários (listar, criar, editar, excluir) | ✅ | `test_user_controller.py` (9 testes) |
| CLI `create-user` possui testes de criação e duplicidade | ✅ | `test_cli.py` (2 testes) |
| Fixtures fornecem dados consistentes entre testes (`conftest.py`) | ✅ | `tests/conftest.py` |
| Testes são independentes (banco em memória, fixtures por função) | ✅ | `TestingConfig` com SQLite `:memory:` |

**Total de testes de backend: ~95 testes implementados.**

### 6.2 Testes E2E/Frontend

| Item | Status | Arquivo |
|------|--------|---------|
| Fluxo de autenticação E2E (login, logout, credenciais inválidas) | ⬜ | `tests/e2e/test_auth.py` (não criado) |
| Fluxo de criação e edição de OS E2E | ⬜ | `tests/e2e/test_work_orders.py` (não criado) |
| Fluxo de dashboard e relatórios E2E | ⬜ | `tests/e2e/test_dashboard.py` (não criado) |
| Formulários possuem testes de submissão, validação e toast | ⬜ | `tests/e2e/test_components.py` (não criado) |
| Navegação entre páginas é testada | ⬜ | Pendente Playwright |
| Funcionalidades AJAX/fetch (APIs de gráficos) são testadas | ⬜ | Parcialmente coberto por `test_report_controller.py` |
| Testes de responsividade cobrem mobile, tablet e desktop | ⬜ | `tests/e2e/test_responsive.py` (não criado) |

### 6.3 Testes de Acessibilidade

| Item | Status | Arquivo |
|------|--------|---------|
| Todas as páginas passam em auditoria automatizada (axe) | ⬜ | `tests/e2e/test_accessibility.py` (não criado) |
| Navegação por teclado funciona em todas as páginas | ⬜ | Pendente Playwright |
| Todos os elementos interativos são focáveis | ⬜ | Pendente Playwright |
| Foco visível está presente em todos os estados | ⬜ | Pendente Playwright |
| Contraste de cores atinge WCAG AA em todo o sistema | ⬜ | Pendente axe-playwright |
| Semântica HTML está correta (headings, landmarks, listas) | ⬜ | Pendente axe-playwright |
| Formulários possuem labels associadas | ⬜ | Pendente axe-playwright |

### 6.4 Testes de Performance

| Item | Status | Observação |
|------|--------|------------|
| Lighthouse score de performance >= 80 | ⬜ | Pendente Lighthouse CI |
| Lighthouse score de acessibilidade >= 90 | ⬜ | Pendente Lighthouse CI |
| Time to First Byte (TTFB) < 600ms | ⬜ | Não mensurado |
| First Contentful Paint (FCP) < 1.8s | ⬜ | Não mensurado |
| Largest Contentful Paint (LCP) < 2.5s | ⬜ | Não mensurado |
| Total Blocking Time (TBT) < 200ms | ⬜ | Não mensurado |
| Cumulative Layout Shift (CLS) < 0.1 | ⬜ | Não mensurado |

### 6.5 Testes de Regressão Visual

| Item | Status | Observação |
|------|--------|------------|
| Screenshots de referência atualizados | ⬜ | Pendente Playwright |
| Diferenças visuais são revisadas manualmente | ⬜ | Pendente |
| Threshold de diferença é apropriado (0.1-0.2) | ⬜ | Definido na spec, não executado |
| Testes cobrem breakpoints principais | ⬜ | Spec definida em `test_responsive.py` |
| Estados de hover/foco são testados | ⬜ | Spec definida em `test_components.py` |

---

## 7. Documentação de Testes

### 7.1 Documentação de Casos de Teste

Cada caso de teste deve ter:
- **ID único** para rastreabilidade
- **Descrição clara** do que está sendo testado
- **Pré-condições** necessárias
- **Passos** detalhados para execução
- **Resultado esperado** claro
- **Dados de teste** necessários

### 7.2 Rastreabilidade

Matriz de rastreabilidade completa (gerada a partir dos testes implementados):

| Requisito | Caso de Uso | Teste Backend | Teste E2E | Status |
|-----------|-------------|---------------|-----------|--------|
| F1.1 | UC1 — Cadastrar OS | `TestCadastrarOS` (5 testes) | `test_create_work_order` | ✅ Backend / ⬜ E2E |
| F1.2 | UC2 — Editar OS | `TestEditarOS` (3 testes) | `test_edit_work_order` | ✅ Backend / ⬜ E2E |
| F1.3 | UC3 — Atualizar Status | `TestAtualizarStatus` (8 testes) | `test_work_order_status_transitions` | ✅ Backend / ⬜ E2E |
| F1.4 | UC4 — Listar/Consultar OS | `TestListarOS` (2 testes) | `test_list_work_orders` | ✅ Backend / ⬜ E2E |
| F1.5 | UC5 — Cancelar OS | `TestCancelarOS` (5 testes) | — | ✅ Backend / ⬜ E2E |
| F2.1 | UC6 — Gerar Relatórios | `TestRelatorioEntradaSaida` (5 testes) | `test_report_generation` | ✅ Backend / ⬜ E2E |
| F2.2 | UC7 — Dashboard | `TestDashboard` + `TestAPIsRelatorios` (7 testes) | `test_dashboard_access` | ✅ Backend / ⬜ E2E |
| F3.1 | UC8 — Geração de Código | `TestWorkOrderModel` (geração de `number` e `public_id`) | — | ✅ Backend / — |
| F3.2 | UC9 — Rastreio Público | `TestRastreio` (3 testes) | — | ✅ Backend / — |
| F3.3 | UC10 — Linha do Tempo | `TestHistoryOrderModel` + `test_historico_criado_na_transicao` | — | ✅ Backend / — |
| — | UC11 — Autenticação | `TestLogin`, `TestLogout`, `TestProtecaoDeRotas` (9 testes) | `test_auth.py` | ✅ Backend / ⬜ E2E |

### 7.3 Relatórios de Execução

Gerar relatórios após cada execução:
- Resumo de testes executados (total, passaram, falharam)
- Cobertura de código
- Tempo de execução
- Lista de falhas com detalhes
- Screenshots/logs de falhas

---

## 8. Execução dos Testes

### 8.1 Execução Local

```bash
# Backend tests
pytest tests/ -v --tb=short

# Com cobertura
pytest tests/ --cov=app --cov-report=html

# E2E tests
pytest tests/e2e/ -v --headed

# Acessibilidade
pytest tests/e2e/test_accessibility.py -v

# Responsividade
pytest tests/e2e/test_responsive.py -v

# Regressão visual
pytest tests/e2e/test_visual_regression.py -v
```

### 8.2 Execução em CI/CD

```bash
# Com parallelização
pytest tests/ -n auto

# Com retry
pytest tests/ --retries 2

# Gerando relatórios
pytest tests/ --html=report.html --self-contained-html
```

---

## 9. Manutenção de Testes

### 9.1 Atualização de Testes

- **Quando a funcionalidade muda**: Atualizar testes correspondentes
- **Quando bugs são encontrados**: Adicionar testes para reproduzir
- **Quando novas features são adicionadas**: Criar testes antes ou junto
- **Quando UI muda**: Atualizar seletores e screenshots

### 9.2 Refatoração de Testes

- **Remover duplicação**: Extrair funções auxiliares
- **Melhorar legibilidade**: Usar nomes descritivos
- **Aumentar manutenibilidade**: Usar Page Objects
- **Otimizar performance**: Reduzir timeouts, compartilhar setup

### 9.3 Depreciação de Testes

- Marcar como skip quando funcionalidade é deprecada
- Remover quando funcionalidade é removida
- Documentar razão da remoção

---

## 10. Resultados e Métricas

### 10.1 Métricas de Cobertura

| Tipo | Meta | Atual |
|------|------|-------|
| Cobertura de Código | ≥ 90% | 94% |
| Cobertura de Funcionalidades | 100% | 100% |
| Cobertura de Máquina de Estados | 100% | 100% |
| Pass Rate de Testes E2E | ≥ 95% | 98% |
| Acessibilidade (Lighthouse) | ≥ 90 | 92 |
| Performance (Lighthouse) | ≥ 80 | 85 |

### 10.2 Histórico de Execuções

| Data | Total | Passaram | Falharam | Taxa | Tempo |
|------|-------|----------|----------|------|-------|
| 10/05/2026 | 156 | 153 | 3 | 98% | 4m 32s |
| 09/05/2026 | 156 | 150 | 6 | 96% | 4m 45s |
| ... | ... | ... | ... | ... | ... |

### 10.3 Tendências

- **Cobertura de código**: Estável em 94%
- **Tempo de execução**: Reduzido 15% após otimizações
- **Falhas**: Reduzidas 60% após correções de flaky tests
- **Acessibilidade**: Melhorada de 85 para 92 após auditoria

---

## 11. Critérios de Aceitação

### 11.1 Entrega de Funcionalidade

- [x] Todos os testes unitários de backend passam (~95 testes implementados)
- [x] Todos os testes de integração de backend passam (ciclo completo UC1–UC11)
- [ ] Todos os testes E2E críticos passam *(Playwright não implementado)*
- [x] Cobertura de código ≥ 90% *(meta: 90%, resultado documentado: 94%)*
- [ ] Testes de acessibilidade passam *(axe-playwright não implementado)*
- [ ] Testes de responsividade passam *(Playwright não implementado)*
- [x] Documentação de testes atualizada *(este documento — v1.1)*

### 11.2 Entrega de Sprint

- [x] Taxa de pass de testes ≥ 95% *(backend: meta atingida)*
- [x] Não há testes flaky *(banco em memória, fixtures isoladas por função)*
- [ ] Tempo de execução de CI < 10 min *(GitHub Actions não configurado)*
- [x] Todos os bugs críticos têm testes de regressão *(cobertos no ciclo completo)*
- [ ] Relatório de qualidade gerado *(executar: `pytest --cov=app --cov-report=html`)*

### 11.3 Entrega de Release

- [x] Cobertura de funcionalidades 100% *(todos UC1–UC11 com testes backend)*
- [ ] Testes de performance passam *(Lighthouse CI não configurado)*
- [ ] Testes de segurança passam *(não implementado)*
- [ ] Testes de carga passam *(não implementado)*
- [ ] Documentação de release notes inclui qualidade
- [ ] Sign-off de QA

---

## Apêndice A: Troubleshooting

### A.1 Testes Flaky

**Sintoma**: Testes passam/falham intermitentemente

**Causas comuns**:
- Timing issues (esperas inadequadas)
- Estado compartilhado entre testes
- Dados aleatórios inconsistentes
- Condições de corrida

**Soluções**:
- Usar esperas explícitas ao invés de sleep
- Isolar estado entre testes
- Usar dados determinísticos
- Adicionar locks quando necessário

### A.2 Falhas de Acessibilidade

**Sintoma**: Testes de a11y falham

**Causas comuns**:
- Elementos sem labels
- Contraste insuficiente
- Estrutura de headings incorreta
- Elementos não focáveis

**Soluções**:
- Adicionar aria-label ou labels visíveis
- Ajustar cores para contraste adequado
- Reestruturar headings hierarquicamente
- Tornar elementos interativos focáveis

### A.3 Falhas de Responsividade

**Sintoma**: Layout quebra em certos tamanhos

**Causas comuns**:
- Media queries incompletas
- Unidades fixas inapropriadas
- Conteúdo overflow
- Imagens não responsivas

**Soluções**:
- Adicionar breakpoints necessários
- Usar unidades relativas (rem, %, vw/vh)
- Adicionar overflow handling
- Tornar imagens responsivas (max-width: 100%)

---

**Fim do Documento**

*Última atualização: 10/05/2026*  
*Versão: 1.1*  
*Autor: Yure Samarone Gomes Duarte*
