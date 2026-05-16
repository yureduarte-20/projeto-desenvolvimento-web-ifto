"""
Testes do Tracking Controller — EletroService (Módulo de Transparência ao Cliente)
Cobre: UC9 (Consultar Status por Código de Rastreamento) e UC10 (Linha do Tempo)
Acesso público — sem autenticação.

Rastreabilidade:
    F3.1 — Geração de código único (validado via model)
    F3.2 — Consulta pública por código de rastreamento
    F3.3 — Visualização da linha do tempo
"""
import pytest
from app.models.work_order import WorkOrder
from app.models.history_order import HistoryOrder


class TestTrackingPublico:
    """Testes de acesso público ao módulo de rastreamento (UC9 e UC10)."""

    def test_pagina_inicial_rastreio_sem_codigo(self, client, db):
        """UC9: GET /rastreio/search sem parâmetro deve retornar 200 e o formulário."""
        response = client.get('/rastreio/search')
        assert response.status_code == 200
        html = response.data.decode('utf-8')
        assert 'Rastrear' in html

    def test_uc9_codigo_valido_retorna_resultado(self, client, sample_work_order):
        """UC9/F3.2: Código de rastreamento válido deve exibir status da OS."""
        response = client.get(f'/rastreio/search?code={sample_work_order.public_id}')
        assert response.status_code == 200
        html = response.data.decode('utf-8')
        assert sample_work_order.number in html
        assert sample_work_order.status in html

    def test_uc9_codigo_inexistente_exibe_erro(self, client, db):
        """UC9: Código inexistente deve exibir mensagem de erro, não 404."""
        response = client.get('/rastreio/search?code=codigo-que-nao-existe-99999')
        assert response.status_code == 200
        html = response.data.decode('utf-8')
        assert 'não encontrado' in html.lower() or 'não encontrada' in html.lower()

    def test_uc9_sem_autenticacao(self, client, sample_work_order):
        """UC9: Endpoint deve funcionar sem nenhuma sessão autenticada."""
        # client puro (sem authenticated_client) — não faz login
        response = client.get(f'/rastreio/search?code={sample_work_order.public_id}')
        # Não deve redirecionar para login
        assert response.status_code == 200
        assert '/auth/login' not in response.headers.get('Location', '')

    def test_uc10_linha_do_tempo_exibida(self, client, sample_work_order):
        """UC10/F3.3: A página de resultado deve conter o histórico cronológico."""
        response = client.get(f'/rastreio/search?code={sample_work_order.public_id}')
        html = response.data.decode('utf-8')
        # Deve exibir entrada de abertura registrada no histórico
        assert 'Em Orçamento' in html

    def test_uc10_descricao_historico_exibida(self, client, sample_work_order):
        """UC10/F3.3: Descrição dos eventos do histórico deve aparecer na linha do tempo."""
        response = client.get(f'/rastreio/search?code={sample_work_order.public_id}')
        html = response.data.decode('utf-8')
        assert 'Abertura' in html or 'Ordem de Serviço' in html

    def test_uc9_codigo_vazio_exibe_formulario(self, client, db):
        """UC9: GET com code='' deve exibir formulário sem mensagem de erro."""
        response = client.get('/rastreio/search?code=')
        assert response.status_code == 200
        html = response.data.decode('utf-8')
        # Formulário deve estar presente
        assert 'form' in html.lower()
        # Não deve exibir mensagem de erro de "não encontrado"
        assert 'não encontrad' not in html.lower()

    def test_uc9_public_id_unico_por_os(self, client, db, sample_requester):
        """UC9/F3.1: Cada OS tem seu próprio public_id único e consultável."""
        os1 = WorkOrder(requester_id=sample_requester.id, description='OS 1 de teste')
        os2 = WorkOrder(requester_id=sample_requester.id, description='OS 2 de teste')
        db.session.add_all([os1, os2])
        db.session.flush()
        HistoryOrder.save_transition(os1.id, None, 'Em Orçamento', 'Abertura OS1')
        HistoryOrder.save_transition(os2.id, None, 'Em Orçamento', 'Abertura OS2')
        db.session.commit()

        r1 = client.get(f'/rastreio/search?code={os1.public_id}')
        r2 = client.get(f'/rastreio/search?code={os2.public_id}')

        assert r1.status_code == 200
        assert r2.status_code == 200
        assert os1.number in r1.data.decode('utf-8')
        assert os2.number in r2.data.decode('utf-8')
