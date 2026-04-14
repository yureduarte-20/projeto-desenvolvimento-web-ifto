from flask import Blueprint, render_template, redirect, url_for, flash, request
from app.extensions import db
from app.models.requester import Requester
from app.models.work_order import WorkOrder
from app.models.history_order import HistoryOrder
from app.forms.work_order_forms import WorkOrderForm, WorkOrderEditForm
from datetime import datetime, timezone

bp = Blueprint('work_orders', __name__, url_prefix='/ordens')

# Máquina de estados baseada no Fluxo de Status.mermaid
STATUS_TRANSITIONS = {
    'Em Orçamento':         {'next': 'Em Manutenção',          'can_cancel': True,  'label': 'Iniciar Manutenção'},
    'Em Manutenção':        {'next': 'Aguardando Pagamento',   'can_cancel': True,  'label': 'Concluir Manutenção'},
    'Aguardando Pagamento': {'next': 'Aguardando Retirada',    'can_cancel': False, 'label': 'Registrar Pagamento'},
    'Aguardando Retirada':  {'next': 'Finalizado',             'can_cancel': False, 'label': 'Entregar ao Cliente'},
    'Finalizado':           {'next': None,                      'can_cancel': False, 'label': None},
    'Cancelado':            {'next': None,                      'can_cancel': False, 'label': None},
}

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

@bp.route('/<int:id>/editar', methods=['GET', 'POST'])
def edit(id):
    order = WorkOrder.query.get_or_404(id)
    form = WorkOrderEditForm(obj=order)
    
    # Identificar transições possíveis
    config = STATUS_TRANSITIONS.get(order.status, {})
    next_status = config.get('next')
    can_cancel = config.get('can_cancel')
    advance_label = config.get('label')
    
    # OS já finalizada ou cancelada é apenas leitura
    is_terminal = next_status is None and not can_cancel

    if form.validate_on_submit() and not is_terminal:
        action = request.form.get('action', 'save') # save, advance, cancel
        
        old_status = order.status
        new_status = old_status
        
        # Atualizar campos básicos
        order.description = form.description.data
        order.estimated_delivery_date = form.estimated_delivery_date.data
        
        # Campos financeiros (disponíveis a partir de Em Manutenção)
        if order.status != 'Em Orçamento':
            order.final_price = form.final_price.data
            order.labor_cost = form.labor_cost.data

        # Lógica de Transição
        history_desc = form.history_note.data or "Atualização de informações"
        
        if action == 'advance' and next_status:
            new_status = next_status
            order.status = new_status
            history_desc = form.history_note.data or f"Status alterado para {new_status}"
            if new_status == 'Finalizado':
                order.delivered_at = datetime.now(timezone.utc)
        
        elif action == 'cancel' and can_cancel:
            new_status = 'Cancelado'
            order.status = new_status
            order.is_canceled = True
            order.cancelation_reason = form.cancelation_reason.data
            history_desc = f"OS Cancelada. Motivo: {form.cancelation_reason.data}"

        # Salvar histórico se houve mudança ou nota
        if new_status != old_status or form.history_note.data:
            history = HistoryOrder(
                work_order_id=order.id,
                old_status=old_status if new_status != old_status else None,
                new_status=new_status,
                description=history_desc
            )
            db.session.add(history)
            
        try:
            db.session.commit()
            flash(f'Ordem de Serviço {order.number} atualizada!', 'success')
            return redirect(url_for('work_orders.list_orders'))
        except Exception as e:
            db.session.rollback()
            flash('Erro ao atualizar a Ordem de Serviço.', 'danger')
            print(f"Erro: {e}")
            
    return render_template('work_orders/edit.html', 
                           order=order, 
                           form=form, 
                           next_status=next_status, 
                           can_cancel=can_cancel,
                           advance_label=advance_label,
                           is_terminal=is_terminal)

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
