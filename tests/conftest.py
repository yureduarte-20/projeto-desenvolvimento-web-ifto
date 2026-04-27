"""
Fixtures globais do pytest para o EletroService.
Configura aplicação Flask com banco em memória (SQLite :memory:) e
fornece fixtures reutilizáveis para autenticação, dados de teste e client HTTP.
"""
import pytest
from app import create_app
from app.extensions import db as _db
from app.models.user import User
from app.models.requester import Requester
from app.models.work_order import WorkOrder
from app.models.history_order import HistoryOrder


@pytest.fixture(scope='session')
def app():
    """Cria instância da aplicação Flask para toda a sessão de testes."""
    app = create_app('testing')
    return app


@pytest.fixture(scope='function')
def db(app):
    """Cria e destrói todas as tabelas para cada teste (isolamento total)."""
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.remove()
        _db.drop_all()


@pytest.fixture(scope='function')
def client(app, db):
    """Fornece um test client do Flask com banco inicializado."""
    with app.test_client() as client:
        with app.app_context():
            yield client


@pytest.fixture(scope='function')
def sample_user(db):
    """Cria e retorna um usuário de teste persistido no banco."""
    user = User(name='Admin Teste', email='admin@teste.com')
    user.set_password('senha123')
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture(scope='function')
def sample_requester(db, sample_user):
    """Cria e retorna um solicitante (cliente) de teste."""
    requester = Requester(
        name='Cliente Teste',
        email='cliente@teste.com',
        phone='(63) 99999-0000',
        document='123.456.789-00',
        user_id=sample_user.id
    )
    db.session.add(requester)
    db.session.commit()
    return requester


@pytest.fixture(scope='function')
def sample_work_order(db, sample_requester):
    """Cria e retorna uma Ordem de Serviço de teste no status inicial."""
    order = WorkOrder(
        requester_id=sample_requester.id,
        description='Tela quebrada do notebook, necessita troca completa',
        status='Em Orçamento'
    )
    db.session.add(order)
    db.session.flush()

    # Criar histórico inicial (como faz o UC1)
    history = HistoryOrder(
        work_order_id=order.id,
        new_status='Em Orçamento',
        description='Abertura da Ordem de Serviço'
    )
    db.session.add(history)
    db.session.commit()
    return order


@pytest.fixture(scope='function')
def authenticated_client(client, sample_user):
    """Fornece um test client já autenticado como admin."""
    client.post('/auth/login', data={
        'email': 'admin@teste.com',
        'password': 'senha123'
    }, follow_redirects=True)
    return client
