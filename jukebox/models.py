from jukebox import db


class User(db.Model):
    id = db.Column(db.Integer(), primary_key=True)  # User_id #Primary key
    username = db.Column(db.String(length=50), nullable=False, unique=True)
    password_hash = db.Column(db.String(length=60), nullable=False)
    spotify_key = db.Column(db.String(length=100), nullable=True)
    session_id = db.Column(db.String(length=5), db.ForeignKey("session.name"))


class Session(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(length=5), nullable=False, unique=True)
    users = db.relationship("User", backref="owned_user", lazy=True)


class Song(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(length=75), nullable=False, unique=False)
    artist = db.Column(db.String(length=75), nullable=True, unique=False)
    album = db.Column(db.String(length=75), nullable=True, unique=False)
    queued_by = db.Column(db.String(length=50), nullable=False, unique=False)
    length = db.Column(db.String(length=20), nullable=True, unique=False)
