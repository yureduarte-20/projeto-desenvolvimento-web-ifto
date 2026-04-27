"""
Testes do Auth Controller — EletroService
Cobre: UC11 — Fazer Login (login, logout, proteção de rotas)
"""
import pytest


class TestLogin:
    """Testes de autenticação (UC11)."""

    def test_login_page_acessivel(self, client):
        """GET /auth/login deve retornar 200."""
        response = client.get('/auth/login')
        assert response.status_code == 200

    def test_login_valido(self, client, sample_user):
        """UC11: Login com credenciais corretas deve redirecionar."""
        response = client.post('/auth/login', data={
            'email': 'admin@teste.com',
            'password': 'senha123'
        }, follow_redirects=False)
        # Deve redirecionar (302) para a página principal
        assert response.status_code == 302

    def test_login_valido_redirect_index(self, client, sample_user):
        """UC11: Login válido deve redirecionar para a página principal."""
        response = client.post('/auth/login', data={
            'email': 'admin@teste.com',
            'password': 'senha123'
        }, follow_redirects=True)
        assert response.status_code == 200

    def test_login_email_invalido(self, client, sample_user):
        """UC11: Login com email inexistente deve falhar com flash de erro."""
        response = client.post('/auth/login', data={
            'email': 'inexistente@teste.com',
            'password': 'senha123'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert 'Email ou senha incorretos' in response.data.decode('utf-8')

    def test_login_senha_incorreta(self, client, sample_user):
        """UC11: Login com senha errada deve falhar com flash de erro."""
        response = client.post('/auth/login', data={
            'email': 'admin@teste.com',
            'password': 'senha_errada'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert 'Email ou senha incorretos' in response.data.decode('utf-8')

    def test_login_redirect_se_autenticado(self, authenticated_client):
        """UC11: Usuário já logado acessando /auth/login deve ser redirecionado."""
        response = authenticated_client.get('/auth/login', follow_redirects=False)
        assert response.status_code == 302


class TestLogout:
    """Testes de logout (UC11)."""

    def test_logout(self, authenticated_client):
        """UC11: Logout deve redirecionar para login."""
        response = authenticated_client.get('/auth/logout', follow_redirects=False)
        assert response.status_code == 302

    def test_logout_mensagem(self, authenticated_client):
        """UC11: Logout deve exibir mensagem de saída."""
        response = authenticated_client.get('/auth/logout', follow_redirects=True)
        assert response.status_code == 200
        assert 'saiu do sistema' in response.data.decode('utf-8')


class TestProtecaoDeRotas:
    """Testes de proteção de rotas (login_required) — UC11 como pré-condição."""

    def test_index_requer_login(self, client):
        """Rota / sem autenticação deve redirecionar para login."""
        response = client.get('/', follow_redirects=False)
        assert response.status_code == 302
        assert '/auth/login' in response.headers.get('Location', '')

    def test_ordens_requer_login(self, client):
        """Rota /ordens/ sem autenticação deve redirecionar para login."""
        response = client.get('/ordens/', follow_redirects=False)
        assert response.status_code == 302

    def test_relatorios_requer_login(self, client):
        """Rota /relatorios/ sem autenticação deve redirecionar para login."""
        response = client.get('/relatorios/', follow_redirects=False)
        assert response.status_code == 302

    def test_users_requer_login(self, client):
        """Rota /users/ sem autenticação deve redirecionar para login."""
        response = client.get('/users/', follow_redirects=False)
        assert response.status_code == 302
