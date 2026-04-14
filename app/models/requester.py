from app.extensions import db
from datetime import datetime, timezone

class Requester(db.Model):
    __tablename__ = 'requesters'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    document = db.Column(db.String(20), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True) # Opcional: usuário pode se cadastrar depois
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    user = db.relationship('User', backref=db.backref('requester', uselist=False))
    work_orders = db.relationship('WorkOrder', back_populates='requester', lazy=True)

    def __repr__(self):
        return f'<Requester {self.email}>'
