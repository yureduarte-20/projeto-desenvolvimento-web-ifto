from flask import Blueprint, render_template, request
from app.models.work_order import WorkOrder

bp = Blueprint('tracking', __name__, url_prefix='/rastreio')


@bp.route('/search')
def search():
    """UC9 — Consultar Status por Código de Rastreamento (acesso público).

    Spec: /app/controllers/tracking_controller.py — ação: criar
    Não requer autenticação. Recebe 'code' via GET query param.
    Retorna status atual e linha do tempo da OS (UC10 embutido na mesma página).
    """
    code = request.args.get('code', '').strip()

    if not code:
        return render_template('tracking/index.html', error=None)

    work_order = WorkOrder.query.filter_by(public_id=code).first()

    if not work_order:
        return render_template(
            'tracking/index.html',
            error='Código de rastreamento não encontrado. Verifique e tente novamente.',
            code=code,
        )

    # UC10: ordena histórico cronologicamente decrescente para linha do tempo
    history = sorted(work_order.history, key=lambda h: h.changed_at, reverse=True)

    return render_template('tracking/result.html', work_order=work_order, history=history)
