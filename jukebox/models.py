from jukebox import db, login_manager
from jukebox import bcrypt
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)  # Primary key
    username = db.Column(db.String(length=50), nullable=False, unique=True)
    password_hash = db.Column(db.String(length=60), nullable=False)
    spotify_key = db.Column(db.String(), nullable=True, unique=True)
    session_id = db.Column(
        db.String(length=5), db.ForeignKey("session.name")
    )  # Foreign key is session_name (Not the id number)

    @property
    def password(self):
        """Getter property"""
        return self.password

    @password.setter
    def password(self, password_plain):
        """Function takes a string input and generates a hash to store in the database"""
        self.password_hash = bcrypt.generate_password_hash(password_plain).decode(
            "utf-8"
        )

    def check_password_correction(self, attempted_password):
        """Method for determining if a plain text password string matches the stored hash version

        Args:
            attempted_password (str): plain text password inputted from login form

        Returns:
            bool: returns True if password matches, False otherwise
        """
        return bcrypt.check_password_hash(self.password_hash, attempted_password)

    def __repr__(self):
        return self.username


class Session(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(length=5), nullable=False, unique=True)
    host_user = db.Column(db.String(length=5), nullable=False, unique=True)
    user_count = db.Column(db.Integer(), nullable=False, unique=False)
    veto_count= db.Column(db.Integer(), nullable=False, unique=False)
    users = db.relationship("User", backref="has_user", lazy=True)
    songs = db.relationship("Song", backref="has_song", lazy=True)


class Song(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(length=75), nullable=False, unique=False)
    artist = db.Column(db.String(length=75), nullable=True, unique=False)
    album = db.Column(db.String(length=75), nullable=True, unique=False)
    queued_by = db.Column(db.String(length=50), nullable=False, unique=False)
    length = db.Column(db.String(length=20), nullable=True, unique=False)
    session_id = db.Column(
        db.String(length=5), db.ForeignKey("session.name")
    )  # Foreign key is session_name (Not the id number)