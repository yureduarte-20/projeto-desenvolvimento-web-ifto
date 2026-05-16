from app.extensions import db
from datetime import datetime, timezone


class HistoryOrder(db.Model):
    __tablename__ = 'history_orders'

    id = db.Column(db.Integer, primary_key=True)
    old_status = db.Column(db.String(50), nullable=True)  # None na abertura (primeiro status)
    new_status = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    changed_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    work_order_id = db.Column(db.Integer, db.ForeignKey('work_orders.id'), nullable=False)

    work_order = db.relationship('WorkOrder', back_populates='history')

    def __repr__(self):
        return f'<HistoryOrder {self.id} (OS {self.work_order_id})>'

    @staticmethod
    def save_transition(work_order_id, old_status, new_status, description=None):
        """Adiciona entrada na linha do tempo da OS à sessão atual.

        Spec: /app/models/history_order.py — ação: criar
        Deve ser chamado após qualquer mudança de status (UC1, UC3, UC5).
        O commit() é responsabilidade do caller para manter atomicidade.

        Args:
            work_order_id: ID da WorkOrder relacionada.
            old_status: Status anterior (None na abertura).
            new_status: Novo status efetivado.
            description: Observação opcional sobre a transição.
        """
        entry = HistoryOrder(
            work_order_id=work_order_id,
            old_status=old_status,
            new_status=new_status,
            description=description,
            changed_at=datetime.now(timezone.utc),
        )
        db.session.add(entry)

