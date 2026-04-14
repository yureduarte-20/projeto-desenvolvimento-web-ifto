from flask import Blueprint, render_template, redirect, url_for, flash
from app.extensions import db
from app.models.requester import Requester
from app.models.work_order import WorkOrder
from app.models.history_order import HistoryOrder
from app.forms.work_order_forms import WorkOrderForm

bp = Blueprint('work_orders', __name__, url_prefix='/ordens')

@bp.route('/nova', methods=['GET', 'POST'])
def create():
    # ... (existing code remains same)
    form = WorkOrderForm()
    
    if form.validate_on_submit():
        # 1. Verificar se o cliente (Requester) já existe pelo e-mail
        requester = Requester.query.filter_by(email=form.requester_email.data).first()
        
        if not requester:
            # Criar novo requerente caso não exista
            requester = Requester(
                name=form.requester_name.data,
                email=form.requester_email.data,
                phone=form.requester_phone.data,
                document=form.requester_document.data
            )
            db.session.add(requester)
            db.session.flush() # Para pegar o ID gerado sem fazer commit
        
        # 2. Criar a Ordem de Serviço
        work_order = WorkOrder(
            requester_id=requester.id,
            description=form.description.data,
            estimated_delivery_date=form.estimated_delivery_date.data,
            status='Em Orçamento'
        )
        db.session.add(work_order)
        db.session.flush() # Para pegar o ID gerado da OS
        
        # 3. Criar o Histórico Inicial
        history = HistoryOrder(
            work_order_id=work_order.id,
            new_status='Em Orçamento',
            description='Abertura da Ordem de Serviço'
        )
        db.session.add(history)
        
        try:
            db.session.commit()
            flash(f'Ordem de Serviço {work_order.number} criada com sucesso!', 'success')
            return redirect(url_for('work_orders.list_orders')) # Redireciona para a lista
        except Exception as e:
            db.session.rollback()
            flash('Erro ao criar a Ordem de Serviço. Tente novamente.', 'danger')
            print(f"Erro: {e}")

    return render_template('work_orders/create.html', form=form)

@bp.route('/')
def list_orders():
    orders = WorkOrder.query.order_by(WorkOrder.date.desc()).all()
    return render_template('work_orders/list.html', orders=orders)

@bp.route('/<int:id>/delete', methods=['POST'])
def delete(id):
    order = WorkOrder.query.get_or_404(id)
    try:
        db.session.delete(order)
        db.session.commit()
        flash(f'Ordem de Serviço {order.number} excluída com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Erro ao excluir a Ordem de Serviço.', 'danger')
        print(f"Erro: {e}")
    
    return redirect(url_for('work_orders.list_orders'))

@bp.route('/rastreio/<string:public_id>')
def track(public_id):
    order = WorkOrder.query.filter_by(public_id=public_id).first_or_404()
    # Ordenar o histórico para exibir a timeline corretamente
    history = sorted(order.history, key=lambda x: x.changed_at, reverse=True)
    return render_template('work_orders/show_public.html', order=order, history=history)
