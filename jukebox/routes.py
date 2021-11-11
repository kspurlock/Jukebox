from jukebox import app
from flask import render_template, redirect, url_for, flash, get_flashed_messages, request
from jukebox.forms import RegisterForm, LoginForm
from jukebox.models import User, Session, Song
from jukebox import db
from flask_login import login_user, logout_user, login_required, current_user


@app.route("/")
@app.route("/home")
def home_page():
    """Provides routing to home page"""
    return render_template("home.html")


@app.route("/login", methods=["GET", "POST"])
def login_page():
    """Provides routing to the login page"""

    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()

        if attempted_user and attempted_user.check_password_correction(
            attempted_password=form.password.data
        ):
            login_user(attempted_user)
            flash(f"Success! You are logged in as: {attempted_user.username}", category="success")

            return redirect(url_for("home_page"))
        else:
            flash("There is no account with this username and password. Please try again!", category="danger")

    return render_template("login.html", form=form)

@app.route("/logout")
def logout_page():
    logout_user()

    flash("You have been logged out, see ya!", category = 'info')
    return redirect(url_for("home_page"))

@app.route("/register", methods=["GET", "POST"])
def register_page():
    """Provides routing to the registration page"""
    form = RegisterForm()

    if form.validate_on_submit():
        # Create a database object
        user_to_create = User(
            username=form.username.data,
            password=form.password_first.data,  # Password param is the setter property
        )
        db.session.add(user_to_create)
        db.session.commit()
        login_user(user_to_create) # Automatically login after registration
        return redirect(url_for("home_page"))
    if form.errors != {}:  # If errors found from validation
        for err_msg in form.errors.values():
            flash(f"Error on creating a user: {err_msg[0]}")
    return render_template("register.html", form=form)

@app.route("/spotify-add")
def spotify_add():
    return


@app.route("/spotify-success/") # There is going to be a request here ?=...
def spotify_success():
    """May need this to get the spotify user key on redirect"""
    query_string = str(request.query_string)
    query_string = query_string[7:]
    current_user.spotify_key = query_string
    return redirect(url_for("home_page"))


@app.route("/player")
@login_required
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
