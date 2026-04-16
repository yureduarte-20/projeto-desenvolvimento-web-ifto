from flask import Blueprint, render_template, request, jsonify
from app.extensions import db
from app.models.work_order import WorkOrder
from app.models.requester import Requester
from app.models.history_order import HistoryOrder
from datetime import datetime, timedelta, timezone
from sqlalchemy import func, extract
from flask_login import login_required
bp = Blueprint('reports', __name__, url_prefix='/relatorios')

@bp.route('/')
@login_required
def index():
    """Página inicial dos relatórios"""
    return render_template('reports/index.html')

@bp.route('/entrada-saida')
@login_required
def entrada_saida():
    """Relatório detalhado de entrada e saída de Ordens de Serviço por período"""
    # Obter parâmetros de data
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    
    # Definir datas padrão (últimos 30 dias)
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=30)
    
    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').replace(tzinfo=timezone.utc)
        except ValueError:
            pass
    
    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').replace(tzinfo=timezone.utc)
        except ValueError:
            pass
    
    # Ajustar end_date para incluir todo o dia
    end_date = end_date.replace(hour=23, minute=59, second=59)
    
    # Consultar ordens criadas no período (entradas)
    orders_created = WorkOrder.query.filter(
        WorkOrder.created_at >= start_date,
        WorkOrder.created_at <= end_date
    ).order_by(WorkOrder.created_at.desc()).all()
    
    # Consultar ordens entregues no período (saídas)
    orders_delivered = WorkOrder.query.filter(
        WorkOrder.delivered_at >= start_date,
        WorkOrder.delivered_at <= end_date,
        WorkOrder.status == 'Finalizado'
    ).order_by(WorkOrder.delivered_at.desc()).all()
    
    # Consultar ordens canceladas no período
    orders_canceled = WorkOrder.query.filter(
        WorkOrder.created_at >= start_date,
        WorkOrder.created_at <= end_date,
        WorkOrder.is_canceled == True
    ).order_by(WorkOrder.created_at.desc()).all()
    
    # Estatísticas gerais
    total_created = len(orders_created)
    total_delivered = len(orders_delivered)
    total_canceled = len(orders_canceled)
    
    # Calcular tempo médio de entrega
    avg_delivery_time = None
    if orders_delivered:
        total_days = 0
        for order in orders_delivered:
            if order.created_at and order.delivered_at:
                delta = order.delivered_at - order.created_at
                total_days += delta.days
        avg_delivery_time = total_days / len(orders_delivered) if len(orders_delivered) > 0 else 0
    
    return render_template('reports/entrada_saida.html',
                         start_date=start_date,
                         end_date=end_date,
                         orders_created=orders_created,
                         orders_delivered=orders_delivered,
                         orders_canceled=orders_canceled,
                         total_created=total_created,
                         total_delivered=total_delivered,
                         total_canceled=total_canceled,
                         avg_delivery_time=avg_delivery_time)

@bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard com gráficos e métricas de produtividade"""
    # Obter parâmetros de data
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    
    # Definir datas padrão (últimos 30 dias)
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=30)
    
    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').replace(tzinfo=timezone.utc)
        except ValueError:
            pass
    
    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').replace(tzinfo=timezone.utc)
        except ValueError:
            pass
    
    # Ajustar end_date para incluir todo o dia
    end_date = end_date.replace(hour=23, minute=59, second=59)
    
    # Estatísticas por status
    status_stats = db.session.query(
        WorkOrder.status,
        func.count(WorkOrder.id).label('count')
    ).filter(
        WorkOrder.created_at >= start_date,
        WorkOrder.created_at <= end_date
    ).group_by(WorkOrder.status).all()
    
    # Estatísticas por dia (para gráfico de linha)
    daily_stats = db.session.query(
        func.date(WorkOrder.created_at).label('date'),
        func.count(WorkOrder.id).label('count')
    ).filter(
        WorkOrder.created_at >= start_date,
        WorkOrder.created_at <= end_date
    ).group_by(func.date(WorkOrder.created_at)).order_by('date').all()
    
    # Top clientes (por número de ordens)
    top_clients = db.session.query(
        Requester.name,
        func.count(WorkOrder.id).label('order_count')
    ).join(WorkOrder, Requester.id == WorkOrder.requester_id).filter(
        WorkOrder.created_at >= start_date,
        WorkOrder.created_at <= end_date
    ).group_by(Requester.id, Requester.name).order_by(func.count(WorkOrder.id).desc()).limit(10).all()
    
    # Métricas financeiras
    revenue = db.session.query(
        func.sum(WorkOrder.final_price).label('total_revenue')
    ).filter(
        WorkOrder.status == 'Finalizado',
        WorkOrder.delivered_at >= start_date,
        WorkOrder.delivered_at <= end_date
    ).scalar() or 0
    
    avg_order_value = db.session.query(
        func.avg(WorkOrder.final_price).label('avg_value')
    ).filter(
        WorkOrder.status == 'Finalizado',
        WorkOrder.final_price.isnot(None),
        WorkOrder.delivered_at >= start_date,
        WorkOrder.delivered_at <= end_date
    ).scalar() or 0
    
    # Taxa de cancelamento
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
    
    return render_template('reports/dashboard.html',
                         start_date=start_date,
                         end_date=end_date,
                         status_stats=status_stats,
                         daily_stats=daily_stats,
                         top_clients=top_clients,
                         revenue=revenue,
                         avg_order_value=avg_order_value,
                         total_orders=total_orders,
                         canceled_orders=canceled_orders,
                         cancellation_rate=cancellation_rate)

@bp.route('/api/status-data')
@login_required
def api_status_data():
    """API para dados de status (usado em gráficos)"""
    # Obter dados para gráfico de pizza de status
    status_stats = db.session.query(
        WorkOrder.status,
        func.count(WorkOrder.id).label('count')
    ).group_by(WorkOrder.status).all()
    
    data = {
        'labels': [stat[0] for stat in status_stats],
        'datasets': [{
            'data': [stat[1] for stat in status_stats],
            'backgroundColor': [
                '#36a2eb',  # Em Orçamento - azul
                '#ff6384',  # Em Manutenção - vermelho
                '#ff9f40',  # Aguardando Pagamento - laranja
                '#4bc0c0',  # Aguardando Retirada - turquesa
                '#9966ff',  # Finalizado - roxo
                '#ffcd56',  # Cancelado - amarelo
            ]
        }]
    }
    
    return jsonify(data)

@bp.route('/api/daily-data')
@login_required
def api_daily_data():
    """API para dados diários (usado em gráfico de linha)"""
    # Últimos 7 dias
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=7)
    
    daily_stats = db.session.query(
        func.date(WorkOrder.created_at).label('date'),
        func.count(WorkOrder.id).label('count')
    ).filter(
        WorkOrder.created_at >= start_date,
        WorkOrder.created_at <= end_date
    ).group_by(func.date(WorkOrder.created_at)).order_by('date').all()
    
    # Preencher dias faltantes
    dates = []
    counts = []
    current_date = start_date.date()
    
    while current_date <= end_date.date():
        dates.append(current_date.strftime('%d/%m'))
        # Encontrar contagem para esta data
        count = 0
        for stat in daily_stats:
            if stat[0] == current_date:
                count = stat[1]
                break
        counts.append(count)
        current_date += timedelta(days=1)
    
    data = {
        'labels': dates,
        'datasets': [{
            'label': 'Ordens Criadas',
            'data': counts,
            'borderColor': '#36a2eb',
            'backgroundColor': 'rgba(54, 162, 235, 0.2)',
            'fill': True
        }]
    }
    
    return jsonify(data)