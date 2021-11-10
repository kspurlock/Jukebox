from jukebox import app
from flask import render_template, redirect, url_for, flash, get_flashed_messages
from jukebox.forms import RegisterForm
from jukebox.models import User, Session, Song
from jukebox import db


@app.route("/")
@app.route("/home")
def home_page():
    """Provides routing to home page"""
    return render_template("home.html")


@app.route("/login")
def login_page():
    """Provides routing to the login page"""
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register_page():
    """Provides routing to the registration page"""
    form = RegisterForm()

    if form.validate_on_submit():
        # Create a database object
        user_to_create = User(
            username=form.username.data, password_hash=form.password_init.data
        )
        db.session.add(user_to_create)
        db.session.commit()
        return redirect(url_for("home_page"))
    if form.errors != {}:  # If not errors found from validation
        for err_msg in form.errors.values():
            flash(f"Error on creating a user: {err_msg[0]}", category="danger")
    return render_template("register.html", form=form)


@app.route("/player")
def player_page():
    """Provides routing to the player page"""

    # Mock examples of the information that needs to be passed here
    queue_list = [
        {
            "song_name": "The Great Vurve - 2005 Remaster",
            "artist_name": "Talking Heads",
            "album_name": "Remain in Light (Deluxe Version)",
            "queued_by": "kianworld",
            "length": "6:27",
        },
        {
            "song_name": "The Great Vurve - 2005 Remaster",
            "artist_name": "Talking Heads",
            "album_name": "Remain in Light (Deluxe Version)",
            "queued_by": "kianworld",
            "length": "6:27",
        },
    ]

    queue_list = Song.query.all()
    user_list = User.query.all()

    return render_template("player.html", queue=queue_list, users=user_list)