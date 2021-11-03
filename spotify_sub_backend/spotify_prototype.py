import os
import sys
import json
import spotipy
import webbrowser
import spotipy.util as util
from json.decoder import JSONDecodeError

username = sys.argv[1] # Specifies cache file association
scope = "user-read-private user-read-playback-state user-modify-playback-state" # This is the app permissions

try:
    token = util.prompt_for_user_token(username, scope)
except (AttributeError, JSONDecodeError):
    os.remove(f".cache-{username}")
    token = util.prompt_for_user_token(username, scope)

spotifyObject = spotipy.Spotify(auth=token)
devices = spotifyObject.devices()
print(json.dumps(devices, sort_keys=True, indent=4))
deviceID = devices["devices"][0]["id"]

track = spotifyObject.current_user_playing_track()
print(json.dumps(track, sort_keys=True, indent=4)+'\n')
artist = track["item"]["artists"][0]["name"]
track = track["item"]["name"]

if artist != "":
    print("Currently playing " + artist + " - " + track)

user = spotifyObject.current_user()
displayName = user["display_name"]
follower = user["followers"]["total"]

while True:
    print("\n>>>Welcome to Spotify " + displayName + " :)")
    print("\n>>>You have " + str(follower) + " followers.")
    print("\n0 - search for an artist")
    print("\n1 - exit\n")
    choice = input("\nEnter your choice: ")

    if choice == "0":
        searchQuery = input("\nOk, what's their name?: ")
        searchResults = spotifyObject.search(searchQuery, 1, 0, "artist")

        artist = searchResults['artists']['items'][0]
        print(artist['name'])
        print(str(artist['followers']['total']) + " followers")
        print(artist['genres'][0]+"\n")
        webbrowser.open(artist['images'][0]['url'])
        artistID = artist['id']

        trackURIS = []
        trackArt = []
        z = 0

        albumResults = spotifyObject.artist_albums(artistID)
        albumResults = albumResults['items']

        for item in albumResults:
            print("ALBUM: " + item['name'])
            albumID = item['id']
            albumArt = item['images'][0]['url']

            trackResults = spotifyObject.album_tracks(albumID)
            trackResults = trackResults['items']

            for item in trackResults:
                print(str(z) + ": " + item['name'])
                trackURIS.append(item['uri'])
                trackArt.append(albumArt)
                z+=1
            print()

        while True:
            songSelection = input("Enter a song number to see the album art: ")
            if songSelection == "x":
                break
            trackSelectionList = []
            trackSelectionList.append(trackURIS[int(songSelection)])
            spotifyObject.start_playback(deviceID, None, trackSelectionList)
            webbrowser.open(trackArt[int(songSelection)])

    if choice == "1":
        break
    

