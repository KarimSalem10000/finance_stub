from flask import Flask
from flask_migrate import Migrate
from api import api  # Make sure API imports are set up correctly
from models import Customer  # Importing models after db has been initialized in extensions
from ext import db  # Import the centralized SQLAlchemy instance

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///customers.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)  # Initialize the SQLAlchemy instance with your Flask app
migrate = Migrate(app, db)  # Initialize Flask-Migrate with the app and the db

with app.app_context():
    db.create_all()  # Create all database tables

api.init_app(app)  # Attach the API to the app

if __name__ == '__main__':
    app.run(debug=True, port=8080)
