import os
import sys
import json
import spotipy
import webbrowser
import spotipy.util as util
from json.decoder import JSONDecodeError

"""Definitely need to remove these at some point"""
client_id = "d5bf099821e44c9ebf883855e178c731"  # SPOTIPY_CLIENT_ID
client_secret = "8ac58375e2474fb096fe663d727e9ee2"  # SPOTIPY_CLIENT_SECRET
redirect_URI = "http://127.0.0.1:5000/spotify-success/"  # SPOTIPY_REDIRECT_URI


def get_user_access(username):
    scope = "user-read-playback-state user-modify-playback-state"

    token = util.prompt_for_user_token(
        username,
        scope,
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_URI,
    )

    #os.remove(f".cache-{username}")
    """
    except (AttributeError, JSONDecodeError):
        os.remove(f".cache-{username}")
        token = util.prompt_for_user_token(
            username,
            scope,
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_URI,
        )
    """
    # Should take us to spotify-success/<key> route