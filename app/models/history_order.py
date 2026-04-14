from app.extensions import db
from datetime import datetime, timezone

class HistoryOrder(db.Model):
    __tablename__ = 'history_orders'

    id = db.Column(db.Integer, primary_key=True)
    old_status = db.Column(db.String(50), nullable=True) # Pode ser null na inserção/primeiro status
    new_status = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    changed_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    work_order_id = db.Column(db.Integer, db.ForeignKey('work_orders.id'), nullable=False)

    work_order = db.relationship('WorkOrder', back_populates='history')

    def __repr__(self):
        return f'<HistoryOrder {self.id} (OS {self.work_order_id})>'
