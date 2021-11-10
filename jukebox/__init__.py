"""
This file contains all Flask submodules that need to be initialized/called
before utilizing anything else in the application.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__) # Create a flask application
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///jukebox.db' # Tell the server where the database is
app.config['SECRET_KEY'] = 'aa153300de53422ff3fe4c61' # Assign secret key to the server for form security
db = SQLAlchemy(app) # Database manager
bcrypt = Bcrypt(app) # Password hashing manager
login_manager = LoginManager(app) # Login manager

from jukebox import routes # This is placed here to avoid circular imports