# Especificações de Frontend - EletroService

**Versão:** 1.0  
**Data:** 10/05/2026  
**Autor:** Yure Samarone Gomes Duarte  

---

## 1. Visão Geral

O frontend do EletroService é uma aplicação web desenvolvida com o framework Flask (Python), utilizando templates Jinja2, Bootstrap 5.3 para estilização e JavaScript vanilla para interatividade. O sistema segue uma arquitetura MVC tradicional com renderização server-side.

### 1.1 Stack Tecnológico

| Camada | Tecnologia | Versão | Finalidade |
|--------|------------|--------|------------|
| **Framework** | Flask | 3.x | Backend e renderização |
| **Templates** | Jinja2 | 3.x | Engine de templates |
| **CSS Framework** | Bootstrap | 5.3.3 | Estilização base |
| **Icons** | Bootstrap Icons | 1.11.1 | Ícones do sistema |
| **Charts** | Chart.js | 4.x | Gráficos e dashboards |
| **JS Runtime** | Vanilla JS | ES6+ | Interatividade |

### 1.2 Estrutura de Diretórios

```
app/
├── templates/              # Templates Jinja2
│   ├── base.html          # Layout base
│   ├── index.html         # Página inicial
│   ├── auth/              # Autenticação
│   │   └── login.html
│   ├── work_orders/       # Ordens de serviço
│   │   ├── list.html
│   │   ├── create.html
│   │   ├── edit.html
│   │   └── show_public.html
│   ├── reports/           # Relatórios
│   │   ├── index.html
│   │   ├── dashboard.html
│   │   └── entrada_saida.html
│   └── users/             # Gestão de usuários
│       ├── list.html
│       ├── create.html
│       └── edit.html
├── static/                # Assets estáticos
│   ├── css/
│   │   └── style.css      # Estilos customizados
│   └── js/
│       └── app.js         # Scripts da aplicação
└── ...
```

---

## 2. Design System

### 2.1 Paleta de Cores

#### Cores Primárias (Bootstrap)

| Nome | Hex | Uso |
|------|-----|-----|
| Primary | `#0d6efd` | Botões primários, links, navegação ativa |
| Secondary | `#6c757d` | Botões secundários, textos muted |
| Success | `#198754` | Sucesso, finalizado, confirmar |
| Danger | `#dc3545` | Erros, cancelamento, exclusão |
| Warning | `#ffc107` | Alertas, aguardando pagamento |
| Info | `#0dcaf0` | Informações, em orçamento |
| Light | `#f8f9fa` | Fundos, cards |
| Dark | `#212529` | Textos, headers |

#### Cores de Status (EletroService)

| Status | Classe Bootstrap | Cor | Uso |
|--------|------------------|-----|-----|
| Em Orçamento | `bg-info text-dark` | Ciano | OS recém-criada |
| Em Manutenção | `bg-primary` | Azul | OS em reparo |
| Aguardando Pagamento | `bg-warning text-dark` | Amarelo | Serviço concluído |
| Aguardando Retirada | `bg-secondary` | Cinza | Pagamento confirmado |
| Finalizado | `bg-success` | Verde | OS concluída |
| Cancelado | `bg-danger` | Vermelho | OS cancelada |

### 2.2 Tipografia

| Elemento | Fonte | Tamanho | Peso | Uso |
|----------|-------|---------|------|-----|
| H1 | System UI / -apple-system | 2.5rem (40px) | 700 | Títulos de página |
| H2 | System UI | 2rem (32px) | 600 | Seções principais |
| H3 | System UI | 1.75rem (28px) | 600 | Subseções |
| H4 | System UI | 1.5rem (24px) | 600 | Cards headers |
| H5 | System UI | 1.25rem (20px) | 600 | Labels, títulos menores |
| Body | System UI | 1rem (16px) | 400 | Texto padrão |
| Small | System UI | 0.875rem (14px) | 400 | Legendas, hints |
| Lead | System UI | 1.25rem (20px) | 300 | Destaques, hero text |

### 2.3 Espaçamento

| Nome | Valor | Uso |
|------|-------|-----|
| xs | 0.25rem (4px) | Espaçamento mínimo |
| sm | 0.5rem (8px) | Input groups, botões pequenos |
| md | 1rem (16px) | Cards, formulários |
| lg | 1.5rem (24px) | Seções, containers |
| xl | 3rem (48px) | Hero sections, grandes gaps |

### 2.4 Breakpoints Responsivos

| Breakpoint | Dimensão | Uso |
|------------|----------|-----|
| xs | < 576px | Mobile portrait |
| sm | >= 576px | Mobile landscape |
| md | >= 768px | Tablet |
| lg | >= 992px | Desktop |
| xl | >= 1200px | Large desktop |
| xxl | >= 1400px | Extra large |

---

## 3. Componentes de Interface

### 3.1 Layout Base (base.html)

O layout base é a fundação de todas as páginas, fornecendo:

- **Navbar responsiva** com menu colapsável
- **Sistema de mensagens flash** com auto-dismiss
- **Container principal** para conteúdo
- **Footer** (quando necessário)
- **Scripts base** (Bootstrap, app.js)

```html
<!-- Estrutura base -->
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}EletroService{% endblock %}</title>
    <!-- Bootstrap CSS -->
    <!-- Custom CSS -->
</head>
<body>
    <!-- Navbar -->
    <!-- Flash Messages -->
    <!-- Main Content -->
    <!-- Scripts -->
</body>
</html>
```

### 3.2 Cards

Cards são usados extensivamente para agrupar informações relacionadas.

**Card Padrão:**
```html
<div class="card shadow-sm">
    <div class="card-header bg-primary text-white">
        <h5 class="card-title mb-0">Título do Card</h5>
    </div>
    <div class="card-body">
        <!-- Conteúdo -->
    </div>
</div>
```

**Card de Métrica (Dashboard):**
```html
<div class="card border-primary border-2 h-100">
    <div class="card-body">
        <div class="d-flex justify-content-between align-items-start">
            <div>
                <h6 class="card-subtitle text-muted">Título</h6>
                <h2 class="mt-2 text-primary">Valor</h2>
            </div>
            <div class="bg-primary bg-opacity-10 p-2 rounded">
                <i class="bi bi-icon text-primary fs-4"></i>
            </div>
        </div>
    </div>
</div>
```

### 3.3 Formulários

**Estrutura de Campo com Validação:**
```html
<div class="mb-3">
    <label for="field_name" class="form-label">Label do Campo</label>
    <input type="text" 
           class="form-control {{ 'is-invalid' if form.field_name.errors else '' }}" 
           id="field_name" 
           name="field_name"
           value="{{ form.field_name.data or '' }}">
    {% if form.field_name.errors %}
        <div class="invalid-feedback">
            {{ form.field_name.errors[0] }}
        </div>
    {% endif %}
</div>
```

**Input com Ícone (Input Group):**
```html
<div class="input-group">
    <span class="input-group-text"><i class="bi bi-calendar-date"></i></span>
    <input type="date" class="form-control" name="date_field">
</div>
```

**Select com Bootstrap:**
```html
<div class="mb-3">
    <label class="form-label">Status</label>
    <select class="form-select" name="status">
        <option value="" selected>Selecione...</option>
        <option value="Em Orçamento">Em Orçamento</option>
        <option value="Em Manutenção">Em Manutenção</option>
        <!-- ... -->
    </select>
</div>
```

### 3.4 Tabelas

**Tabela com Ações:**
```html
<div class="table-responsive">
    <table class="table table-hover">
        <thead class="table-light">
            <tr>
                <th>Coluna 1</th>
                <th>Coluna 2</th>
                <th class="text-end">Ações</th>
            </tr>
        </thead>
        <tbody>
            {% for item in items %}
            <tr>
                <td>{{ item.field1 }}</td>
                <td>{{ item.field2 }}</td>
                <td class="text-end">
                    <div class="btn-group" role="group">
                        <a href="{{ url_for('edit', id=item.id) }}" 
                           class="btn btn-sm btn-outline-primary" title="Editar">
                            <i class="bi bi-pencil-square"></i>
                        </a>
                        <button type="button" 
                                class="btn btn-sm btn-outline-danger" 
                                data-bs-toggle="modal" 
                                data-bs-target="#deleteModal{{ item.id }}" title="Excluir">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
```

### 3.5 Modais

**Modal de Confirmação de Exclusão:**
```html
<div class="modal fade" id="deleteModal{{ item.id }}" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Confirmar Exclusão</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <p>Tem certeza que deseja excluir <strong>{{ item.name }}</strong>?</p>
                <p class="text-muted small">Esta ação não pode ser desfeita.</p>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                <form action="{{ url_for('delete', id=item.id) }}" method="POST" class="d-inline">
                    <button type="submit" class="btn btn-danger">Confirmar Exclusão</button>
                </form>
            </div>
        </div>
    </div>
</div>
```

### 3.6 Timeline (Linha do Tempo)

```html
<div class="timeline mt-4">
    {% for item in history %}
    <div class="timeline-item position-relative ps-4 pb-4 border-start border-2 border-light">
        <div class="timeline-marker position-absolute rounded-circle bg-primary" 
             style="width: 14px; height: 14px; left: -8px; top: 5px;"></div>
        <div class="timeline-content">
            <div class="d-flex justify-content-between align-items-center mb-1">
                <span class="fw-bold">{{ item.new_status }}</span>
                <small class="text-muted">{{ item.changed_at.strftime('%d/%m/%Y %H:%M') }}</small>
            </div>
            <p class="text-muted small mb-0">{{ item.description or 'Sem observações' }}</p>
        </div>
    </div>
    {% endfor %}
</div>

<style>
.timeline-item:last-child {
    border-start-color: transparent !important;
}
.timeline-marker {
    border: 3px solid white;
    box-shadow: 0 0 0 2px var(--bs-primary);
}
</style>
```

### 3.7 Badges de Status

```html
{% if status == 'Em Orçamento' %}
    <span class="badge bg-info text-dark">{{ status }}</span>
{% elif status == 'Em Manutenção' %}
    <span class="badge bg-primary">{{ status }}</span>
{% elif status == 'Aguardando Pagamento' %}
    <span class="badge bg-warning text-dark">{{ status }}</span>
{% elif status == 'Aguardando Retirada' %}
    <span class="badge bg-secondary">{{ status }}</span>
{% elif status == 'Finalizado' %}
    <span class="badge bg-success">{{ status }}</span>
{% elif status == 'Cancelado' %}
    <span class="badge bg-danger">{{ status }}</span>
{% endif %}
```

---

## 4. Comportamento Visual

### 4.1 Transições e Animações

**Durações Padrão:**
| Tipo | Duração | Uso |
|------|---------|-----|
| Hover rápido | 150ms | Botões, links |
| Hover padrão | 200ms | Cards, menus |
| Transição | 300ms | Modais, accordions |
| Animação | 500ms | Toasts, alerts |

**Efeitos Hover em Cards:**
```css
.card {
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.card:hover {
    transform: translateY(-5px);
    box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15) !important;
}
```

### 4.2 Estados de Feedback

**Loading States:**
```html
<!-- Botão com loading -->
<button class="btn btn-primary" type="button" disabled>
    <span class="spinner-border spinner-border-sm me-2" role="status"></span>
    Processando...
</button>

<!-- Skeleton loading para tabelas -->
<div class="placeholder-glow">
    <span class="placeholder col-12"></span>
</div>
```

**Toasts/Notificações:**
```html
<div class="toast-container position-fixed bottom-0 end-0 p-3">
    <div class="toast align-items-center text-white bg-success" role="alert">
        <div class="d-flex">
            <div class="toast-body">
                <i class="bi bi-check-circle me-2"></i>Operação realizada com sucesso!
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    </div>
</div>
```

### 4.3 Estados Vazios

```html
<!-- Estado vazio para listas -->
<div class="text-center py-5">
    <i class="bi bi-inbox fs-1 text-muted d-block mb-3"></i>
    <p class="text-muted mb-0">Nenhum registro encontrado.</p>
    <a href="{{ url_for('create') }}" class="btn btn-primary mt-3">
        <i class="bi bi-plus-lg me-1"></i>Criar Novo
    </a>
</div>

<!-- Estado vazio para buscas -->
<div class="text-center py-5">
    <i class="bi bi-search fs-1 text-muted d-block mb-3"></i>
    <p class="text-muted">Nenhum resultado encontrado para "{{ search_term }}".</p>
    <a href="{{ url_for('list') }}" class="btn btn-outline-secondary mt-2">
        Limpar Busca
    </a>
</div>
```

---

## 5. Responsividade

### 5.1 Grid System

Utilizando o sistema de grid do Bootstrap 5:

```html
<!-- Layout de 3 colunas em desktop, 1 em mobile -->
<div class="row">
    <div class="col-12 col-md-4 mb-3">
        <!-- Card 1 -->
    </div>
    <div class="col-12 col-md-4 mb-3">
        <!-- Card 2 -->
    </div>
    <div class="col-12 col-md-4 mb-3">
        <!-- Card 3 -->
    </div>
</div>

<!-- Layout com sidebar em desktop, stack em mobile -->
<div class="row">
    <div class="col-12 col-lg-8">
        <!-- Conteúdo principal -->
    </div>
    <div class="col-12 col-lg-4 mt-4 mt-lg-0">
        <!-- Sidebar -->
    </div>
</div>
```

### 5.2 Tabelas Responsivas

```html
<div class="table-responsive">
    <table class="table table-hover">
        <!-- ... -->
    </table>
</div>
```

### 5.3 Navegação Responsiva

A navbar colapsa automaticamente em dispositivos menores:

```html
<nav class="navbar navbar-expand-lg navbar-dark bg-dark">
    <div class="container">
        <a class="navbar-brand" href="/">EletroService</a>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
            <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarNav">
            <!-- Menu items -->
        </div>
    </div>
</nav>
```

---

## 6. Acessibilidade

### 6.1 Requisitos Obrigatórios

| Requisito | Implementação | Prioridade |
|-----------|---------------|------------|
| **Contraste** | Razão mínima 4.5:1 para texto normal | Alta |
| **Navegação por Teclado** | Todos os elementos interativos focáveis | Alta |
| **Foco Visível** | Outline claro em elementos focados | Alta |
| **Labels de Formulário** | Todos os inputs possuem `<label>` | Alta |
| **Alt Text** | Imagens com descrição apropriada | Média |
| **ARIA Labels** | Elementos sem texto visível | Média |
| **Skip Links** | Link para pular navegação | Média |

### 6.2 Implementações

**Foco Visível:**
```css
/* Estilo consistente para foco */
*:focus-visible {
    outline: 3px solid #0d6efd;
    outline-offset: 2px;
}

/* Remover outline padrão, mas manter para keyboard */
*:focus:not(:focus-visible) {
    outline: none;
}
```

**Labels e ARIA:**
```html
<!-- Label explícito -->
<label for="email" class="form-label">Email *</label>
<input type="email" id="email" name="email" class="form-control" required aria-required="true">

<!-- Label com ícone (acessibilidade) -->
<label for="search" class="form-label">
    <i class="bi bi-search" aria-hidden="true"></i>
    <span class="visually-hidden">Buscar</span>
</label>

<!-- Botão com aria-label -->
<button type="button" class="btn btn-primary" aria-label="Fechar modal">
    <i class="bi bi-x-lg" aria-hidden="true"></i>
</button>
```

**Skip Link:**
```html
<!-- No início do body -->
<a href="#main-content" class="visually-hidden-focusable">
    Pular para conteúdo principal
</a>

<!-- Main content -->
<main id="main-content" class="container">
    <!-- Conteúdo -->
</main>
```

### 6.3 Validação de Acessibilidade

- [ ] Navegação completa via teclado (Tab, Shift+Tab, Enter, Space, Esc)
- [ ] Leitura de tela (NVDA, JAWS, VoiceOver) identifica todos os elementos
- [ ] Contraste validado em todas as telas (WebAIM Contrast Checker)
- [ ] Formulários possuem labels associados
- [ ] Imagens possuem alt text apropriado
- [ ] Links e botões possuem textos descritivos
- [ ] Modais gerenciam foco corretamente
- [ ] Skip links funcionam em todas as páginas

---

## 7. Fluxos de Navegação

### 7.1 Fluxo Principal (Administrador)

```
Login → Dashboard → Menu Principal
    ├── Ordens de Serviço
    │   ├── Listar (com filtros)
    │   ├── Criar Nova OS
    │   ├── Editar OS
    │   └── Excluir OS (com confirmação)
    ├── Relatórios
    │   ├── Dashboard de Produtividade
    │   └── Relatório de Entrada/Saída
    └── Usuários
        ├── Listar
        ├── Criar
        ├── Editar
        └── Excluir
```

### 7.2 Fluxo de Cliente (Público)

```
Página Inicial → Rastreamento
    ├── Inserir Código
    ├── Visualizar Status Atual
    └── Expandir Linha do Tempo
```

### 7.3 Fluxo de Criação de OS

```
1. Acessar "Ordens de Serviço" → "Nova OS"
2. Preencher dados do solicitante:
   - Nome (obrigatório)
   - Email (obrigatório)
   - Telefone
   - Documento
3. Preencher dados da OS:
   - Descrição do problema (obrigatório, mín. 10 chars)
   - Data prevista de entrega (opcional)
4. Validar e submeter
5. Redirecionar para listagem com mensagem de sucesso
```

### 7.4 Fluxo de Atualização de Status

```
1. Acessar edição da OS
2. Visualizar status atual e próximo status disponível
3. Adicionar nota de atualização (opcional)
4. Clicar em "Avançar Status" ou "Cancelar OS"
5. Confirmar operação no modal de confirmação
6. Sistema registra no histórico e redireciona
```

---

## 8. Validações Visuais

### 8.1 Validação de Formulários

**Estados de Validação:**

| Estado | Classe | Aparência |
|--------|--------|-----------|
| Padrão | `form-control` | Borda cinza padrão |
| Foco | `form-control:focus` | Borda azul (primary) com shadow |
| Válido | `is-valid` | Borda verde + ícone de check |
| Inválido | `is-invalid` | Borda vermelha + mensagem de erro |

**Feedback de Erro:**
```html
<input type="email" 
       class="form-control is-invalid" 
       id="email" 
       name="email"
       value="email-invalido">
<div class="invalid-feedback">
    Por favor, informe um endereço de email válido.
</div>
```

**Indicadores de Campo Obrigatório:**
```html
<label for="name" class="form-label">
    Nome <span class="text-danger">*</span>
</label>
<input type="text" class="form-control" id="name" name="name" required>
```

### 8.2 Mensagens de Erro

**Toast de Erro:**
```html
<div class="toast align-items-center text-white bg-danger" role="alert">
    <div class="d-flex">
        <div class="toast-body">
            <i class="bi bi-exclamation-triangle me-2"></i>
            Erro ao processar a solicitação. Tente novamente.
        </div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
    </div>
</div>
```

**Alert de Erro na Página:**
```html
<div class="alert alert-danger alert-dismissible fade show" role="alert">
    <i class="bi bi-exclamation-triangle-fill me-2"></i>
    <strong>Erro!</strong> Não foi possível salvar a ordem de serviço.
    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
</div>
```

### 8.3 Mensagens de Sucesso

**Toast de Sucesso:**
```html
<div class="toast align-items-center text-white bg-success" role="alert">
    <div class="d-flex">
        <div class="toast-body">
            <i class="bi bi-check-circle me-2"></i>
            Ordem de serviço criada com sucesso!
        </div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
    </div>
</div>
```

**Flash Message (Server-side):**
```html
{% with messages = get_flashed_messages(with_categories=true) %}
    {% if messages %}
        {% for category, message in messages %}
            <div class="alert alert-{{ category }} alert-dismissible fade show" role="alert">
                {{ message }}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        {% endfor %}
    {% endif %}
{% endwith %}
```

---

## 9. Feedbacks de Carregamento

### 9.1 Skeleton Loading

```html
<!-- Estado de loading para cards -->
<div class="card" aria-busy="true" aria-label="Carregando dados">
    <div class="card-body">
        <div class="placeholder-glow">
            <span class="placeholder col-6"></span>
        </div>
        <div class="placeholder-glow mt-3">
            <span class="placeholder col-12"></span>
            <span class="placeholder col-10"></span>
        </div>
    </div>
</div>
```

### 9.2 Spinners

```html
<!-- Spinner em botão -->
<button class="btn btn-primary" type="button" disabled>
    <span class="spinner-border spinner-border-sm me-2" aria-hidden="true"></span>
    <span role="status">Processando...</span>
</button>

<!-- Spinner em página -->
<div class="text-center py-5">
    <div class="spinner-border text-primary" role="status" style="width: 3rem; height: 3rem;">
        <span class="visually-hidden">Carregando...</span>
    </div>
    <p class="mt-3 text-muted">Carregando dados...</p>
</div>

<!-- Spinner de progresso -->
<div class="progress" role="progressbar" aria-label="Progresso" aria-valuenow="75" aria-valuemin="0" aria-valuemax="100">
    <div class="progress-bar progress-bar-striped progress-bar-animated" style="width: 75%">75%</div>
</div>
```

### 9.3 Placeholder de Conteúdo

```html
<!-- Estado de loading para tabela -->
<tr class="placeholder-glow">
    <td><span class="placeholder col-6"></span></td>
    <td><span class="placeholder col-8"></span></td>
    <td><span class="placeholder col-4"></span></td>
    <td><span class="placeholder col-3"></span></td>
</tr>
```

---

## 10. Consistência de Layout

### 10.1 Padrões de Página

**Página de Listagem:**
```
+--------------------------------------------------+
| Header com Título + Botão Novo                   |
+--------------------------------------------------+
| [Card com Tabela Responsiva]                     |
| +----------------------------------------------+ |
| | Colunas | Ações (Editar/Excluir)             | |
| +----------------------------------------------+ |
| [Paginação se necessário]                        |
+--------------------------------------------------+
```

**Página de Formulário:**
```
+--------------------------------------------------+
| Header com Título + Botão Voltar                 |
+--------------------------------------------------+
| [Card Seção 1 - Dados Principais]                |
| [Card Seção 2 - Dados Adicionais]                |
| ...                                              |
| [Botões: Cancelar | Salvar]                      |
+--------------------------------------------------+
```

**Página de Detalhes:**
```
+--------------------------------------------------+
| Header com Status + Ações Principais             |
+--------------------------------------------------+
| [Card Informações Principais]                    |
| [Card Timeline/Histórico]                        |
| [Card Dados Técnicos/Adicionais]                 |
+--------------------------------------------------+
```

### 10.2 Hierarquia Visual

**Ordem de Importância Visual:**
1. **Títulos de página** (H1) - Maior destaque
2. **Botões de ação primária** - Cores vibrantes (primary, success)
3. **Dados importantes** - Badges, números grandes
4. **Cards de seção** - Containers bem definidos
5. **Texto secundário** - Cores muted, tamanho menor
6. **Dados auxiliares** - tooltips, hints

### 10.3 Alinhamento e Espaçamento

**Padrões de Container:**
```html
<!-- Container padrão -->
<div class="container py-4">
    <!-- Conteúdo -->
</div>

<!-- Container fluido -->
<div class="container-fluid px-4 py-4">
    <!-- Conteúdo -->
</div>

<!-- Container centralizado com max-width -->
<div class="container">
    <div class="row justify-content-center">
        <div class="col-md-8 col-lg-6">
            <!-- Conteúdo centralizado -->
        </div>
    </div>
</div>
```

**Espaçamento Consistente:**
```html
<!-- Margins -->
<div class="mb-4">  <!-- margin-bottom: 1.5rem -->
<div class="mt-3">  <!-- margin-top: 1rem -->
<div class="my-4">  <!-- margin-y: 1.5rem -->

<!-- Paddings -->
<div class="p-4">   <!-- padding: 1.5rem -->
<div class="px-3">  <!-- padding-x: 1rem -->
<div class="py-4">  <!-- padding-y: 1.5rem -->

<!-- Combinações comuns -->
<div class="card p-4 mb-4">
<div class="container py-4">
<div class="px-3 py-2">
```

---

## 11. Integração Frontend/Backend

### 11.1 Contrato de Dados

**Padrão de Resposta JSON:**
```json
{
    "success": true,
    "data": {
        // Dados específicos do endpoint
    },
    "message": "Operação realizada com sucesso",
    "meta": {
        "page": 1,
        "per_page": 10,
        "total": 100
    }
}
```

**Padrão de Erro:**
```json
{
    "success": false,
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Dados de entrada inválidos",
        "details": {
            "email": ["Email inválido"],
            "name": ["Nome é obrigatório"]
        }
    }
}
```

### 11.2 Rotas da API (Frontend)

| Endpoint | Método | Descrição | Response |
|----------|--------|-----------|----------|
| `/relatorios/api/status-data` | GET | Dados para gráfico de status | JSON Chart.js |
| `/relatorios/api/daily-data` | GET | Dados para gráfico diário | JSON Chart.js |
| `/api/work-orders` | GET | Lista paginada de OS | JSON |
| `/api/work-orders/:id` | GET | Detalhes de uma OS | JSON |

### 11.3 Manipulação de Dados no Frontend

**Fetch API para Gráficos:**
```javascript
// Carregar dados para gráfico de status
async function loadStatusChart() {
    try {
        const response = await fetch('/relatorios/api/status-data');
        if (!response.ok) throw new Error('Erro ao carregar dados');
        
        const data = await response.json();
        renderStatusChart(data);
    } catch (error) {
        console.error('Erro:', error);
        showErrorMessage('Não foi possível carregar o gráfico');
    }
}
```

**Atualização Dinâmica de Métricas:**
```javascript
// Atualizar métricas do dashboard
async function updateQuickMetrics() {
    const response = await fetch('/relatorios/api/status-data');
    const data = await response.json();
    
    // Calcular totais
    let total = 0, completed = 0, canceled = 0;
    data.labels.forEach((label, i) => {
        const count = data.datasets[0].data[i];
        total += count;
        if (label === 'Finalizado') completed = count;
        if (label === 'Cancelado') canceled = count;
    });
    
    // Atualizar DOM
    document.getElementById('totalOrders').textContent = total;
    document.getElementById('completedOrders').textContent = completed;
    document.getElementById('canceledOrders').textContent = canceled;
}
```

---

## 12. Regras de Renderização

### 12.1 Renderização Condicional

**Exibição por Autenticação:**
```html
{% if current_user.is_authenticated %}
    <!-- Conteúdo para usuários logados -->
    <a href="{{ url_for('auth.logout') }}">Sair</a>
{% else %}
    <!-- Conteúdo para visitantes -->
    <a href="{{ url_for('auth.login') }}">Login</a>
{% endif %}
```

**Exibição por Permissão/Status:**
```html
{% if order.status != 'Finalizado' and order.status != 'Cancelado' %}
    <!-- Botões de ação apenas para OS ativas -->
    <button class="btn btn-primary">Avançar Status</button>
{% endif %}
```

**Renderização de Campos Condicionais:**
```html
<!-- Campos financeiros aparecem apenas após "Em Orçamento" -->
{% if order.status != 'Em Orçamento' %}
<div class="col-md-6">
    <label class="form-label">Valor da Mão de Obra</label>
    <input type="number" class="form-control" name="labor_cost" value="{{ order.labor_cost }}">
</div>
{% endif %}
```

### 12.2 Renderização de Listas

**Loop com Estado Vazio:**
```html
{% for order in orders %}
    <tr>
        <td>{{ order.number }}</td>
        <td>{{ order.requester.name }}</td>
        <td>{{ order.status }}</td>
    </tr>
{% else %}
    <tr>
        <td colspan="3" class="text-center py-5">
            <i class="bi bi-inbox fs-1 text-muted d-block mb-3"></i>
            <p class="text-muted">Nenhuma ordem de serviço encontrada.</p>
            <a href="{{ url_for('work_orders.create') }}" class="btn btn-primary">
                Criar Nova OS
            </a>
        </td>
    </tr>
{% endfor %}
```

**Paginação (quando implementada):**
```html
<nav aria-label="Navegação de páginas">
    <ul class="pagination justify-content-center">
        <li class="page-item {% if not has_prev %}disabled{% endif %}">
            <a class="page-link" href="?page={{ current_page - 1 }}">Anterior</a>
        </li>
        {% for page in range(1, total_pages + 1) %}
        <li class="page-item {% if page == current_page %}active{% endif %}">
            <a class="page-link" href="?page={{ page }}">{{ page }}</a>
        </li>
        {% endfor %}
        <li class="page-item {% if not has_next %}disabled{% endif %}">
            <a class="page-link" href="?page={{ current_page + 1 }}">Próxima</a>
        </li>
    </ul>
</nav>
```

### 12.3 Formatação de Dados

**Datas:**
```html
<!-- Formato brasileiro: DD/MM/YYYY -->
<span>{{ order.date.strftime('%d/%m/%Y') }}</span>

<!-- Com hora: DD/MM/YYYY às HH:MM -->
<span>{{ order.date.strftime('%d/%m/%Y às %H:%M') }}</span>
```

**Valores Monetários:**
```html
<!-- Formato: R$ 1.234,56 -->
<span>R$ {{ "%.2f"|format(order.final_price) }}</span>

<!-- Ou com filter custom -->
<span>{{ order.final_price | currency }}</span>
```

**Textos (truncate):**
```html
<!-- Limitar texto longo -->
<p>{{ long_text|truncate(100) }}</p>
```

---

## 13. Tratamento de Estados Vazios

### 13.1 Estados Vazios por Contexto

**Lista Vazia:**
```html
<div class="text-center py-5">
    <i class="bi bi-inbox fs-1 text-muted d-block mb-3"></i>
    <h5 class="text-muted">Nenhum registro encontrado</h5>
    <p class="text-muted mb-3">Comece criando um novo registro.</p>
    <a href="{{ url_for('create') }}" class="btn btn-primary">
        <i class="bi bi-plus-lg me-1"></i>Criar Novo
    </a>
</div>
```

**Busca sem Resultados:**
```html
<div class="text-center py-5">
    <i class="bi bi-search fs-1 text-muted d-block mb-3"></i>
    <h5 class="text-muted">Nenhum resultado encontrado</h5>
    <p class="text-muted mb-3">Sua busca por "{{ search_term }}" não retornou resultados.</p>
    <div class="d-flex justify-content-center gap-2">
        <a href="{{ url_for('list') }}" class="btn btn-outline-secondary">
            Limpar Busca
        </a>
        <a href="{{ url_for('create') }}" class="btn btn-primary">
            Criar Novo
        </a>
    </div>
</div>
```

**Erro de Carregamento:**
```html
<div class="text-center py-5">
    <i class="bi bi-exclamation-triangle fs-1 text-warning d-block mb-3"></i>
    <h5 class="text-muted">Erro ao carregar dados</h5>
    <p class="text-muted mb-3">Não foi possível carregar os dados. Tente novamente.</p>
    <button class="btn btn-primary" onclick="location.reload()">
        <i class="bi bi-arrow-clockwise me-1"></i>Recarregar Página
    </button>
</div>
```

### 13.2 Placeholders de Conteúdo

```html
<!-- Placeholder para cards em loading -->
<div class="card" aria-busy="true">
    <div class="card-body">
        <h5 class="card-title placeholder-glow">
            <span class="placeholder col-6"></span>
        </h5>
        <p class="card-text placeholder-glow">
            <span class="placeholder col-7"></span>
            <span class="placeholder col-4"></span>
            <span class="placeholder col-4"></span>
            <span class="placeholder col-6"></span>
            <span class="placeholder col-8"></span>
        </p>
    </div>
</div>
```

---

## 14. Comportamento de Formulários

### 14.1 Validação em Tempo Real

```javascript
// Validação de email em tempo real
document.getElementById('email').addEventListener('blur', function(e) {
    const email = e.target.value;
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    
    if (email && !emailRegex.test(email)) {
        e.target.classList.add('is-invalid');
        // Mostrar mensagem de erro
    } else {
        e.target.classList.remove('is-invalid');
        e.target.classList.add('is-valid');
    }
});

// Validação de senha forte
document.getElementById('password').addEventListener('input', function(e) {
    const password = e.target.value;
    const strength = checkPasswordStrength(password);
    updatePasswordStrengthIndicator(strength);
});
```

### 14.2 Máscaras de Input

```javascript
// Máscara de telefone
function formatPhone(value) {
    return value
        .replace(/\D/g, '')
        .replace(/(\d{2})(\d)/, '($1) $2')
        .replace(/(\d{5})(\d)/, '$1-$2')
        .replace(/(-\d{4})\d+?$/, '$1');
}

document.getElementById('phone').addEventListener('input', function(e) {
    e.target.value = formatPhone(e.target.value);
});

// Máscara de CPF/CNPJ
function formatDocument(value) {
    const cleaned = value.replace(/\D/g, '');
    if (cleaned.length <= 11) {
        // CPF: 000.000.000-00
        return cleaned
            .replace(/(\d{3})(\d)/, '$1.$2')
            .replace(/(\d{3})(\d)/, '$1.$2')
            .replace(/(\d{3})(\d{1,2})$/, '$1-$2');
    } else {
        // CNPJ: 00.000.000/0000-00
        return cleaned
            .replace(/(\d{2})(\d)/, '$1.$2')
            .replace(/(\d{3})(\d)/, '$1.$2')
            .replace(/(\d{3})(\d)/, '$1/$2')
            .replace(/(\d{4})(\d{1,2})$/, '$1-$2');
    }
}
```

### 14.3 Autosave e Recuperação

```javascript
// Autosave de formulário
let autoSaveInterval;
const form = document.getElementById('workOrderForm');

function startAutoSave() {
    autoSaveInterval = setInterval(() => {
        saveDraft();
    }, 30000); // A cada 30 segundos
}

function saveDraft() {
    const formData = new FormData(form);
    const draft = {};
    formData.forEach((value, key) => {
        draft[key] = value;
    });
    
    localStorage.setItem('workOrderDraft', JSON.stringify(draft));
    localStorage.setItem('workOrderDraftTime', new Date().toISOString());
    
    showToast('Rascunho salvo', 'info');
}

function restoreDraft() {
    const draft = localStorage.getItem('workOrderDraft');
    const draftTime = localStorage.getItem('workOrderDraftTime');
    
    if (draft && draftTime) {
        const timeDiff = Date.now() - new Date(draftTime).getTime();
        const hoursDiff = timeDiff / (1000 * 60 * 60);
        
        if (hoursDiff < 24) { // Restaurar apenas se menos de 24h
            const draftData = JSON.parse(draft);
            
            // Preencher formulário
            Object.keys(draftData).forEach(key => {
                const field = form.querySelector(`[name="${key}"]`);
                if (field) field.value = draftData[key];
            });
            
            showToast('Rascunho restaurado', 'info');
        }
    }
}

// Inicializar
if (form) {
    restoreDraft();
    startAutoSave();
    
    // Salvar ao enviar
    form.addEventListener('submit', () => {
        localStorage.removeItem('workOrderDraft');
        localStorage.removeItem('workOrderDraftTime');
    });
}
```

---

## 15. Padrões de Interação

### 15.1 Clique vs Duplo Clique

- **Clique único:** Seleção, navegação, ativação de botões
- **Duplo clique:** Edição rápida em tabelas (quando implementado)
- **Clique longo:** Menu contextual em dispositivos touch

### 15.2 Hover States

**Elementos Interativos:**
```css
/* Botões */
.btn:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

/* Cards */
.card:hover {
    transform: translateY(-5px);
    box-shadow: 0 0.5rem 1rem rgba(0,0,0,0.15);
}

/* Links em tabelas */
.table a:hover {
    text-decoration: underline;
}

/* Itens de menu */
.nav-link:hover {
    background-color: rgba(255,255,255,0.1);
}
```

### 15.3 Atalhos de Teclado

| Atalho | Ação | Contexto |
|--------|------|----------|
| `Ctrl + N` | Nova OS | Qualquer página |
| `Ctrl + F` | Buscar/Foco no search | Páginas de lista |
| `Esc` | Fechar modal | Modais abertos |
| `Enter` | Confirmar ação | Modais de confirmação |
| `Tab` | Navegar entre campos | Formulários |
| `Ctrl + S` | Salvar rascunho | Formulários |

---

## 16. Padronização de Design System

### 16.1 Nomenclatura de Classes

**Padrão BEM (Block Element Modifier):**
```html
<!-- Block -->
<div class="order-card">
    <!-- Element -->
    <div class="order-card__header">
        <h3 class="order-card__title"></h3>
    </div>
    <!-- Element com Modifier -->
    <div class="order-card__status order-card__status--urgent"></div>
</div>
```

**Classes Utilitárias (Bootstrap):**
```html
<div class="d-flex justify-content-between align-items-center p-3 mb-4 bg-light rounded">
```

### 16.2 Organização de CSS

**Estrutura do style.css:**
```css
/* 1. Variáveis e Configurações */
:root {
    --primary-color: #0d6efd;
    --secondary-color: #6c757d;
    /* ... */
}

/* 2. Reset e Base */
body {
    background-color: #f8f9fa;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* 3. Utilitários */
.cursor-pointer { cursor: pointer; }
.transition-all { transition: all 0.2s ease; }

/* 4. Componentes Customizados */
.card {
    box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
    transition: transform 0.2s, box-shadow 0.2s;
}

.card:hover {
    transform: translateY(-2px);
    box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
}

/* 5. Timeline Customizada */
.timeline {
    position: relative;
}

.timeline-item {
    position: relative;
    padding-left: 1.5rem;
    padding-bottom: 1.5rem;
    border-left: 2px solid #dee2e6;
}

.timeline-item:last-child {
    border-left-color: transparent;
}

.timeline-marker {
    position: absolute;
    left: -0.5rem;
    top: 0.25rem;
    width: 1rem;
    height: 1rem;
    border-radius: 50%;
    background-color: var(--primary-color);
    border: 3px solid white;
    box-shadow: 0 0 0 2px var(--primary-color);
}

/* 6. Utilitários de Status */
.status-badge {
    display: inline-flex;
    align-items: center;
    padding: 0.375rem 0.75rem;
    border-radius: 0.375rem;
    font-size: 0.875rem;
    font-weight: 500;
}

.status-badge::before {
    content: '';
    display: inline-block;
    width: 0.5rem;
    height: 0.5rem;
    border-radius: 50%;
    margin-right: 0.5rem;
}

/* 7. Media Queries */
@media (max-width: 768px) {
    .card-title {
        font-size: 1.1rem;
    }
    
    .table-responsive {
        font-size: 0.875rem;
    }
    
    .btn-group .btn {
        padding: 0.25rem 0.5rem;
        font-size: 0.875rem;
    }
}

/* 8. Animações */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

.animate-fade-in {
    animation: fadeIn 0.3s ease-out;
}

@keyframes slideIn {
    from { transform: translateX(-100%); }
    to { transform: translateX(0); }
}

.animate-slide-in {
    animation: slideIn 0.3s ease-out;
}
```

---

## 17. Melhorias Implementadas

### 17.1 Melhorias Visuais

1. **Sistema de Cores Consistente**: Padronização de cores para cada status de OS
2. **Cards com Hover Effects**: Animações sutis para melhor feedback visual
3. **Timeline Customizada**: Visualização clara do histórico de alterações
4. **Badges Informativos**: Indicadores visuais de status e métricas
5. **Toast Notifications**: Feedback não-intrusivo para ações do usuário

### 17.2 Melhorias de UX

1. **Copy to Clipboard**: Funcionalidade de copiar link de rastreio
2. **Confirmações em Modais**: Confirmação antes de exclusão/cancelamento
3. **Estados de Loading**: Feedback durante carregamento de dados
4. **Estados Vazios Informativos**: Orientação quando não há dados
5. **Tooltips e Hints**: Ajuda contextual em campos complexos

### 17.3 Melhorias de Responsividade

1. **Tabelas Responsivas**: Scroll horizontal em dispositivos pequenos
2. **Cards em Grid**: Layout adaptativo para diferentes tamanhos de tela
3. **Menu Colapsável**: Navbar responsiva com toggle
4. **Fontes Escaláveis**: Tamanhos relativos para melhor legibilidade
5. **Touch Targets**: Áreas de toque adequadas para dispositivos móveis

### 17.4 Melhorias de Acessibilidade

1. **ARIA Labels**: Identificação de elementos para leitores de tela
2. **Foco Visível**: Indicação clara do elemento focado
3. **Contraste Adequado**: Cores acessíveis conforme WCAG
4. **Labels Associadas**: Todos os inputs possuem labels
5. **Mensagens de Erro Claras**: Feedback compreensível para erros

---

## 18. Checklist de Qualidade Frontend

### 18.1 Verificações Visuais

- [ ] Paleta de cores consistente em toda a aplicação
- [ ] Tipografia legível e hierárquica
- [ ] Espaçamento consistente entre elementos
- [ ] Alinhamento correto de textos e componentes
- [ ] Contraste adequado entre texto e fundo
- [ ] Ícones padronizados e significativos
- [ ] Animações suaves e não intrusivas

### 18.2 Verificações Funcionais

- [ ] Todos os links e botões funcionam corretamente
- [ ] Formulários validam dados antes do envio
- [ ] Mensagens de erro são claras e úteis
- [ ] Confirmações são solicitadas para ações destrutivas
- [ ] Feedback visual para todas as ações do usuário
- [ ] Estados de loading são exibidos durante processamentos
- [ ] Redirecionamentos ocorrem após ações bem-sucedidas

### 18.3 Verificações de Responsividade

- [ ] Layout adapta-se a diferentes tamanhos de tela
- [ ] Navegação funciona em dispositivos móveis
- [ ] Tabelas são legíveis em telas pequenas
- [ ] Touch targets têm tamanho adequado
- [ ] Fontes são legíveis em todos os dispositivos
- [ ] Imagens escalam corretamente
- [ ] Modais e overlays funcionam em mobile

### 18.4 Verificações de Acessibilidade

- [ ] Navegação completa via teclado
- [ ] Foco visível em todos os elementos interativos
- [ ] Contraste mínimo de 4.5:1 para texto
- [ ] Todos os inputs possuem labels associados
- [ ] Imagens possuem alt text apropriado
- [ ] Leitor de tela identifica todos os elementos
- [ ] Skip links funcionam corretamente

### 18.5 Verificações de Performance

- [ ] Páginas carregam em menos de 3 segundos
- [ ] Imagens são otimizadas
- [ ] CSS e JS são minificados em produção
- [ ] Não há render-blocking resources
- [ ] Lazy loading é aplicado onde apropriado
- [ ] Caching está configurado corretamente

---

## 19. Manutenção e Evolução

### 19.1 Versionamento

O versionamento do frontend segue o padrão Semantic Versioning (SemVer):

| Versão | Descrição | Exemplo |
|--------|-----------|---------|
| **MAJOR** | Mudanças incompatíveis | 2.0.0 - Redesign completo |
| **MINOR** | Novas funcionalidades | 1.1.0 - Novo dashboard |
| **PATCH** | Correções de bugs | 1.0.1 - Fix de layout |

### 19.2 Changelog

**Formato do Changelog:**
```markdown
## [1.1.0] - 2026-05-10
### Adicionado
- Novo componente de timeline
- Suporte a dark mode
- Gráficos interativos no dashboard

### Modificado
- Melhorias no layout responsivo
- Atualização para Bootstrap 5.3

### Corrigido
- Correção de contraste em badges
- Fix de navegação por teclado em modais

## [1.0.1] - 2026-04-27
### Corrigido
- Correção de layout em telas pequenas
- Ajuste de cores para acessibilidade
```

### 19.3 Documentação de Componentes

Cada componente deve ser documentado com:

```markdown
## Componente: OrderCard

### Descrição
Card para exibição de resumo de ordem de serviço.

### Props/Parâmetros
| Nome | Tipo | Obrigatório | Descrição |
|------|------|-------------|-----------|
| order | Object | Sim | Objeto da ordem de serviço |
| showActions | Boolean | Não | Exibe botões de ação (padrão: true) |

### Exemplo de Uso
```html
{% for order in orders %}
    {% include 'components/order_card.html' with order=order %}
{% endfor %}
```

### Estados
- **Default:** Card padrão com informações
- **Hover:** Elevação e shadow aumentados
- **Selected:** Borda destacada

### Acessibilidade
- Foco visível com outline
- Role="article" para semântica
- Labels descritivas para ações
```

---

## 20. Referências

### 20.1 Documentação Oficial

- [Bootstrap 5 Documentation](https://getbootstrap.com/docs/5.3/)
- [Bootstrap Icons](https://icons.getbootstrap.com/)
- [Chart.js Documentation](https://www.chartjs.org/docs/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Jinja2 Documentation](https://jinja.palletsprojects.com/)

### 20.2 Guias de Acessibilidade

- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [MDN Accessibility Guide](https://developer.mozilla.org/en-US/docs/Web/Accessibility)
- [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)

### 20.3 Ferramentas de Desenvolvimento

- **Lighthouse:** Auditoria de performance e acessibilidade
- **WAVE:** Avaliação de acessibilidade
- ** axe DevTools:** Teste de acessibilidade
- **Web Developer Extension:** Ferramentas de desenvolvimento

---

## Apêndice A: Checklist de Revisão de Código Frontend

### Antes de Commit

- [ ] Código segue as convenções de nomenclatura
- [ ] Não há código comentado ou console.log
- [ ] HTML é válido e semântico
- [ ] CSS é organizado e sem duplicação
- [ ] JavaScript é modular e sem erros
- [ ] Imagens são otimizadas
- [ ] Acessibilidade foi verificada
- [ ] Responsividade foi testada

### Antes de Merge

- [ ] Revisão de código por outro desenvolvedor
- [ ] Testes manuais em diferentes navegadores
- [ ] Testes em dispositivos móveis
- [ ] Validação de acessibilidade com ferramentas
- [ ] Checklist de performance
- [ ] Documentação atualizada

---

**Fim do Documento**

*Última atualização: 10/05/2026*
*Versão: 1.0*
*Autor: Yure Samarone Gomes Duarte*
