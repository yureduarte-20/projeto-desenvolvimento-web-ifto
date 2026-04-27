"""
Testes dos Models — EletroService
Cobre: User, Requester, WorkOrder, HistoryOrder
Rastreabilidade: UC8 (geração de código), regras de negócio, relacionamentos, máquina de estados
"""
import pytest
from datetime import datetime, timezone
from app.models.user import User
from app.models.requester import Requester
from app.models.work_order import WorkOrder
from app.models.history_order import HistoryOrder
from app.controllers.work_order_controller import STATUS_TRANSITIONS


# ============================================================================
# User Model
# ============================================================================

class TestUserModel:
    """Testes do modelo User."""

    def test_criar_usuario(self, db):
        """Deve criar usuário com nome e email."""
        user = User(name='João Silva', email='joao@teste.com')
        user.set_password('segura123')
        db.session.add(user)
        db.session.commit()

        assert user.id is not None
        assert user.name == 'João Silva'
        assert user.email == 'joao@teste.com'
        assert user.created_at is not None

    def test_set_password_gera_hash(self, db):
        """set_password deve gerar hash diferente da senha em texto."""
        user = User(name='Teste', email='hash@teste.com')
        user.set_password('minhasenha')
        db.session.add(user)
        db.session.commit()

        assert user.password_hash is not None
        assert user.password_hash != 'minhasenha'

    def test_check_password_valida_corretamente(self, db):
        """check_password deve retornar True para senha correta e False para incorreta."""
        user = User(name='Teste', email='check@teste.com')
        user.set_password('senha_certa')
        db.session.add(user)
        db.session.commit()

        assert user.check_password('senha_certa') is True
        assert user.check_password('senha_errada') is False

    def test_repr_usuario(self, db):
        """__repr__ deve retornar formato legível."""
        user = User(name='Teste', email='repr@teste.com')
        user.set_password('123456')
        db.session.add(user)
        db.session.commit()

        assert '<User repr@teste.com>' == repr(user)

    def test_user_mixin_is_authenticated(self, sample_user):
        """UserMixin deve fornecer is_authenticated=True."""
        assert sample_user.is_authenticated is True


# ============================================================================
# Requester Model
# ============================================================================

class TestRequesterModel:
    """Testes do modelo Requester (Solicitante/Cliente)."""

    def test_criar_requester(self, db):
        """Deve criar solicitante com todos os campos obrigatórios."""
        requester = Requester(
            name='Maria Souza',
            email='maria@teste.com',
            phone='(63) 98888-1111',
            document='987.654.321-00'
        )
        db.session.add(requester)
        db.session.commit()

        assert requester.id is not None
        assert requester.name == 'Maria Souza'
        assert requester.phone == '(63) 98888-1111'

    def test_requester_user_opcional(self, db):
        """O campo user_id deve ser opcional (nullable)."""
        requester = Requester(
            name='Sem Usuário',
            email='semusuario@teste.com',
            phone='(63) 90000-0000',
            document='111.222.333-44'
        )
        db.session.add(requester)
        db.session.commit()

        assert requester.user_id is None
        assert requester.user is None

    def test_requester_relacionamento_user(self, db, sample_user):
        """Requester deve se relacionar corretamente com User."""
        requester = Requester(
            name='Com Usuário',
            email='comusuario@teste.com',
            phone='(63) 91111-2222',
            document='555.666.777-88',
            user_id=sample_user.id
        )
        db.session.add(requester)
        db.session.commit()

        assert requester.user.id == sample_user.id
        assert requester.user.email == 'admin@teste.com'

    def test_requester_relacionamento_work_orders(self, sample_requester, sample_work_order):
        """Requester deve conter lista de work_orders."""
        assert len(sample_requester.work_orders) >= 1
        assert sample_requester.work_orders[0].id == sample_work_order.id

    def test_repr_requester(self, sample_requester):
        """__repr__ deve retornar formato legível."""
        assert '<Requester cliente@teste.com>' == repr(sample_requester)


# ============================================================================
# WorkOrder Model — UC8 (Geração de Código de Rastreio)
# ============================================================================

class TestWorkOrderModel:
    """Testes do modelo WorkOrder. Cobre UC8 (geração automática de códigos)."""

    def test_criar_ordem_status_padrao(self, db, sample_requester):
        """UC1/T1: O status padrão de uma nova OS deve ser 'Em Orçamento'."""
        order = WorkOrder(
            requester_id=sample_requester.id,
            description='Teste de criação padrão do status'
        )
        db.session.add(order)
        db.session.commit()

        assert order.status == 'Em Orçamento'

    def test_geracao_automatica_number(self, db, sample_requester):
        """UC8/F3.1: O campo number deve ser gerado automaticamente no formato OS-YYYYMMDD-XXXX."""
        order = WorkOrder(
            requester_id=sample_requester.id,
            description='Teste geração de número'
        )
        db.session.add(order)
        db.session.commit()

        assert order.number is not None
        assert order.number.startswith('OS-')
        # Formato: OS-YYYYMMDD-XXXX (total ~16 chars)
        parts = order.number.split('-')
        assert len(parts) == 3
        assert len(parts[1]) == 8  # YYYYMMDD

    def test_geracao_automatica_public_id(self, db, sample_requester):
        """UC8/F3.1: O campo public_id deve ser gerado automaticamente (UUID)."""
        order = WorkOrder(
            requester_id=sample_requester.id,
            description='Teste geração de public_id'
        )
        db.session.add(order)
        db.session.commit()

        assert order.public_id is not None
        assert len(order.public_id) == 36  # UUID padrão

    def test_unicidade_number(self, db, sample_requester):
        """UC8: Dois números de OS devem ser únicos."""
        order1 = WorkOrder(
            requester_id=sample_requester.id,
            description='Teste unicidade 1'
        )
        order2 = WorkOrder(
            requester_id=sample_requester.id,
            description='Teste unicidade 2'
        )
        db.session.add_all([order1, order2])
        db.session.commit()

        assert order1.number != order2.number

    def test_unicidade_public_id(self, db, sample_requester):
        """UC8: Dois public_id devem ser únicos."""
        order1 = WorkOrder(
            requester_id=sample_requester.id,
            description='Teste unicidade public_id 1'
        )
        order2 = WorkOrder(
            requester_id=sample_requester.id,
            description='Teste unicidade public_id 2'
        )
        db.session.add_all([order1, order2])
        db.session.commit()

        assert order1.public_id != order2.public_id

    def test_relacionamento_requester(self, sample_work_order, sample_requester):
        """WorkOrder deve se relacionar com Requester."""
        assert sample_work_order.requester.id == sample_requester.id
        assert sample_work_order.requester.name == 'Cliente Teste'

    def test_relacionamento_history(self, sample_work_order):
        """WorkOrder deve ter histórico (HistoryOrder) acessível."""
        assert len(sample_work_order.history) >= 1
        assert sample_work_order.history[0].new_status == 'Em Orçamento'

    def test_cascade_delete_history(self, db, sample_work_order):
        """Ao excluir WorkOrder, seu histórico deve ser excluído (cascade)."""
        order_id = sample_work_order.id
        db.session.delete(sample_work_order)
        db.session.commit()

        remaining = HistoryOrder.query.filter_by(work_order_id=order_id).all()
        assert len(remaining) == 0

    def test_repr_work_order(self, sample_work_order):
        """__repr__ deve retornar formato legível com número da OS."""
        assert f'<WorkOrder {sample_work_order.number}>' == repr(sample_work_order)

    def test_campos_financeiros_opcionais(self, db, sample_requester):
        """Campos final_price e labor_cost devem ser opcionais."""
        order = WorkOrder(
            requester_id=sample_requester.id,
            description='Teste campos financeiros opcionais'
        )
        db.session.add(order)
        db.session.commit()

        assert order.final_price is None
        assert order.labor_cost is None

    def test_campos_cancelamento_padrao(self, db, sample_requester):
        """is_canceled padrão False, cancelation_reason padrão None."""
        order = WorkOrder(
            requester_id=sample_requester.id,
            description='Teste cancelamento padrão'
        )
        db.session.add(order)
        db.session.commit()

        assert order.is_canceled is False
        assert order.cancelation_reason is None


# ============================================================================
# HistoryOrder Model — UC10 (Linha do Tempo)
# ============================================================================

class TestHistoryOrderModel:
    """Testes do modelo HistoryOrder. Cobre UC10 (linha do tempo)."""

    def test_criar_historico_inicial(self, db, sample_work_order):
        """UC10/F3.3: Histórico inicial deve ter old_status=None."""
        history = sample_work_order.history[0]
        assert history.old_status is None
        assert history.new_status == 'Em Orçamento'
        assert history.description == 'Abertura da Ordem de Serviço'

    def test_historico_registra_timestamp(self, db, sample_work_order):
        """UC10/F3.3: Cada entrada do histórico deve ter changed_at."""
        history = sample_work_order.history[0]
        assert history.changed_at is not None
        assert isinstance(history.changed_at, datetime)

    def test_criar_historico_com_transicao(self, db, sample_work_order):
        """UC10: Transição de status deve registrar old_status e new_status."""
        history = HistoryOrder(
            work_order_id=sample_work_order.id,
            old_status='Em Orçamento',
            new_status='Em Manutenção',
            description='Orçamento aprovado pelo cliente'
        )
        db.session.add(history)
        db.session.commit()

        assert history.old_status == 'Em Orçamento'
        assert history.new_status == 'Em Manutenção'

    def test_repr_historico(self, db, sample_work_order):
        """__repr__ deve retornar formato legível."""
        history = sample_work_order.history[0]
        expected = f'<HistoryOrder {history.id} (OS {sample_work_order.id})>'
        assert expected == repr(history)


# ============================================================================
# Máquina de Estados (STATUS_TRANSITIONS) — UC3
# ============================================================================

class TestStatusTransitions:
    """Testes do dicionário STATUS_TRANSITIONS. Cobre UC3 e UC5."""

    def test_status_transitions_possui_todos_status(self):
        """Deve conter todos os 6 status do fluxo."""
        expected_statuses = {
            'Em Orçamento', 'Em Manutenção', 'Aguardando Pagamento',
            'Aguardando Retirada', 'Finalizado', 'Cancelado'
        }
        assert set(STATUS_TRANSITIONS.keys()) == expected_statuses

    def test_em_orcamento_avanca_para_manutencao(self):
        """T2: Em Orçamento → Em Manutenção."""
        assert STATUS_TRANSITIONS['Em Orçamento']['next'] == 'Em Manutenção'

    def test_em_orcamento_permite_cancelamento(self):
        """T3: Em Orçamento pode cancelar."""
        assert STATUS_TRANSITIONS['Em Orçamento']['can_cancel'] is True

    def test_em_manutencao_avanca_para_aguardando_pagamento(self):
        """T4: Em Manutenção → Aguardando Pagamento."""
        assert STATUS_TRANSITIONS['Em Manutenção']['next'] == 'Aguardando Pagamento'

    def test_em_manutencao_permite_cancelamento(self):
        """T5: Em Manutenção pode cancelar."""
        assert STATUS_TRANSITIONS['Em Manutenção']['can_cancel'] is True

    def test_aguardando_pagamento_avanca_para_retirada(self):
        """T6: Aguardando Pagamento → Aguardando Retirada."""
        assert STATUS_TRANSITIONS['Aguardando Pagamento']['next'] == 'Aguardando Retirada'

    def test_aguardando_pagamento_nao_cancela(self):
        """Aguardando Pagamento NÃO pode cancelar."""
        assert STATUS_TRANSITIONS['Aguardando Pagamento']['can_cancel'] is False

    def test_aguardando_retirada_avanca_para_finalizado(self):
        """T7: Aguardando Retirada → Finalizado."""
        assert STATUS_TRANSITIONS['Aguardando Retirada']['next'] == 'Finalizado'

    def test_aguardando_retirada_nao_cancela(self):
        """Aguardando Retirada NÃO pode cancelar."""
        assert STATUS_TRANSITIONS['Aguardando Retirada']['can_cancel'] is False

    def test_finalizado_sem_proximo_status(self):
        """Finalizado é estado terminal — next=None."""
        assert STATUS_TRANSITIONS['Finalizado']['next'] is None

    def test_finalizado_nao_cancela(self):
        """Finalizado NÃO pode cancelar."""
        assert STATUS_TRANSITIONS['Finalizado']['can_cancel'] is False

    def test_cancelado_sem_proximo_status(self):
        """Cancelado é estado terminal — next=None."""
        assert STATUS_TRANSITIONS['Cancelado']['next'] is None

    def test_cancelado_nao_cancela(self):
        """Cancelado NÃO pode re-cancelar."""
        assert STATUS_TRANSITIONS['Cancelado']['can_cancel'] is False
