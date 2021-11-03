from logging import debug
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///jukebox.db'
db = SQLAlchemy(app)

class User(db.Model):
    user_id = db.Column(db.Integer(), primary_key=True) #User_id #Primary key
    name = db.Column(db.String(length=50), nullable=False, unique=False) #User_handle
    # session_id = db.Column(db.Integer(), foreign_key=True) #Session_id #Foreign key
    
class Session(db.Model):
    session_id = db.Column(db.Integer(), primary_key=True)

class Song(db.Model):
    song_id = db.Column(db.Integer(), primary_key=True)
    song_name = db.Column(db.String(length=75), nullable=False, unique=False)
    artist_name = db.Column(db.String(length=75), nullable=True, unique=False)
    album_name = db.Column(db.String(length=75), nullable=True, unique=False)
    length = db.Column(db.String(length=20), nullable=True, unique=False)


@app.route("/")
@app.route("/home")
def home_page():
    """Provides routing to home page"""
    return render_template("home.html")

@app.route("/main")
def main_page():
    """Provides routing to the player page"""
    return render_template("main.html")
