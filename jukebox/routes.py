from sqlalchemy.sql.elements import Null
from werkzeug.exceptions import BadRequestKeyError
from jukebox import app
from flask import (
    render_template,
    redirect,
    url_for,
    flash,
    get_flashed_messages,
    request,
    jsonify,
    abort,
)
from jukebox.forms import RegisterForm, LoginForm, JoinSessionForm
from jukebox.models import User, Session, Song, load_user
from jukebox import db
from flask_login import login_user, logout_user, login_required, current_user
from jukebox.spot import get_user_access
from sqlalchemy.exc import IntegrityError
import random


@app.route("/", methods=["GET", "POST"])
@app.route("/home", methods=["GET", "POST"])
def home_page():
    """Provides routing to home page"""
    form = JoinSessionForm()
    if request.method == "POST":
        if form.validate_on_submit():
            attempted_session = Session.query.filter_by(
                name=form.session_field.data
            ).first()

            if attempted_session == None:
                flash("This session doesn't exist!", category="info")
                return redirect(url_for("home_page"))

            else:
                try:
                    user_obj = User.query.filter_by(id=int(current_user.id)).first()
                    user_obj.session_id = form.session_field.data
                    attempted_session.user_count += 1
                    db.session.commit()

                    return redirect(
                        url_for("player_page", session_id=form.session_field.data)
                    )
                    
                except AttributeError as e:
                    flash("You need to be logged in to join a session!", category="info")
                    return redirect(url_for("login_page"))


    elif request.method == "GET":
        return render_template("home.html", session_form=form)


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
            attempted_user.session_id = (
                None  # Accounts for if the user left a session by closing tab
            )
            db.session.commit()
            flash(
                f"Success! You are logged in as: {attempted_user.username}",
                category="success",
            )

            return redirect(url_for("home_page"))
        else:
            flash(
                "There is no account with this username and password. Please try again!",
                category="danger",
            )

    return render_template("login.html", form=form)


@app.route("/logout")
def logout_page():
    logout_user()

    flash("You have been logged out, see ya!", category="info")
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

        try: 
            db.session.add(user_to_create)
            db.session.commit()
            login_user(user_to_create)  # Automatically login after registration
            return redirect(url_for("home_page"))
        except IntegrityError:
            flash("This username already exists, try again!")
            return render_template("register.html", form=form)
    if form.errors != {}:  # If errors found from validation
        for err_msg in form.errors.values():
            flash(f"Error on creating a user: {err_msg[0]}")
    return render_template("register.html", form=form)


@app.route("/spotify-add")
@login_required
def spotify_add():
    """Initial route that leads from the home page to the spotify permission page"""
    get_user_access(current_user.username)


@app.route("/spotify-success/")  # There is going to be a REST variable here (code?v=...)
@login_required
def spotify_success():
    """May need this to get the spotify user key on redirect"""
    try:
        query_string = request.args["code"]
        try:
            user_obj = User.query.filter_by(id=int(current_user.id)).first()
            user_obj.spotify_key = query_string
            db.session.commit()
            flash("Spotify account linked!", category="success")
            return redirect(url_for("home_page"))

        except IntegrityError:  # Occurs when a Spotify key has been linked to another account
            flash("Spotify cannot be linked: Linked elsewhere.", category="danger")
            return redirect(url_for("home_page"))

    except BadRequestKeyError:  # Occurs when the user denies the Spotify permission page
        flash("Spotify cannot be linked: Permission Denied", category="info")
        return redirect(url_for("home_page"))


@app.route("/create-session")
@login_required
def create_session():
    new_session_name = str(random.randint(10000, 99999))
    duplicate = Session.query.filter_by(name=new_session_name).first()

    while duplicate != None:
        # Ensure that a unique session name is found
        new_session_name = str(random.randint(10000, 99999))
        duplicate = Session.query.filter_by(name=new_session_name)

    try:
        session_to_create = Session(
            name=new_session_name, host_user=current_user.id, user_count=1, veto_count=0
        )
        db.session.add(session_to_create)
        user_obj = User.query.filter_by(
            id=int(current_user.id)
        ).first()  # Probably need to change this to .name at some point, duplicate reference
        user_obj.session_id = new_session_name
        db.session.commit()
        return redirect(url_for("player_page", session_id=new_session_name))

    except IntegrityError:
        flash("Could not create session.", category="info")
        return redirect(url_for("home_page"))


@app.route("/player/leave-session/<session_id>")
def leave_session(session_id):
    """Performs cleanup whenever a user leaves a session"""
    # Find what session we need to modify
    session_id_ = str(session_id)
    session_obj = Session.query.filter_by(name=session_id_).first()
    session_obj.user_count -= 1

    # Find what user is leaving
    user_obj = User.query.filter_by(id=str(current_user.id)).first()
    user_obj.session_id = None

    if session_obj.user_count == 0:
        # If there is no users left in the session

        # Delete all songs that belong to the session
        Song.query.filter(Song.session_id == session_id_).delete()

        # Delete the session
        Session.query.filter(Session.name == session_id_).delete()

    elif session_obj.host_user == user_obj.id:
        # Case where the host leaves, need to reassign host privilege

        # Find the next user in the session after the host has left
        second_user = User.query.filter_by(session_id=session_id_).first()
        session_obj.host_user = second_user.id

    # Commit all changes
    db.session.commit()

    # Return to the home page
    return redirect(url_for("home_page"))


@app.route("/player/<session_id>", methods=["GET", "POST"])
@login_required
def player_page(session_id):
    """Provides routing to the player page"""
    user_obj = User.query.filter_by(id=str(current_user.id)).first()
    session_obj = Session.query.filter_by(name=session_id).first()

    if user_obj.session_id != str(session_id):
        # Handles the case where a user tries to join through the URL

        flash("Hey! you can't join a session like that!", category="danger")
        return redirect(url_for("home_page"))

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

    queue_list = Song.query.filter_by(session_id=session_id).all()
    user_list = User.query.filter_by(session_id=session_id).all()

    """
    #GET request for JS file
    if request.method == 'GET':
        return jsonify()

    #POST request for JS file
    if request.method == 'POST':
        print(request.get_json())
    """
    return render_template(
        "player.html",
        session_obj=session_obj,
        session_id=session_id,
        queue=queue_list,
        users=user_list,
    )

@app.route("/player/<session_id>/update-userlist", methods=["POST"])
def update_userlist(session_id):
    user_list = User.query.filter_by(session_id=str(session_id)).all()
    session_obj = Session.query.filter_by(name=str(session_id)).first()

    return jsonify("", render_template("player-userlist.html", users=user_list, session_obj=session_obj))

@app.route("/player/<session_id>/search-song", methods=["POST"])
def search_song(session_id):
    song_search = []
    for i in range(10):
        song_test = {
        "id": i,
        "title": "test_title",
        "artist": "test_artist",
        "album": "test_album",
        "length": str(random.randint(0,10)),
        "image_url": "https://www.w3schools.com/images/w3schools_green.jpg",
        "playback_uri": "none"}
        song_search.append(song_test)
    

    # Who sent the request
    user_obj = User.query.filter_by(id=int(request.form["sentUser"])).first()
    return jsonify("", render_template("player-searchlist.html", song_search=song_search))

@app.route("/player/<session_id>/add-song", methods=["POST"])
def add_song(session_id):
    print(request.form['song_id'])

    return jsonify("", "yep")


@app.errorhandler(404)
def not_found_error(err_msg):
    flash(f"{err_msg}")
    return render_template("404.html")

"""Test routes go down here"""

@app.route("/test-route", methods=["GET", "POST"])
def test_route():

    if request.method == "POST":
        data = request.form.get("field1")
        print(data)
    if request.method =="GET":
        print(1)

    return render_template("test_page.html")

@app.route("/404-error-test")
def error_page_test():
    abort(404)


@app.route("/purge-database")
@login_required
def purge_database_test():
    user_obj = User.query.filter_by(id=int(current_user.id)).first()

    if user_obj.username == "admin":
        logout_user()
        db.drop_all()
        db.create_all()
        db.session.commit()
        flash("Database purged", category="success")
        return redirect(url_for("home_page"))

    else:
        flash("You do not have the privilege to do this!", category="danger")
        return redirect(url_for("home_page"))
