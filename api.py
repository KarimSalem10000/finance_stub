from flask_restx import Resource, fields, reqparse, Api
from ext import db
from models import Customer, LoanInfo, PaymentHistory, LoanCustomerIds
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
        return 10.0
    elif credit_score < 700:
        return 5.0
    elif credit_score < 800:
        return 3.5
    else:
        return 2.0

def calculate_max_loan(annual_income):
    return annual_income * 0.1 * 3

def calculate_monthly_payment(loan_amount, apr):# (loan_amount,apr)
    return (loan_amount * (1 + apr)) / 36
# apr =2.0

customer_model = api.model('Customer', {
    'first_name': fields.String(required=True, description='First name'),
    'last_name': fields.String(required=True, description='Last name'),
    'ssn': fields.String(required=True, description='Social Security Number'),
    'birth_date': fields.String(required=True, description='Date of Birth'),
    'address': fields.String(required=True, description='Address'),
    'credit_score': fields.Integer(description='Credit Score', required=False),  # Not required if generated
    'apr': fields.Float(description='Annual Percentage Rate', required=False),  # Not required if calculated
    'annual_income': fields.Float(description='Anual Income', required=False),  # Not required if provided
    'total_loan_amount': fields.Float(description='Total Loan Amount', required=True),  # Required field
    'max_loan': fields.Float(description='Max Loan', required=False)  # Not required if calculated

})

loaninfo_model = api.model('LoanInfo', {
    'customer_id': fields.Integer(required=True, description='Customer ID'),
    'requested_amount': fields.Float(required=True, description='Requested loan amount'),
    'downpayment': fields.Float(required=True, description='Downpayment amount'),
    'monthly_payment': fields.Float(required=True, description='Monthly payment amount'),
    'balance': fields.Float(required=True, description='Remaining balance after payment'),
    'status': fields.String(description='Loan status')
})

payment_model = api.model('Payment', {
    'loan_info_id': fields.Integer(required=True, description='Loan Request ID'),
    'amount': fields.Float(required=True, description='Payment amount'),
    'payment_date': fields.DateTime(description='Date and time of payment'),
    'amount': fields.Float(required=True, description='Payment amount'),
    'balance': fields.Float(required=True, description='Remaining balance after payment')
})

loancustomer_model = api.model('LoanCustomer', {
    'customer_id': fields.Integer(required=True, description='Customer ID'),
    'loan_id': fields.Integer(required=True, description='Loan ID')
})

@ns.route('/credit-score')
class CreditScore(Resource):
    @ns.expect(api.model('Customer', {
        'first_name': fields.String(required=True, description='First name'),
        'last_name': fields.String(required=True, description='Last name'),
        'ssn': fields.String(required=True, description='Social Security Number'),
        'birth_date': fields.String(required=True, description='Date of Birth'),
        'address': fields.String(required=True, description='Address'),
        'annual_income': fields.Float(required=True, description='Annual Income'),
        'loan_amount': fields.Float(required=True, description='Loan Amount')
        }))
    @ns.marshal_with(customer_model)
    def post(self):
        data = api.payload
        customer = Customer.query.filter_by(ssn=data['ssn']).first()
        if customer:
            # Existing customer handling
            # Calculate the proposed new total loan amount
            proposed_total_loan = customer.total_loan_amount + data['loan_amount']
            annual_income = data['annual_income']
            
            # Check if the new total exceeds the max loan amount
            if proposed_total_loan > customer.max_loan:
                return {"message": "Loan amount request exceeds your loan limit."}, 400

            # Update the customer's total loan amount
            customer.total_loan_amount = proposed_total_loan
            customer.annual_income = annual_income
            
            # Update database entry
            db.session.commit()

            return customer.to_dict(), 200
            #add the new totla to the existing total of loan ammount
            # this would be done using the exsiting apr and the given formual
            # total_loan_amount = (annual_income * 0.1 * 3) + downpayment
            # if this excisted the amount then reject the loan

            # maybe monthly paymenty  should be separated  
        else:
            credit_score = random.choice(credit_scores)
            apr = determine_apr(credit_score)
            # Calculate max loan
            max_loan = calculate_max_loan(data['annual_income'])
            if data['loan_amount'] > max_loan:
                return {"message": "Loan amount request exceeds your loan limit."}, 400
            new_customer = Customer(
                first_name=data['first_name'],
                last_name=data['last_name'],
                ssn=data['ssn'],
                birth_date=data['birth_date'],
                address=data['address'],
                credit_score=credit_score,
                apr=apr,
                annual_income=data['annual_income'],
                total_loan_amount=data['loan_amount'],
                #if this doesn't woprk reject the loan
                #monthly payment = (loan amount * 1+apr) / 36
                max_loan=max_loan
            )
            db.session.add(new_customer)
            db.session.commit()
            #assuamgin i can call a class or change the class infor a function
            return new_customer.to_dict(), 201

@ns.route('/get-customer')
class GetCustomer(Resource):
    @ns.expect(parser)
    @ns.marshal_with(customer_model)  # Assuming customer_model is defined as your output schema
    def get(self):
        # Parse the arguments from the incoming request
        args = parser.parse_args()
        ssn = args['ssn']  # Extract the SSN provided in the request
        
        # Query the database for the customer with the provided SSN
        customer = Customer.query.filter_by(ssn=ssn).first()
        if customer:
            return customer.to_dict(), 200  # Return the customer data and HTTP 200 OK
        else:
            # Return an error message if no customer is found
            api.abort(404, f"No customer found with SSN {ssn}")
#end point for payments
#endpioint for get payment history get total payment

#todo 2
#add a new endpoint for payments

@ns.route('/loan-info')
@ns.param('customer_id', 'Customer ID')
class LoanInfoResource(Resource):
    @ns.expect(api.model('LoanInfo', {
        'customer_id': fields.Integer(required=True, description="Customer ID"),
        'requested_amount': fields.Float(required=True, description="Requested loan amount"),
        'downpayment': fields.Float(required=True, description="Downpayment amount")
        }))
    
    def post(self):
        data = api.payload
        customer = Customer.query.filter_by(id=data['customer_id']).first()
        proposed_total_loan = customer.total_loan_amount + data['requested_amount']
        if proposed_total_loan > customer.max_loan:
                return {"message": "Loan amount request exceeds your loan limit."}, 400

            # Update the customer's total loan amount
        customer.total_loan_amount = proposed_total_loan
        loan_info = LoanInfo(
            customer_id=data['customer_id'],
            requested_amount=data['requested_amount'],
            downpayment=data['downpayment'],
            monthly_payment=calculate_monthly_payment(data['requested_amount'], customer.apr),# customer.apr
            balance=data['requested_amount'],
            status='pending' )
        db.session.add(loan_info)
        db.session.commit()
        LoanCustomer_Ids = LoanCustomerIds(
            customer_id=data['customer_id'],
            loan_info_id=loan_info.id
        )
        db.session.add(LoanCustomer_Ids)
        db.session.commit()
        return {'message': 'Loan request created successfully', 'id': loan_info.id}, 201

@ns.route('/loan-info/<int:customer_id>')
@ns.param('customer_id', 'Customer ID')
class LoanInfoList(Resource):
    def get(self, customer_id):
        loans = LoanInfo.query.filter_by(customer_id=customer_id).all()
        if not loans:
            return {'message': 'No loans found for this customer.'}, 404
        return {'loans': [loan.to_dict() for loan in loans]}, 200


@ns.route('/payments')
class PaymentHistoryResource(Resource):
    @ns.expect(api.model('Payment', {
        'amount': fields.Float(required=True, description="Payment amount"),
        'ssn': fields.String(required=True, description="Social Security Number of the customer making the payment")
    }))
    def post(self):
        data = api.payload
        customer = Customer.query.filter_by(ssn=data['ssn']).first()
        if not customer:
            api.abort(404, "No customer found with the given SSN")
        
        loan_info_id = LoanCustomerIds.query.filter_by(customer_id=customer.id).first().loan_info_id

        loan_info = LoanInfo.query.filter_by(id=loan_info_id, customer_id=customer.id).first()
        if not loan_info:
            api.abort(404, "No loan information found with the given ID that matches the customer ID")

        # Calculate new balance and check for payment issues
        new_balance = loan_info.balance - data['amount']
        if new_balance < 0:
            api.abort(400, "Payment amount exceeds current balance")

        # Create and save the payment history
        payment_history = PaymentHistory(
            loan_info_id=loan_info_id,
            amount=data['amount'],
            balance=new_balance # Assuming you're recording the payment timestamp
        )
        db.session.add(payment_history)

        # Update loan_info's current balance
        loan_info.balance = new_balance
        db.session.commit()

        return {'message': 'Payment recorded successfully', 'new_balance': new_balance}, 201

@ns.route('/payment-history/<int:loan_info_id>')
@ns.param('loan_info_id', 'Loan Request ID')
class PaymentHistoryList(Resource):
    def get(self, loan_info_id):
        payments = PaymentHistory.query.filter_by(loan_info_id=loan_info_id).all()
        if not payments:
            return {'message': 'No payment history found for this loan.'}, 404
        return {'payments': [payment.to_dict() for payment in payments]}, 200
