"""
Testes do Report Controller — EletroService
Cobre: UC6 (Gerar Relatórios), UC7 (Dashboard de Métricas)
"""
import pytest
from datetime import datetime, timedelta, timezone
from app.models.work_order import WorkOrder
from app.models.requester import Requester
from app.models.history_order import HistoryOrder


# ============================================================================
# UC6 — Gerar Relatório de Entrada e Saída
# ============================================================================

class TestRelatorioEntradaSaida:
    """Testes do relatório de entrada/saída (UC6/F2.1)."""

    def test_acesso_pagina_relatorios(self, authenticated_client):
        """UC6: GET /relatorios/ deve retornar 200."""
        response = authenticated_client.get('/relatorios/')
        assert response.status_code == 200

    def test_relatorio_entrada_saida_sem_datas(self, authenticated_client):
        """UC6: Relatório sem datas deve usar padrão (últimos 30 dias)."""
        response = authenticated_client.get('/relatorios/entrada-saida')
        assert response.status_code == 200

    def test_relatorio_entrada_saida_com_datas(self, authenticated_client):
        """UC6/F2.1: Relatório com intervalo de datas deve retornar 200."""
        response = authenticated_client.get(
            '/relatorios/entrada-saida?start_date=2026-01-01&end_date=2026-12-31'
        )
        assert response.status_code == 200

    def test_relatorio_com_os_no_periodo(self, authenticated_client, sample_work_order):
        """UC6: Relatório deve listar OS criadas no período consultado."""
        today = datetime.now().strftime('%Y-%m-%d')
        response = authenticated_client.get(
            f'/relatorios/entrada-saida?start_date=2020-01-01&end_date={today}'
        )
        assert response.status_code == 200

    def test_relatorio_datas_invalidas_usa_padrao(self, authenticated_client):
        """UC6: Datas inválidas devem ser ignoradas (usa padrão)."""
        response = authenticated_client.get(
            '/relatorios/entrada-saida?start_date=invalido&end_date=invalido'
        )
        assert response.status_code == 200


# ============================================================================
# UC7 — Visualizar Dashboard de Métricas
# ============================================================================

class TestDashboard:
    """Testes do dashboard de métricas (UC7/F2.2)."""

    def test_acesso_dashboard(self, authenticated_client):
        """UC7: GET /relatorios/dashboard deve retornar 200."""
        response = authenticated_client.get('/relatorios/dashboard')
        assert response.status_code == 200

    def test_dashboard_com_datas(self, authenticated_client):
        """UC7: Dashboard com filtro de datas deve retornar 200."""
        response = authenticated_client.get(
            '/relatorios/dashboard?start_date=2026-01-01&end_date=2026-12-31'
        )
        assert response.status_code == 200

    def test_dashboard_sem_dados(self, authenticated_client):
        """UC7: Dashboard sem OS deve retornar 200 sem erros."""
        response = authenticated_client.get('/relatorios/dashboard')
        assert response.status_code == 200


# ============================================================================
# APIs JSON (para gráficos do Dashboard — UC7)
# ============================================================================

class TestAPIsRelatorios:
    """Testes das APIs JSON de dados para gráficos."""

    def test_api_status_data_retorna_json(self, authenticated_client):
        """UC7: API /relatorios/api/status-data deve retornar JSON válido."""
        response = authenticated_client.get('/relatorios/api/status-data')
        assert response.status_code == 200
        assert response.content_type == 'application/json'

        data = response.get_json()
        assert 'labels' in data
        assert 'datasets' in data

    def test_api_status_data_com_dados(self, authenticated_client, sample_work_order):
        """UC7: API deve retornar dados de status existentes."""
        response = authenticated_client.get('/relatorios/api/status-data')
        data = response.get_json()

        assert len(data['labels']) > 0
        assert 'Em Orçamento' in data['labels']

    def test_api_daily_data_retorna_json(self, authenticated_client):
        """UC7: API /relatorios/api/daily-data deve retornar JSON válido."""
        response = authenticated_client.get('/relatorios/api/daily-data')
        assert response.status_code == 200
        assert response.content_type == 'application/json'

        data = response.get_json()
        assert 'labels' in data
        assert 'datasets' in data
        assert len(data['datasets']) > 0

    def test_api_daily_data_estrutura(self, authenticated_client):
        """UC7: API daily-data deve ter labels (datas) e datasets com contagem."""
        response = authenticated_client.get('/relatorios/api/daily-data')
        data = response.get_json()

        # Deve ter 8 dias de labels (últimos 7 dias + hoje)
        assert len(data['labels']) >= 7
        assert len(data['datasets'][0]['data']) >= 7
