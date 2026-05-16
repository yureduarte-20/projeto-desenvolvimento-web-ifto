from flask import Blueprint, render_template, request, jsonify
from app.extensions import db, cache
from app.models.work_order import WorkOrder
from app.models.requester import Requester
from datetime import datetime, timedelta, timezone
from sqlalchemy import func
from flask_login import login_required

bp = Blueprint('reports', __name__, url_prefix='/relatorios')


def _parse_date_range(req):
    """Extrai e valida start_date/end_date dos query params.

    Spec: report_controller — eliminar duplicação de parse de datas.
    Retorna (start_date, end_date) como objetos datetime UTC.
    Padrão: últimos 30 dias quando parâmetros ausentes ou inválidos.
    """
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=30)

    raw_start = req.args.get('start_date')
    raw_end = req.args.get('end_date')

    if raw_start:
        try:
            start_date = datetime.strptime(raw_start, '%Y-%m-%d').replace(tzinfo=timezone.utc)
        except ValueError:
            pass

    if raw_end:
        try:
            end_date = datetime.strptime(raw_end, '%Y-%m-%d').replace(tzinfo=timezone.utc)
        except ValueError:
            pass

    # Inclui todo o último dia do intervalo
    end_date = end_date.replace(hour=23, minute=59, second=59)
    return start_date, end_date


@bp.route('/')
@login_required
def index():
    """Página inicial dos relatórios."""
    return render_template('reports/index.html')


@bp.route('/entrada-saida')
@login_required
def entrada_saida():
    """Relatório detalhado de entrada e saída de OS por período (UC6)."""
    start_date, end_date = _parse_date_range(request)

    orders_created = WorkOrder.query.filter(
        WorkOrder.created_at >= start_date,
        WorkOrder.created_at <= end_date
    ).order_by(WorkOrder.created_at.desc()).all()

    orders_delivered = WorkOrder.query.filter(
        WorkOrder.delivered_at >= start_date,
        WorkOrder.delivered_at <= end_date,
        WorkOrder.status == 'Finalizado'
    ).order_by(WorkOrder.delivered_at.desc()).all()

    orders_canceled = WorkOrder.query.filter(
        WorkOrder.created_at >= start_date,
        WorkOrder.created_at <= end_date,
        WorkOrder.is_canceled == True
    ).order_by(WorkOrder.created_at.desc()).all()

    # Tempo médio de entrega em dias
    avg_delivery_time = None
    if orders_delivered:
        days = [
            (o.delivered_at - o.created_at).days
            for o in orders_delivered
            if o.created_at and o.delivered_at
        ]
        avg_delivery_time = sum(days) / len(days) if days else 0

    return render_template(
        'reports/entrada_saida.html',
        start_date=start_date,
        end_date=end_date,
        orders_created=orders_created,
        orders_delivered=orders_delivered,
        orders_canceled=orders_canceled,
        total_created=len(orders_created),
        total_delivered=len(orders_delivered),
        total_canceled=len(orders_canceled),
        avg_delivery_time=avg_delivery_time,
    )


@bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard com gráficos e métricas de produtividade (UC7)."""
    start_date, end_date = _parse_date_range(request)

    status_stats = db.session.query(
        WorkOrder.status,
        func.count(WorkOrder.id).label('count')
    ).filter(
        WorkOrder.created_at >= start_date,
        WorkOrder.created_at <= end_date
    ).group_by(WorkOrder.status).all()

    daily_stats = db.session.query(
        func.date(WorkOrder.created_at).label('date'),
        func.count(WorkOrder.id).label('count')
    ).filter(
        WorkOrder.created_at >= start_date,
        WorkOrder.created_at <= end_date
    ).group_by(func.date(WorkOrder.created_at)).order_by('date').all()

    top_clients = db.session.query(
        Requester.name,
        func.count(WorkOrder.id).label('order_count')
    ).join(WorkOrder, Requester.id == WorkOrder.requester_id).filter(
        WorkOrder.created_at >= start_date,
        WorkOrder.created_at <= end_date
    ).group_by(Requester.id, Requester.name).order_by(
        func.count(WorkOrder.id).desc()
    ).limit(10).all()

    revenue = db.session.query(
        func.sum(WorkOrder.final_price)
    ).filter(
        WorkOrder.status == 'Finalizado',
        WorkOrder.delivered_at >= start_date,
        WorkOrder.delivered_at <= end_date
    ).scalar() or 0

    avg_order_value = db.session.query(
        func.avg(WorkOrder.final_price)
    ).filter(
        WorkOrder.status == 'Finalizado',
        WorkOrder.final_price.isnot(None),
        WorkOrder.delivered_at >= start_date,
        WorkOrder.delivered_at <= end_date
    ).scalar() or 0

    total_orders = db.session.query(func.count(WorkOrder.id)).filter(
        WorkOrder.created_at >= start_date,
        WorkOrder.created_at <= end_date
    ).scalar() or 0

    canceled_orders = db.session.query(func.count(WorkOrder.id)).filter(
        WorkOrder.created_at >= start_date,
        WorkOrder.created_at <= end_date,
        WorkOrder.is_canceled == True
    ).scalar() or 0

    cancellation_rate = (canceled_orders / total_orders * 100) if total_orders > 0 else 0

    return render_template(
        'reports/dashboard.html',
        start_date=start_date,
        end_date=end_date,
        status_stats=status_stats,
        daily_stats=daily_stats,
        top_clients=top_clients,
        revenue=revenue,
        avg_order_value=avg_order_value,
        total_orders=total_orders,
        canceled_orders=canceled_orders,
        cancellation_rate=cancellation_rate,
    )


@bp.route('/api/status-data')
@login_required
@cache.cached(timeout=300, key_prefix='api_status_data')
def api_status_data():
    """API JSON para gráfico de pizza de status (UC7).

    Cache: 300s (SimpleCache in-memory).
    Spec: /app/controllers/report_controller.py — otimização de desempenho.
    """
    status_stats = db.session.query(
        WorkOrder.status,
        func.count(WorkOrder.id).label('count')
    ).group_by(WorkOrder.status).all()

    data = {
        'labels': [s[0] for s in status_stats],
        'datasets': [{
            'data': [s[1] for s in status_stats],
            'backgroundColor': [
                '#36a2eb',  # Em Orçamento
                '#ff6384',  # Em Manutenção
                '#ff9f40',  # Aguardando Pagamento
                '#4bc0c0',  # Aguardando Retirada
                '#9966ff',  # Finalizado
                '#ffcd56',  # Cancelado
            ],
        }],
    }
    return jsonify(data)


@bp.route('/api/daily-data')
@login_required
@cache.cached(timeout=300, key_prefix='api_daily_data')
def api_daily_data():
    """API JSON para gráfico de linha de OS por dia (UC7).

    Cache: 300s (SimpleCache in-memory).
    Spec: /app/controllers/report_controller.py — otimização de desempenho.
    """
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=7)

    daily_stats = db.session.query(
        func.date(WorkOrder.created_at).label('date'),
        func.count(WorkOrder.id).label('count')
    ).filter(
        WorkOrder.created_at >= start_date,
        WorkOrder.created_at <= end_date
    ).group_by(func.date(WorkOrder.created_at)).order_by('date').all()

    # Preenche dias sem OS com count=0
    dates, counts = [], []
    current = start_date.date()
    stat_map = {s[0]: s[1] for s in daily_stats}

    while current <= end_date.date():
        dates.append(current.strftime('%d/%m'))
        counts.append(stat_map.get(current, 0))
        current += timedelta(days=1)

    data = {
        'labels': dates,
        'datasets': [{
            'label': 'Ordens Criadas',
            'data': counts,
            'borderColor': '#36a2eb',
            'backgroundColor': 'rgba(54, 162, 235, 0.2)',
            'fill': True,
        }],
    }
    return jsonify(data)