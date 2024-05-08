from sqlalchemy.orm import validates
from ext import db
import datetime

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    credit_score = db.Column(db.Integer, nullable=False)
    apr = db.Column(db.Float, nullable=False)
    max_loan = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'credit_score': self.credit_score,
            'apr': self.apr,
            'max_loan': self.max_loan
        }
    
    def __repr__(self):
        return f"Customer(  '{self.credit_score}' , '{self.apr}','{self.max_loan}')"
