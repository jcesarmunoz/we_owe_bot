"""
Modelos de base de datos SQLAlchemy
"""
from datetime import datetime
from app import db


class User(db.Model):
    """
    Modelo de Usuario para gestión de autorización

    Attributes:
        id: ID interno del usuario (Primary Key)
        telegram_id: ID único de Telegram del usuario (usado para autorización)
        name: Nombre del usuario
        is_authorized: Flag para activar/desactivar acceso
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    telegram_id = db.Column(db.BigInteger, unique=True,
                            nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
    is_authorized = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(
        db.DateTime, default=datetime.utcnow, nullable=False)

    # Relaciones
    expenses_paid = db.relationship('Expense', foreign_keys='Expense.payer_id',
                                    backref='payer', lazy='dynamic')
    expenses_debt = db.relationship('Expense', foreign_keys='Expense.debtor_id',
                                    backref='debtor', lazy='dynamic')

    def __repr__(self):
        return f'<User {self.name} (telegram_id: {self.telegram_id})>'

    def to_dict(self):
        """Convierte el objeto a diccionario"""
        return {
            'id': self.id,
            'telegram_id': self.telegram_id,
            'name': self.name,
            'is_authorized': self.is_authorized,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Expense(db.Model):
    """
    Modelo de Gasto para transacciones compartidas

    Attributes:
        id: ID del gasto (Primary Key)
        created_at: Fecha y hora de creación
        description: Concepto del gasto
        amount: Monto del gasto
        currency: Moneda del gasto
        payer_id: ID del usuario que pagó (Foreign Key a User.id)
        debtor_id: ID del usuario que debe (Foreign Key a User.id)
        raw_text: Mensaje original del usuario
        is_settled: Flag que indica si la deuda está saldada
        category: Categoría del gasto (opcional)
    """
    __tablename__ = 'expenses'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(
        db.DateTime, default=datetime.utcnow, nullable=False)
    description = db.Column(db.String(500), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(10), nullable=False, default='COP')
    payer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    debtor_id = db.Column(
        db.Integer, db.ForeignKey('users.id'), nullable=False)
    raw_text = db.Column(db.Text, nullable=True)
    is_settled = db.Column(db.Boolean, default=False, nullable=False)
    category = db.Column(db.String(100), nullable=True)
    due_date = db.Column(db.Date, nullable=True)

    def __repr__(self):
        return f'<Expense {self.description} - {self.amount} {self.currency}>'

    def to_dict(self):
        """Convierte el objeto a diccionario"""
        return {
            'id': self.id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'description': self.description,
            'amount': float(self.amount),
            'currency': self.currency,
            'payer_id': self.payer_id,
            'debtor_id': self.debtor_id,
            'raw_text': self.raw_text,
            'is_settled': self.is_settled,
            'category': self.category,
            'due_date': self.due_date.isoformat() if self.due_date else None
        }
