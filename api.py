from flask_restx import Resource, fields, reqparse, Api
from ext import db
from models import Customer
import random

# Create a parser instance
parser = reqparse.RequestParser()

# Add arguments to parser
parser.add_argument('ssn', type=str, required=True, help="Social Security Number is required for identification")


api = Api(version='1.0', title='Customer API', description='A simple Customer API')
ns = api.namespace('customers', description='Customer operations')

credit_scores = [350, 600, 600, 600, 600, 700, 700, 700, 800, 780, 720, 900]

def determine_apr(credit_score):
    if credit_score < 500:
        return 0.20
    elif credit_score < 700:
        return 0.15
    elif credit_score < 800:
        return 0.10
    else:
        return 0.05

def calculate_max_loan(annual_income):
    return annual_income * 0.1 * 3

def calculate_monthly_payment(loan_amount, apr):
    monthly_interest_rate = apr / 12
    total_payments =  36
    return loan_amount * (monthly_interest_rate * (1 + monthly_interest_rate) ** total_payments) / ((1 + monthly_interest_rate) ** total_payments - 1)

# apr =2.0

customer_model = api.model('Customer', {
    'credit_score': fields.Integer(description='Credit Score', required=False),  # Not required if generated
    'apr': fields.Float(description='Annual Percentage Rate', required=False),  # Not required if calculated
    'max_loan': fields.Float(description='Max Loan', required=False)  # Not required if calculated

})

@ns.route('/credit-score')
class CreditScore(Resource):
    @ns.expect(api.model('Customer', {
        'first_name': fields.String(required=True, description='First name'),
        'last_name': fields.String(required=True, description='Last name'),
        'birth_date': fields.String(required=True, description='Date of Birth'),
        'address': fields.String(required=True, description='Address'),
        'ssn': fields.String(required=True, description='Social Security Number'),
        'annual_income': fields.Float(required=True, description='Annual Income')
        }))
    @ns.marshal_with(customer_model)
    def post(self):
        data = api.payload
        credit_score = random.choice(credit_scores)
        apr = determine_apr(credit_score)
        # Calculate max loan
        max_loan = calculate_max_loan(data['annual_income'])
        new_customer = Customer(
            credit_score=credit_score,
            apr=apr,
            max_loan=max_loan
        )
        db.session.add(new_customer)
        db.session.commit()
        #assuamgin i can call a class or change the class infor a function
        return new_customer.to_dict(), 201
