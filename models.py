from sqlalchemy.orm import validates
from ext import db
import datetime

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    ssn = db.Column(db.String(11), nullable=False, unique=True)
    birth_date = db.Column(db.String(10), nullable=False)
    address = db.Column(db.String(100), nullable=False)
    credit_score = db.Column(db.Integer, nullable=False)
    apr = db.Column(db.Float, nullable=False)
    annual_income = db.Column(db.Float, nullable=False)
    total_loan_amount = db.Column(db.Float, nullable=False)
    max_loan = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'ssn': self.ssn,
            'birth_date': self.birth_date,
            'address': self.address,
            'credit_score': self.credit_score,
            'apr': self.apr,
            'annual_income': self.annual_income,
            'total_loan_amount': self.total_loan_amount,
            'max_loan': self.max_loan
        }
    
    def __repr__(self):
        return f"Customer('{self.first_name}', '{self.last_name}', '{self.ssn}', '{self.birth_date}', '{self.address}', '{self.credit_score}', '{self.annual_income}' , '{self.total_loan_amount}' , '{self.max_loan}')"

    @validates('ssn')
    def validate_ssn(self, key, ssn):
        if len(ssn) != 9:
            raise ValueError("SSN must be exactly 9 digits long")
        if not ssn.isdigit():
            raise ValueError("SSN must contain only digits")
        return ssn


class LoanInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    requested_amount = db.Column(db.Float, nullable=False)
    downpayment = db.Column(db.Float, nullable=False)
    monthly_payment = db.Column(db.Float, nullable=False)
    balance = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='pending')  # e.g., pending, approved, declined
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'requested_amount': self.requested_amount,
            'downpayment': self.downpayment,
            'monthly_payment': self.monthly_payment,
            'balance': self.balance,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }

class PaymentHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    loan_info_id = db.Column(db.Integer, db.ForeignKey('loan_info.id'), nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    amount = db.Column(db.Float, nullable=False)
    balance = db.Column(db.Float, nullable=False)  # Remaining balance after payment

    def to_dict(self):
        return {
            'id': self.id,
            'loan_info_id': self.loan_info_id,
            'payment_date': self.created_at.isoformat(),
            'amount': self.amount,
            'balance': self.balance
        }
class LoanCustomerIds(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    loan_info_id = db.Column(db.Integer, db.ForeignKey('loan_info.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'loan_info_id': self.loan_info_id
        }

    