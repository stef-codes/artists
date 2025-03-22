import streamlit as st
import os
import requests
import base64
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Spotify API Credentials
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE_URL = "https://api.spotify.com/v1/"

def get_spotify_token():
    """Authenticate and get an access token"""
    auth_string = f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}"
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = base64.b64encode(auth_bytes).decode("utf-8")
    
    headers = {
        "Authorization": f"Basic {auth_base64}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    data = {"grant_type": "client_credentials"}
    response = requests.post(SPOTIFY_TOKEN_URL, headers=headers, data=data)
    json_result = response.json()
    return json_result.get("access_token")

def search_artist(token, artist_name):
    """Search for an artist by name"""
    headers = {"Authorization": f"Bearer {token}"}
    query = f"?q={artist_name}&type=artist&limit=1"
    response = requests.get(SPOTIFY_API_BASE_URL + "search" + query, headers=headers)
    
    if response.status_code == 200:
        json_result = response.json()
        if json_result["artists"]["items"]:
            return json_result["artists"]["items"][0]
    return None

# Streamlit UI
st.title("Spotify Artist Search")
artist_name = st.text_input("Enter Artist Name:")

if st.button("Search"):
    if artist_name:
        token = get_spotify_token()
        if token:
            artist = search_artist(token, artist_name)
            if artist:
                st.success(f"**Artist Found: {artist['name']}**")
                st.image(artist["images"][0]["url"] if artist.get("images") else None, width=200)
                st.write(f"**Popularity:** {artist['popularity']}/100")
                st.write(f"**Genres:** {', '.join(artist['genres']) if artist['genres'] else 'N/A'}")
                st.write(f"**Followers:** {artist['followers']['total']:,}")
                st.write(f"[Spotify Profile]({artist['external_urls']['spotify']})")
            else:
                st.error("Artist not found.")
        else:
            st.error("Failed to authenticate with Spotify API.")
    else:
        st.warning("Please enter an artist name.")
