from logging import debug
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///jukebox.db' # Tell the server where the database is
app.config['SECRET_KEY'] = 'aa153300de53422ff3fe4c61' # Assign secret key to the server for form security
db = SQLAlchemy(app)

from jukebox import routes