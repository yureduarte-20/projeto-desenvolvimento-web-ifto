from flask import Blueprint, render_template, redirect, url_for, flash, request
from app.extensions import db
from app.models.requester import Requester
from app.models.work_order import WorkOrder
from app.models.history_order import HistoryOrder
from app.forms.work_order_forms import WorkOrderForm, WorkOrderEditForm
from datetime import datetime, timezone
from flask_login import login_required

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
@login_required
def create():
    """UC1 — Cadastrar Ordem de Serviço.

    Spec: /app/controllers/work_order_controller.py — ação: modificar
    Cria Requester se não existir, instancia WorkOrder e registra
    o histórico inicial via HistoryOrder.save_transition().
    """
    form = WorkOrderForm()

    if form.validate_on_submit():
        # 1. Reusar Requester existente ou criar novo (por e-mail)
        requester = Requester.query.filter_by(email=form.requester_email.data).first()
        if not requester:
            requester = Requester(
                name=form.requester_name.data,
                email=form.requester_email.data,
                phone=form.requester_phone.data,
                document=form.requester_document.data,
            )
            db.session.add(requester)
            db.session.flush()

        # 2. Criar a OS com status inicial forçado
        work_order = WorkOrder(
            requester_id=requester.id,
            description=form.description.data,
            estimated_delivery_date=form.estimated_delivery_date.data,
            status='Em Orçamento',
        )
        work_order.generate_public_id()
        db.session.add(work_order)
        db.session.flush()

        try:
            # 3. Registrar entrada inicial na linha do tempo (UC8)
            HistoryOrder.save_transition(
                work_order_id=work_order.id,
                old_status=None,
                new_status='Em Orçamento',
                description='Abertura da Ordem de Serviço',
            )
            db.session.commit()
            flash(f'Ordem de Serviço {work_order.number} criada com sucesso!', 'success')
            return redirect(url_for('work_orders.list_orders'))
        except Exception as e:
            db.session.rollback()
            flash('Erro ao criar a Ordem de Serviço. Tente novamente.', 'danger')
            print(f"Erro: {e}")

    return render_template('work_orders/create.html', form=form)


@bp.route('/')
@login_required
def list_orders():
    """UC4 — Consultar e Listar Ordens de Serviço."""
    orders = WorkOrder.query.order_by(WorkOrder.date.desc()).all()
    return render_template('work_orders/list.html', orders=orders)


@bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def edit(id):
    """UC2 — Editar OS / UC3 — Atualizar Status / UC5 — Cancelar OS.

    Spec: /app/controllers/work_order_controller.py — ação: modificar
    Lógica de transição de status delegada ao STATUS_TRANSITIONS.
    Histórico registrado via HistoryOrder.save_transition().
    """
    order = WorkOrder.query.get_or_404(id)
    form = WorkOrderEditForm(obj=order)

    config = STATUS_TRANSITIONS.get(order.status, {})
    next_status = config.get('next')
    can_cancel = config.get('can_cancel')
    advance_label = config.get('label')
    is_terminal = next_status is None and not can_cancel

    if form.validate_on_submit() and not is_terminal:
        action = request.form.get('action', 'save')

        old_status = order.status
        new_status = old_status

        order.description = form.description.data
        order.estimated_delivery_date = form.estimated_delivery_date.data

        # Campos financeiros disponíveis para edição nos status de Orçamento e Manutenção
        if order.status in ['Em Orçamento', 'Em Manutenção']:
            order.final_price = form.final_price.data
            order.labor_cost = form.labor_cost.data

        history_desc = form.history_note.data or 'Atualização de informações'

        if action == 'advance' and next_status:
            new_status = next_status
            order.status = new_status
            history_desc = form.history_note.data or f'Status alterado para {new_status}'
            if new_status == 'Finalizado':
                order.delivered_at = datetime.now(timezone.utc)

        elif action == 'cancel' and can_cancel:
            new_status = 'Cancelado'
            order.status = new_status
            order.is_canceled = True
            order.cancelation_reason = form.cancelation_reason.data
            history_desc = f'OS Cancelada. Motivo: {form.cancelation_reason.data}'

        try:
            # Registrar na linha do tempo se houve mudança de status ou nota explícita
            if new_status != old_status or form.history_note.data:
                HistoryOrder.save_transition(
                    work_order_id=order.id,
                    old_status=old_status if new_status != old_status else None,
                    new_status=new_status,
                    description=history_desc,
                )
            db.session.commit()

            flash(f'Ordem de Serviço {order.number} atualizada!', 'success')
            return redirect(url_for('work_orders.list_orders'))
        except Exception as e:
            db.session.rollback()
            flash('Erro ao atualizar a Ordem de Serviço.', 'danger')
            print(f"Erro: {e}")

    return render_template(
        'work_orders/edit.html',
        order=order,
        form=form,
        next_status=next_status,
        can_cancel=can_cancel,
        advance_label=advance_label,
        is_terminal=is_terminal,
    )


@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Excluir OS e seu histórico (cascade)."""
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
