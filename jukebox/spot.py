from jukebox import app
from jukebox import db
from flask import (
    redirect,
    url_for,
    flash,
    request,
    session
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
import requests

API_BASE = "https://accounts.spotify.com"
REDIRECT_URI = "http://127.0.0.1:9874/spotify-callback/"
SCOPE = "user-read-private user-read-playback-state user-modify-playback-state"
SHOW_DIALOG = True
CLI_ID = "d5bf099821e44c9ebf883855e178c731"
CLI_SECRET = "8ac58375e2474fb096fe663d727e9ee2"

"""Definitely need to remove these at some point"""

@app.route("/spotify-add")
@login_required
def spotify_add():
    """Initial route that leads from the home page to the spotify permission page"""
    auth_url = f'{API_BASE}/authorize?client_id={CLI_ID}&response_type=code&redirect_uri={REDIRECT_URI}&scope={SCOPE}&show_dialog={SHOW_DIALOG}'
    print(auth_url)
    return redirect(auth_url)

@app.route("/spotify-callback/")  # There is going to be a REST variable here (code?v=...)
@login_required
def spotify_callback():
    code = request.args.get('code')

    auth_token_url = f"{API_BASE}/api/token"
    res = requests.post(auth_token_url, data={
        "grant_type":"authorization_code",
        "code":code,
        "redirect_uri":"http://127.0.0.1:9874/spotify-callback/",
        "client_id": CLI_ID,
        "client_secret": CLI_SECRET
        })

    res_body = res.json()
    access_token = res_body.get("access_token")
    
    user_obj = User.query.filter_by(id=int(current_user.id)).first()
    user_obj.spotify_key = access_token
    db.session.commit()

    flash("Spotify added successfully!", category="success")
    return redirect(url_for("home_page"))

def return_formatted_query(user_id, searchQuery, limit=20):
    user_obj = User.query.filter_by(id=int(user_id)).first()
    user_token = user_obj.spotify_key
    spotifyObject = spotipy.Spotify(auth=user_token)

    searchResults = spotifyObject.search(searchQuery, limit=limit, offset=0, type="track")

    formattedResults = []
    for song, idx in zip(searchResults["tracks"]["items"], range(len(searchResults["tracks"]["items"]))):
        dic = {
            "id": idx,
            "title": song["name"],
            "artist": song["artists"][0]["name"],
            "album": song["album"]["name"],
            "length": convertTime(song["duration_ms"]),
            "album_image_url": song["album"]["images"][2]["url"],
            "playback_uri":  song["uri"]
            }
        formattedResults.append(dic)

    return formattedResults

def startPlayback(user_id, session_id, song_title, trackURI,):
    user_obj = User.query.filter_by(id=int(user_id)).first() # Need to loop through this for all users in session and play
    user_token = user_obj.spotify_key
    spotifyObject = spotipy.Spotify(auth=user_token)

    spotifyObject.start_playback(uris=[trackURI])

    return


def convertTime(ms):
    seconds=int((ms/1000)%60)
    minutes=int((ms/(1000*60))%60)

    return (f"{minutes}:{seconds}")