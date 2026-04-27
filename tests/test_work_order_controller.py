"""
Testes do Work Order Controller — EletroService
Cobre: UC1 (Cadastrar OS), UC2 (Editar OS), UC3 (Atualizar Status),
       UC4 (Consultar/Listar), UC5 (Cancelar OS), UC9 (Rastreio), UC10 (Linha do Tempo)
"""
import pytest
from app.models.work_order import WorkOrder
from app.models.requester import Requester
from app.models.history_order import HistoryOrder


# ============================================================================
# UC1 — Cadastrar Ordem de Serviço
# ============================================================================

class TestCadastrarOS:
    """Testes de criação de OS (UC1 + UC8)."""

    def test_acesso_pagina_criacao(self, authenticated_client):
        """UC1: GET /ordens/nova deve retornar 200."""
        response = authenticated_client.get('/ordens/nova')
        assert response.status_code == 200

    def test_criar_os_com_dados_validos(self, authenticated_client, app):
        """UC1/F1.1: Deve criar OS com status 'Em Orçamento' e gerar código de rastreio (UC8)."""
        response = authenticated_client.post('/ordens/nova', data={
            'requester_name': 'Maria Silva',
            'requester_email': 'maria@teste.com',
            'requester_phone': '(63) 98888-1111',
            'requester_document': '999.888.777-66',
            'description': 'Celular não liga após cair na água, possível oxidação da placa'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert 'criada com sucesso' in response.data.decode('utf-8')

        # Verificar no banco
        with app.app_context():
            order = WorkOrder.query.first()
            assert order is not None
            assert order.status == 'Em Orçamento'
            assert order.number is not None
            assert order.public_id is not None

    def test_criar_os_cria_requester_novo(self, authenticated_client, app):
        """UC1: Ao criar OS com email novo, deve criar Requester automaticamente."""
        authenticated_client.post('/ordens/nova', data={
            'requester_name': 'João Novo',
            'requester_email': 'joao.novo@teste.com',
            'requester_phone': '(63) 97777-2222',
            'requester_document': '111.222.333-44',
            'description': 'Televisor com vertical lines na tela LCD'
        }, follow_redirects=True)

        with app.app_context():
            requester = Requester.query.filter_by(email='joao.novo@teste.com').first()
            assert requester is not None
            assert requester.name == 'João Novo'

    def test_criar_os_usa_requester_existente(self, authenticated_client, sample_requester, app):
        """UC1: Ao criar OS com email existente, deve reusar o Requester."""
        authenticated_client.post('/ordens/nova', data={
            'requester_name': 'Cliente Teste',
            'requester_email': 'cliente@teste.com',  # mesmo email do sample_requester
            'requester_phone': '(63) 99999-0000',
            'requester_document': '123.456.789-00',
            'description': 'Notebook com problemas no teclado, teclas sem resposta'
        }, follow_redirects=True)

        with app.app_context():
            # Deve ter apenas 1 requester com esse email
            requesters = Requester.query.filter_by(email='cliente@teste.com').all()
            assert len(requesters) == 1

    def test_criar_os_gera_historico_inicial(self, authenticated_client, app):
        """UC1/UC8: A criação deve gerar entrada no histórico (linha do tempo)."""
        authenticated_client.post('/ordens/nova', data={
            'requester_name': 'Pedro Hist',
            'requester_email': 'pedro.hist@teste.com',
            'requester_phone': '(63) 96666-3333',
            'requester_document': '444.555.666-77',
            'description': 'Micro-ondas parou de aquecer, magnetron possivelmente danificado'
        }, follow_redirects=True)

        with app.app_context():
            order = WorkOrder.query.first()
            assert len(order.history) == 1
            assert order.history[0].new_status == 'Em Orçamento'
            assert order.history[0].old_status is None


# ============================================================================
# UC4 — Consultar e Listar Ordens de Serviço
# ============================================================================

class TestListarOS:
    """Testes de listagem de OS (UC4)."""

    def test_listar_os_vazio(self, authenticated_client):
        """UC4: Listagem sem OS deve retornar 200."""
        response = authenticated_client.get('/ordens/')
        assert response.status_code == 200

    def test_listar_os_com_dados(self, authenticated_client, sample_work_order):
        """UC4/F1.4: Listagem deve exibir OS existentes."""
        response = authenticated_client.get('/ordens/')
        assert response.status_code == 200
        assert sample_work_order.number in response.data.decode('utf-8')


# ============================================================================
# UC2 — Editar Ordem de Serviço
# ============================================================================

class TestEditarOS:
    """Testes de edição de OS (UC2)."""

    def test_acesso_pagina_edicao(self, authenticated_client, sample_work_order):
        """UC2: GET /ordens/<id>/editar deve retornar 200."""
        response = authenticated_client.get(f'/ordens/{sample_work_order.id}/editar')
        assert response.status_code == 200

    def test_editar_descricao(self, authenticated_client, sample_work_order, app):
        """UC2/F1.2: Deve atualizar a descrição da OS."""
        response = authenticated_client.post(
            f'/ordens/{sample_work_order.id}/editar',
            data={
                'description': 'Descrição atualizada com informações complementares',
                'action': 'save'
            },
            follow_redirects=True
        )
        assert response.status_code == 200

        with app.app_context():
            order = WorkOrder.query.get(sample_work_order.id)
            assert order.description == 'Descrição atualizada com informações complementares'

    def test_editar_os_404_inexistente(self, authenticated_client):
        """UC2: Editar OS inexistente deve retornar 404."""
        response = authenticated_client.get('/ordens/99999/editar')
        assert response.status_code == 404


# ============================================================================
# UC3 — Atualizar Status da OS (Máquina de Estados)
# ============================================================================

class TestAtualizarStatus:
    """Testes de transição de status (UC3). Cobre T2–T7 + testes negativos."""

    def test_t2_avancar_em_orcamento_para_manutencao(self, authenticated_client, sample_work_order, app):
        """T2: Em Orçamento → Em Manutenção."""
        response = authenticated_client.post(
            f'/ordens/{sample_work_order.id}/editar',
            data={
                'description': sample_work_order.description,
                'action': 'advance',
                'history_note': 'Orçamento aprovado pelo cliente'
            },
            follow_redirects=True
        )
        assert response.status_code == 200

        with app.app_context():
            order = WorkOrder.query.get(sample_work_order.id)
            assert order.status == 'Em Manutenção'

    def test_t4_avancar_manutencao_para_aguardando_pagamento(self, authenticated_client, sample_work_order, db, app):
        """T4: Em Manutenção → Aguardando Pagamento."""
        # Preparar: avançar para Em Manutenção
        sample_work_order.status = 'Em Manutenção'
        db.session.commit()

        response = authenticated_client.post(
            f'/ordens/{sample_work_order.id}/editar',
            data={
                'description': sample_work_order.description,
                'action': 'advance',
                'history_note': 'Reparo concluído com sucesso'
            },
            follow_redirects=True
        )
        assert response.status_code == 200

        with app.app_context():
            order = WorkOrder.query.get(sample_work_order.id)
            assert order.status == 'Aguardando Pagamento'

    def test_t6_avancar_aguardando_pagamento_para_retirada(self, authenticated_client, sample_work_order, db, app):
        """T6: Aguardando Pagamento → Aguardando Retirada."""
        sample_work_order.status = 'Aguardando Pagamento'
        db.session.commit()

        response = authenticated_client.post(
            f'/ordens/{sample_work_order.id}/editar',
            data={
                'description': sample_work_order.description,
                'action': 'advance',
                'history_note': 'Pagamento confirmado'
            },
            follow_redirects=True
        )
        assert response.status_code == 200

        with app.app_context():
            order = WorkOrder.query.get(sample_work_order.id)
            assert order.status == 'Aguardando Retirada'

    def test_t7_avancar_aguardando_retirada_para_finalizado(self, authenticated_client, sample_work_order, db, app):
        """T7: Aguardando Retirada → Finalizado. Deve registrar delivered_at."""
        sample_work_order.status = 'Aguardando Retirada'
        db.session.commit()

        response = authenticated_client.post(
            f'/ordens/{sample_work_order.id}/editar',
            data={
                'description': sample_work_order.description,
                'action': 'advance',
                'history_note': 'Equipamento entregue ao cliente'
            },
            follow_redirects=True
        )
        assert response.status_code == 200

        with app.app_context():
            order = WorkOrder.query.get(sample_work_order.id)
            assert order.status == 'Finalizado'
            assert order.delivered_at is not None

    def test_nao_avancar_de_finalizado(self, authenticated_client, sample_work_order, db, app):
        """Finalizado é terminal — avançar não deve alterar status."""
        sample_work_order.status = 'Finalizado'
        db.session.commit()

        response = authenticated_client.post(
            f'/ordens/{sample_work_order.id}/editar',
            data={
                'description': sample_work_order.description,
                'action': 'advance'
            },
            follow_redirects=True
        )

        with app.app_context():
            order = WorkOrder.query.get(sample_work_order.id)
            assert order.status == 'Finalizado'

    def test_nao_avancar_de_cancelado(self, authenticated_client, sample_work_order, db, app):
        """Cancelado é terminal — avançar não deve alterar status."""
        sample_work_order.status = 'Cancelado'
        sample_work_order.is_canceled = True
        db.session.commit()

        response = authenticated_client.post(
            f'/ordens/{sample_work_order.id}/editar',
            data={
                'description': sample_work_order.description,
                'action': 'advance'
            },
            follow_redirects=True
        )

        with app.app_context():
            order = WorkOrder.query.get(sample_work_order.id)
            assert order.status == 'Cancelado'

    def test_historico_criado_na_transicao(self, authenticated_client, sample_work_order, app):
        """UC3/UC10: Transição deve criar entrada na linha do tempo."""
        authenticated_client.post(
            f'/ordens/{sample_work_order.id}/editar',
            data={
                'description': sample_work_order.description,
                'action': 'advance',
                'history_note': 'Nota de teste para histórico'
            },
            follow_redirects=True
        )

        with app.app_context():
            order = WorkOrder.query.get(sample_work_order.id)
            # Deve ter pelo menos 2: abertura + transição
            assert len(order.history) >= 2
            last_history = sorted(order.history, key=lambda h: h.id)[-1]
            assert last_history.old_status == 'Em Orçamento'
            assert last_history.new_status == 'Em Manutenção'

    def test_ciclo_completo_happy_path(self, authenticated_client, app):
        """Integração: Ciclo completo T1→T2→T4→T6→T7."""
        # T1: Criar OS (status inicial Em Orçamento)
        authenticated_client.post('/ordens/nova', data={
            'requester_name': 'Ciclo Completo',
            'requester_email': 'ciclo@teste.com',
            'requester_phone': '(63) 95555-4444',
            'requester_document': '777.888.999-00',
            'description': 'Teste de ciclo completo da ordem de serviço'
        }, follow_redirects=True)

        with app.app_context():
            order = WorkOrder.query.filter_by(description='Teste de ciclo completo da ordem de serviço').first()
            assert order.status == 'Em Orçamento'
            order_id = order.id

        # T2: Em Orçamento → Em Manutenção
        authenticated_client.post(f'/ordens/{order_id}/editar', data={
            'description': 'Teste de ciclo completo da ordem de serviço',
            'action': 'advance'
        }, follow_redirects=True)

        with app.app_context():
            order = WorkOrder.query.get(order_id)
            assert order.status == 'Em Manutenção'

        # T4: Em Manutenção → Aguardando Pagamento
        authenticated_client.post(f'/ordens/{order_id}/editar', data={
            'description': 'Teste de ciclo completo da ordem de serviço',
            'action': 'advance',
            'final_price': '150.00',
            'labor_cost': '80.00'
        }, follow_redirects=True)

        with app.app_context():
            order = WorkOrder.query.get(order_id)
            assert order.status == 'Aguardando Pagamento'

        # T6: Aguardando Pagamento → Aguardando Retirada
        authenticated_client.post(f'/ordens/{order_id}/editar', data={
            'description': 'Teste de ciclo completo da ordem de serviço',
            'action': 'advance'
        }, follow_redirects=True)

        with app.app_context():
            order = WorkOrder.query.get(order_id)
            assert order.status == 'Aguardando Retirada'

        # T7: Aguardando Retirada → Finalizado
        authenticated_client.post(f'/ordens/{order_id}/editar', data={
            'description': 'Teste de ciclo completo da ordem de serviço',
            'action': 'advance'
        }, follow_redirects=True)

        with app.app_context():
            order = WorkOrder.query.get(order_id)
            assert order.status == 'Finalizado'
            assert order.delivered_at is not None
            # Verificar que o histórico tem 5 entradas (abertura + 4 transições)
            assert len(order.history) == 5


# ============================================================================
# UC5 — Cancelar Ordem de Serviço
# ============================================================================

class TestCancelarOS:
    """Testes de cancelamento de OS (UC5)."""

    def test_t3_cancelar_em_orcamento(self, authenticated_client, sample_work_order, app):
        """T3: Cancelar a partir de 'Em Orçamento'."""
        response = authenticated_client.post(
            f'/ordens/{sample_work_order.id}/editar',
            data={
                'description': sample_work_order.description,
                'action': 'cancel',
                'cancelation_reason': 'Desistência do cliente'
            },
            follow_redirects=True
        )
        assert response.status_code == 200

        with app.app_context():
            order = WorkOrder.query.get(sample_work_order.id)
            assert order.status == 'Cancelado'
            assert order.is_canceled is True
            assert order.cancelation_reason == 'Desistência do cliente'

    def test_t5_cancelar_em_manutencao(self, authenticated_client, sample_work_order, db, app):
        """T5: Cancelar a partir de 'Em Manutenção'."""
        sample_work_order.status = 'Em Manutenção'
        db.session.commit()

        response = authenticated_client.post(
            f'/ordens/{sample_work_order.id}/editar',
            data={
                'description': sample_work_order.description,
                'action': 'cancel',
                'cancelation_reason': 'Equipamento sem conserto viável'
            },
            follow_redirects=True
        )
        assert response.status_code == 200

        with app.app_context():
            order = WorkOrder.query.get(sample_work_order.id)
            assert order.status == 'Cancelado'
            assert order.is_canceled is True

    def test_nao_cancelar_aguardando_pagamento(self, authenticated_client, sample_work_order, db, app):
        """UC5: Não deve permitir cancelamento a partir de 'Aguardando Pagamento'."""
        sample_work_order.status = 'Aguardando Pagamento'
        db.session.commit()

        response = authenticated_client.post(
            f'/ordens/{sample_work_order.id}/editar',
            data={
                'description': sample_work_order.description,
                'action': 'cancel',
                'cancelation_reason': 'Tentativa inválida'
            },
            follow_redirects=True
        )

        with app.app_context():
            order = WorkOrder.query.get(sample_work_order.id)
            # Status não deve mudar
            assert order.status == 'Aguardando Pagamento'
            assert order.is_canceled is False

    def test_nao_cancelar_aguardando_retirada(self, authenticated_client, sample_work_order, db, app):
        """UC5: Não deve permitir cancelamento a partir de 'Aguardando Retirada'."""
        sample_work_order.status = 'Aguardando Retirada'
        db.session.commit()

        response = authenticated_client.post(
            f'/ordens/{sample_work_order.id}/editar',
            data={
                'description': sample_work_order.description,
                'action': 'cancel',
                'cancelation_reason': 'Tentativa inválida'
            },
            follow_redirects=True
        )

        with app.app_context():
            order = WorkOrder.query.get(sample_work_order.id)
            assert order.status == 'Aguardando Retirada'

    def test_cancelamento_registra_historico(self, authenticated_client, sample_work_order, app):
        """UC5/UC10: Cancelamento deve registrar na linha do tempo."""
        authenticated_client.post(
            f'/ordens/{sample_work_order.id}/editar',
            data={
                'description': sample_work_order.description,
                'action': 'cancel',
                'cancelation_reason': 'Sem peças disponíveis'
            },
            follow_redirects=True
        )

        with app.app_context():
            order = WorkOrder.query.get(sample_work_order.id)
            last_history = sorted(order.history, key=lambda h: h.id)[-1]
            assert last_history.new_status == 'Cancelado'
            assert 'Cancelada' in last_history.description


# ============================================================================
# Excluir OS
# ============================================================================

class TestExcluirOS:
    """Testes de exclusão de OS."""

    def test_excluir_os(self, authenticated_client, sample_work_order, app):
        """Deve excluir OS e seus históricos (cascade)."""
        order_id = sample_work_order.id
        response = authenticated_client.post(
            f'/ordens/{order_id}/delete',
            follow_redirects=True
        )
        assert response.status_code == 200
        assert 'excluída com sucesso' in response.data.decode('utf-8')

        with app.app_context():
            assert WorkOrder.query.get(order_id) is None

    def test_excluir_os_404(self, authenticated_client):
        """Excluir OS inexistente deve retornar 404."""
        response = authenticated_client.post('/ordens/99999/delete')
        assert response.status_code == 404


# ============================================================================
# UC9 & UC10 — Consulta por Rastreio e Linha do Tempo
# ============================================================================

class TestRastreio:
    """Testes do módulo de rastreio público (UC9 e UC10)."""

    def test_uc9_rastrear_por_public_id(self, authenticated_client, sample_work_order):
        """UC9/F3.2: Consulta com public_id válido deve retornar dados da OS."""
        response = authenticated_client.get(
            f'/ordens/rastreio/{sample_work_order.public_id}'
        )
        assert response.status_code == 200

    def test_uc9_rastrear_id_inexistente_404(self, authenticated_client):
        """UC9: Consulta com public_id inexistente deve retornar 404."""
        response = authenticated_client.get('/ordens/rastreio/uuid-invalido-99999')
        assert response.status_code == 404

    def test_uc10_historico_exibido(self, authenticated_client, sample_work_order):
        """UC10/F3.3: A página de rastreio deve conter dados do histórico."""
        response = authenticated_client.get(
            f'/ordens/rastreio/{sample_work_order.public_id}'
        )
        html = response.data.decode('utf-8')
        # Deve conter referência ao status
        assert 'Em Orçamento' in html or 'Abertura' in html
