# Relatório de Inspeção de Cibersegurança

**Data da Inspeção:** 16 de Maio de 2026  
**Escopo:** `app/controllers/` e `app/forms/`  
**Nível de Profundidade:** PROFUNDA  

---

## Resumo Executivo

A aplicação web foi avaliada conforme os padrões de desenvolvimento seguro e as categorias da lista OWASP Top 10. O uso nativo do Jinja2 para a renderização visual e do ORM do SQLAlchemy mitigou classes inteiras de vulnerabilidades, como injeção de SQL e Cross-Site Scripting (XSS). Contudo, foram identificadas falhas conceituais de autorização, integridade de requisições e ausência de limites de requisições.

- **Contagem de Achados por Severidade:**
  - **Crítica:** 0
  - **Alta:** 2
  - **Média:** 3
  - **Baixa:** 1

- **As 5 Ações Mais Urgentes:**
  1. Corrigir a falha de **Open Redirect** no controlador de autenticação, validando de maneira absoluta a URL do parâmetro `next`.
  2. Implementar **validação explícita de CSRF** nas rotas isoladas de exclusão (POST direto sem validação via FlaskForm).
  3. Adicionar políticas de **Rate Limiting** para mitigar Força Bruta de senhas no Login e impedir varredura (enumeração) no Rastreamento Público.
  4. Estruturar o controle de acesso introduzindo **RBAC (Role-Based Access Control)** para prevenir IDOR e acessos indevidos.
  5. Fortalecer as defesas da camada HTTP implementando cabeçalhos de segurança (**Flask-Talisman**: CSP, X-Frame-Options) e cookies seguros (HttpOnly, SameSite).

---

## Detalhamento das Vulnerabilidades

### 1. Open Redirect via Validação Inadequada do Parâmetro `next`
- **Localização:** `app/controllers/auth_controller.py`, função `login`, linha 26.
- **Descrição:** A validação que tenta garantir redirecionamentos seguros utilizando `next_page.startswith('/')` é fraca e pode ser contornada. Um invasor pode fornecer uma URL baseada em protocolo relativo, como `//malicious.com`, que será aprovada e fará com que o navegador redirecione o usuário para um domínio externo.
- **Evidência:**
  ```python
  next_page = request.args.get('next')
  if not next_page or not next_page.startswith('/'):
      next_page = url_for('main.index')
  return redirect(next_page)
  ```
- **Impacto:** Amplamente utilizado para facilitar campanhas de Phishing. Após autenticarem-se com sucesso, usuários confiam no link e acabam cedendo informações sensíveis em um painel espelho clonado por atacantes.
- **Severidade:** **Alta**
- **Recomendação:** Use `urllib.parse.urlparse` para atestar a legitimidade do domínio.
  ```python
  from urllib.parse import urlparse, urljoin
  def is_safe_url(target):
      ref_url = urlparse(request.host_url)
      test_url = urlparse(urljoin(request.host_url, target))
      return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc
  
  if not next_page or not is_safe_url(next_page):
      next_page = url_for('main.index')
  ```
- **Referências:** CWE-601, OWASP Top 10 (A01: Broken Access Control).

### 2. Ausência de Proteção CSRF em Ações Destrutivas
- **Localização:** 
  - `app/controllers/user_controller.py`, função `delete`, linha 61.
  - `app/controllers/work_order_controller.py`, função `delete`, linha 162.
- **Descrição:** Rotas que executam exclusões utilizam requisições `POST` simples em URLs previsíveis (ex: `/<int:id>/delete`), porém não checam o envio do token CSRF (já que não utilizam `form.validate_on_submit()`). 
- **Evidência:**
  ```python
  @bp.route('/<int:id>/delete', methods=['POST'])
  @login_required
  def delete(id):
      user = User.query.get_or_404(id)
      db.session.delete(user)
  ```
- **Impacto:** Um site malicioso pode forjar uma requisição POST oculta para o sistema EletroService. Se um administrador estiver com sessão ativa no navegador, a exclusão ocorrerá em background sem seu consentimento.
- **Severidade:** **Alta**
- **Recomendação:** A forma mais eficaz é aplicar proteção global através da biblioteca oficial `CSRFProtect` do `flask_wtf`:
  ```python
  from flask_wtf.csrf import CSRFProtect
  csrf = CSRFProtect(app)
  ```
- **Referências:** CWE-352, OWASP Top 10 (A01: Broken Access Control).

### 3. Falta de Rate Limiting (Proteção a Ataques de Força Bruta e Enumeração)
- **Localização:** 
  - `app/controllers/auth_controller.py`, função `login`, linha 9.
  - `app/controllers/tracking_controller.py`, função `search`, linha 7.
- **Descrição:** Os endpoints de login e busca de ordens de serviço pelo `public_id` não limitam o número de requisições por IP.
- **Evidência:** Ausência de anotações limitadoras como `@limiter.limit()`.
- **Impacto:** Permite disparos automatizados na tentativa de descobrir senhas ou varrer aleatoriamente `public_ids` válidos de Ordens de Serviço.
- **Severidade:** **Média**
- **Recomendação:** Utilizar o módulo `Flask-Limiter`.
  ```python
  @bp.route('/search')
  @limiter.limit("10 per minute")
  def search():
  ```
- **Referências:** CWE-307, CWE-799, OWASP Top 10 (A07: Authentication Failures).

### 4. Controle de Acesso Insuficiente (Missing Function Level Access Control / IDOR)
- **Localização:** `app/controllers/user_controller.py` e `app/controllers/work_order_controller.py`.
- **Descrição:** Qualquer usuário autenticado no sistema tem plenos poderes para criar, editar ou excluir registros, inclusive deletar sua própria conta via painel. Não há verificação baseada em nível de privilégio (Admin vs Funcionário Comum).
- **Evidência:** Na linha 64 de `user_controller.py`:
  ```python
  user = User.query.get_or_404(id)
  db.session.delete(user) # Qualquer usuário deleta qualquer usuário
  ```
- **Impacto:** Um funcionário de suporte com acesso restrito pode elevar seus privilégios para apagar gerentes ou manipular ordens de serviço livremente.
- **Severidade:** **Média**
- **Recomendação:** Introduzir `@admin_required` ou RBAC simples. Impedir a auto-exclusão explícita:
  ```python
  if user.id == current_user.id:
      abort(403, description="Não é permitido remover a própria conta.")
  ```
- **Referências:** CWE-284, CWE-285, OWASP Top 10 (A01: Broken Access Control).

### 5. Má Configuração de Segurança (Security Headers e Cookies)
- **Localização:** Diretivas globais (implícito nos controllers web).
- **Descrição:** O sistema não emite cabeçalhos protetivos fundamentais (HSTS, CSP, X-Frame-Options) e não exige as tags de segurança nos cookies da sessão.
- **Impacto:** Deixa a aplicação vulnerável a manipulações de iframe (Clickjacking) e interceptação de sessão via canais inseguros se não estiver forçando HTTPS em produção.
- **Severidade:** **Média**
- **Recomendação:** Instalar o pacote `Flask-Talisman` em `extensions.py` e ajustar a configuração de cookies nativos do Flask:
  ```python
  app.config.update(
      SESSION_COOKIE_SECURE=True,
      SESSION_COOKIE_HTTPONLY=True,
      SESSION_COOKIE_SAMESITE='Lax',
  )
  ```
- **Referências:** CWE-693, OWASP Top 10 (A02: Security Misconfiguration / A05: Security Misconfiguration).

### 6. Complexidade de Senha Inadequada
- **Localização:** `app/forms/user_forms.py` linhas 8 e 14.
- **Descrição:** O validador da senha restringe apenas um tamanho mínimo muito baixo (6 caracteres).
- **Evidência:**
  ```python
  Length(min=6, message="A senha deve ter no mínimo 6 caracteres.")
  ```
- **Impacto:** Permite a definição de senhas fáceis de deduzir em um sistema que contém informações pessoais sensíveis (CPFs e contatos de clientes).
- **Severidade:** **Baixa**
- **Recomendação:** Exigir no mínimo 12 caracteres (padrão NIST) ou validar a força da senha por meio de expressões regulares.
- **Referências:** CWE-521, OWASP Top 10 (A07: Authentication Failures).
