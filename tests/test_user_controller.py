"""
Testes do User Controller — EletroService
Cobre: CRUD de usuários (gestão interna, sem UC específico)
"""
import pytest
from app.models.user import User


class TestListarUsuarios:
    """Testes de listagem de usuários."""

    def test_listar_usuarios(self, authenticated_client):
        """GET /users/ deve retornar 200."""
        response = authenticated_client.get('/users/')
        assert response.status_code == 200

    def test_listar_exibe_usuario_existente(self, authenticated_client, sample_user):
        """Listagem deve exibir o usuário admin de teste."""
        response = authenticated_client.get('/users/')
        assert response.status_code == 200
        assert 'admin@teste.com' in response.data.decode('utf-8')


class TestCriarUsuario:
    """Testes de criação de usuário via interface web."""

    def test_acesso_pagina_criacao(self, authenticated_client):
        """GET /users/create deve retornar 200."""
        response = authenticated_client.get('/users/create')
        assert response.status_code == 200

    def test_criar_usuario_valido(self, authenticated_client, app):
        """Deve criar usuário com dados válidos."""
        response = authenticated_client.post('/users/create', data={
            'name': 'Operador Dois',
            'email': 'operador2@teste.com',
            'password': 'senha456'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert 'criado com sucesso' in response.data.decode('utf-8')

        with app.app_context():
            user = User.query.filter_by(email='operador2@teste.com').first()
            assert user is not None
            assert user.name == 'Operador Dois'

    def test_criar_usuario_email_duplicado(self, authenticated_client, sample_user):
        """Deve falhar ao criar usuário com email já existente."""
        response = authenticated_client.post('/users/create', data={
            'name': 'Duplicado',
            'email': 'admin@teste.com',  # email do sample_user
            'password': 'senha789'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert 'já está em uso' in response.data.decode('utf-8')


class TestEditarUsuario:
    """Testes de edição de usuário."""

    def test_acesso_pagina_edicao(self, authenticated_client, sample_user):
        """GET /users/<id>/edit deve retornar 200."""
        response = authenticated_client.get(f'/users/{sample_user.id}/edit')
        assert response.status_code == 200

    def test_editar_nome_usuario(self, authenticated_client, sample_user, app):
        """Deve atualizar o nome do usuário."""
        response = authenticated_client.post(
            f'/users/{sample_user.id}/edit',
            data={
                'name': 'Admin Renomeado',
                'email': 'admin@teste.com'
            },
            follow_redirects=True
        )
        assert response.status_code == 200
        assert 'atualizado com sucesso' in response.data.decode('utf-8')

        with app.app_context():
            user = User.query.get(sample_user.id)
            assert user.name == 'Admin Renomeado'

    def test_editar_email_duplicado(self, authenticated_client, db, sample_user, app):
        """Deve falhar ao editar email para um já usado por outro usuário."""
        # Criar segundo usuário
        user2 = User(name='Outro', email='outro@teste.com')
        user2.set_password('outrasenha')
        db.session.add(user2)
        db.session.commit()

        response = authenticated_client.post(
            f'/users/{sample_user.id}/edit',
            data={
                'name': 'Admin Teste',
                'email': 'outro@teste.com'  # email do user2
            },
            follow_redirects=True
        )
        assert response.status_code == 200
        assert 'já está em uso' in response.data.decode('utf-8')

    def test_editar_usuario_404(self, authenticated_client):
        """Editar usuário inexistente deve retornar 404."""
        response = authenticated_client.get('/users/99999/edit')
        assert response.status_code == 404


class TestExcluirUsuario:
    """Testes de exclusão de usuário."""

    def test_excluir_usuario(self, authenticated_client, db, app):
        """Deve excluir o usuário do banco."""
        # Criar usuário para excluir
        user = User(name='Para Excluir', email='excluir@teste.com')
        user.set_password('excluir123')
        db.session.add(user)
        db.session.commit()
        user_id = user.id

        response = authenticated_client.post(
            f'/users/{user_id}/delete',
            follow_redirects=True
        )
        assert response.status_code == 200
        assert 'removido com sucesso' in response.data.decode('utf-8')

        with app.app_context():
            assert User.query.get(user_id) is None

    def test_excluir_usuario_404(self, authenticated_client):
        """Excluir usuário inexistente deve retornar 404."""
        response = authenticated_client.post('/users/99999/delete')
        assert response.status_code == 404
