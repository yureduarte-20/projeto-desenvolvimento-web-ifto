import uuid
from app.extensions import db
from datetime import datetime, timezone
import random

class WorkOrder(db.Model):
    __tablename__ = 'work_orders'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    status = db.Column(db.String(50), default='Em Orçamento', nullable=False)
    requester_id = db.Column(db.Integer, db.ForeignKey('requesters.id'), nullable=False)
    estimated_delivery_date = db.Column(db.DateTime, nullable=True)
    
    number = db.Column(db.String(20), unique=True, nullable=False)
    public_id = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    
    final_price = db.Column(db.Float, nullable=True)
    labor_cost = db.Column(db.Float, nullable=True)
    
    delivered_at = db.Column(db.DateTime, nullable=True)
    is_canceled = db.Column(db.Boolean, default=False)
    cancelation_reason = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=False)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    requester = db.relationship('Requester', back_populates='work_orders')
    history = db.relationship('HistoryOrder', back_populates='work_order', lazy=True, cascade='all, delete-orphan')

    def __init__(self, **kwargs):
        super(WorkOrder, self).__init__(**kwargs)
        if not self.number:
            # Simple number generator for now: OS-YYYYMMDD-RND
            date_str = datetime.now().strftime('%Y%m%d')
            rnd_str = str(random.randint(1000, 9999))
            self.number = f"OS-{date_str}-{rnd_str}"

    def __repr__(self):
        return f'<WorkOrder {self.number}>'
