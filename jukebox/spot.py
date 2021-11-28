from jukebox import app
from jukebox import db
from flask import (
    redirect,
    url_for,
    flash,
    request,
    g
)
from jukebox.models import User, Session, Song
from jukebox import db
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import BadRequestKeyError

import os
import sys
import json
import spotipy
import webbrowser
import spotipy.util as util
from json.decoder import JSONDecodeError

"""Definitely need to remove these at some point"""
os.environ["SPOTIPY_CLIENT_ID"] = "d5bf099821e44c9ebf883855e178c731"
os.environ["SPOTIPY_CLIENT_SECRET"] = "8ac58375e2474fb096fe663d727e9ee2"
os.environ["SPOTIPY_REDIRECT_URI"] = "http://127.0.0.1:5000/spotify-success/"

@app.route("/spotify-add")
@login_required
def spotify_add():
    """Initial route that leads from the home page to the spotify permission page"""
    get_user_access(str(current_user.username))

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

def return_formatted_query(user_id, searchQuery):
    user_obj = User.query.filter_by(id=int(user_id)).first()
    user_token = user_obj.spotify_key
    print(user_token)
    spotifyObject = spotipy.Spotify(auth=user_token)

    searchResults = spotifyObject.search(searchQuery, limit=10, offset=0, type="track")
    formattedResults = []

    for song, idx in zip(searchResults["tracks"]["items"], range(len(searchResults["tracks"]["items"]))):
        dic = {
            "id": idx,
            "title": song["name"],
            "artist": song["artists"][0]["name"],
            "album": song["album"]["name"],
            "length": song["duration_ms"],
            "album_image_url": song["album"]["images"][2]["url"],
            "playback_uri":  song["uri"]
            }
        formattedResults.append(dic)

    return formattedResults



def get_user_access(username):
    scope = "user-read-playback-state user-modify-playback-state"

    util.prompt_for_user_token(
        username,
        scope,
    )

    # Should take us to spotify-success/<key> route