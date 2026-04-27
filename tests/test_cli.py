"""
Testes do CLI — EletroService
Cobre: Comando create-user (gestão de usuários via terminal)
"""
import pytest
from app.models.user import User


class TestCreateUserCLI:
    """Testes do comando CLI 'create-user'."""

    def test_criar_usuario_via_cli(self, app, db):
        """Deve criar usuário no banco via comando CLI."""
        runner = app.test_cli_runner()
        result = runner.invoke(args=[
            'create-user', 'CLI Admin', 'cliadmin@teste.com', 'senhaforte'
        ])

        assert 'criado com sucesso' in result.output

        with app.app_context():
            user = User.query.filter_by(email='cliadmin@teste.com').first()
            assert user is not None
            assert user.name == 'CLI Admin'
            assert user.check_password('senhaforte') is True

    def test_criar_usuario_duplicado_via_cli(self, app, db, sample_user):
        """Deve falhar ao criar usuário com email já existente."""
        runner = app.test_cli_runner()
        result = runner.invoke(args=[
            'create-user', 'Duplicado', 'admin@teste.com', 'outrasenha'
        ])

        assert 'já existe' in result.output
