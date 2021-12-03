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
    return redirect(auth_url)

@app.route("/spotify-callback/")  # There is going to be a REST variable here (code?v=...)
@login_required
def spotify_callback():
    """Captures the refresh and access tokens from the Spotify API and appends them to the User's db entry"""
    code = request.args.get('code') # Capture the refresh token from query string

    auth_token_url = f"{API_BASE}/api/token" # Spotify resource URL to retrieve User token

    # Post the following json information to the Spotify API and store the response
    res = requests.post(auth_token_url, data={
        "grant_type":"authorization_code",
        "code":code,
        "redirect_uri":"http://127.0.0.1:9874/spotify-callback/",
        "client_id": CLI_ID,
        "client_secret": CLI_SECRET
        })

    res_body = res.json() # Convert response to JSON
    access_token = res_body.get("access_token") # Retrieve access token
    
    # Append the access token and refresh token to the User
    user_obj = User.query.filter_by(id=int(current_user.id)).first()
    user_obj.spotify_key = access_token
    user_obj.spotify_refresh = code
    db.session.commit()

    flash("Spotify added successfully!", category="success")
    return redirect(url_for("home_page"))

def refresh_token(user_id):
    user_obj = User.query.filter_by(id=int(user_id)).first()
    auth_token_url = f"{API_BASE}/api/token" # Spotify resource URL to retrieve User token

    res = requests.post(auth_token_url, data={
        "grant_type":"authorization_code",
        "code":user_obj.spotify_refresh,
        "redirect_uri":"http://127.0.0.1:9874/spotify-callback/",
        "client_id": CLI_ID,
        "client_secret": CLI_SECRET
        })

    res_body = res.json() # Convert response to JSON
    access_token = res_body.get("access_token") # Retrieve access token
    
    # Append the access token and refresh token to the User
    user_obj.spotify_key = access_token
    db.session.commit()


def return_formatted_query(user_id, song_title, artist_name=None, limit=20):
    """Handles the formatting of a POST query from the player page, returns list of songs"""

    # Here need to retrieve the requesting user's spotify key in order to search
    user_obj = User.query.filter_by(id=int(user_id)).first()
    user_token = user_obj.spotify_key
    spotifyObject = spotipy.Spotify(auth=user_token)

    # Perform the search using SpotiPy interface
    try:
        if artist_name != None:
            searchResults = spotifyObject.search(song_title + " " + artist_name, limit=limit, offset=0, type="track,artist")
        else:
            searchResults = spotifyObject.search(song_title, limit=limit, offset=0, type="track")

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

        # Return the formatted list of songs
        return formattedResults
    except spotipy.exceptions.SpotifyException:
        refresh_token(user_id)
    

def startPlayback(user_id, session_id, song_title, trackURI,):

    for user_obj in User.query.filter_by(session_id=str(session_id)).all(): # Need to loop through this for all users in session and play
        user_token = user_obj.spotify_key
        spotifyObject = spotipy.Spotify(auth=user_token)
        spotifyObject.start_playback(uris=[trackURI])

    return


def convertTime(ms):
    seconds=int((ms/1000)%60)
    if len(str(seconds)) == 1:
        seconds = str(seconds) + "0"
    minutes=int((ms/(1000*60))%60)
    
    return (f"{minutes}:{seconds}")