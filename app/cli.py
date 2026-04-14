import click
from flask.cli import with_appcontext
from app.extensions import db
from app.models.user import User

@click.command('create-user')
@click.argument('name')
@click.argument('email')
@click.argument('password')
@with_appcontext
def create_user_command(name, email, password):
    """Cria um novo usuário no sistema."""
    # Verificar se usuário já existe
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        click.echo(f'Erro: O usuário com email {email} já existe.')
        return

    try:
        new_user = User(name=name, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        click.echo(f'Usuário {name} ({email}) criado com sucesso!')
    except Exception as e:
        db.session.rollback()
        click.echo(f'Erro ao criar usuário: {e}')

def init_app(app):
    """Registra os comandos CLI no aplicativo."""
    app.cli.add_command(create_user_command)
